from warnings import warn


class UnstableFeatureWarning(UserWarning):
    pass


def warning_unstable_feature_or_operator() -> None:
    warn("Operator `|` is experimental/unstable. Prefer `call` method instead.", UnstableFeatureWarning, stacklevel=3)
