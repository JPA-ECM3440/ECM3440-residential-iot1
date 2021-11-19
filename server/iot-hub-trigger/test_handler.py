from unittest.mock import MagicMock, patch

from azure.functions import EventHubEvent
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

from handler import handle_event


class MatchMethod:
    def __init__(self, method: str, payload: str):
        self.method = method
        self.payload = payload

    def __eq__(self, other: CloudToDeviceMethod):
        return self.method == other.method_name and self.payload == other.payload


@patch("handler.IoTHubRegistryManager")
@patch("os.getenv")
def test_event_with_over_500(mock_getenv, mock_registry_manager):
    event = MagicMock(spec=EventHubEvent)
    event.get_body.return_value = b'{"soil_moisture": 572}'
    event.iothub_metadata = {'connection-device-id': 12345}
    mock_getenv.return_value = "test_conn_string"
    mocked_registry_manager = MagicMock(spec=IoTHubRegistryManager)
    mock_registry_manager.return_value = mocked_registry_manager

    handle_event([3, "four", event])

    mock_registry_manager.assert_called_once_with("test_conn_string")
    mocked_registry_manager.invoke_device_method.assert_called_once_with(12345, MatchMethod("relay_off", "{}"))


@patch("handler.IoTHubRegistryManager")
@patch("os.getenv")
def test_event_with_under_500(mock_getenv, mock_registry_manager):
    event = MagicMock(spec=EventHubEvent)
    event.get_body.return_value = b'{"soil_moisture": 123}'
    event.iothub_metadata = {'connection-device-id': 12345}
    mock_getenv.return_value = "test_conn_string"
    mocked_registry_manager = MagicMock(spec=IoTHubRegistryManager)
    mock_registry_manager.return_value = mocked_registry_manager

    handle_event([3, "four", event])

    mock_registry_manager.assert_called_once_with("test_conn_string")
    mocked_registry_manager.invoke_device_method.assert_called_once_with(12345, MatchMethod("relay_on", "{}"))


def test_event_with_no_value():
    event = MagicMock(spec=EventHubEvent)
    event.get_body.return_value = b'{"other_key": "foo"}'
    event.iothub_metadata = {'connection-device-id': 12345}

    handle_event([3, "four", event])
