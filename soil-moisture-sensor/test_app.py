from unittest.mock import MagicMock, patch, mock_open

from azure.iot.device import IoTHubDeviceClient
from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_relay import GroveRelay

from app import SoilMoistureMonitor, connect, main


@patch('app.MethodResponse')
def test_relay_on(mock_method_response):
    mock_device_client = MagicMock(spec=IoTHubDeviceClient)
    mock_adc = MagicMock(spec=ADC)
    mock_relay = MagicMock(spec=GroveRelay)
    mock_request = MagicMock()

    mock_request.name = 'relay_on'

    mock_soil_moisture_monitor = SoilMoistureMonitor(adc=mock_adc, device_client=mock_device_client, relay=mock_relay)
    mock_soil_moisture_monitor.handle_request(request=mock_request)

    mock_method_response.create_from_method_request.assert_called_once_with(mock_request, 200)
    mock_device_client.send_method_response.assert_called_once_with(
        mock_method_response.create_from_method_request.return_value
    )
    mock_relay.on.assert_called_once()


@patch('app.MethodResponse')
def test_relay_off(mock_method_response):
    mock_device_client = MagicMock(spec=IoTHubDeviceClient)
    mock_adc = MagicMock(spec=ADC)
    mock_relay = MagicMock(spec=GroveRelay)
    mock_request = MagicMock()

    mock_request.name = 'relay_off'

    mock_soil_moisture_monitor = SoilMoistureMonitor(adc=mock_adc, device_client=mock_device_client, relay=mock_relay)
    mock_soil_moisture_monitor.handle_request(request=mock_request)

    mock_method_response.create_from_method_request.assert_called_once_with(mock_request, 200)
    mock_device_client.send_method_response.assert_called_once_with(
        mock_method_response.create_from_method_request.return_value
    )
    mock_relay.off.assert_called_once()


@patch('app.json')
@patch('app.Message')
def test_get_reading(mock_message, mock_json):
    mock_device_client = MagicMock(spec=IoTHubDeviceClient)
    mock_adc = MagicMock(spec=ADC)
    mock_relay = MagicMock(spec=GroveRelay)
    mock_soil_moisture_monitor = SoilMoistureMonitor(adc=mock_adc, device_client=mock_device_client, relay=mock_relay)
    mock_soil_moisture_monitor.get_reading()
    mock_adc.read.assert_called_once_with(0)
    mock_message.assert_called_once_with(mock_json.dumps({'soil_moisture': mock_adc.read.return_value}))
    mock_device_client.send_message.assert_called_once_with(mock_message.return_value)


@patch('app.IoTHubDeviceClient')
def test_connect(mock_client):
    mock_device_client = MagicMock(spec=IoTHubDeviceClient)
    mock_adc = MagicMock(spec=ADC)
    mock_relay = MagicMock(spec=GroveRelay)
    mock_client.create_from_connection_string.return_value = mock_device_client
    return_value = connect('test_value')
    mock_client.create_from_connection_string.assert_called_once_with('test_value')
    mock_device_client.connect.assert_called_once()
    assert return_value == mock_device_client


@patch('app.CounterFitConnection')
@patch('os.getenv')
@patch('app.connect')
@patch('app.take_readings')
@patch('app.SoilMoistureMonitor')
@patch('app.GroveRelay')
@patch('app.ADC')
def test_main(mock_adc, mock_grove_relay, mock_soil_moisture_monitor, mock_take_readings, mock_connect, mock_getenv, mock_counter_fit):
    mock_getenv.return_value = 'test_connection_string'
    mock_device_client = MagicMock(spec=IoTHubDeviceClient)
    mock_connect.return_value = mock_device_client
    main()
    mock_adc.assert_called_once()
    mock_grove_relay.assert_called_once_with(5)
    mock_connect.assert_called_once_with(connection_string='test_connection_string')
    mock_soil_moisture_monitor.assert_called_once_with(adc=mock_adc.return_value, relay=mock_grove_relay.return_value, device_client=mock_device_client)
    mock_take_readings.assert_called_once_with(mock_soil_moisture_monitor.return_value)
    mock_counter_fit.init.assert_called_once_with('127.0.0.1', 5000)
