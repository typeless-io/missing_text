import pymupdf  # PyMuPDF
from pymupdf import Rect
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
    """
    Returns the number of pages in a PDF document.

    Args:
        doc (pymupdf.Document): The PDF document.

    Returns:
        int: The total number of pages in the PDF.
    """
    try:
        return len(doc)
    except Exception as e:
        logger.exception(f"Error getting page count: {str(e)}")
        return 0


def _extract_text_from_page(page: pymupdf.Page, page_num: int) -> Dict[str, Any]:
    """
    Extracts text from a single PDF page.

    Args:
        page (pymupdf.Page): The PDF page to extract text from.
        page_num (int): The 0-based page number.

    Returns:
        Dict[str, Any]: A dictionary containing the page number and the extracted text content.
    """
    try:
        text = page.get_text()
        return {"page_number": page_num + 1, "content": text}
    except Exception as e:
        logger.exception(f"Error extracting text from page {page_num + 1}: {e}")
        return {
            "page_number": page_num + 1,
            "content": f"Error: Unable to extract text from page {page_num + 1}",
        }


def _extract_tables_from_page(page: pymupdf.Page, page_num: int) -> List[Dict[str, Any]]:
    """
    Extracts tables from a single PDF page using PyMuPDF.

    Args:
        page (pymupdf.Page): The PDF page to extract tables from.
        page_num (int): The 0-based page number.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing the page number,
                              extracted table content, and metadata (columns and shape).
    """
    try:
        tables = page.find_tables()
        result = []
        for table in tables:
            df = pd.DataFrame(table.extract())
            result.append(
                {
                    "page_number": page_num + 1,
                    "content": json.loads(
                        json.dumps(df.to_dict(orient="records"), cls=DecimalEncoder)
                    ),
                    "metadata": {"columns": list(df.columns), "shape": df.shape},
                }
            )
        return result
    except Exception as e:
        logger.exception(f"Error extracting tables from page {page_num + 1}: {e}")
        return []


def _extract_images_from_page(
    page: pymupdf.Page, doc: pymupdf.Document, page_num: int
) -> List[Dict[str, Any]]:
    """
    Extracts images from a single PDF page and applies OCR.

    Args:
        page (pymupdf.Page): The PDF page to extract images from.
        doc (pymupdf.Document): The entire PDF document to extract image data.
        page_num (int): The 0-based page number.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing the page number,
                              OCR'd image content, and image data (base64 encoded).
    """
    images = []
    try:
        image_list = page.get_images(full=True)
        if not image_list:
            logger.info(f"No images found on page {page.number + 1}")
        else:
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    if base_image and base_image["image"]:
                        image_bytes = base_image["image"]
                        image = Image.open(io.BytesIO(image_bytes))
                        images.append({
                            "page_number": page_num + 1,
                            "content": pytesseract.image_to_string(image),
                            "image_data": base64.b64encode(image_bytes).decode('utf-8')
                        })
                    else:
                        logger.warning(f"Skipping image on page {page_num + 1}: Unable to extract image data")
                except ValueError as e:
                    logger.warning(f"Skipping image on page {page_num + 1} due to ValueError: {str(e)}")
                except Exception as e:
                    logger.exception(f"Error processing image on page {page_num + 1}: {str(e)}")
    except Exception as e:
        logger.exception(f"Error extracting images from page {page_num + 1}: {str(e)}")
    return images


def _convert_page_as_image(page: pymupdf.Page, page_num: int, zoom: float = 2.0) -> Dict[str, Any]:
    """
    Converts a single PDF page to an image and encodes it in base64.

    Args:
        page (pymupdf.Page): The PDF page to convert to an image.
        page_num (int): The 0-based page number.
        zoom (float): Zoom factor for the image resolution. Defaults to 2.0 (approx 144 dpi).

    Returns:
        Dict[str, Any]: A dictionary containing the page number, the base64-encoded image, and the zoom factor.
    """
    try:
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        return {
            "page_number": page_num + 1,
            "image": base64.b64encode(img_byte_arr).decode('utf-8'),
            "zoom": zoom
        }
    except Exception as e:
        logger.exception(f"Error converting page {page_num + 1} to image: {e}")
        return {
            "page_number": page_num + 1,
            "image": None,
            "error": f"Error converting page {page_num + 1} to image",
            "zoom": zoom
        }


def _extract_segments_from_page(page: pymupdf.Page, doc: pymupdf.Document, page_num: int) -> Dict[str, Any]:
    """
    Extracts and categorizes different content segments from a PDF page.

    This function identifies text blocks, images, tables, charts, and LaTeX-like content,
    assigning bounding boxes and content information to each segment.

    Args:
        page (pymupdf.Page): A PyMuPDF page object.
        doc (pymupdf.Document): The PyMuPDF document object.
        page_num (int): The 0-based page number.

    Returns:
        Dict[str, Any]: A dictionary containing the page number and a list of segments,
                        where each segment is a dictionary with type, content, and bounding box.
    """
    segments = []
    try:
        # Extract text segments
        text_blocks = page.get_text("blocks")
        for block in text_blocks:
            segments.append({"type": "text", "content": block[4], "bbox": block[:4]})

        # Extract image segments
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                if base_image and base_image["image"]:
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    # Get image bounding box
                    image_rect = page.get_image_bbox(img)
                    segments.append(
                        {
                            "type": "image",
                            "content": pytesseract.image_to_string(image),
                            "bbox": list(image_rect),
                            "image_data": base64.b64encode(image_bytes).decode("utf-8"),
                        }
                    )
                else:
                    logger.warning(f"Skipping image on page {page_num + 1}: Unable to extract image data")
            except pymupdf.FileDataError as e:
                logger.warning(f"Skipping image on page {page_num + 1} due to FileDataError: {str(e)}")
            except ValueError as e:
                logger.warning(f"Skipping image on page {page_num + 1} due to ValueError: {str(e)}")
                try:
                    image_rect = page.get_image_bbox(xref)
                    segments.append(
                        {
                            "type": "image",
                            "content": "Image data not available",
                            "bbox": list(image_rect),
                        }
                    )
                except Exception as inner_e:
                    logger.warning(f"Unable to get bounding box for image on page {page_num + 1}: {str(inner_e)}")
            except Exception as e:
                logger.exception(f"Error processing image on page {page_num + 1}: {str(e)}")

        # Extract table segments (using PyMuPDF's find_tables)
        tables = page.find_tables()
        for table in tables:
            segments.append(
                {
                    "type": "table",
                    "content": f"Table ({len(table.cells)} cells)",
                    "bbox": list(table.bbox),
                }
            )

        # Attempt to detect charts (this is a simple heuristic and may need refinement)
        drawings = page.get_drawings()
        for drawing in drawings:
            if len(drawing["items"]) > 10:  # Assume it's a chart if it has many drawing items
                bbox = Rect(drawing["rect"])
                segments.append(
                    {"type": "chart", "content": "Possible chart", "bbox": list(bbox)}
                )

        # Detect LaTeX-like content (simple heuristic, may need refinement)
        latex_patterns = [r"\begin{equation}", r"\end{equation}", r"\frac{", r"\sum_"]
        for block in text_blocks:
            if any(pattern in block[4] for pattern in latex_patterns):
                segments.append(
                    {"type": "latex", "content": block[4], "bbox": block[:4]}
                )

    except Exception as e:
        logger.exception(f"Error extracting segments from page {page_num + 1}: {str(e)}")

    return {"page_number": page_num + 1, "segments": segments}


### SYNCHRONOUS FUNCTIONS ###


def validate_path(file_path: Union[str, Path], safe_mode: bool = True) -> Path:
    """Validate and resolve the given file path."""
    path = Path(file_path).resolve()
    if safe_mode:
        # If it's a directory, no need to check for file extension
        if path.is_dir():
            if not path.is_relative_to(SAFE_MODE_CONFIG.base_directory):
                raise PDFProcessingError(f"Access denied: {path} is outside the allowed directory.")
            return path

        # Check if the file is within the safe root directory
        if not path.is_relative_to(SAFE_MODE_CONFIG.base_directory):
            raise PDFProcessingError(f"Access denied: {path} is outside the allowed directory.")

        # Validate file extension if it's a file
        if path.suffix.lower() not in SAFE_MODE_CONFIG.allowed_extensions:
            raise PDFProcessingError(f"Invalid file type: {path.suffix}")

    return path


def with_safe_mode(func):
    """
    Decorator to allow toggling safe mode for individual function calls.
    """

    def wrapper(*args, **kwargs):
        # Extract safe_mode from kwargs or use default (True)
        safe_mode = kwargs.get("safe_mode", True)

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
    input_data: Union[bytes, str, Path],
    safe_mode: bool = True,
    text: bool = True,
    table: bool = True,
    image: bool = True,
    encode_page: bool = True,
    segment: bool = True,
    zoom: float = 2.0
) -> Dict[str, Any]:
    """
    Extracts page-separated text, images, tables, and other content from the given PDF file (synchronously).

    Args:
        input_data (Union[bytes, str, Path]): The in-memory content of the PDF (as bytes) or the file path (as str or Path).
                                              If a byte stream is provided, it directly loads the PDF content.
                                              If a file path is provided, it validates the file's existence and opens it.
        safe_mode (bool, optional): Whether to enable safe mode for file handling. Defaults to True.
        text (bool, optional): Whether to extract text content. Defaults to True.
        table (bool, optional): Whether to extract tables. Defaults to True.
        image (bool, optional): Whether to extract images. Defaults to True.
        encode_page (bool, optional): Whether to encode and extract each PDF page as an image. Defaults to True.
        segment (bool, optional): Whether to extract and categorize different content segments. Defaults to True.
        zoom (float, optional): Zoom factor for page image rendering. Defaults to 2.0.

    Returns:
        Dict[str, Any]: A dictionary containing extracted content from the PDF.
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
        extracted_content = {}

        for page_num in range(total_pages):
            page = doc[page_num]
            logger.info(f"Processing page {page_num + 1}/{total_pages}")

            if text:
                extracted_content.setdefault("text", []).append(_extract_text_from_page(page, page_num))

            if table:
                extracted_content.setdefault("tables", []).extend(_extract_tables_from_page(page, page_num))

            if image:
                extracted_content.setdefault("images", []).extend(_extract_images_from_page(page, doc, page_num))

            if encode_page:
                extracted_content.setdefault("pages", []).append(_convert_page_as_image(page, page_num, zoom=zoom))

            if segment:
                extracted_content.setdefault("segments", []).append(_extract_segments_from_page(page, doc, page_num))

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
    directory_path: Union[str, Path],
    safe_mode: bool = True,
    text: bool = True,
    table: bool = True,
    image: bool = True,
    encode_page: bool = True,
    segment: bool = True,
    zoom: float = 2.0
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Synchronously extracts content from all PDF files in a given directory.

    Args:
        directory_path (Union[str, Path]): Path to the directory containing PDF files.
        safe_mode (bool, optional): Whether to enable safe mode. Defaults to True.
        text (bool, optional): Whether to extract text. Defaults to True.
        table (bool, optional): Whether to extract tables. Defaults to True.
        image (bool, optional): Whether to extract images. Defaults to True.
        encode_page (bool, optional): Whether to encode page as image. Defaults to True.
        segment (bool, optional): Whether to extract content segments. Defaults to True.
        zoom (float, optional): Zoom factor for page image rendering. Defaults to 2.0.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Extracted content from all PDFs.
    """
    extracted_data = {}
    directory = validate_path(directory_path, safe_mode=safe_mode)
    if not directory.is_dir():
        raise PDFProcessingError(f"Not a directory: {directory}")

    for file_path in traverse_directory(directory_path, safe_mode=safe_mode):
        try:
            extracted_content = sync_extract_pdf(
                file_path,
                safe_mode=safe_mode,
                text=text,
                table=table,
                image=image,
                encode_page=encode_page,
                segment=segment,
                zoom=zoom
            )
            extracted_data[str(file_path.relative_to(directory_path))] = extracted_content
            logger.info(f"Processed {file_path}")
        except PDFProcessingError as e:
            logger.error(f"Error processing {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")

    return extracted_data

### ASYNCHRONOUS FUNCTIONS ###


async def async_extract_pdf(
    input_data: Union[bytes, str, Path],
    safe_mode: bool = True,
    text: bool = True,
    table: bool = True,
    image: bool = True,
    encode_page: bool = True,
    segment: bool = True,
    zoom: float = 2.0
) -> Dict[str, Any]:
    """
    Asynchronously extracts page-separated text, images, tables, and other content from a PDF file.

    Args:
        input_data (Union[bytes, str, Path]): The in-memory content of the PDF (bytes) or the file path (str or Path).
        safe_mode (bool, optional): Whether to enable safe mode. Defaults to True.
        text (bool, optional): Whether to extract text. Defaults to True.
        table (bool, optional): Whether to extract tables. Defaults to True.
        image (bool, optional): Whether to extract images. Defaults to True.
        encode_page (bool, optional): Whether to encode each page as an image. Defaults to True.
        segment (bool, optional): Whether to extract content segments. Defaults to True.
        zoom (float, optional): Zoom factor for page image rendering. Defaults to 2.0.

    Returns:
        Dict[str, Any]: A dictionary containing extracted content from the PDF.
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
        extracted_content = {}

        for page_num in range(total_pages):
            page = doc[page_num]
            logger.info(f"Processing page {page_num + 1}/{total_pages}")

            if text:
                extracted_content.setdefault("text", []).append(_extract_text_from_page(page, page_num))
            if table:
                extracted_content.setdefault("tables", []).extend(_extract_tables_from_page(page, page_num))
            if image:
                extracted_content.setdefault("images", []).extend(_extract_images_from_page(page, doc, page_num))
            if encode_page:
                extracted_content.setdefault("pages", []).append(_convert_page_as_image(page, page_num, zoom=zoom))
            if segment:
                extracted_content.setdefault("segments", []).append(_extract_segments_from_page(page, doc, page_num))

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
    directory_path: Union[str, Path],
    safe_mode: bool = True,
    text: bool = True,
    table: bool = True,
    image: bool = True,
    encode_page: bool = True,
    segment: bool = True,
    zoom: float = 2.0
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Asynchronously extracts content from all PDF files in a given directory.

    Args:
        directory_path (Union[str, Path]): Path to the directory containing PDF files.
        safe_mode (bool, optional): Whether to enable safe mode. Defaults to True.
        text (bool, optional): Whether to extract text. Defaults to True.
        table (bool, optional): Whether to extract tables. Defaults to True.
        image (bool, optional): Whether to extract images. Defaults to True.
        encode_page (bool, optional): Whether to encode each page as an image. Defaults to True.
        segment (bool, optional): Whether to extract content segments. Defaults to True.
        zoom (float, optional): Zoom factor for page image rendering. Defaults to 2.0.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Extracted content from all PDFs.
    """
    extracted_data = {}
    directory = validate_path(directory_path, safe_mode=safe_mode)
    if not directory.is_dir():
        raise PDFProcessingError(f"Not a directory: {directory}")

    for file_path in traverse_directory(directory_path, safe_mode=safe_mode):
        try:
            extracted_content = await async_extract_pdf(
                file_path,
                safe_mode=safe_mode,
                text=text,
                table=table,
                image=image,
                encode_page=encode_page,
                segment=segment,
                zoom=zoom
            )
            extracted_data[str(file_path.relative_to(directory_path))] = extracted_content
            logger.info(f"Processed {file_path}")
        except PDFProcessingError as e:
            logger.error(f"Error processing {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")

    return extracted_data


### MAIN EXTRACTION FUNCTION ###


def extract_pdfs(
    input_path: Union[str, bytes, Path],
    safe_mode: bool = True,
    text: bool = True,
    table: bool = True,
    image: bool = True,
    encode_page: bool = True,
    segment: bool = True,
    zoom: float = 2.0
) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Dynamically processes either a single PDF file or all PDFs in a directory,
    using either synchronous or asynchronous extraction based on the current context.

    Args:
        input_path (Union[str, bytes, Path]): Path to a PDF file, directory, or in-memory PDF bytes.
        safe_mode (bool, optional): Whether to enable safe mode. Defaults to True.
        text (bool, optional): Whether to extract text. Defaults to True.
        table (bool, optional): Whether to extract tables. Defaults to True.
        image (bool, optional): Whether to extract images. Defaults to True.
        encode_page (bool, optional): Whether to encode each page as an image. Defaults to True.
        segment (bool, optional): Whether to extract content segments. Defaults to True.
        zoom (float, optional): Zoom factor for page image rendering. Defaults to 2.0.

    Returns:
        Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]: Extracted content.
    """
    if _is_running_async():
        return asyncio.create_task(extract_pdfs_async(
            input_path,
            safe_mode=safe_mode,
            text=text,
            table=table,
            image=image,
            encode_page=encode_page,
            segment=segment,
            zoom=zoom
        ))
    else:
        return extract_pdfs_sync(
            input_path,
            safe_mode=safe_mode,
            text=text,
            table=table,
            image=image,
            encode_page=encode_page,
            segment=segment,
            zoom=zoom
        )

def extract_pdfs_sync(
    input_path: Union[str, bytes, Path],
    safe_mode: bool = True,
    text: bool = True,
    table: bool = True,
    image: bool = True,
    encode_page: bool = True,
    segment: bool = True,
    zoom: float = 2.0
) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Synchronous function to process PDFs (single or directory).
    """
    if isinstance(input_path, bytes):
        return sync_extract_pdf(
            input_path,
            safe_mode=safe_mode,
            text=text,
            table=table,
            image=image,
            encode_page=encode_page,
            segment=segment,
            zoom=zoom
        )

    path = validate_path(input_path, safe_mode=safe_mode)
    if path.is_dir():
        return sync_extract_pdfs_from_directory(
            path,
            safe_mode=safe_mode,
            text=text,
            table=table,
            image=image,
            encode_page=encode_page,
            segment=segment,
            zoom=zoom
        )
    elif path.is_file():
        return sync_extract_pdf(
            path,
            safe_mode=safe_mode,
            text=text,
            table=table,
            image=image,
            encode_page=encode_page,
            segment=segment,
            zoom=zoom
        )
    else:
        raise PDFProcessingError(
            f"Invalid input: {path} is neither a valid PDF file nor a directory."
        )

async def extract_pdfs_async(
    input_path: Union[str, bytes, Path],
    safe_mode: bool = True,
    text: bool = True,
    table: bool = True,
    image: bool = True,
    encode_page: bool = True,
    segment: bool = True,
    zoom: float = 2.0
) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Asynchronous function to process PDFs (single or directory).
    """
    if isinstance(input_path, bytes):
        return await async_extract_pdf(
            input_path,
            safe_mode=safe_mode,
            text=text,
            table=table,
            image=image,
            encode_page=encode_page,
            segment=segment,
            zoom=zoom
        )

    path = validate_path(input_path, safe_mode=safe_mode)
    if path.is_dir():
        return await async_extract_pdfs_from_directory(
            path,
            safe_mode=safe_mode,
            text=text,
            table=table,
            image=image,
            encode_page=encode_page,
            segment=segment,
            zoom=zoom
        )
    elif path.is_file():
        return await async_extract_pdf(
            path,
            safe_mode=safe_mode,
            text=text,
            table=table,
            image=image,
            encode_page=encode_page,
            segment=segment,
            zoom=zoom
        )
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
