import inspect
from typing import Type, Optional, Any, Callable
from .container import DIContainer, container

def bind(container: DIContainer = container, *, bind_to: Optional[Type] = None, singleton: bool = False):
    """
    Decorator for registering a provider.
    Usage:
        @bind(container, singleton=True)
        def provider() -> MyType:
            ...
    Or:
        @bind(container, bind_to=IMyInterface, singleton=True)
        def provider():
            ...
    """
    def wrapper(fn: Callable[..., Any]):
        resolved_key = bind_to
        if resolved_key is None:
            sig = inspect.signature(fn)
            return_type = sig.return_annotation
            if return_type is inspect.Signature.empty:
                raise TypeError(
                    f"@bind must have a return type annotation or use bind_to=..."
                )
            resolved_key = return_type

        container.register(resolved_key, fn, singleton=singleton)
        return fn

    return wrapper
