import pytest
from unittest.mock import patch, MagicMock
from missing_text.streamlit_app import main

# A valid base64-encoded 1x1 PNG image without the data URI prefix
VALID_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="

# A complete, valid PDF structure
VALID_PDF_CONTENT = (
    b"%PDF-1.7\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj"
    b"3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj"
    b"xref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF"
)


@pytest.mark.parametrize("file_content", [VALID_PDF_CONTENT])
@patch("missing_text.streamlit_app.sync_extract_pdf")
@patch("streamlit.file_uploader")
@patch("streamlit.button")
@patch("streamlit.success")
@patch("streamlit.title")
def test_streamlit_app(
    mock_title,
    mock_success,
    mock_button,
    mock_file_uploader,
    mock_sync_extract_pdf,
    file_content,
):
    # Mock the file uploader to return a file-like object
    mock_file = MagicMock()
    mock_file.getvalue.return_value = file_content
    mock_file_uploader.return_value = mock_file

    # Mock the button to simulate a click
    mock_button.return_value = True

    # Mock the PDF extraction function with correctly formatted base64 images
    # mock_sync_extract_pdf.return_value = {
    #     "text": "Sample extracted text",
    #     "tables": [{"content": [{"col1": "data1", "col2": "data2"}]}],
    #     "images": [
    #         {"image_data": VALID_BASE64_IMAGE, "content": "OCR text"}
    #     ],  # No data URI prefix
    #     "segments": [
    #         {
    #             "segments": [
    #                 {
    #                     "type": "text",
    #                     "content": "Sample segment",
    #                     "bbox": [0, 0, 100, 100],
    #                 }
    #             ]
    #         }
    #     ],
    #     "pages": [{"image": VALID_BASE64_IMAGE}],  # No data URI prefix
    # }

    mock_sync_extract_pdf.return_value = mock_sync_extract_pdf.return_value = {
        "text": [
            {"page_number": 1, "content": "Sample extracted text from page 1"},
            {"page_number": 2, "content": "Sample extracted text from page 2"},
        ],
        "tables": [
            {
                "page_number": 1,
                "content": [
                    {"col1": "data1", "col2": "data2"}
                ],  # Table data from page 1
                "metadata": {
                    "columns": ["col1", "col2"],
                    "shape": (2, 2),
                },  # Example table metadata
            },
            {
                "page_number": 2,
                "content": [
                    {"col1": "value1", "col2": "value2"}
                ],  # Table data from page 2
                "metadata": {
                    "columns": ["col1", "col2"],
                    "shape": (2, 2),
                },  # Example table metadata
            },
        ],
        "images": [
            {
                "page_number": 1,
                "image_data": VALID_BASE64_IMAGE,
                "content": "OCR text from image on page 1",
            },
            {
                "page_number": 2,
                "image_data": VALID_BASE64_IMAGE,
                "content": "OCR text from image on page 2",
            },
        ],
        "segments": [
            {
                "page_number": 1,
                "segments": [
                    {
                        "type": "text",
                        "content": "Sample text segment",
                        "bbox": [0, 0, 100, 100],
                    }
                ],
            },
            {
                "page_number": 2,
                "segments": [
                    {
                        "type": "image",
                        "content": "Sample image segment",
                        "bbox": [50, 50, 150, 150],
                    }
                ],
            },
        ],
        "pages": [
            {
                "page_number": 1,
                "image": VALID_BASE64_IMAGE,  # Base64-encoded full page 1
            },
            {
                "page_number": 2,
                "image": VALID_BASE64_IMAGE,  # Base64-encoded full page 2
            },
        ],
    }

    # Run the main function of the Streamlit app
    main()

    # Assert the mock objects were called as expected
    mock_title.assert_called_once_with("MissingText - Processed Document Analyser")
    mock_file_uploader.assert_called_once_with("Choose a PDF file", type="pdf")
    mock_button.assert_called_once_with("Start Processing")
    mock_success.assert_called_once_with(
        "PDF processed successfully. Navigate to other tabs to view the results."
    )
    mock_sync_extract_pdf.assert_called_once()


@patch("streamlit.file_uploader")
@patch("streamlit.button")
@patch("streamlit.warning")
@patch("streamlit.title")
def test_streamlit_app_no_file(
    mock_title, mock_warning, mock_button, mock_file_uploader
):
    # Mock the file uploader to return None (no file uploaded)
    mock_file_uploader.return_value = None

    # Mock the button to not be clicked
    mock_button.return_value = True

    # Run the app
    main()

    # Check if the title was set
    mock_title.assert_called_once_with("MissingText - Processed Document Analyser")

    # Check if the file uploader was called
    mock_file_uploader.assert_called_once_with("Choose a PDF file", type="pdf")

    # Check for all expected warnings, excluding extra `call.call()` entries
    actual_calls = [call[0][0] for call in mock_warning.call_args_list]

    expected_warnings = [
        "Please upload a PDF file before processing.",
        # "No images extracted. Please process a PDF first.",
        # "No OCR text available. Please process a PDF first."
    ]

    # Debug: Print the actual warnings for clarity
    print("Actual warnings:", actual_calls)

    # Assert that each expected warning is in the actual calls
    for expected_warning in expected_warnings:
        assert (
            expected_warning in actual_calls
        ), f"Expected warning '{expected_warning}' not found."
