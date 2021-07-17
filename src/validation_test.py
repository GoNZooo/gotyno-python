from dataclasses import dataclass
from typing import Literal, Union
import unittest
from validation import (Unknown, ValidationResult, validate_dict, validate_float,
                        validate_from_string, validate_int, validate_interface, validate_literal,
                        validate_string, Valid, Invalid, validate_string_map)
import json


@dataclass(frozen=True)
class SomeType:
    some_field: str
    some_other_field: int
    type: Literal["SomeType"] = 'SomeType'

    @staticmethod
    def validate(value: Unknown) -> ValidationResult['SomeType']:
        """
        Validates a value as being of type `SomeType`
        """
        result = validate_interface(value,
                                    {'type': validate_literal('SomeType'),
                                     'some_field': validate_string,
                                     'some_other_field': validate_int}
                                    )

        if isinstance(result, Invalid):
            return result

        return Valid(SomeType(**result.value))

    @staticmethod
    def decode(string: Union[str, bytes]) -> ValidationResult['SomeType']:
        """
        Decodes a string into a SomeType
        """
        return validate_from_string(string, SomeType.validate)

    def encode(self) -> str:
        """
        Encodes this SomeType into a string
        """
        return json.dumps({**self.__dict__, 'type': 'SomeType'})


class TestValidator(unittest.TestCase):
    "A test suite for our validation functions"

    def test_validate_string_with_valid_values(self):
        self.assertEqual(validate_string('hullaballoo'), Valid('hullaballoo'))
        self.assertEqual(validate_string(b'hullaballoo'), Valid('hullaballoo'))

    def test_validate_string_with_invalid_values(self):
        self.assertEqual(validate_string(1), Invalid(
            'Value is not string: 1 (<class \'int\'>)'))
        self.assertEqual(validate_string(True), Invalid(
            'Value is not string: True (<class \'bool\'>)'))
        self.assertEqual(validate_string(None), Invalid(
            'Value is not string: None (<class \'NoneType\'>)'))
        self.assertEqual(validate_string([]), Invalid(
            'Value is not string: [] (<class \'list\'>)'))
        self.assertEqual(validate_string({}), Invalid(
            'Value is not string: {} (<class \'dict\'>)'))

    def test_validate_int_with_valid_values(self):
        self.assertEqual(validate_int(1), Valid(1))

    def test_validate_int_with_invalid_values(self):
        self.assertEqual(validate_int(True), Invalid(
            'Value is not int: True (<class \'bool\'>)'))
        self.assertEqual(validate_int(None), Invalid(
            'Value is not int: None (<class \'NoneType\'>)'))

    def test_validate_float_with_valid_values(self):
        self.assertEqual(validate_float(1.0), Valid(1.0))

    def test_validate_float_with_invalid_values(self):
        self.assertEqual(validate_float(True), Invalid(
            'Value is not float: True (<class \'bool\'>)'))
        self.assertEqual(validate_float(None), Invalid(
            'Value is not float: None (<class \'NoneType\'>)'))
        self.assertEqual(validate_float([]), Invalid(
            'Value is not float: [] (<class \'list\'>)'))
        self.assertEqual(validate_float({}), Invalid(
            'Value is not float: {} (<class \'dict\'>)'))
        self.assertEqual(validate_float('1.0'), Invalid(
            'Value is not float: 1.0 (<class \'str\'>)'))

    def test_validate_dict_with_valid_values(self):
        self.assertEqual(validate_dict(
            {'a': 1}, validate_t=validate_string, validate_u=validate_int), Valid({'a': 1}))
        self.assertEqual(validate_dict(
            {42: 1}, validate_t=validate_int, validate_u=validate_int), Valid({42: 1}))

    def test_validate_dict_with_invalid_values(self):
        self.assertEqual(validate_dict(
            1, validate_t=validate_string, validate_u=validate_string), Invalid(
            'Expected dict, got: 1 (<class \'int\'>)'))
        self.assertEqual(validate_dict(
            True, validate_t=validate_string, validate_u=validate_string), Invalid(
            'Expected dict, got: True (<class \'bool\'>)'))
        self.assertEqual(validate_dict(
            {'a': 1}, validate_t=validate_string, validate_u=validate_string), Invalid(
            {'a': 'Value is not string: 1 (<class \'int\'>)'}))

    def test_validate_string_map_with_valid_values(self):
        self.assertEqual(validate_string_map(
            {'a': 42}, validate_int), Valid({'a': 42}))

    def test_example_class_functionality(self):
        valid_object = {'type': 'SomeType',
                        'some_field': '1', 'some_other_field': 1}
        valid_constructed = SomeType(some_field='1', some_other_field=1)
        self.assertEqual(SomeType.validate(valid_object),
                         Valid(SomeType(some_field='1', some_other_field=1)))

        self.assertEqual(valid_constructed.encode(),
                         '{"some_field": "1", "some_other_field": 1, "type": "SomeType"}')
        self.assertEqual(SomeType.decode(valid_constructed.encode()),
                         Valid(SomeType(some_field='1', some_other_field=1)))
