from __future__ import annotations

from typing import cast

from pypipeline import Pipeline


def test_pipeline_normal():
    def pipe_f1(a: str, *, b: int) -> str:
        return f"pipe_f1 function result {a} {b}"

    def pipe_f2(a: str) -> str:
        return f"pipe_f2 function result {a}"

    pipeline = Pipeline().then(pipe_f1).then(pipe_f2)
    print(pipeline.call("a", b=1))
    assert pipeline.call("a", b=1) == "pipe_f2 function result pipe_f1 function result a 1"


def test_pipeline_unpack_tuple():
    def pipe_f1(a: str, *, b: int) -> tuple[int, str]:
        return int(a), str(b)

    def pipe_f2(n: int, s: str) -> str:
        return f"pipe_f2 function result {n} {s}"

    pipeline = Pipeline().then(pipe_f1, result_unpack="tuple").then(pipe_f2)
    assert pipeline.call("17", b=1) == "pipe_f2 function result 17 1"


def test_pipeline_complex_01():
    def float_to_string(f: float, precision: int = 2) -> str:
        return f"{f:.{precision}f}"

    pipeline = (
        Pipeline()
        .then(lambda n, p: (cast("int", n), cast("int", p)), result_unpack="tuple")
        .then(lambda n, p: (cast("int", n + 13), cast("int", p)), result_unpack="tuple")
        .then(lambda n, p: (cast("float", n / 5), cast("int", p)), result_unpack="tuple")
        .then(float_to_string)
    )

    assert pipeline.call(1, 2) == "2.80"
    print(pipeline.call(1, 2))


def test_pipeline_complex_02():
    pipeline = (
        Pipeline()
        .then(lambda n, d: (cast("int", n // d), cast("int", n % d)))
        .then(lambda r: (f"q: {r[0]}, rem: {r[1]}", *r), result_unpack="tuple")
        .then(lambda s, q, r: cast("int", len(s) * q + r))
    )

    print(pipeline.call(17, 5))

def test_pipeline_tuple_unpack_edge_case():
    """Tuple unpack should not affect pipeline output if applied to the last stage."""
    pipeline_unp = (
        Pipeline()
        .then(lambda n, p: (cast("int", n + 13), cast("int", p)), result_unpack="tuple")
        .then(lambda n, p: (cast("float", n / 5), cast("int", p)), result_unpack="tuple")
    )
    pipeline_norm = (
        Pipeline()
        .then(lambda n, p: (cast("int", n + 13), cast("int", p)), result_unpack="tuple")
        .then(lambda n, p: (cast("float", n / 5), cast("int", p)))
    )
    r_unp = pipeline_unp.call(1, 2)
    r_norm = pipeline_norm.call(1, 2)
    assert r_unp == r_norm
    assert r_norm[0] == 2.8
