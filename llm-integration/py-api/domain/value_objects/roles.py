from enum import Enum

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    DEVELOPER = "developer"
    EVENT = "event"

    @classmethod
    def message_roles(cls):
        """Roles that produce message_text events."""
        return {cls.USER, cls.ASSISTANT, cls.SYSTEM, cls.DEVELOPER}
