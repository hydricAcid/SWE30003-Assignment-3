from abc import ABC, abstractmethod
from typing import Dict


class User(ABC):
    """Abstract information holder for shared human user identifiers."""

    def __init__(self, user_id: str, full_name: str, phone: str) -> None:
        self.user_id = user_id
        self.full_name = full_name
        self.phone = phone

    @abstractmethod
    def to_dict(self) -> Dict[str, str]:
        """Serialise user attributes into a dictionary for csv storage."""
        raise NotImplementedError
