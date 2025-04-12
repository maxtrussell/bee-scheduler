import bisect
from datetime import datetime, date, timedelta
import os
from typing import Optional

import requests

BEEMINDER_TOKEN = os.getenv("BEEMINDER_TOKEN")
BEEMINDER_USER = os.getenv("BEEMINDER_USER")

BASE_URL = "https://www.beeminder.com/api/v1"


# Schedules a rate change from start to end
def schedule_rate(
    goal_name: str,
    start: date,
    end: date,
    rate: float,
    remove_overlapping: bool = False,
):
    # For start to be included, we need the date to reflect the starting boundary of the day.
    # This is a requirement for this function to behave consistently with "Take a Break" in the UI.
    start -= timedelta(days=1)

    # All beeminder datetimes are at 9 AM. For consistency, adjust start and end times.
    start_timestamp = int(
        datetime(year=start.year, month=start.month, day=start.day, hour=9).timestamp()
    )
    end_timestamp = int(
        datetime(year=end.year, month=end.month, day=end.day, hour=9).timestamp()
    )
    roadall = get_goal(goal_name)["roadall"]

    # Find the active rate at the time this block will be inserted.
    active_rate = 0
    for segment_start, _, segment_rate in roadall:
        active_rate = segment_rate
        if segment_start >= start_timestamp:
            break

    start_segment = [int(start_timestamp), None, active_rate]
    end_segment = [int(end_timestamp), None, rate]

    # Detect any pre-existing points that fall within the schedule rate period.
    overlapping_indices = [
        i for i, s in enumerate(roadall) if start_timestamp <= s[0] <= end_timestamp
    ]

    if overlapping_indices:
        if not remove_overlapping:
            raise Exception("Rate cannot be scheduled, too many overlapping segments")

        # Remove any overlapping segments.
        i = min(overlapping_indices)
        j = max(overlapping_indices)
        roadall = roadall[:i] + roadall[j + 1 :]

    # Add the new segments into roadall, while maintaining chronological order.
    bisect.insort(roadall, start_segment)
    bisect.insort(roadall, end_segment)

    # Remove any unnecessary segments.
    roadall = __simplify_segments(roadall)

    update_goal(goal_name, {"roadall": roadall})


# Removes segments from a graph by matching the segment start time.
def remove_segments(goal_name: str, to_remove: set[int]):
    roadall = get_goal(goal_name)["roadall"]

    new_roadall = [s for s in roadall if s[0] not in to_remove]
    update_goal(goal_name, {"roadall": new_roadall})


def get_goal(name: str) -> dict:
    resp = requests.get(
        f"{BASE_URL}/users/{BEEMINDER_USER}/goals/{name}.json",
        params=__get_params(),
    )
    resp.raise_for_status()
    return resp.json()


def update_goal(name: str, data: dict) -> dict:
    resp = requests.put(
        f"{BASE_URL}/users/{BEEMINDER_USER}/goals/{name}.json",
        json=__get_params(data),
    )
    resp.raise_for_status()
    return resp.json()


def __get_params(data: Optional[dict] = None):
    base = {
        "auth_token": BEEMINDER_TOKEN,
    }
    if data:
        base |= data
    return base


# If multiple, consecutive segments have the same rate, all but
# the final may be removed.
def __simplify_segments(
    roadall: list[list[int, float, float]],
) -> list[list[int, float, float]]:
    to_remove = set()
    prev_rate = None
    for i, segment in enumerate(roadall):
        rate = segment[2]
        if prev_rate is not None and rate == prev_rate:
            to_remove.add(i - 1)
        prev_rate = rate

    return [s for i, s in enumerate(roadall) if i not in to_remove]
