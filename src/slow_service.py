#!/usr/bin/env python

import sys
import time
import random
import flask
import influxdb
import functools

class Metrics():
    def __init__(self, influx=None, time_func=time.clock):
        self._influx = influx
        self._time = time_func
    
    def _send_metric(self, series, metric_name, metric_value, metric_time=None):
        if self._influx is not None:
            if metric_time is None:
                metric_time = time.time()
            data = [{
                'name': series,
                'points': [[metric_time, metric_value]],
                'columns': ['time', metric_name]
            }]
            print data
            self._influx.write_points(data)

    def execution_time(self, func):
        """ Log the exec time of a function to InfluxDB """
        @functools.wraps(func)
        def timed_func(*args, **kwargs):
            func_name = func.__name__
            invocation_time = time.time()
            start = self._time()
            return_value = func(*args, **kwargs)
            elapsed = self._time() - start
            self._send_metric(func_name, 'exec_time', elapsed, invocation_time)
            return return_value

        return timed_func


def predelay(delay=0, random_delay=False):
    """ A function factory to create a pre-delay decorator 

    Holy nested closures, Batman!
    """
    def decorator(func):
        @functools.wraps(func)
        def delayed_func(*args, **kwargs):
            my_delay = random.random() * delay if random_delay else delay
            time.sleep(my_delay)
            return func(*args, **kwargs)

        return delayed_func

    return decorator

def main():
    port = None
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    # Set up the metrics gathering object
    influx = influxdb.client.InfluxDBClient('localhost', 8086, 'testuser', 'testpassword', 'hello_metrics')
    metrics = Metrics(influx=influx, time_func=time.time)

    # Set up the flask app
    app = flask.Flask("slow_service")

    @app.route("/")
    @metrics.execution_time
    @predelay(0.5, random_delay=True)
    def hello():
        return "Hello, world!"

    app.run(port=port, debug=True)


if __name__ == "__main__":
    main()
