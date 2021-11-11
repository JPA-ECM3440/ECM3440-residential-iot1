from typing import List

from azure.functions import EventHubEvent
from handler import handle_event


def main(events: List[EventHubEvent]):
    return handle_event(events)
