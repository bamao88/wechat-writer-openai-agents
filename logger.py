"""Logger module with trace ID generation for request tracking."""

import uuid
from datetime import datetime


def create_trace_id() -> str:
    """Generate a unique trace ID for request tracking.

    Format: trace_YYYYMMDD_HHMMSS_xxxxxxxx
    - YYYYMMDD: Date
    - HHMMSS: Time
    - xxxxxxxx: 8-character random UUID suffix

    Returns:
        A unique trace ID string.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return f"trace_{timestamp}_{short_uuid}"
