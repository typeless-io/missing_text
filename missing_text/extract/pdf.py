import pymupdf  # PyMuPDF
import io
import json
import base64
from typing import Dict, Any, List, Union, Optional
import pandas as pd
import pytesseract
from PIL import Image
import logging
import asyncio
from .utils import DecimalEncoder
import os
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)


class PDFProcessingError(Exception):
    """Custom exception for errors during PDF processing."""

    pass


class SafeModeConfig:
    """
    Configuration class for safe mode.

    Attributes:
        enabled (bool): Whether safe mode is enabled.
        base_directory (Path): The base directory for file operations when safe mode is enabled.
        allowed_extensions (set): Set of allowed file extensions when safe mode is enabled.
    """

    def __init__(
        self,
        enabled: bool = True,
        base_directory: Optional[Union[str, Path]] = None,
        allowed_extensions: Optional[set] = None,
    ):
        self.enabled = enabled
        self.base_directory = Path(base_directory or Path.cwd()).resolve()
        self.allowed_extensions = allowed_extensions or {".pdf"}

    def __str__(self):
        return f"SafeModeConfig(enabled={self.enabled}, base_directory='{self.base_directory}', allowed_extensions={self.allowed_extensions})"


# Initialize default SafeModeConfig
SAFE_MODE_CONFIG = SafeModeConfig()


def set_safe_mode(
    enabled: bool,
    base_directory: Optional[Union[str, Path]] = None,
    allowed_extensions: Optional[set] = None,
):
    """
    Set the safe mode configuration.

    Args:
        enabled (bool): Whether to enable safe mode.
        base_directory (Optional[Union[str, Path]]): The base directory for file operations when safe mode is enabled.
        allowed_extensions (Optional[set]): Set of allowed file extensions when safe mode is enabled.

    Note:
        Safe mode, when enabled, provides the following security measures:
        1. Restricts file access to the specified base directory and its subdirectories.
        2. Allows only specified file extensions to be processed.
        3. Prevents potential path traversal attacks.

        When disabled, these restrictions are lifted, but it may expose your application to security risks.
        Use with caution and only in trusted environments.
    """
    global SAFE_MODE_CONFIG
    SAFE_MODE_CONFIG = SafeModeConfig(enabled, base_directory, allowed_extensions)
    logger.info(f"Safe mode configuration updated: {SAFE_MODE_CONFIG}")


def _is_running_async() -> bool:
    """
    Helper function to detect if the current execution context is asynchronous.

    Returns:
        bool: True if running in an asynchronous context, False otherwise.
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


### HELPER FUNCTIONS ###


def _get_page_count(doc: pymupdf.Document) -> int:
    """Returns the number of pages in a PDF document."""
    return len(doc)


def _extract_text_from_page(page: pymupdf.Page) -> str:
    """Extracts text from a single PDF page."""
    return page.get_text()


def _extract_tables_from_page(page: pymupdf.Page) -> List[Dict[str, Any]]:
    """Extracts tables from a single PDF page using pandas."""
    tables = page.find_tables()
    result = []
    for table in tables:
        df = pd.DataFrame(table.extract())
        result.append(
            {
                "content": json.loads(
                    json.dumps(df.to_dict(orient="records"), cls=DecimalEncoder)
                ),
                "metadata": {"columns": list(df.columns), "shape": df.shape},
            }
        )
    return result


def _extract_images_from_page(
    page: pymupdf.Page, doc: pymupdf.Document
) -> List[Dict[str, Any]]:
    """Extracts images from a single PDF page and applies OCR."""
    images = []
    image_list = page.get_images(full=True)
    if not image_list:
        logger.info(f"No images found on page {page.number + 1}")

    for img in image_list:
        xref = img[0]
        base_image = doc.extract_image(xref)
        if base_image:
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            ocr_text = pytesseract.image_to_string(image)
            images.append(
                {
                    "content": ocr_text,
                    "image_data": base64.b64encode(image_bytes).decode("utf-8"),
                    "xref": xref,
                }
            )
    return images


### SYNCHRONOUS FUNCTIONS ###


def validate_path(file_path: Union[str, Path], safe_mode: bool = True) -> Path:
    """Validate and resolve the given file path."""
    path = Path(file_path).resolve()
    if safe_mode:
        if not path.is_relative_to(SAFE_MODE_CONFIG.base_directory):
            raise PDFProcessingError(
                f"Access denied: {path} is outside the allowed directory."
            )
        if path.suffix.lower() not in SAFE_MODE_CONFIG.allowed_extensions:
            raise PDFProcessingError(f"Invalid file type: {path.suffix}")
    return path


def with_safe_mode(func):
    """
    Decorator to allow toggling safe mode for individual function calls.
    """

    def wrapper(*args, safe_mode=True, **kwargs):
        global SAFE_MODE_CONFIG
        original_safe_mode = SAFE_MODE_CONFIG.enabled
        SAFE_MODE_CONFIG.enabled = safe_mode
        try:
            return func(*args, **kwargs)
        finally:
            SAFE_MODE_CONFIG.enabled = original_safe_mode

    return wrapper


@with_safe_mode
def sync_extract_pdf(
    input_data: Union[bytes, str, Path], safe_mode: bool = True
) -> Dict[str, Any]:
    """
    Extracts page-separated text, images, and tables from the given PDF file (synchronously).

    Args:
        input_data (Union[bytes, str, Path]): The in-memory content of the PDF (bytes) or the file path (str or Path).
        safe_mode (bool, optional): Whether to enable safe mode for this function call. Defaults to True.

    Returns:
        Dict[str, Any]: A dictionary with page-separated text, images, and tables.
    """
    try:
        if isinstance(input_data, bytes):
            doc = pymupdf.open(stream=input_data, filetype="pdf")
        else:
            file_path = validate_path(input_data, safe_mode=safe_mode)
            if not file_path.is_file():
                raise PDFProcessingError(f"File not found: {file_path}")
            doc = pymupdf.open(str(file_path))

        total_pages = _get_page_count(doc)
        extracted_content = {"pages": []}

        for page_num in range(total_pages):
            page = doc[page_num]
            logger.info(f"Processing page {page_num + 1}/{total_pages}")

            # Extract text, tables, and images for the current page
            page_content = {
                "text": _extract_text_from_page(page),
                "tables": _extract_tables_from_page(page),
                "images": _extract_images_from_page(page, doc),
            }

            extracted_content["pages"].append(page_content)

        logger.info("PDF processing complete")
        return extracted_content

    except (ValueError, RuntimeError) as e:
        raise PDFProcessingError(f"Invalid or corrupted PDF file: {str(e)}")
    except FileNotFoundError as e:
        raise PDFProcessingError(f"File not found: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to extract content from PDF: {str(e)}")
        raise PDFProcessingError(f"Failed to extract content from PDF: {str(e)}")


def sync_extract_pdfs_from_directory(
    directory_path: Union[str, Path], safe_mode: bool = True
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Synchronously extracts content from all PDF files in a given directory and its subdirectories.

    Args:
        directory_path (Union[str, Path]): Path to the directory containing PDF files.
        safe_mode (bool, optional): Whether to enable safe mode for this extraction. Defaults to True.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Extracted content from all PDFs.
    """
    extracted_data = {}
    directory = validate_path(directory_path, safe_mode=safe_mode)
    if not directory.is_dir():
        raise PDFProcessingError(f"Not a directory: {directory}")

    for file_path in traverse_directory(directory_path, safe_mode=safe_mode):
        try:
            extracted_content = sync_extract_pdf(file_path, safe_mode=safe_mode)
            extracted_data[str(file_path.relative_to(directory_path))] = (
                extracted_content
            )
            logger.info(f"Processed {file_path}")
        except PDFProcessingError as e:
            logger.error(f"Error processing {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")

    return extracted_data


# def extract_pdfs(input_path: Union[str, bytes]) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
#     """
#     Dynamically processes either a single PDF file or all PDFs in a directory.

#     Args:
#         input_path (Union[str, bytes]): Path to a PDF file, directory, or in-memory PDF bytes.

#     Returns:
#         Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
#         - If a single PDF, returns extracted content for that PDF.
#         - If a directory, returns a dictionary where each key is a PDF file name, and the value is its extracted content.
#     """
#     if isinstance(input_path, bytes):
#         # Process in-memory PDF bytes
#         return sync_extract_pdf(input_path)

#     elif os.path.isdir(input_path):
#         # Process all PDFs in a directory
#         return sync_extract_pdfs_from_directory(input_path)

#     elif os.path.isfile(input_path) and input_path.endswith(".pdf"):
#         # Process a single PDF file
#         return sync_extract_pdf(input_path)

#     else:
#         raise PDFProcessingError(f"Invalid input: {input_path} is neither a valid PDF file nor a directory.")


### ASYNCHRONOUS FUNCTIONS ###


async def async_extract_pdf(
    input_data: Union[bytes, str, Path], safe_mode: bool = True
) -> Dict[str, Any]:
    """
    Asynchronously extracts page-separated text, images, and tables from a PDF file.

    Args:
        input_data (Union[bytes, str, Path]): The in-memory content of the PDF (bytes) or the file path (str or Path).
        safe_mode (bool, optional): Whether to enable safe mode for this extraction. Defaults to True.

    Returns:
        Dict[str, Any]: A dictionary with page-separated text, images, and tables.
    """
    try:
        if isinstance(input_data, bytes):
            doc = pymupdf.open(stream=input_data, filetype="pdf")
        else:
            file_path = validate_path(input_data, safe_mode=safe_mode)
            if not file_path.is_file():
                raise PDFProcessingError(f"File not found: {file_path}")
            doc = pymupdf.open(str(file_path))

        total_pages = _get_page_count(doc)
        extracted_content = {"pages": []}

        for i in range(total_pages):
            page = doc[i]
            logger.info(f"Processing page {i + 1}/{total_pages}")

            # Extract text, tables, and images for the current page
            page_content = {
                "text": _extract_text_from_page(page),
                "tables": _extract_tables_from_page(page),
                "images": _extract_images_from_page(page, doc),
            }

            extracted_content["pages"].append(page_content)

            await asyncio.sleep(0)  # Yield control back to the event loop

        logger.info("Asynchronous PDF processing complete")
        return extracted_content

    except (ValueError, RuntimeError) as e:
        raise PDFProcessingError(f"Invalid or corrupted PDF file: {str(e)}")
    except FileNotFoundError as e:
        raise PDFProcessingError(f"File not found: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to extract content from PDF: {str(e)}")
        raise PDFProcessingError(f"Failed to extract content from PDF: {str(e)}")


async def async_extract_pdfs_from_directory(
    directory_path: Union[str, Path], safe_mode: bool = True
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Asynchronously extracts content from all PDF files in a given directory and its subdirectories.

    Args:
        directory_path (Union[str, Path]): Path to the directory containing PDF files.
        safe_mode (bool, optional): Whether to enable safe mode for this extraction. Defaults to True.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary where each key is a PDF file name,
        and the value is the extracted content for that PDF.
    """
    extracted_data = {}
    directory = validate_path(directory_path, safe_mode=safe_mode)
    if not directory.is_dir():
        raise PDFProcessingError(f"Not a directory: {directory}")

    for file_path in traverse_directory(directory_path, safe_mode=safe_mode):
        try:
            extracted_content = await async_extract_pdf(file_path, safe_mode=safe_mode)
            extracted_data[str(file_path.relative_to(directory_path))] = (
                extracted_content
            )
            logger.info(f"Processed {file_path}")
        except PDFProcessingError as e:
            logger.error(f"Error processing {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")

    return extracted_data


### MAIN EXTRACTION FUNCTION ###


def extract_pdfs(
    input_path: Union[str, bytes, Path], safe_mode: bool = True
) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Dynamically processes either a single PDF file or all PDFs in a directory,
    using either synchronous or asynchronous extraction based on the current context.

    Args:
        input_path (Union[str, bytes, Path]): Path to a PDF file, directory, or in-memory PDF bytes.
        safe_mode (bool, optional): Whether to enable safe mode for this function call. Defaults to True.

    Returns:
        Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
        - If a single PDF, returns extracted content for that PDF.
        - If a directory, returns a dictionary where each key is a PDF file name, and the value is its extracted content.

    Example:
            {
                "pdf_file_1.pdf": {
                    "pages": [
                        {"text": "Page 1 content", "images": [...], "tables": [...]},
                        {"text": "Page 2 content", "images": [...], "tables": [...]}
                    ]
                },
                "pdf_file_2.pdf": {
                    "pages": [
                        {"text": "Page 1 content", "images": [...], "tables": [...]}
                    ]
                }
            }
    """
    if _is_running_async():
        # Running in an asynchronous context, call the async version
        return asyncio.create_task(extract_pdfs_async(input_path, safe_mode=safe_mode))
    else:
        # Running in a synchronous context, call the sync version
        return extract_pdfs_sync(input_path, safe_mode=safe_mode)


def extract_pdfs_sync(
    input_path: Union[str, bytes, Path], safe_mode: bool = True
) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Synchronous function to process PDFs (single or directory).
    """
    if isinstance(input_path, bytes):
        return sync_extract_pdf(input_path, safe_mode=safe_mode)

    path = validate_path(input_path, safe_mode=safe_mode)
    if path.is_dir():
        return sync_extract_pdfs_from_directory(path, safe_mode=safe_mode)
    elif path.is_file():
        return sync_extract_pdf(path, safe_mode=safe_mode)
    else:
        raise PDFProcessingError(
            f"Invalid input: {path} is neither a valid PDF file nor a directory."
        )


async def extract_pdfs_async(
    input_path: Union[str, bytes, Path], safe_mode: bool = True
) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Asynchronous function to process PDFs (single or directory).
    """
    if isinstance(input_path, bytes):
        return await async_extract_pdf(input_path, safe_mode=safe_mode)

    path = validate_path(input_path, safe_mode=safe_mode)
    if path.is_dir():
        return await async_extract_pdfs_from_directory(path, safe_mode=safe_mode)
    elif path.is_file():
        return await async_extract_pdf(path, safe_mode=safe_mode)
    else:
        raise PDFProcessingError(
            f"Invalid input: {path} is neither a valid PDF file nor a directory."
        )


def traverse_directory(
    directory_path: Union[str, Path], safe_mode: bool = True
) -> List[Path]:
    """
    Traverse a directory and its subdirectories to find all files with allowed extensions.

    Args:
        directory_path (Union[str, Path]): The directory to traverse.

    Returns:
        List[Path]: A list of Path objects for all valid files found.
    """
    directory = validate_path(directory_path, safe_mode=safe_mode)
    if not directory.is_dir():
        raise PDFProcessingError(f"Not a directory: {directory}")

    valid_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            try:
                file_path = validate_path(Path(root) / file, safe_mode=safe_mode)
                valid_files.append(file_path)
            except PDFProcessingError as e:
                logger.warning(f"Skipping file: {file}. Reason: {str(e)}")

    return valid_files
