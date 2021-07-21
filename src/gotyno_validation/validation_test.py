from dataclasses import dataclass
from typing import Generic, Literal, Optional, TypeVar, Union
import unittest
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


@dataclass(frozen=True)
class SomeType:
    some_field: str
    some_other_field: int
    maybe_some_field: Optional[str]
    type: Literal['SomeType'] = 'SomeType'

    @staticmethod
    def validate(value: v.Unknown) -> v.ValidationResult['SomeType']:
        return v.validate_interface(value, {'some_field': v.validate_string, 'some_other_field': v.validate_int, 'maybe_some_field': v.validate_optional(v.validate_string), 'type': v.validate_literal('SomeType')}, SomeType)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> v.ValidationResult['SomeType']:
        return v.validate_from_string(string, SomeType.validate)

    def encode(self) -> str:
        return v.dumps(self.__dict__)


@dataclass(frozen=True)
class Holder(Generic[T]):
    value: T

    @staticmethod
    def validate(validate_t: Validator[T]) -> Validator['Holder[T]']:
        def validate_HolderT(value: Unknown) -> ValidationResult['Holder[T]']:
            return validate_interface(value, {'value': validate_t}, Holder)
        return validate_HolderT

    @staticmethod
    def decode(string: Union[str, bytes]) -> ValidationResult['Holder[T]']:
        return validate_from_string(string, Holder.validate)

    def encode(self) -> str:
        return json.dumps(self.__dict__)


@dataclass(frozen=True)
class NotifyUserPayload:
    id: int
    message: str

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotifyUserPayload']:
        return validation.validate_interface(value, {'id': validation.validate_int, 'message': validation.validate_string})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotifyUserPayload']:
        return validation.validate_from_string(string, NotifyUserPayload.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'id': self.id, 'message': self.message}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class Notification:
    id: int
    message: str
    seen: bool

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['Notification']:
        return validation.validate_interface(value, {'id': validation.validate_int, 'message': validation.validate_string, 'seen': validation.validate_bool})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['Notification']:
        return validation.validate_from_string(string, Notification.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'id': self.id, 'message': self.message, 'seen': self.seen}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class AddNotificationError:
    userId: int
    notification: Notification
    error: str

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['AddNotificationError']:
        return validation.validate_interface(value, {'userId': validation.validate_int, 'notification': Notification.validate, 'error': validation.validate_string})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['AddNotificationError']:
        return validation.validate_from_string(string, AddNotificationError.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'userId': self.userId, 'notification': Notification.to_json(self.notification), 'error': self.error}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class RemoveNotificationError:
    userId: int
    notificationId: int
    error: str

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['RemoveNotificationError']:
        return validation.validate_interface(value, {'userId': validation.validate_int, 'notificationId': validation.validate_int, 'error': validation.validate_string})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['RemoveNotificationError']:
        return validation.validate_from_string(string, RemoveNotificationError.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'userId': self.userId, 'notificationId': self.notificationId, 'error': self.error}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class RemoveNotificationResult:
    remainingNotifications: typing.List[Notification]
    removedNotification: Notification

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['RemoveNotificationResult']:
        return validation.validate_interface(value, {'remainingNotifications': validation.validate_list(Notification.validate), 'removedNotification': Notification.validate})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['RemoveNotificationResult']:
        return validation.validate_from_string(string, RemoveNotificationResult.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'remainingNotifications': encoding.list_to_json(Notification.to_json)(self.remainingNotifications), 'removedNotification': Notification.to_json(self.removedNotification)}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class RemoveNotificationPayload:
    userId: int
    id: int

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['RemoveNotificationPayload']:
        return validation.validate_interface(value, {'userId': validation.validate_int, 'id': validation.validate_int})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['RemoveNotificationPayload']:
        return validation.validate_from_string(string, RemoveNotificationPayload.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'userId': self.userId, 'id': self.id}

    def encode(self) -> str:
        return json.dumps(self.to_json())


class NotificationCommand:
    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotificationCommand']:
        return validation.validate_with_type_tags(value, 'type', {'GetNotifications': GetNotifications.validate, 'NotifyUser': NotifyUser.validate, 'RemoveNotification': RemoveNotification.validate, 'ClearNotifications': ClearNotifications.validate, 'ClearAllNotifications': ClearAllNotifications.validate})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotificationCommand']:
        return validation.validate_from_string(string, NotificationCommand.validate)


@dataclass(frozen=True)
class GetNotifications(NotificationCommand):
    data: int

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['GetNotifications']:
        return validation.validate_with_type_tag(value, 'type', 'GetNotifications', {'data': validation.validate_int}, GetNotifications)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['GetNotifications']:
        return validation.validate_from_string(string, GetNotifications.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'GetNotifications', 'data': self.data}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class NotifyUser(NotificationCommand):
    data: NotifyUserPayload

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotifyUser']:
        return validation.validate_with_type_tag(value, 'type', 'NotifyUser', {'data': NotifyUserPayload.validate}, NotifyUser)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotifyUser']:
        return validation.validate_from_string(string, NotifyUser.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'NotifyUser', 'data': self.data.to_json()}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class RemoveNotification(NotificationCommand):
    data: RemoveNotificationPayload

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['RemoveNotification']:
        return validation.validate_with_type_tag(value, 'type', 'RemoveNotification', {'data': RemoveNotificationPayload.validate}, RemoveNotification)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['RemoveNotification']:
        return validation.validate_from_string(string, RemoveNotification.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'RemoveNotification', 'data': self.data.to_json()}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class ClearNotifications(NotificationCommand):
    data: int

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['ClearNotifications']:
        return validation.validate_with_type_tag(value, 'type', 'ClearNotifications', {'data': validation.validate_int}, ClearNotifications)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['ClearNotifications']:
        return validation.validate_from_string(string, ClearNotifications.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'ClearNotifications', 'data': self.data}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class ClearAllNotifications(NotificationCommand):
    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['ClearAllNotifications']:
        return validation.validate_with_type_tag(value, 'type', 'ClearAllNotifications', {}, ClearAllNotifications)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['ClearAllNotifications']:
        return validation.validate_from_string(string, ClearAllNotifications.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'ClearAllNotifications'}

    def encode(self) -> str:
        return json.dumps(self.to_json())


class NotificationCommandSuccess:
    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotificationCommandSuccess']:
        return validation.validate_with_type_tags(value, 'type', {'Notifications': Notifications.validate, 'NotificationAdded': NotificationAdded.validate, 'NotificationRemoved': NotificationRemoved.validate, 'NotificationsCleared': NotificationsCleared.validate, 'AllNotificationsCleared': AllNotificationsCleared.validate})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotificationCommandSuccess']:
        return validation.validate_from_string(string, NotificationCommandSuccess.validate)


@dataclass(frozen=True)
class Notifications(NotificationCommandSuccess):
    data: typing.List[Notification]

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['Notifications']:
        return validation.validate_with_type_tag(value, 'type', 'Notifications', {'data': validation.validate_list(Notification.validate)}, Notifications)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['Notifications']:
        return validation.validate_from_string(string, Notifications.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'Notifications', 'data': encoding.list_to_json(Notification.to_json)(self.data)}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class NotificationAdded(NotificationCommandSuccess):
    data: NotifyUserPayload

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotificationAdded']:
        return validation.validate_with_type_tag(value, 'type', 'NotificationAdded', {'data': NotifyUserPayload.validate}, NotificationAdded)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotificationAdded']:
        return validation.validate_from_string(string, NotificationAdded.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'NotificationAdded', 'data': self.data.to_json()}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class NotificationRemoved(NotificationCommandSuccess):
    data: RemoveNotificationResult

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotificationRemoved']:
        return validation.validate_with_type_tag(value, 'type', 'NotificationRemoved', {'data': RemoveNotificationResult.validate}, NotificationRemoved)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotificationRemoved']:
        return validation.validate_from_string(string, NotificationRemoved.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'NotificationRemoved', 'data': self.data.to_json()}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class NotificationsCleared(NotificationCommandSuccess):
    data: int

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotificationsCleared']:
        return validation.validate_with_type_tag(value, 'type', 'NotificationsCleared', {'data': validation.validate_int}, NotificationsCleared)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotificationsCleared']:
        return validation.validate_from_string(string, NotificationsCleared.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'NotificationsCleared', 'data': self.data}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class AllNotificationsCleared(NotificationCommandSuccess):
    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['AllNotificationsCleared']:
        return validation.validate_with_type_tag(value, 'type', 'AllNotificationsCleared', {}, AllNotificationsCleared)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['AllNotificationsCleared']:
        return validation.validate_from_string(string, AllNotificationsCleared.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'AllNotificationsCleared'}

    def encode(self) -> str:
        return json.dumps(self.to_json())


class NotificationCommandFailure:
    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotificationCommandFailure']:
        return validation.validate_with_type_tags(value, 'type', {'NotificationNotRemoved': NotificationNotRemoved.validate, 'NotificationNotAdded': NotificationNotAdded.validate, 'InvalidCommand': InvalidCommand.validate})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotificationCommandFailure']:
        return validation.validate_from_string(string, NotificationCommandFailure.validate)


@dataclass(frozen=True)
class NotificationNotRemoved(NotificationCommandFailure):
    data: RemoveNotificationError

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotificationNotRemoved']:
        return validation.validate_with_type_tag(value, 'type', 'NotificationNotRemoved', {'data': RemoveNotificationError.validate}, NotificationNotRemoved)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotificationNotRemoved']:
        return validation.validate_from_string(string, NotificationNotRemoved.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'NotificationNotRemoved', 'data': self.data.to_json()}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class NotificationNotAdded(NotificationCommandFailure):
    data: AddNotificationError

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotificationNotAdded']:
        return validation.validate_with_type_tag(value, 'type', 'NotificationNotAdded', {'data': AddNotificationError.validate}, NotificationNotAdded)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotificationNotAdded']:
        return validation.validate_from_string(string, NotificationNotAdded.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'NotificationNotAdded', 'data': self.data.to_json()}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class InvalidCommand(NotificationCommandFailure):
    data: str

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['InvalidCommand']:
        return validation.validate_with_type_tag(value, 'type', 'InvalidCommand', {'data': validation.validate_string}, InvalidCommand)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['InvalidCommand']:
        return validation.validate_from_string(string, InvalidCommand.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'InvalidCommand', 'data': self.data}

    def encode(self) -> str:
        return json.dumps(self.to_json())


class NotificationCommandResult:
    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotificationCommandResult']:
        return validation.validate_with_type_tags(value, 'type', {'CommandSuccess': CommandSuccess.validate, 'CommandFailure': CommandFailure.validate})

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['NotificationCommandResult']:
        return validation.validate_from_string(string, NotificationCommandResult.validate)


@dataclass(frozen=True)
class CommandSuccess(NotificationCommandResult):
    data: NotificationCommandSuccess

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['CommandSuccess']:
        return validation.validate_with_type_tag(value, 'type', 'CommandSuccess', {'data': NotificationCommandSuccess.validate}, CommandSuccess)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['CommandSuccess']:
        return validation.validate_from_string(string, CommandSuccess.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'CommandSuccess', 'data': self.data.to_json()}

    def encode(self) -> str:
        return json.dumps(self.to_json())


@dataclass(frozen=True)
class CommandFailure(NotificationCommandResult):
    data: NotificationCommandFailure

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['CommandFailure']:
        return validation.validate_with_type_tag(value, 'type', 'CommandFailure', {'data': NotificationCommandFailure.validate}, CommandFailure)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['CommandFailure']:
        return validation.validate_from_string(string, CommandFailure.validate)

    def to_json(self) -> typing.Dict[str, typing.Any]:
        return {'type': 'CommandFailure', 'data': self.data.to_json()}

    def encode(self) -> str:
        return json.dumps(self.to_json())


class Possibly(Generic[T]):
    @staticmethod
    def validate(validate_T: v.Validator[T]) -> v.Validator['Possibly[T]']:
        def validate_PossiblyT(value: v.Unknown) -> v.ValidationResult['Possibly[T]']:
            return v.validate_with_type_tags(value, 'type', {'NotReally': NotReally.validate, 'Definitely': Definitely.validate(validate_T)})
        return validate_PossiblyT

    @staticmethod
    def decode(string: typing.Union[str, bytes], validate_T: v.Validator[T]) -> v.ValidationResult['Possibly[T]']:
        return v.validate_from_string(string, Possibly.validate(validate_T))


@dataclass(frozen=True)
class NotReally(Possibly[T]):
    @staticmethod
    def validate(value: v.Unknown) -> v.ValidationResult['NotReally']:
        return v.validate_with_type_tag(value, 'type', 'NotReally', {}, NotReally)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> v.ValidationResult['NotReally']:
        return v.validate_from_string(string, NotReally.validate)

    def encode(self) -> str:
        return json.dumps({**self.__dict__, 'type': 'NotReally'})


@dataclass(frozen=True)
class Definitely(Possibly[T]):
    data: T

    @staticmethod
    def validate(validate_T: v.Validator[T]) -> v.Validator['Definitely[T]']:
        def validate_DefinitelyT(value: v.Unknown) -> v.ValidationResult['Definitely[T]']:
            return v.validate_with_type_tag(value, 'type', 'Definitely', {'data': validate_T}, Definitely)
        return validate_DefinitelyT

    @staticmethod
    def decode(string: typing.Union[str, bytes], validate_T: v.Validator[T]) -> v.ValidationResult['Definitely[T]']:
        return v.validate_from_string(string, Definitely.validate(validate_T))

    def encode(self) -> str:
        return json.dumps({**self.__dict__, 'type': 'Definitely'})


class Color(enum.Enum):
    red = 'ff0000'
    green = '00ff00'
    blue = '0000ff'

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['Color']:
        return validation.validate_enumeration_member(value, Color)

    @staticmethod
    def decode(string: typing.Union[str, bytes]) -> validation.ValidationResult['Color']:
        return validation.validate_from_string(string, Color.validate)

    def to_json(self) -> typing.Any:
        return self.value

    def encode(self) -> str:
        return str(self.value)


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
            some_field='1', some_other_field=1, maybe_some_field=None)

        self.assertEqual(SomeType.validate(valid_object),
                         Valid(SomeType(some_field='1', some_other_field=1, maybe_some_field=None)))

        self.assertEqual(valid_constructed.encode(),
                         '{"some_field": "1", "some_other_field": 1, "maybe_some_field": null, "type": "SomeType"}')
        self.assertEqual(SomeType.decode(valid_constructed.encode()),
                         Valid(SomeType(some_field='1', some_other_field=1, maybe_some_field=None)))

        valid_object_with_optional_value = {'type': 'SomeType',
                                            'some_field': '1',
                                            'some_other_field': 1,
                                            'maybe_some_field': 'hello'}
        valid_constructed_with_optional_value = SomeType(
            some_field='1', some_other_field=1, maybe_some_field="hello")

        self.assertEqual(SomeType.validate(valid_object_with_optional_value),
                         Valid(SomeType(some_field='1', some_other_field=1, maybe_some_field="hello")))

        self.assertEqual(valid_constructed_with_optional_value.encode(),
                         '{"some_field": "1", "some_other_field": 1, "maybe_some_field": "hello", "type": "SomeType"}')
        self.assertEqual(SomeType.decode(valid_constructed_with_optional_value.encode()),
                         Valid(SomeType(some_field='1', some_other_field=1, maybe_some_field="hello")))

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
        self.assertEqual(expected_result.encode(), s)

    def test_validate_list_works(self):
        encoded_list = json.dumps([1, 2, 3, 4])
        json_loaded = json.loads(encoded_list)
        result = validate_from_string(
            encoded_list, validate_list(validate_int))
        self.assertIsInstance(result, Valid)

    def test_possibly_works(self):
        definitely = Definitely(42)
        not_really = NotReally()

        definitely_encoded = definitely.encode()
        self.assertEqual(definitely_encoded,
                         '{"data": 42, "type": "Definitely"}')
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
