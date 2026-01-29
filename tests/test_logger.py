"""Test logger module with trace ID generation."""

import re
import pytest


def test_create_trace_id_exists():
    """Verify create_trace_id function exists."""
    from logger import create_trace_id
    assert callable(create_trace_id)


def test_create_trace_id_returns_string():
    """Verify create_trace_id returns a string."""
    from logger import create_trace_id
    trace_id = create_trace_id()
    assert isinstance(trace_id, str)


def test_create_trace_id_format():
    """Verify trace_id follows expected format: trace_YYYYMMDD_HHMMSS_UUID8."""
    from logger import create_trace_id
    trace_id = create_trace_id()
    # Format: trace_YYYYMMDD_HHMMSS_xxxxxxxx
    pattern = r'^trace_\d{8}_\d{6}_[a-z0-9]{8}$'
    assert re.match(pattern, trace_id), f"trace_id '{trace_id}' doesn't match expected format"


def test_create_trace_id_uniqueness():
    """Verify multiple trace_ids are unique."""
    from logger import create_trace_id
    trace_ids = [create_trace_id() for _ in range(10)]
    assert len(set(trace_ids)) == 10, "trace_ids should be unique"


def test_create_trace_id_timestamp_prefix():
    """Verify trace_id starts with 'trace_' followed by timestamp."""
    from logger import create_trace_id
    trace_id = create_trace_id()
    assert trace_id.startswith('trace_')
    parts = trace_id.split('_')
    # Format: trace_YYYYMMDD_HHMMSS_xxxxxxxx (4 parts due to _ in timestamp)
    assert len(parts) == 4
    # Second part should be date (YYYYMMDD)
    assert len(parts[1]) == 8 and parts[1].isdigit()
    # Third part should be time (HHMMSS)
    assert len(parts[2]) == 6 and parts[2].isdigit()
    # Fourth part should be uuid (8 chars)
    assert len(parts[3]) == 8
