"""
Stage 1 Paths (Branch 2)
------------------------

This class must satisfy two constraints:

1. Stage 1 downloader calls `Paths()` with NO arguments.
2. Stage 1 tests monkeypatch Paths and construct it WITH arguments.

Therefore:
    - All fields must have defaults.
    - All fields must still accept explicit Path arguments.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Paths:
    raw_dir: Path = Path("./raw")
    metadata_dir: Path = Path("./metadata")
    config_dir: Path = Path("./config")
    intermediate_dir: Path = Path("./intermediate")
    logs_dir: Path = Path("./logs")   # ⭐ REQUIRED FOR ORCHESTRATOR


    def __repr__(self):
        return (
            "Stage1Paths(\n"
            f"  raw_dir={self.raw_dir},\n"
            f"  metadata_dir={self.metadata_dir},\n"
            f"  config_dir={self.config_dir},\n"
            f"  intermediate_dir={self.intermediate_dir},\n"
            f"  logs_dir={self.logs_dir}\n"
            ")"
        )
