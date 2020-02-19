import RPi.GPIO as GPIO
import time

servoPINA = 17
servoPINB = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPINA, GPIO.OUT)
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPINB, GPIO.OUT)

pa = GPIO.PWM(servoPINA, 50) # GPIO 17 for PWM with 50Hz
pb = GPIO.PWM(servoPINB, 50) # GPIO 18 for PWM with 50Hz
pa.start(2.5) # Initialization
pb.start(2.5) # Initialization
try:
  while True:
    pa.ChangeDutyCycle(5)
    pb.ChangeDutyCycle(5)
    time.sleep(0.5)
    pa.ChangeDutyCycle(7.5)
    pb.ChangeDutyCycle(7.5)
    time.sleep(0.5)
    pa.ChangeDutyCycle(10)
    pb.ChangeDutyCycle(10)
    time.sleep(0.5)
    pa.ChangeDutyCycle(12.5)
    pb.ChangeDutyCycle(12.5)
    time.sleep(0.5)
    pa.ChangeDutyCycle(10)
    pb.ChangeDutyCycle(10)
    time.sleep(0.5)
    pa.ChangeDutyCycle(7.5)
    pb.ChangeDutyCycle(7.5)
    time.sleep(0.5)
    pa.ChangeDutyCycle(5)
    pb.ChangeDutyCycle(5)
    time.sleep(0.5)
    pa.ChangeDutyCycle(2.5)
    pb.ChangeDutyCycle(2.5)
    time.sleep(0.5)
except KeyboardInterrupt:
  pa.stop()
  pb.stop()
  GPIO.cleanup()
