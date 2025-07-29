from typing import Callable, Type, TypeVar, Dict, Union, Awaitable, Any, Optional
import asyncio
from .errors import DependencyNotFound

T = TypeVar("T")

class DIContainer:
    def __init__(self):
        self._providers: Dict[Type[Any], tuple[Callable[[], Union[T, Awaitable[T]]], bool]] = {}
        self._singletons: Dict[Type[Any], Any] = {}

    def register(
        self,
        bind_to: Type[T],
        provider: Callable[[], Union[T, Awaitable[T]]],
        singleton: bool = False
    ):
        """Bind a type to a provider function."""
        self._providers[bind_to] = (provider, singleton)

    def reset(self):
        """Reset all cached singleton instances (does not remove bindings)."""
        self._singletons.clear()

    async def resolve(self, bind_to: Type[T]) -> T:
        """Resolve a type, returning an instance (cached if singleton)."""
        if bind_to not in self._providers:
            raise DependencyNotFound(bind_to)

        provider, singleton = self._providers[bind_to]

        if singleton and bind_to in self._singletons:
            return self._singletons[bind_to]

        instance = provider()
        if asyncio.iscoroutine(instance):
            instance = await instance

        if singleton:
            self._singletons[bind_to] = instance

        return instance
    
    def has_instance(self, bind_to: Type[T]) -> bool:
        return bind_to in self._singletons

container = DIContainer()