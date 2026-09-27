"""
conftest.py — pytest configuration for EHSA backend tests.

Adds the 'backend' directory to sys.path so that 'app.*' imports work
without installing the package.
"""
import sys
from pathlib import Path

# Add backend/ to the path so pytest can find 'app.*' modules
sys.path.insert(0, str(Path(__file__).parent.parent))
