"""Synchronization interfaces and implementations."""

from .sync_abstract import ISyncManager
from .sync_noop import NoopSyncManager

__all__ = ["ISyncManager", "NoopSyncManager"]
