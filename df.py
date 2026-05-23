from gpiozero import PWMOutputDevice, DigitalOutputDevice
import serial

print("serial init")
ser = serial.Serial('/dev/serial0', 115200, timeout=0.1)

print("RPWM 18")
RPWM = PWMOutputDevice(18, frequency=1000)

print("LPWM 19")
LPWM = PWMOutputDevice(19, frequency=1000)

print("L_EN 23")
L_EN = DigitalOutputDevice(23)

print("R_EN 24")
R_EN = DigitalOutputDevice(24)

print("RPWM2 12")
RPWM2 = PWMOutputDevice(12, frequency=1000)

print("LPWM2 13")
LPWM2 = PWMOutputDevice(13, frequency=1000)

print("L_EN2 5")
L_EN2 = DigitalOutputDevice(5)

print("R_EN2 6")
R_EN2 = DigitalOutputDevice(6)

print("PUL 17")
PUL = DigitalOutputDevice(17, initial_value=True)

print("DIR 27")
DIR = DigitalOutputDevice(27, initial_value=True)

print("all gpio init ok")
