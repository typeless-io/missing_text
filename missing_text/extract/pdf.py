import pymupdf  # PyMuPDF
import io
from io import BytesIO
import json
import base64
from typing import Dict, Any, List, Union
import pandas as pd
import pytesseract
from PIL import Image
import logging
import asyncio
from .utils import DecimalEncoder
import os

# Set up logging
logger = logging.getLogger(__name__)


class PDFProcessingError(Exception):
    """Custom exception for errors during PDF processing."""

    pass

# Add your existing sync and async extraction functions here

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

def sync_extract_pdf(input_data: Union[bytes, str]) -> Dict[str, Any]:
    """
    Extracts page-separated text, images, and tables from the given PDF file (synchronously).
    
    Args:
        input_data (Union[bytes, str]): The in-memory content of the PDF (bytes) or the file path (str).
    
    Returns:
        Dict[str, Any]: A dictionary with page-separated text, images, and tables.
    """
    try:
        if isinstance(input_data, bytes):
            doc = pymupdf.open(stream=input_data, filetype="pdf")
        else:
            if not os.path.isfile(input_data):
                raise PDFProcessingError(f"File not found: {input_data}")
            doc = pymupdf.open(input_data)

        total_pages = _get_page_count(doc)
        extracted_content = {"pages": []}

        for page_num in range(total_pages):
            page = doc[page_num]
            logger.info(f"Processing page {page_num + 1}/{total_pages}")

            # Extract text, tables, and images for the current page
            page_content = {
                "text": _extract_text_from_page(page),
                "tables": _extract_tables_from_page(page),
                "images": _extract_images_from_page(page, doc)
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


def sync_extract_pdfs_from_directory(directory_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extracts content from all PDF files in a given directory.

    Args:
        directory_path (str): Path to the directory containing PDF files.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary where each key is a PDF file name,
        and the value is the extracted content for that PDF.
    """
    extracted_data = {}

    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):  # Process only PDF files
            file_path = os.path.join(directory_path, filename)
            try:
                extracted_data[filename] = sync_extract_pdf(file_path)
                print(f"Processed {filename}")
            except PDFProcessingError as e:
                print(f"Error processing {filename}: {e}")

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

async def async_extract_pdf(input_data: Union[bytes, str]) -> Dict[str, Any]:
    """
    Asynchronously extracts page-separated text, images, and tables from a PDF file.

    Args:
        input_data (Union[bytes, str]): The in-memory content of the PDF (bytes) or the file path (str).
    
    Returns:
        Dict[str, Any]: A dictionary with page-separated text, images, and tables.
    """
    try:
        if isinstance(input_data, bytes):
            doc = pymupdf.open(stream=input_data, filetype="pdf")
        else:
            if not os.path.isfile(input_data):
                raise PDFProcessingError(f"File not found: {input_data}")
            doc = pymupdf.open(input_data)

        total_pages = _get_page_count(doc)
        extracted_content = {"pages": []}

        for i in range(total_pages):
            page = doc[i]
            logger.info(f"Processing page {i + 1}/{total_pages}")
            
            # Extract text, tables, and images for the current page
            page_content = {
                "text": _extract_text_from_page(page),
                "tables": _extract_tables_from_page(page),
                "images": _extract_images_from_page(page, doc)
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

async def async_extract_pdfs_from_directory(directory_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Asynchronously extracts content from all PDF files in a given directory.

    Args:
        directory_path (str): Path to the directory containing PDF files.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary where each key is a PDF file name,
        and the value is the extracted content for that PDF.
    """
    extracted_data = {}

    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):  # Process only PDF files
            file_path = os.path.join(directory_path, filename)
            try:
                extracted_data[filename] = await async_extract_pdf(file_path)
                print(f"Processed {filename}")
            except PDFProcessingError as e:
                print(f"Error processing {filename}: {e}")

    return extracted_data

### MAIN EXTRACTION FUNCTION ###

def extract_pdfs(input_path: Union[str, bytes]) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Dynamically processes either a single PDF file or all PDFs in a directory, 
    using either synchronous or asynchronous extraction based on the current context.
    
    Args:
        input_path (Union[str, bytes]): Path to a PDF file, directory, or in-memory PDF bytes.

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
        return asyncio.create_task(extract_pdfs_async(input_path))
    else:
        # Running in a synchronous context, call the sync version
        return extract_pdfs_sync(input_path)


def extract_pdfs_sync(input_path: Union[str, bytes]) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Synchronous function to process PDFs (single or directory).
    """
    if isinstance(input_path, bytes):
        return sync_extract_pdf(input_path)
    elif os.path.isdir(input_path):
        return sync_extract_pdfs_from_directory(input_path)
    elif os.path.isfile(input_path) and input_path.endswith(".pdf"):
        return sync_extract_pdf(input_path)
    else:
        raise PDFProcessingError(f"Invalid input: {input_path} is neither a valid PDF file nor a directory.")


async def extract_pdfs_async(input_path: Union[str, bytes]) -> Union[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    """
    Asynchronous function to process PDFs (single or directory).
    """
    if isinstance(input_path, bytes):
        return await async_extract_pdf(input_path)
    elif os.path.isdir(input_path):
        return await async_extract_pdfs_from_directory(input_path)
    elif os.path.isfile(input_path) and input_path.endswith(".pdf"):
        return await async_extract_pdf(input_path)
    else:
        raise PDFProcessingError(f"Invalid input: {input_path} is neither a valid PDF file nor a directory.")