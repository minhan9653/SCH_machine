import serial
import time

ser = serial.Serial('/dev/serial0', 115200, timeout=0.1)

while True:
    data = ser.read(9)

    if len(data) == 9:
        print(data)
    else:
        print("데이터 없음")

    time.sleep(0.1)