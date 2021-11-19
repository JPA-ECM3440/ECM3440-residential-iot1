import logging
from time import sleep
from typing import Optional

import requests.exceptions
from counterfit_connection import CounterFitConnection
from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_relay import GroveRelay


# Waits synchronously since this is done on startup
def wait_till_counterfit(
        hostname: str = 'localhost',
        port: int = 5000, *,
        max_attempts: int = -1,
        time_between: int = 10
):
    attempts = 0
    while max_attempts == -1 or attempts < max_attempts:
        try:
            logging.debug(f"Attempting connection to {hostname}:{port}")
            CounterFitConnection.init(hostname, port)
            return
        except requests.exceptions.ConnectionError:
            logging.warning(f"Error connecting to {hostname}:{port}, retrying in {time_between}")
            sleep(time_between)
            logging.warning(f"Error connecting to {hostname}:{port}, retrying now")
            attempts += 1

    raise requests.exceptions.ConnectionError(f"Failed {max_attempts} times to connect to {hostname}:{port}")


class CircuitBrokenADC(ADC):
    def __init__(self, pin: int = None):
        self.pin = pin
        super().__init__(pin)

    def read(self, channel=None) -> Optional[int]:
        pin = channel if channel is not None else self.pin
        try:
            return CounterFitConnection.get_sensor_int_value(pin)
        except requests.exceptions.ConnectionError:
            logging.error("Could not retrieve adc value")
            return None


class CircuitBrokenRelay(GroveRelay):
    def __init__(self, pin):
        self.pin = pin
        super().__init__(pin)

    def on(self) -> bool:
        return self._set_state(True)

    def off(self) -> bool:
        return self._set_state(False)

    def _set_state(self, val: bool):
        try:
            CounterFitConnection.set_actuator_boolean_value(self.pin, val)
            return True
        except requests.exceptions.ConnectionError:
            logging.error(f"Could not set relay to {val}")
            return False

