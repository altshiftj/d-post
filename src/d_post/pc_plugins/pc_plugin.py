"""Base interface for PC-level plugins that supply configuration overlays."""

from abc import ABC, abstractmethod

from d_post.core.config import PCConfig


class PCPlugin(ABC):
    """Base interface for PC-level configuration plugins."""

    @abstractmethod
    def get_config(self) -> PCConfig:
        """Return the configuration describing this PC environment."""
        raise NotImplementedError
