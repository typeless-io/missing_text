from sentence_transformers import SentenceTransformer


def sentence_transformer_embedder(
    text_list: list[str], model_name: str = "all-MiniLM-L6-v2"
) -> list[tuple[str, list[float]]]:
    """
    Generates embeddings for a list of text inputs using Sentence Transformers.

    Args:
        text_list (list of str): A list of text strings to embed.
        model_name (str, optional): The name of the Sentence Transformer model to use. Defaults to "all-MiniLM-L6-v2".

    Returns:
        list of tuple: A list containing tuples of original text and its corresponding embeddings.

    Example:
        >>> texts = ["Hello world", "How are you?"]
        >>> sentence_transformer_embedder(texts)
        [("Hello world", [0.1, 0.2, ...]), ("How are you?", [0.3, 0.4, ...])]
    """

    if not isinstance(text_list, list) or not all(
        isinstance(text, str) for text in text_list
    ):
        raise TypeError("text_list must be a list of strings")
    if not isinstance(model_name, str):
        raise ValueError("model_name must be a string")

    try:
        # Load the specified Sentence Transformer model
        model = SentenceTransformer(model_name)
    except Exception as e:
        raise ValueError(f"Failed to load model '{model_name}': {e}")

    # Generate embeddings for each text in the list
    embeddings = model.encode(
        text_list, convert_to_tensor=False, show_progress_bar=True
    )

    # Convert numpy arrays to Python lists
    return [
        (text, embedding.tolist()) for text, embedding in zip(text_list, embeddings)
    ]
