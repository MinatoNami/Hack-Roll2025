import time
import adafruit_dht
import board
from RPLCD.i2c import CharLCD

import RPi.GPIO as GPIO

import serial

import paho.mqtt.client as mqtt

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN)

#hostname = "192.168.86.24" # Replace this with host ip address
hostname = "10.42.0.32" # Replace this with host ip address
broker_port = 1883
topic = "sensor"

client = mqtt.Client()
client.connect(hostname, broker_port, 60)

dht_device = adafruit_dht.DHT11(board.D4)

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.reset_input_buffer()

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()
distance_light = [0, 0]

while True:
    try:
        temperature_c = dht_device.temperature
        # temperature_f = temperature_c * (9 / 5) + 32

        humidity = dht_device.humidity
        #print("humidity and temperature", humidity, temperature_c)
        if(ser.in_waiting > 0):
            line = ser.readline().decode('utf-8').rstrip()
            raw_reading = line.split(" ")
            if(len(raw_reading)==2):
                distance_light=raw_reading
            
        lcd.cursor_pos = (0,0)
        lcd.write_string('Tem/H: ' + str(temperature_c) + 'C/' + str(humidity) + '%')
        lcd.cursor_pos = (1,0)
        lcd.write_string('D/L: ' + str(distance_light[0]) + '/' + str(distance_light[1]) + '\n')
        output = str(temperature_c) + "+" + str(humidity)+ "+" + str(distance_light[0])+ "+" + str(distance_light[1])
        print("Message to client:", output)
        client.publish(topic, output)
    except RuntimeError as err:
        print(err.args[0])
    time.sleep(1.0)
    ser.flushInput()

