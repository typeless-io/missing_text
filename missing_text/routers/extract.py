from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
import aiofiles
import logging
import os
from missing_text.extract.pdf import sync_extract_pdf, async_extract_pdf, extract_pdfs

FILE_SIZE_THRESHOLD = 10 * 1024 * 1024  # 10 MB
router = APIRouter()

# Helper function to handle file processing (refactored to reduce duplication)
async def process_pdf(input_data, is_bytes: bool = False) -> dict:
    file_location = None  # Initialize file_location for later use
    try:
        file_size = len(input_data)

        if file_size <= FILE_SIZE_THRESHOLD:
            logging.info("Processing small data in-memory using async method.")
            extracted_content = await async_extract_pdf(input_data)
        else:
            logging.info("Processing large data using sync method with a temporary file.")
            
            # Create a temporary file asynchronously
            async with aiofiles.tempfile.NamedTemporaryFile('wb', delete=False) as temp_file:
                file_location = temp_file.name
                await temp_file.write(input_data)  # Write byte data to the temp file
            
            # Run sync_extract_pdf in a thread pool asynchronously
            extracted_content = await run_in_threadpool(sync_extract_pdf, file_location)

        return extracted_content

    except Exception as e:
        logging.error(f"Error during PDF extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    finally:
        if file_location and os.path.exists(file_location):
            os.remove(file_location)
            logging.info(f"Temporary file {file_location} has been cleaned up.")


@router.post("/extract/pdf")
async def extract_pdf(file: UploadFile = File(...)):
    """Handles PDF extraction from uploaded files"""
    file_content = await file.read()
    return JSONResponse(content=await process_pdf(file_content))


@router.post("/extract/pdf-bytes")
async def extract_pdf_bytes(request: Request):
    """Handles PDF extraction from byte streams"""
    byte_data = await request.body()
    return JSONResponse(content=await process_pdf(byte_data, is_bytes=True))


@router.post("/extract/pdf-path")
async def extract_pdf_path(file_path: str):
    """
    Handles PDF extraction using a file path or directory path.
    
    Args:
        file_path (str): Path to the PDF file or directory containing PDFs.
    
    Returns:
        JSONResponse: Extracted content from the PDF or directory of PDFs.
    
    Example:
        curl -X POST "http://localhost:8000/extract/pdf-path?file_path=sample/data/file.pdf"
    """

    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"File or directory does not exist: {file_path}")
    
    try:
        # Call the dynamic extract_pdfs function (handles both files and directories)
        extracted_content = await extract_pdfs(file_path)
        return JSONResponse(content=extracted_content)
    
    except Exception as e:
        logging.error(f"Error during PDF extraction from path: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF or directory: {str(e)}")