import json
import typing
from dataclasses import dataclass
from gotyno_validation import validation
from gotyno_validation import encoding


@dataclass(frozen=True)
class NotifyUserPayload:
    id: int
    message: str

    @staticmethod
    def validate(value: validation.Unknown) -> validation.ValidationResult['NotifyUserPayload']:
        return validation.validate_interface(value, {'id': validation.validate_int, 'message': validation.validate_string}, NotifyUserPayload)

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
        return validation.validate_interface(value, {'id': validation.validate_int, 'message': validation.validate_string, 'seen': validation.validate_bool}, Notification)

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
        return validation.validate_interface(value, {'userId': validation.validate_int, 'notification': Notification.validate, 'error': validation.validate_string}, AddNotificationError)

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
        return validation.validate_interface(value, {'userId': validation.validate_int, 'notificationId': validation.validate_int, 'error': validation.validate_string}, RemoveNotificationError)

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
        return validation.validate_interface(value, {'remainingNotifications': validation.validate_list(Notification.validate), 'removedNotification': Notification.validate}, RemoveNotificationResult)

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
        return validation.validate_interface(value, {'userId': validation.validate_int, 'id': validation.validate_int}, RemoveNotificationPayload)

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

    def to_json(self) -> typing.Dict[str, typing.Any]:
        raise NotImplementedError(
            '`to_json` is not implemented for base class `NotificationCommand`')

    def encode(self) -> str:
        raise NotImplementedError(
            '`encode` is not implemented for base class `NotificationCommand`')


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

    def to_json(self) -> typing.Dict[str, typing.Any]:
        raise NotImplementedError(
            '`to_json` is not implemented for base class `NotificationCommandSuccess`')

    def encode(self) -> str:
        raise NotImplementedError(
            '`encode` is not implemented for base class `NotificationCommandSuccess`')


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

    def to_json(self) -> typing.Dict[str, typing.Any]:
        raise NotImplementedError(
            '`to_json` is not implemented for base class `NotificationCommandFailure`')

    def encode(self) -> str:
        raise NotImplementedError(
            '`encode` is not implemented for base class `NotificationCommandFailure`')


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

    def to_json(self) -> typing.Dict[str, typing.Any]:
        raise NotImplementedError(
            '`to_json` is not implemented for base class `NotificationCommandResult`')

    def encode(self) -> str:
        raise NotImplementedError(
            '`encode` is not implemented for base class `NotificationCommandResult`')


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
