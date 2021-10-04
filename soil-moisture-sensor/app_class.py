import json
import os
import time

from counterfit_connection import CounterFitConnection
from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_relay import GroveRelay
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse


class SoilMoistureMonitor:

    def __init__(self, device_client: IoTHubDeviceClient, adc: ADC, relay: GroveRelay):
        self.device_client = device_client
        self.adc = adc
        self.relay = relay

    def handle_request(self, request):
        if request.name == "relay_on":
            self.relay.on()
        elif request.name == "relay_off":
            self.relay.off()

        method_response = MethodResponse.create_from_method_request(request, 200)
        self.device_client.send_method_response(method_response)

    def get_reading(self):
        soil_moisture = self.adc.read(0)
        print("Soil moisture:", soil_moisture)
        message = Message(json.dumps({'soil_moisture': soil_moisture}))
        self.device_client.send_message(message)


def connect(connection_string='<connection string>'):
    device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
    print('Connecting')
    device_client.connect()
    print('Connected')
    return device_client


def take_readings(soil_moisture_monitor):
    while True:
        soil_moisture_monitor.get_reading()
        time.sleep(10)


def main():
    device_client = connect(connection_string=os.getenv('connection_string'))
    adc = ADC()
    relay = GroveRelay(5)
    soil_moisture_monitor = SoilMoistureMonitor(
        device_client=device_client,
        adc=adc,
        relay=relay
    )
    
    CounterFitConnection.init('127.0.0.1', 5000)
    take_readings(soil_moisture_monitor)


if __name__ == 'main':
    main()
