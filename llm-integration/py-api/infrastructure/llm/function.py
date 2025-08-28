from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
import json

JSON_TYPE_MAP = {
    str:  "string",
    int:  "integer",
    float:"number",
    bool: "boolean",
    dict: "object",
    list: "array",
}

@dataclass
class Param:
    name: str
    py_type: type = str
    description: str = ""
    required: bool = True
    default: Any = field(default_factory=lambda: ... )

class LLMFunction:
    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable[..., Any],
        params: List[Param],
    ):
        if not callable(handler):
            raise ValueError("handler must be callable")
        self.name = name
        self.description = description
        self.handler = handler
        self.params: List[Param] = params
        self._index = {p.name: i for i, p in enumerate(self.params)}

    def __call__(self, *args, **kwargs) -> Any:
        """Call with positional/keyword args; validates & converts types."""
        bound = self._bind_args(args, kwargs)
        return self.handler(**bound)

    # ---------- Internal helpers ----------

    def _bind_args(self, args: tuple, kwargs: dict) -> Dict[str, Any]:
        """
        Merge positional + keyword into a dict keyed by param names.
        Validate required and type-convert where possible.
        """
        bound: Dict[str, Any] = {}

        # 1) positional by order
        if len(args) > len(self.params):
            raise TypeError(f"{self.name} expected ≤ {len(self.params)} arguments, got {len(args)}")

        for i, value in enumerate(args):
            p = self.params[i]
            bound[p.name] = self._coerce_type(p, value)

        # 2) keywords (override positional if present)
        for key, value in kwargs.items():
            if key not in self._index:
                raise TypeError(f"{self.name} got unexpected keyword argument '{key}'")
            p = self.params[self._index[key]]
            bound[key] = self._coerce_type(p, value)

        # 3) fill defaults + check required
        for p in self.params:
            if p.name not in bound:
                if p.default is not ...:
                    bound[p.name] = self._coerce_type(p, p.default)
                elif p.required:
                    raise TypeError(f"{self.name} missing required argument: '{p.name}'")

        return bound

    def _coerce_type(self, param: Param, value: Any) -> Any:
        param_type = param.py_type

        if isinstance(value, param_type) or value is None:
            return value

        raise TypeError(f"{self.name}.{param.name} expected {param_type.__name__}, got {type(value).__name__} ({value!r})")
