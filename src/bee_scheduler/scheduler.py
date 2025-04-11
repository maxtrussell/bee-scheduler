import bisect
from datetime import datetime, date
import os
from typing import Optional

import requests

BEEMINDER_TOKEN = os.getenv("BEEMINDER_TOKEN")
BEEMINDER_USER = os.getenv("BEEMINDER_USER")

BASE_URL = "https://www.beeminder.com/api/v1"


# Schedules a rate change from start to end
def schedule_rate(goal_name: str, start: date, end: date, rate: float):
    start_timestamp = int(
        datetime(year=start.year, month=start.month, day=start.day).timestamp()
    )
    end_timestamp = int(
        datetime(year=end.year, month=end.month, day=end.day).timestamp()
    )
    roadall = get_goal(goal_name)["roadall"]

    # Find the active rate at the time this block will be inserted.
    active_rate = 0
    for segment_start, _, segment_rate in roadall:
        active_rate = segment_rate
        if segment_start > start_timestamp:
            break

    start_segment = [int(start_timestamp), None, active_rate]
    end_segment = [int(end_timestamp), None, rate]

    # Add the new segments into roadall, while maintaining chronological order.
    bisect.insort(roadall, start_segment)
    bisect.insort(roadall, end_segment)

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
