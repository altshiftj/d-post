"""Public-safe sync backend that performs no external uploads."""

from __future__ import annotations

from d_post.core.records.local_record import LocalRecord
from d_post.core.sync.sync_abstract import ISyncManager


class NoopSyncManager(ISyncManager):
    """Mark local record files as synced without calling external services."""

    def sync_record_to_database(self, local_record: LocalRecord) -> bool:
        """Acknowledge all tracked files so the public build stays offline-safe."""
        for file_path in list(local_record.files_uploaded):
            local_record.mark_uploaded(file_path)
        local_record.is_in_db = True
        return False
