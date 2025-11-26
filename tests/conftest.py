"""
Pytest configuration and fixtures for SpikeAgent tests.
"""

import os
import sys

# Add src to path so tests can import spikeagent
_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _root_dir not in sys.path:
    sys.path.insert(0, os.path.join(_root_dir, 'src'))

