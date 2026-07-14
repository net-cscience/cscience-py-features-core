from abc import ABCMeta


class FeatureBaseMeta(ABCMeta):
    def __call__(
        cls,
        *args: object,
        **kwargs: object,
    ) -> object:
        raise TypeError(
            f"{cls.__name__} cannot be instantiated directly. "
            f"Use {cls.__name__}.get_instance(config)."
        )