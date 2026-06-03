from __future__ import annotations

from datetime import datetime

TIMELINE_TEMPLATE = """
<div style="font-family: monospace;">
{entries}
</div>
"""

ENTRY_TEMPLATE = """
<div style="margin: 8px 0; padding: 8px; border-left: 3px solid {color};">
  <span style="color: #8b949e;">{time}</span>
  <span style="color: {color}; font-weight: bold;">[{event_type}]</span>
  <span>{description}</span>
</div>
"""


async def generate_timeline(events: list[dict]) -> str:
    entries = []
    for event in sorted(events, key=lambda e: e.get("timestamp", "")):
        color = "#58a6ff"
        if event.get("threat_score", 0) >= 0.7:
            color = "#da3633"
        elif event.get("threat_score", 0) >= 0.4:
            color = "#d29922"
        ts = event.get("timestamp", "")
        if isinstance(ts, datetime):
            ts = ts.isoformat()
        entries.append(ENTRY_TEMPLATE.format(
            time=str(ts)[:19],
            event_type=event.get("event_type", "unknown"),
            description=event.get("description", f"Event from {event.get('source_ip', 'unknown')}"),
            color=color,
        ))
    return TIMELINE_TEMPLATE.format(entries="\n".join(entries))
