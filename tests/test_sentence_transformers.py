import pytest
from missing_text.embed.sentence_transformers import sentence_transformer_embedder


@pytest.mark.parametrize(
    "texts",
    [
        (["Hello world", "How are you?"]),
        (["This is a test", "Another test sentence", "Yet another one"]),
    ],
)
def test_sentence_transformer_embedder(texts):
    result = sentence_transformer_embedder(texts)

    assert len(result) == len(texts)
    for text, embedding in result:
        assert isinstance(text, str)
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)


@pytest.mark.parametrize(
    "model_name",
    [
        "all-MiniLM-L6-v2",
        "paraphrase-MiniLM-L6-v2",
    ],
)
def test_sentence_transformer_embedder_different_models(model_name):
    texts = ["Test sentence for different models"]
    result = sentence_transformer_embedder(texts, model_name=model_name)

    assert len(result) == 1
    text, embedding = result[0]
    assert text == texts[0]
    assert isinstance(embedding, list)
    assert len(embedding) > 0


def test_sentence_transformer_embedder_empty_input():
    result = sentence_transformer_embedder([])
    assert result == []


@pytest.mark.parametrize(
    "invalid_input",
    [
        None,
        "Not a list",
        [1, 2, 3],
    ],
)
def test_sentence_transformer_embedder_invalid_input(invalid_input):
    with pytest.raises((ValueError, TypeError)):
        sentence_transformer_embedder(invalid_input)


@pytest.mark.parametrize(
    "invalid_model",
    [
        "non_existent_model",
        123,
        None,
    ],
)
def test_sentence_transformer_embedder_invalid_model(invalid_model):
    texts = ["Test sentence"]
    with pytest.raises(ValueError):
        sentence_transformer_embedder(texts, model_name=invalid_model)
