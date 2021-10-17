import json
import logging
import os
from typing import List

import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod


def dispatch_event(device_id: str, method_name: str, payload: str = '{}'):
    direct_method = CloudToDeviceMethod(method_name=method_name, payload=payload)
    conn_str = os.getenv('REGISTRY_MANAGER_CONNECTION_STRING')
    registry_manager = IoTHubRegistryManager(conn_str)

    logging.info(f"Sending direct method request for {direct_method.method_name} for device {device_id}")

    registry_manager.invoke_device_method(device_id, direct_method)


def main(events: List[func.EventHubEvent]):
    event = events[-1]
    content = json.loads(event.get_body().decode('utf-8'))
    device_id = event.iothub_metadata['connection-device-id']

    logging.info(f"Received {content} from {device_id}")

    soil_moisture = content['soil_moisture']

    if soil_moisture > 500:
        dispatch_event(device_id, 'relay_off')
    else:
        dispatch_event(device_id, 'relay_on')
