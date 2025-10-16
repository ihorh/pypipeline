"""Type-safe functional pipeline composition with support for result unpacking between stages.

This module implements a generic pipeline builder that preserves full callable signatures
as much as current python type system allows.

Key Features
------------

* chain arbitrary callables with `.then()` or `>>`
* unpack result before passing it to the next stage with `result_unpack="tuple"`
* strict typing and argument and return type propagation

Public API
----------
* `Pipeline` - Entry point for building a new pipeline chain.
* `compose` - Compose two callables `f` and `g` in a type-safe way.

Examples
--------
```python
pipeline = (
    Pipeline()
    >> (lambda a, b: a + b)
    >> (lambda c: c * 2)
result = pipeline.call(1, 2)
)
```

"""

from pypipeline._compose import compose
from pypipeline._pipeline import Pipeline

__all__ = ["Pipeline", "compose"]
