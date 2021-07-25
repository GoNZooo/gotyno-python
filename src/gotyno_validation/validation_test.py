from dataclasses import dataclass
from typing import Generic, Literal, Optional, TypeVar, Union
import unittest
from gotyno_validation.gotyno_output import Color, Definitely, NotReally, Possibly, SomeType
from gotyno_validation.notifications import AllNotificationsCleared, CommandSuccess, NotificationAdded, NotificationCommandResult, NotifyUserPayload
from gotyno_validation.validation import (Unknown, ValidationResult, Validator, validate_dict, validate_enumeration_member, validate_float,
                                          validate_from_string, validate_int, validate_interface, validate_list, validate_literal,
                                          validate_optional, validate_string, Valid, Invalid, validate_string_map)
import json
import gotyno_validation.validation as v
import gotyno_validation.validation as validation
import gotyno_validation.encoding as encoding
import typing
import enum

T = TypeVar('T')


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
        valid_constructed = SomeType(
            type="SomeType",
            some_field='1',
            some_other_field=1,
            maybe_some_field=None)

        self.assertEqual(SomeType.validate(valid_object),
                         Valid(SomeType(type="SomeType",
                                        some_field='1',
                                        some_other_field=1,
                                        maybe_some_field=None)))

        self.assertEqual(valid_constructed.encode(),
                         '{"type": "SomeType", "some_field": "1", "some_other_field": 1, "maybe_some_field": null}')
        self.assertEqual(SomeType.decode(valid_constructed.encode()),
                         Valid(SomeType(type="SomeType",
                                        some_field='1',
                                        some_other_field=1,
                                        maybe_some_field=None)))

        valid_object_with_optional_value = {'type': 'SomeType',
                                            'some_field': '1',
                                            'some_other_field': 1,
                                            'maybe_some_field': 'hello'}
        valid_constructed_with_optional_value = SomeType(type="SomeType",
                                                         some_field='1',
                                                         some_other_field=1,
                                                         maybe_some_field="hello")

        self.assertEqual(SomeType.validate(valid_object_with_optional_value),
                         Valid(SomeType(type="SomeType",
                                        some_field='1',
                                        some_other_field=1,
                                        maybe_some_field="hello")))

        self.assertEqual(valid_constructed_with_optional_value.encode(),
                         '{"type": "SomeType", "some_field": "1", "some_other_field": 1, "maybe_some_field": "hello"}')
        self.assertEqual(SomeType.decode(valid_constructed_with_optional_value.encode()),
                         Valid(SomeType(type="SomeType",
                                        some_field='1',
                                        some_other_field=1,
                                        maybe_some_field="hello")))

    def test_decoding_deep_union_works(self):
        s = """
{
  "type": "CommandSuccess",
  "data": {
    "type": "NotificationAdded",
    "data": {
      "id": 0,
      "message": "Hello!"
    }
  }
}
          """
        expected_result = CommandSuccess(
            NotificationAdded(NotifyUserPayload(0, "Hello!")))
        decode_result = NotificationCommandResult.decode(s)

        self.assertIsInstance(decode_result, Valid)
        self.assertEqual(decode_result.value.data.data,
                         NotifyUserPayload(0, "Hello!"))
        self.assertEqual(decode_result.value, expected_result)

    def test_validate_list_works(self):
        encoded_list = json.dumps([1, 2, 3, 4])
        json_loaded = json.loads(encoded_list)
        result = validate_from_string(
            encoded_list, validate_list(validate_int))
        self.assertIsInstance(result, Valid)

    def test_possibly_works(self):
        definitely = Definitely(42)
        not_really = NotReally()

        definitely_encoded = definitely.encode(encoding.basic_to_json)
        self.assertEqual(definitely_encoded,
                         '{"type": "Definitely", "data": 42}')
        not_really_encoded = not_really.encode()
        self.assertEqual(not_really_encoded, '{"type": "NotReally"}')

        definitely_decoded = Definitely.decode(
            definitely_encoded, validate_T=validate_int)
        self.assertIsInstance(definitely_decoded, v.Valid)
        self.assertEqual(definitely_decoded.value, Definitely(42))

        not_really_decoded = NotReally.decode(not_really_encoded)
        self.assertIsInstance(not_really_decoded, v.Valid)
        self.assertEqual(not_really_decoded.value, NotReally())

        definitely_decoded_as_possibly = Possibly.decode(
            definitely_encoded, validate_T=validate_int)
        self.assertIsInstance(definitely_decoded_as_possibly, v.Valid)
        self.assertEqual(definitely_decoded_as_possibly.value, Definitely(42))

        not_really_decoded_as_possibly = Possibly.decode(
            not_really_encoded, validate_T=validate_int)
        self.assertIsInstance(not_really_decoded_as_possibly, v.Valid)
        self.assertEqual(not_really_decoded_as_possibly.value, NotReally())

    def test_enumeration_validation_works(self):
        red = Color.red
        green = Color.green
        blue = Color.blue

        not_enum_member = 'f0f0f0'

        red_result = validate_enumeration_member(red, Color)
        self.assertIsInstance(red_result, v.Valid)

        green_result = validate_enumeration_member(green, Color)
        self.assertIsInstance(green_result, v.Valid)

        blue_result = validate_enumeration_member(blue, Color)
        self.assertIsInstance(blue_result, v.Valid)

        not_enum_result = validate_enumeration_member(not_enum_member, Color)
        self.assertIsInstance(not_enum_result, Invalid)

    def empty_union_case_works(self):
        all_notifications_cleared = AllNotificationsCleared()
        all_notifications_cleared_encoded = all_notifications_cleared.encode()
        all_notifications_cleared_decoded = AllNotificationsCleared.decode(all_notifications_cleared.encode())
