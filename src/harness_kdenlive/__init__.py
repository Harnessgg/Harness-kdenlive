"""Agent-first harness for editing Kdenlive project files."""

from harness_kdenlive.core.transaction import TransactionManager
from harness_kdenlive.core.xml_engine import KdenliveProject

__all__ = ["KdenliveProject", "TransactionManager"]

__version__ = "0.4.0"
