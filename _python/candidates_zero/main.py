import cv2
import time

import serializer as serializer
import strategy1 as strategy1
import strategy2 as strategy2
import serial_handler as ser
import camera as cam

SAVE_VIDEO = False
TARGET_FPS = 10
WIDTH = 320
HEIGHT = 240

def millis():
	return time.time_ns() // 1000000

def main():
	picam = cam.initialize(WIDTH, HEIGHT, TARGET_FPS, SAVE_VIDEO)
	serial_port = ser.initialize_serial_port()

	if not serial_port:
		print("[{}]: [MAIN.PY] No se pudo abrir el puerto serial. Saliendo.".format(millis()))
		return

	previous_capture = millis()
	line_centroid = (-1, -1)
	ball_centroid = (-1, -1)
	data = serializer.default_packet

	try:
		ser.write_serial_data(serial_port, serializer.pack_data(data))

		while True:
			raw_data = ser.read_serial_data(serial_port)
			if raw_data:
				unpacked_data = serializer.unpack_data(raw_data)
				if unpacked_data:
					# print("unpacked", unpacked_data)
					data = data._replace(
						yaw = unpacked_data.yaw,
						floor_color = unpacked_data.floor_color,
						motor_distance = unpacked_data.motor_distance,
						front_wall = unpacked_data.front_wall,
						left_wall = unpacked_data.left_wall,
						right_wall = unpacked_data.right_wall,
						start = unpacked_data.start,
						test_pid_error_sum = unpacked_data.test_pid_error_sum,
						reset_pid = unpacked_data.reset_pid,
						reset_distance = unpacked_data.reset_distance,
						kicker_active = unpacked_data.kicker_active
					)

					# data = strategy3.challenge(data)
					# data = strategy1.challenge(data, ball_centroid)
					data = strategy2.challenge(data, line_centroid)

					# print("Sending data: ", data)
					ser.write_serial_data(serial_port, serializer.pack_data(data))

			# if (millis() - previous_capture) >= (1000 / TARGET_FPS):
			# 	frame = cam.get_ball_preprocessed_frame(picam)
			# 	ball_centroid = cam.get_ball_centroid(picam, frame)
			# 	previous_capture = millis()

			if (millis() - previous_capture) >= (1000 / TARGET_FPS):
					frame = cam.get_line_preprocessed_frame(picam)
					line_centroid = cam.get_line_centroid(picam, frame)
					previous_capture = millis()


			time.sleep(0.01)

	except KeyboardInterrupt:
		print("[{}]: [MAIN.PY] Saliendo.".format(millis()))
	finally:
		picam.stop()
		if SAVE_VIDEO:
			picam.out.release()
			cv2.destroyAllWindows()
		print("Camara detenida. Programa finalizado.")

if __name__ == "__main__":
	main()