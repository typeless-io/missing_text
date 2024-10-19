from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
import aiofiles
import logging
import os
from typing import List
from missing_text.extract.pdf import (
    sync_extract_pdf,
    async_extract_pdf,
    extract_pdfs,
    validate_path,
    set_safe_mode,
    SAFE_MODE_CONFIG,
    PDFProcessingError,
)

FILE_SIZE_THRESHOLD = 10 * 1024 * 1024  # 10 MB
router = APIRouter()


# Helper function to handle file processing (refactored to reduce duplication)
async def process_pdf(
    input_data, is_bytes: bool = False, safe_mode: bool = True
) -> dict:
    file_location = None  # Initialize file_location for later use
    try:
        file_size = len(input_data)

        if file_size <= FILE_SIZE_THRESHOLD:
            logging.info("Processing small data in-memory using async method.")
            extracted_content = await async_extract_pdf(input_data, safe_mode=safe_mode)
        else:
            logging.info(
                "Processing large data using sync method with a temporary file."
            )

            # Create a temporary file asynchronously
            async with aiofiles.tempfile.NamedTemporaryFile(
                "wb", delete=False
            ) as temp_file:
                file_location = temp_file.name
                await temp_file.write(input_data)  # Write byte data to the temp file

            # Run sync_extract_pdf in a thread pool asynchronously
            extracted_content = await run_in_threadpool(
                sync_extract_pdf, file_location, safe_mode=safe_mode
            )

        return extracted_content

    except Exception as e:
        logging.error(f"Error during PDF extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    finally:
        if file_location and os.path.exists(file_location):
            os.remove(file_location)
            logging.info(f"Temporary file {file_location} has been cleaned up.")


@router.post("/extract/pdf")
async def extract_pdf(file: UploadFile = File(...), safe_mode: bool = True):
    """
    Handles PDF extraction from uploaded files

    Args:
        file (UploadFile): The uploaded PDF file.
        safe_mode (bool, optional): Whether to enable safe mode for this extraction. Defaults to True.
    """
    file_content = await file.read()
    return JSONResponse(content=await process_pdf(file_content, safe_mode=safe_mode))


@router.post("/extract/pdf-bytes")
async def extract_pdf_bytes(request: Request, safe_mode: bool = True):
    """
    Handles PDF extraction from byte streams

    Args:
        request (Request): The incoming request containing PDF bytes.
        safe_mode (bool, optional): Whether to enable safe mode for this extraction. Defaults to True.
    """
    byte_data = await request.body()
    return JSONResponse(
        content=await process_pdf(byte_data, is_bytes=True, safe_mode=safe_mode)
    )


@router.post("/extract/pdf-path")
async def extract_pdf_path(file_path: str, safe_mode: bool = True):
    """
    Handles PDF extraction using a file path or directory path.

    Args:
        file_path (str): Path to the PDF file or directory containing PDFs.
        safe_mode (bool, optional): Whether to enable safe mode for this extraction. Defaults to True.

    Returns:
        JSONResponse: Extracted content from the PDF or directory of PDFs.

    Example:
        curl -X POST "http://localhost:8000/extract/pdf-path?file_path=sample/data/file.pdf&safe_mode=True"
    """
    try:
        path = validate_path(file_path, safe_mode=safe_mode)
        if not path.exists():
            raise HTTPException(
                status_code=400, detail=f"File or directory does not exist: {path}"
            )

        # Call the dynamic extract_pdfs function (handles both files and directories)
        extracted_content = await extract_pdfs(str(path), safe_mode=safe_mode)
        return JSONResponse(content=extracted_content)

    except PDFProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error during PDF extraction from path: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process PDF or directory: {str(e)}"
        )


# Add a new endpoint to toggle safe mode (for advanced users)
@router.post("/toggle-safe-mode")
async def toggle_safe_mode(
    enable: bool, base_directory: str = None, allowed_extensions: List[str] = None
):
    """
    Toggle safe mode on or off. Use with caution!

    Args:
        enable (bool): True to enable safe mode, False to disable.
        base_directory (str, optional): The base directory for file operations when safe mode is enabled.
        allowed_extensions (List[str], optional): List of allowed file extensions when safe mode is enabled.

    Returns:
        JSONResponse: Current state of safe mode configuration.

    Note:
        Disabling safe mode or changing its configuration can expose your application to security risks.
        Only use this endpoint in trusted environments and with proper authentication/authorization.
    """
    set_safe_mode(
        enable, base_directory, set(allowed_extensions) if allowed_extensions else None
    )
    return JSONResponse(content={"safe_mode_config": str(SAFE_MODE_CONFIG)})
