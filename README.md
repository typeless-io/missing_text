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
   git clone https://github.com/yourusername/missing_text.git
   cd missing_text
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   uv install  # Install primary dependencies
   uv install --group dev # Install development dependencies
   ```

## Usage

Here's a quick example of how to use missing_text:

```python

from missing_text.hello_missing import hello_missing
result = hello_missing()
print(result)
```

For more detailed usage instructions, please refer to the [documentation](docs/README.md).

## Development

To set up the development environment:

1. Follow the installation steps above.
2. Install development dependencies:
   ```bash
   uv pip install -r requirements-dev.txt
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
   uv install --editable .
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
