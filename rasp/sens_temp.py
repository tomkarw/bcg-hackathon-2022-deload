import time
import board
import adafruit_dht

sensor = adafruit_dht.DHT11(board.D17)
while True:
    try:
        temp = sensor.temperature
        humidity = sensor.humidity
        logging.debug("Temperature: {}*C   Humidity: {}% ".format(temp, humidity))
    except RuntimeError as error:
        logging.debug(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        sensor.exit()
        raise error
    time.sleep(2.0)
