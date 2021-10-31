from typing import List

from handler import handle_event


def main(events: List['azure.functions.EventHubEvent']):
    return handle_event(events)
