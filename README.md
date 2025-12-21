# missing_text

A package purpose built for simplifying document processing for LLM based application development

## Description

missing_text is an open-source project that purpose built for simplifying document processing for LLM based application development. It aims to make it easy to ingest documents, extract text and metadata, and prepare the data for training or inference or storage to be used in an LLM based application, so that developers can focus on building their application.

## Installation

This project uses the UV package manager. To install missing_text, follow these steps:

1. Install UV if you haven't already:

   ```
   pip install uv
   ```

2. Clone the repository:

   ```
   git clone https://github.com/typeless-io/missing_text.git
   cd missing_text
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   uv pip install -r pyproject.toml  # Install primary dependencies
   ```

## Usage

### PDF Processing

The package provides powerful PDF processing capabilities with both synchronous and asynchronous options:

```python
from missing_text.extract.pdf import sync_extract_pdf, async_extract_pdf, extract_pdfs

# Process a single PDF synchronously
with open("document.pdf", "rb") as f:
    content = sync_extract_pdf(
        f.read(),
        text=True,      # Extract text
        table=True,     # Extract tables
        image=True,     # Extract images with OCR
        encode_page=True, # Get base64 encoded page images
        segment=True,   # Get content segments with bounding boxes
        zoom=2.0        # Set zoom level for page rendering (default: 2.0)
    )

# Process a PDF asynchronously
async def process_pdf():
    content = await async_extract_pdf("path/to/pdf", safe_mode=True)
    print(content["text"])  # Access extracted text
    print(content["tables"]) # Access extracted tables
    print(content["images"]) # Access extracted images with OCR
    print(content["pages"])  # Access page images
    print(content["segments"]) # Access content segments

# Process multiple PDFs from a directory
results = extract_pdfs(
    "path/to/pdf_directory",
    safe_mode=True,
    text=True,
    table=True,
    image=True
)
```

### Text Splitting

The package includes various text splitting utilities for LLM context preparation:

```python
from missing_text.splitter import (
    character_splitter,
    sentence_splitter,
    paragraph_splitter,
    markdown_header_splitter,
    json_key_splitter,
    html_tag_attribute_splitter,
    latex_section_splitter,
    recursive_character_splitter,
)

# Split text by characters with overlap
chunks = character_splitter(
    "Your long text here",
    chunk_size=100,
    overlap=20
)

# Split by sentences
sentences = sentence_splitter("Multiple sentences. Like this one. And this.")

# Split markdown by headers
sections = markdown_header_splitter(
    "# Section 1\nContent\n# Section 2\nMore content",
    level=1
)

# Advanced recursive splitting with overlap
chunks = recursive_character_splitter(
    text="Your long document text here",
    character_size=800,
    overlap=100,
    delimiters=["\n\n", "\n", "[.!?]", ",", " ", ""]
)
```

### Text Embeddings

The package supports multiple embedding options:

```python
from missing_text.embed.sentence_transformers import sentence_transformer_embedder

# Generate embeddings using Sentence Transformers
texts = ["First sentence", "Second sentence", "Third sentence"]
embeddings = sentence_transformer_embedder(
    texts,
    model_name="all-MiniLM-L6-v2"
)
```

### FastAPI Integration

The package includes a FastAPI server for document processing:

```python
# Start the FastAPI server
missing fastapi --host 0.0.0.0 --port 8000
# OR
missing_text
```

### Streamlit UI

The package includes a Streamlit interface for visual document processing:

```bash
# Start the Streamlit app
missing streamlit --host localhost --port 8501
```

The Streamlit UI provides:

- PDF upload and processing
- Text extraction visualization
- Table extraction with preview
- Image extraction with OCR results
- Content segmentation visualization with bounding boxes (optimized for viewing)
- JSON export of extracted content

## CLI Usage

After installing the package, you can use the CLI as follows:

```bash
# Run the hello_missing function
missing run

# Run with a custom name
missing run --name Alice

# Show the version
missing version

# Start a FastAPI server
missing fastapi

# Start a FastAPI server with custom host and port
missing fastapi --host 0.0.0.0 --port 5000

# Show help
missing --help

#The Streamlit app provides a user-friendly interface to test out the features of Missing Text. To run the Streamlit app, use the following command:
missing streamlit

# Start the Streamlit App with custom host and port
missing streamlit --host 0.0.0.0 --port 8501
```

The FastAPI server can be configured using environment variables or command-line arguments:

- `MISSING_FAST_API_HOST`: Sets the host for the FastAPI server (default: 0.0.0.0)
- `MISSING_FAST_API_PORT`: Sets the port for the FastAPI server (default: 8000)

You can set these in a `.env` file in your project root or as system environment variables.

## Development

To set up the development environment:

1. Follow the installation steps above.
2. Install primary and development dependencies:
   ```bash
   uv pip install -r pyproject.toml  # Install primary dependencies
   uv pip install -r pyproject.toml --extra dev # Install development dependencies
   ```
3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```
4. [Optional] Run pre-commit checks manually:
   ```bash
   pre-commit run --all-files
   ```
5. Build the package locally:
   ```bash
   uv run python -m build
   ```
6. Install the package in editable mode:
   ```bash
   uv pip install --editable .
   ```

## Testing

We use pytest for automated testing. To run the tests:

```bash
pytest
```

If you want to run the tests with coverage, yet to be implemented:

```bash
pytest --cov=missing_text
```

To generate a coverage report:

```bash
pytest --cov=missing_text --cov-report=html --cov-report=term
```

All new features should have corresponding test cases. Tests are located in the `tests/` directory.

## Contributing

We welcome contributions to missing_text! Here's how you can contribute:

1. Check the [Issues](https://github.com/typeless-io/missing_text/issues) page for open issues or create a new one to discuss your ideas.
2. Fork the repository and create a new branch for your feature or bug fix.
3. Write code and tests for your changes.
4. Ensure all tests pass and the code adheres to the project's style guide.
5. Submit a pull request with a clear description of your changes.

Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

For any other queries, please reach out to us at maruthi@typeless.io

## License

This project is licensed under the [Apache License 2.0](LICENSE).

---

For more information, please visit our [GitHub repository](https://github.com/typeless-io/missing_text).
