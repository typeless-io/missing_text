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
   uv pip install -r pyproject.toml  # Install primary dependencies
   ```

## Usage

Here's a quick example of how to use missing_text:

```python

from missing_text.hello_missing import hello_missing
result = hello_missing()
print(result)
```

For more detailed usage instructions, please refer to the [documentation](docs/README.md).

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

Command-line arguments will override environment variables:

```bash
#
```

The FastAPI server will have two endpoints:

- `/`: Returns a welcome message
- `/hello/{name}`: Returns the result of `hello_missing(name)`

You can access these endpoints in your browser or using tools like curl:

```bash
curl http://localhost:8000/
curl http://localhost:8000/hello/Alice
```

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
   uv install --editable .
   ```
7. To add primary dependencies
   ```bash
   uv add <package-name>
   ```
8. To remove primary dependencies
   ```bash
   uv remove <package-name>
   ```
9. To add dev dependencies
   ```bash
   uv add <package-name> --optional dev
   ```
10. To remove dev dependencies

```bash
uv remove <package-name> --optional dev
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
