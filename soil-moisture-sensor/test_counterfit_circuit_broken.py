import logging
from typing import Callable, Tuple, Union, Mapping

import pytest
import requests.exceptions
import responses

import counterfit_circuit_broken

logging.basicConfig(level=logging.DEBUG)


def pass_after_n_attempts(response, n: int = 1):
    count = 0

    def inner(_request: requests.PreparedRequest):
        nonlocal count
        if count >= n:
            return response
        else:
            count += 1
            return requests.exceptions.ConnectionError()

    return inner


def setup_connection():
    responses.add(responses.POST, "http://exampledomain.com:5000/connect", "", status=200)
    counterfit_circuit_broken.wait_till_counterfit("exampledomain.com", time_between=0, max_attempts=10)
    assert responses.calls[-1].request.url == "http://exampledomain.com:5000/connect"


@responses.activate
def test_wait_till_counterfit_with_failing_calls():
    responses.add_callback(
        responses.POST, "http://exampledomain.com:5000/connect",
        pass_after_n_attempts((200, {}, ""), 2)
    )

    counterfit_circuit_broken.wait_till_counterfit("exampledomain.com", time_between=0, max_attempts=10)

    logging.info(list(responses.calls))

    assert len(responses.calls) == 3


@responses.activate
def test_wait_till_counterfit_for_success():
    logging.debug("Starting test_wait_till_counterfit")
    responses.add(responses.POST, "http://exampledomain.com:5000/connect", "", status=200)
    logging.debug("Added callback")

    counterfit_circuit_broken.wait_till_counterfit("exampledomain.com", time_between=0, max_attempts=10)
    logging.debug("Made call")

    assert len(responses.calls) == 1


@responses.activate
def test_wait_till_counterfit_should_fail_after_n():
    with pytest.raises(requests.exceptions.ConnectionError):
        counterfit_circuit_broken.wait_till_counterfit("exampledomain.com", time_between=0, max_attempts=10)

    assert len(responses.calls) == 10
    assert responses.calls[0].request.url == "http://exampledomain.com:5000/connect"


@responses.activate
def test_circuit_broken_adc_read_success():
    with pytest.raises(requests.exceptions.ConnectionError):
        counterfit_circuit_broken.wait_till_counterfit("exampledomain.com", time_between=0, max_attempts=10)

    assert len(responses.calls) == 10
    assert responses.calls[0].request.url == "http://exampledomain.com:5000/connect"


@responses.activate
def test_circuit_broken_adc_read_fail():
    adc = counterfit_circuit_broken.CircuitBrokenADC(0)
    setup_connection()

    result = adc.read()

    assert result is None
    assert len(responses.calls) == 2
    assert responses.calls[-1].request.url == "http://exampledomain.com:5000/sensor_value?port=0"


@responses.activate
def test_circuit_broken_adc_read_success():
    adc = counterfit_circuit_broken.CircuitBrokenADC(0)
    setup_connection()

    responses.add(responses.GET, "http://exampledomain.com:5000/sensor_value?port=0", '{"value": 320}', status=200)

    result = adc.read()

    assert result == 320
    assert len(responses.calls) == 2
    assert responses.calls[-1].request.url == "http://exampledomain.com:5000/sensor_value?port=0"


@responses.activate
def test_circuit_broken_adc_read_success_with_override():
    adc = counterfit_circuit_broken.CircuitBrokenADC(0)
    setup_connection()

    responses.add(responses.GET, "http://exampledomain.com:5000/sensor_value?port=1", '{"value": 320}', status=200)

    result = adc.read(1)

    assert result == 320
    assert len(responses.calls) == 2
    assert responses.calls[1].request.url == "http://exampledomain.com:5000/sensor_value?port=1"


@responses.activate
def test_circuit_broken_adc_read_success_with_override_and_no_base():
    adc = counterfit_circuit_broken.CircuitBrokenADC()
    setup_connection()

    responses.add(responses.GET, "http://exampledomain.com:5000/sensor_value?port=2", '{"value": 320}', status=200)

    result = adc.read(2)

    assert result == 320
    assert len(responses.calls) == 2
    assert responses.calls[1].request.url == "http://exampledomain.com:5000/sensor_value?port=2"


@responses.activate
def test_circuit_broken_relay_on_fail():
    relay = counterfit_circuit_broken.CircuitBrokenRelay(0)
    setup_connection()

    result = relay.on()

    assert not result
    assert len(responses.calls) == 2
    assert responses.calls[1].request.url == "http://exampledomain.com:5000/actuator_value?port=0"
    assert responses.calls[1].request.body == b'{"value": true}'


@responses.activate
def test_circuit_broken_relay_on_success():
    relay = counterfit_circuit_broken.CircuitBrokenRelay(0)
    setup_connection()

    responses.add(responses.POST, "http://exampledomain.com:5000/actuator_value?port=0", '', status=200)
    result = relay.on()

    assert result
    assert len(responses.calls) == 2
    assert responses.calls[1].request.url == "http://exampledomain.com:5000/actuator_value?port=0"
    assert responses.calls[1].request.body == b'{"value": true}'


@responses.activate
def test_circuit_broken_relay_off_fail():
    relay = counterfit_circuit_broken.CircuitBrokenRelay(0)
    setup_connection()

    result = relay.off()

    assert not result
    assert len(responses.calls) == 2
    assert responses.calls[1].request.url == "http://exampledomain.com:5000/actuator_value?port=0"
    assert responses.calls[1].request.body == b'{"value": false}'


@responses.activate
def test_circuit_broken_relay_off_success():
    relay = counterfit_circuit_broken.CircuitBrokenRelay(0)
    setup_connection()

    responses.add(responses.POST, "http://exampledomain.com:5000/actuator_value?port=0", '', status=200)
    result = relay.off()

    assert result
    assert len(responses.calls) == 2
    assert responses.calls[1].request.url == "http://exampledomain.com:5000/actuator_value?port=0"
    assert responses.calls[1].request.body == b'{"value": false}'
