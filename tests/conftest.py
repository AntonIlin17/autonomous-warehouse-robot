"""Test configuration for source-tree imports."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "src" / "warehouse_robot_llm"
sys.path.insert(0, str(PACKAGE_ROOT))
