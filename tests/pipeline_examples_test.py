import random
import re
from statistics import mean, stdev

import pytest

from pypipeline import Pipeline

TEXT = "The quick brown fox, jumping over the lazy dog, suddenly stopped and looked around."

STOP_WORDS = {"the", "and", "over", "a", "an", "around", "suddenly"}

POS_TAGS = {
    "ADJ": ["quick", "brown", "lazy"],
    "NOUN": ["fox", "dog"],
    "VERB": ["jumping", "stopped", "looked"],
}


def tokenize(paragraph: str) -> list[str]:
    """Split text into lowercase tokens using regex on words."""
    return re.findall(r"\b\w+\b", paragraph.lower())


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove stopwords from token list."""
    return [t for t in tokens if t not in STOP_WORDS]


def make_pos_tags(tokens: list[str]) -> list[tuple[str, str]]:
    word_to_pos_tag = {word: pos for pos, words in POS_TAGS.items() for word in words}
    return [(w, word_to_pos_tag.get(w, "UNK")) for w in tokens]


def compose_text(tokens: list[tuple[str, str]]) -> tuple[str, list[tuple[str, str]]]:
    """Join filtered tokens back into a sentence."""
    return " ".join([t for t, _ in tokens]), tokens


def test_pipeline_example_01():
    pipeline = Pipeline() >> tokenize >> remove_stopwords >> make_pos_tags >> compose_text

    text, tags = pipeline.call(TEXT)

    tags_dict = dict(tags)

    assert text == "quick brown fox jumping lazy dog stopped looked"
    assert len(tags) == len(text.split())
    assert tags_dict["brown"] == "ADJ"


def test_pipeline_example_02():
    def random_list_of_ints(n: int) -> list[int]:
        rng = random.Random(42)  # noqa: S311
        return [rng.randint(1, n) for _ in range(1000)]

    def pack_stats(_xs: list[int], n: int, s: int, mean: float, stdev: float) -> dict[str, int | float]:
        return {
            "n": n,
            "sum": s,
            "mean": mean,
            "stdev": stdev,
        }

    pipeline = Pipeline() >> random_list_of_ints

    assert pipeline >> sum | 50 == 25835  # noqa: PLR2004

    pipeline = (
        pipeline.then(lambda xs: (xs, len(xs), sum(xs), float(mean(xs)), float(stdev(xs))), result_unpack="tuple")
        >> pack_stats
    )

    assert pipeline >> (lambda d: d["sum"]) | 50 == 25835  # noqa: PLR2004
    assert pipeline >> (lambda d: d["mean"]) | 50 == 25.835  # noqa: PLR2004

    with pytest.raises(ValueError, match="empty range"):
        _ = pipeline | 0

    class CustomError(Exception): ...

    def raise_custom(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
        msg = f"oops, {args}, {kwargs}"
        raise CustomError(msg)

    pipeline = pipeline >> (lambda x: raise_custom(x))

    with pytest.raises(CustomError, match="oops"):
        _ = pipeline | 10
