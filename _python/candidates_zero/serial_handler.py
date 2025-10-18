import serial
import sys
import time

PACKET_SIZE = 25
SERIAL_TIMEOUT = 0.1

port_name = '/dev/ttyACM0'
baud_rate = 115200

def millis():
	return time.time_ns() // 1000000

def initialize_serial_port():
	try:
		serial_port = serial.Serial(port_name, baud_rate, timeout=SERIAL_TIMEOUT)
		print(f"[{millis()}]: [SERIAL.PY] Serial port {port_name} opened at {baud_rate} baud.")
	except serial.SerialException as e:
		print(f"[{millis()}]: [SERIAL.PY] Error opening serial port {port_name}: {e}")
		sys.exit(1)

	return serial_port

def read_serial_data(serial_port):
	if not (serial_port and serial_port.is_open):
		print(f"[{millis()}]: [SERIAL.PY] Serial port is not open.")
		return None

	if serial_port.in_waiting >= PACKET_SIZE:
		data = serial_port.read(PACKET_SIZE)
#		print(f"[{millis()}]: [SERIAL.PY] Received data: {data}")
		return data

	return None

def write_serial_data(serial_data, data):
	if not (serial_data and serial_data.is_open):
		print(f"[{millis()}]: [SERIAL.PY] Serial port is not open.")
		return

	if len(data) != PACKET_SIZE:
		print(f"[{millis()}]: [SERIAL.PY] Data length {len(data)} does not match PACKET_SIZE {PACKET_SIZE}.")
		return

	serial_data.write(data)
#	print(f"[{millis()}]: [SERIAL.PY] Sent data    : {data}")

def close_serial(serial_port):
	if serial_port and serial_port.is_open:
		serial_port.close()
		print(f"[{millis()}]: [SERIAL.PY] Serial port {port_name} closed.")
