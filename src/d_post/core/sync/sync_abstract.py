"""Abstract interface for syncing LocalRecord data to external stores."""

from __future__ import annotations

from abc import ABC, abstractmethod

from d_post.core.interactions import UserInteractionPort
from d_post.core.records.local_record import LocalRecord


class ISyncManager(ABC):
    """Interface for managing synchronization operations between local records and the database."""

    def __init__(self, interactions: UserInteractionPort):
        self.interactions = interactions

    @abstractmethod
    def sync_record_to_database(self, local_record: LocalRecord):
        """Synchronize a local record to the database."""
        raise NotImplementedError
