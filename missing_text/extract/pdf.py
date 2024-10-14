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

# Set up logging
logger = logging.getLogger(__name__)


class PDFProcessingError(Exception):
    """Custom exception for errors during PDF processing."""

    pass


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
    Extracts text, images, and tables from the given PDF file (synchronously).

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        Dict[str, Any]: A dictionary containing extracted text, images, and tables.
    """
    try:
        # Check if input_data is bytes (in-memory) or a file path (str)
        if isinstance(input_data, BytesIO):
            input_data = input_data.getvalue()

        if isinstance(input_data, bytes):
            doc = pymupdf.open(stream=input_data, filetype="pdf")
        else:
            doc = pymupdf.open(input_data)

        total_pages = _get_page_count(doc)
        extracted_content = {"text": "", "tables": [], "images": []}

        for page_num in range(total_pages):
            page = doc[page_num]
            logger.info(f"Processing page {page_num + 1}/{_get_page_count(doc)}")

            extracted_content["text"] += _extract_text_from_page(page)
            extracted_content["tables"].extend(_extract_tables_from_page(page))
            extracted_content["images"].extend(_extract_images_from_page(page, doc))

        logger.info("PDF processing complete")
        return extracted_content

    except (ValueError, RuntimeError) as e:
        # Handle invalid or corrupted PDF errors
        raise PDFProcessingError(f"Invalid or corrupted PDF file: {str(e)}")
    except Exception as e:
        # Handle any other generic exceptions
        logger.error(f"Failed to extract content from PDF: {str(e)}")
        raise PDFProcessingError(f"Failed to extract content from PDF: {str(e)}")


### ASYNCHRONOUS FUNCTIONS ###


async def async_extract_pdf(input_data: Union[bytes, str]) -> Dict[str, Any]:
    """
    Asynchronously extracts content (text, images, tables) from a PDF file.

    Args:
        input_data (Union[bytes, str]): The in-memory content of the PDF (bytes) or the file path (str).

    Returns:
        Dict[str, Any]: A dictionary containing extracted content.
    """

    try:
        # Check if input_data is bytes (in-memory) or a file path (str)
        # Handle both byte streams and file paths
        if isinstance(input_data, BytesIO):
            input_data = input_data.getvalue()

        if isinstance(input_data, bytes):
            doc = pymupdf.open(stream=input_data, filetype="pdf")
        else:
            doc = pymupdf.open(input_data)

        total_pages = _get_page_count(doc)
        extracted_content = {"text": "", "tables": [], "images": []}

        for i in range(0, total_pages):
            page = doc[i]
            extracted_content["text"] += _extract_text_from_page(page)
            extracted_content["tables"].extend(_extract_tables_from_page(page))
            extracted_content["images"].extend(_extract_images_from_page(page, doc))

            await asyncio.sleep(0)  # Give control back to the event loop

        logger.info("Asynchronous PDF processing complete")
        return extracted_content

    except (ValueError, RuntimeError) as e:
        # Handle invalid or corrupted PDF errors
        raise PDFProcessingError(f"Invalid or corrupted PDF file: {str(e)}")
    except Exception as e:
        # Handle any other generic exceptions
        logger.error(f"Failed to extract content from PDF: {str(e)}")
        raise PDFProcessingError(f"Failed to extract content from PDF: {str(e)}")
