from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
import os
from missing_text.extract.pdf import sync_extract_pdf, async_extract_pdf
import aiofiles

# Define the threshold in bytes (e.g., 10 MB)
FILE_SIZE_THRESHOLD = 10 * 1024 * 1024  # 10 MB

router = APIRouter()

from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool
import logging

# Define the threshold in bytes (e.g., 10 MB)
FILE_SIZE_THRESHOLD = 10 * 1024 * 1024  # 10 MB

router = APIRouter()


@router.post("/extract/pdf")
async def extract_pdf(file: UploadFile = File(...)):
    file_location = None  # Initialize file_location for later use
    try:
        # Try to get the file size from headers, fallback to reading manually if not available
        file_size = file.size
        if file_size is None:
            raise HTTPException(status_code=400, detail="File size not available")

        if file_size <= FILE_SIZE_THRESHOLD:
            # Process in-memory for smaller files
            logging.info("Processing small file in-memory using async method.")
            file_content = await file.read()  # Read the file content into memory
            extracted_content = await async_extract_pdf(file_content)
        else:
            # Use a temporary file for larger files
            logging.info(
                "Processing large file using sync method with a temporary file."
            )

            # Create a temporary file asynchronously
            async with aiofiles.tempfile.NamedTemporaryFile(
                "wb", delete=False
            ) as temp_file:
                file_location = temp_file.name
                await temp_file.write(
                    await file.read()
                )  # Save file content to temp file

            # Run sync_extract_pdf in a thread pool asynchronously
            extracted_content = await run_in_threadpool(sync_extract_pdf, file_location)

        # Return the extracted content
        return JSONResponse(content=extracted_content)

    except HTTPException as http_exc:
        logging.error(f"HTTP error during PDF extraction: {str(http_exc)}")
        raise http_exc
    except Exception as e:
        logging.error(f"Unexpected error during PDF extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
    finally:
        # Ensure temporary file cleanup
        if file_location and os.path.exists(file_location):
            os.remove(file_location)
            logging.info(f"Temporary file {file_location} has been cleaned up.")


@router.post("/extract/pdf-bytes")
async def extract_pdf_bytes(request: Request):
    file_location = None  # Initialize file_location for later use
    try:
        # Read the incoming byte data from the request body
        data = await request.body()

        # Calculate the size of the byte data
        file_size = len(data)

        # Process based on file size
        if file_size <= FILE_SIZE_THRESHOLD:
            logging.info("Processing small byte data in-memory using async method.")
            extracted_content = await async_extract_pdf(data)
        else:
            logging.info(
                "Processing large byte data using sync method with a temporary file."
            )

            # Create a temporary file asynchronously
            async with aiofiles.tempfile.NamedTemporaryFile(
                "wb", delete=False
            ) as temp_file:
                file_location = temp_file.name
                await temp_file.write(data)  # Write byte data to the temp file

            # Run sync_extract_pdf in a thread pool asynchronously
            extracted_content = await run_in_threadpool(sync_extract_pdf, file_location)

        # Return the extracted content
        return JSONResponse(content=extracted_content)

    except Exception as e:
        logging.error(f"Error during PDF extraction from bytes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
    finally:
        # Ensure temporary file cleanup
        if file_location and os.path.exists(file_location):
            os.remove(file_location)
            logging.info(f"Temporary file {file_location} has been cleaned up.")
