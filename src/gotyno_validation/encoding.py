from typing import Any, Callable, TypeVar, Union, Optional, List

T = TypeVar('T')
Encoder = Callable[[T], str]
ToJSON = Callable[[T], Any]


def encode_basic(value: Union[str, int, float, bool]) -> str:
    """
    Encodes a basic value into a string.
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return str(value)
    elif isinstance(value, bool):
        return str(value)
    else:
        raise ValueError(f'Unsupported type: {type(value)}')


def encode_optional(encode_T: Encoder[T]) -> Encoder[Optional[T]]:
    """
    Takes an encoder for a type `T` and creates an encoder for an `Optional[T]`.
    """
    def encode_optional_T(value: Optional[T]) -> str:
        if value is None:
            return 'null'
        else:
            return encode_T(value)

    return encode_optional_T


def encode_list(encode_T: Encoder[T]) -> Encoder[List[T]]:
    """
    Takes an encoder for a type `T` and creates an encoder for a `List[T]`.
    """
    def encode_list_T(value: List[T]) -> str:
        return '[' + ','.join([encode_T(v) for v in value]) + ']'

    return encode_list_T


def basic_to_json(value: Union[str, int, float, bool]) -> Any:
    """
    Converts a basic value into a JSON compatible value.
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, int):
        return value
    elif isinstance(value, float):
        return value
    elif isinstance(value, bool):
        return value
    else:
        raise ValueError(f'Unsupported type: {type(value)}')


def optional_to_json(T_to_json: ToJSON[T]) -> ToJSON[Optional[T]]:
    """
    Takes an encoder for a type `T` and creates an encoder for an `Optional[T]`.
    """
    def optional_T_to_json(value: Optional[T]) -> Any:
        if value is None:
            return None
        else:
            return T_to_json(value)

    return optional_T_to_json


def list_to_json(T_to_json: ToJSON[T]) -> ToJSON[List[T]]:
    """
    Takes an encoder for a type `T` and creates an encoder for a `List[T]`.
    """
    def list_T_to_json(value: List[T]) -> Any:
        return [T_to_json(v) for v in value]

    return list_T_to_json
