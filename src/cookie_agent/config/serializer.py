"""Serialization utilities for configuration dataclasses."""

from dataclasses import asdict, fields, is_dataclass
from typing import Any, Type, TypeVar

T = TypeVar("T")

def serialize_to_dict(obj: Any) -> dict[str, Any]:
    """Recursively serialize a dataclass to a dictionary."""
    if not is_dataclass(obj):
        raise TypeError(f"Expected dataclass, got {type(obj)}")
    return asdict(obj)  # type: ignore[arg-type]

def deserialize_from_dict(cls: Type[T], data: dict[str, Any]) -> T:
    """Recursively instantiate a dataclass from a dictionary using type hints.
    
    This leverages the standard library `dataclasses.fields` to traverse
    the nested structure.
    
    Limitations:
    - Nested complex Union types are not supported.
    - Configuration dataclasses should avoid multiple dataclass Union members.
    """
    if not is_dataclass(cls):
        raise TypeError(f"Expected dataclass type, got {cls}")
        
    init_kwargs: dict[str, Any] = {}
    for field in fields(cls):
        name = field.name
        if name in data:
            val = data[name]
            field_type = field.type
            
            # Simplified generic unwrapping: if the field type is an Optional or Union,
            # this basic serializer expects the structure to match the primary type if it's a dataclass.
            # For 100% pure standard lib we check if field_type itself is a dataclass, 
            # or if the value is a dict and we can infer the dataclass.
            
            # Since Python 3.10+, unions like Config | None are common. 
            # We use a crude extraction for standard types if it's a dataclass class.
            
            # We extract actual type if it's a union/optional. 
            # For strictness in config, we assume fields that are dicts map to dataclasses.
            try:
                origin = getattr(field_type, "__origin__", None)
                args = getattr(field_type, "__args__", [])
                
                # Unwrap Optional
                if origin is None and is_dataclass(field_type) and isinstance(val, dict):
                    init_kwargs[name] = deserialize_from_dict(field_type, val)  # type: ignore[arg-type]
                elif type(None) in args and isinstance(val, dict):
                    # Find the dataclass type in the union args
                    dc_type = next((t for t in args if is_dataclass(t)), None)
                    if dc_type:
                        init_kwargs[name] = deserialize_from_dict(dc_type, val)  # type: ignore[arg-type]
                    else:
                        init_kwargs[name] = val
                else:
                    init_kwargs[name] = val
            except Exception:
                # Fallback to primitive assignment
                init_kwargs[name] = val
        else:
            # Missing fields should either trigger default factories or fail natively on instantiation
            pass
            
    return cls(**init_kwargs)

