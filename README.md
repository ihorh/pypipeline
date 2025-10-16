# PyPipeline

Type-safe functional pipeline composition with support for tuple unpacking.

This module implements a generic pipeline builder that preserves full callable
signatures using Python 3.12+ generic syntax (`[**P]`, `[*Ts]`).

## Installation

For now package is not published to index, however it can be installed from source.

For example with `uv` it can be done in `pyproject.toml` file like this:

```toml
[project]
...
dependencies = ["pypipeline"]

[tool.uv.sources]
pypipeline = { git = "https://github.com/ihorh/pypipeline" }
```
## Key features

* **Composable functions** – chain arbitrary callables with `.then()`
  while retaining static type inference for arguments and return values.

* **Tuple-unpacking pipes** – when a stage returns a tuple, the next stage can
  automatically receive it as multiple positional arguments by specifying
  `result_unpack="tuple"`.

* **Strict typing** – uses `ParamSpec` and type-var tuples to propagate argument
  and return types through every composition step. Type checkers infer
  `(args, kwargs)` of the initial function and final return type of the chain.

## Upcoming Features

* **Dictionary-unpacking**

* **Tuple and Dictionary Unpacking**

## Core classes

* `Pipeline`
    
  Entry point for building a new pipeline chain.
  Supports `.then(f)` (and corresponding shorthand operator `>>`) and
  `.then(f, result_unpack="tuple")`.

* `compose`

  Compose two callables `f` and `g` as `g(f(*args, **kwargs))` in a type-safe way.

## Details

See module docstrings in [__init__.py](src/pypipeline/__init__.py) and [_pipeline.py](src/pypipeline/_pipeline.py).

## Example

> For more examples see [tests](tests/pipeline_examples_test.py).

```python
def f1(x: int, y: int) -> tuple[int, int]:
    return x + 1, y + 1
def f2(a: int, b: int) -> int:
    return a * b
pipeline = Pipeline().then(f1, result_unpack="tuple").then(f2)
pipeline.call(2, 3) # result is 12
```

or even better:

```python
pipeline = Pipeline() >> f1 >> f2
pipeline.call(2, 3) # result is 12
```

or using unstable feature - operator `|`:

```python
result = Pipeline() >> f1 >> f2 | (2, 3) # result should be still 12
```

## Disclaimer

> This library is primarily designed for statically-typed functional composition
> experiments, not for production runtime optimisation.

## License

MIT License
