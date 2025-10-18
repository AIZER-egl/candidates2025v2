import time
import serializer as serializer
import line_handler as line_handler
import math
import angle as angle

STOP = 0#+
ROTATE = 1
FORWARD = 2

WIDTH = 320
HEIGHT = 240

def millis():
	return time.time_ns() // 1000000

previous_time = 0
agarrando_pelota = False
accion_de_piso_ejecutada = False
facing = 0
waiting = False
wait_time = 0
rotating = False
stop = False
soft_stop = False
previous_locked = False
locked = False
previous_distance = 0
print_data = False

def follow_ball(data: serializer._BinaryDataTuple, ball_centroid):
	new_data = data

	cx = ball_centroid[0]
	cy = ball_centroid[1]

	if cx == -1 or cy == -1:
		return new_data

	x = (cx - (WIDTH // 2))
	y = HEIGHT - cy

	theta = (math.atan2(y, x)*180/math.pi-90)*-1

	new_data = new_data._replace(
		motor_move_form = ROTATE,
		motor_facing_target = facing,
		motor_speed_target = 20
	)
	return new_data

def forward(data: serializer._BinaryDataTuple):
	global facing
	new_data = data
	fstop = False
	fwaiting = False
	fwait_time = 0
	flocked = False
	if data.front_wall < 130:
		print("Front wall detected, slowing down", end="")
		new_data = new_data._replace(
			motor_move_form=ROTATE,
			motor_speed_target=15,
			motor_facing_target=facing
		)

		if data.front_wall < 100:
			print(" - robot in front of wall, stoped", end="")
			fstop = True
			fwaiting = True
			fwait_time = millis()
			flocked = True
		print()
	else:
		print("forward, facing: {}, f: {}, r: {}, l: {}".format(facing, data.front_wall, data.right_wall, data.left_wall))
		new_data = new_data._replace(
			motor_move_form=ROTATE,
			motor_speed_target=20,
			motor_facing_target=facing
		)

	return new_data, fstop, fwaiting, fwait_time, flocked

def challenge (data: serializer._BinaryDataTuple, ball_centroid):
	global previous_time, agarrando_pelota, accion_de_piso_ejecutada,\
		facing, waiting, wait_time, stop, previous_distance, soft_stop, locked, previous_locked,\
		rotating, print_data

	new_data = data
	cx = ball_centroid[0]
	cy = ball_centroid[1]
	ball_visible = (not (cx == -1) and not (cy == -1))

	if new_data.front_wall < 90:
		locked = True
	else:
		locked = False

	if rotating:
		print("rotating y: {} facing: {}".format(data.yaw, facing))
		in_angle = angle.threshold(data.yaw, angle.normalize(facing), 10)

		if in_angle:
			rotating = False
			stop = True
			waiting = True
			wait_time = millis()
			print("Finished rotating, waiting...")
		else:
			waiting = False
			stop = False
			new_data = new_data._replace(
				motor_move_form=ROTATE,
				motor_facing_target=facing,
				motor_speed_target=0
			)

	if waiting:
		if (millis() - wait_time) >= 10000:
			waiting = False
			stop = False
			soft_stop = False
			new_data = new_data._replace(reset_pid=True)
			print("Wait finished")
			print("PID restarterd")
		else:
			stop = True

	if ball_visible and not agarrando_pelota and not waiting:
		print("Following ball at ({}, {}) - Wall? {}".format(cx, cy, data.front_wall))
		if data.front_wall < 110:
			stop = True
			waiting = True
			wait_time = millis()

		new_data = follow_ball(data, ball_centroid)

		if cy >= 125:
			print("AGARRANDO PELOTA")
			agarrando_pelota = True
			stop = True
			waiting = True
			wait_time = millis()
			new_data = new_data._replace(
				servo_active=True,
			)

	if not ball_visible and not agarrando_pelota and not waiting and not locked and not rotating:
		print("ball not visible, not agarrando pelota, not waiting and not locked")
		new_data, stop, waiting, wait_time, locked = forward(new_data)
		print_data = True

	if locked and not agarrando_pelota and not rotating:
		print("Locked not rotating not agarrando pelota")
		right_wall = data.right_wall < 220
		left_wall = data.left_wall < 150
		front_wall = data.front_wall < 100

		if right_wall and left_wall and front_wall:
			print("Locked, waiting..., f: {}, r: {}, l: {}".format(data.front_wall, data.right_wall, data.left_wall))
			stop = True
			waiting = True
			wait_time = millis()

		if not right_wall:
			print("Locked, rotating right..., facing: {} f: {}, r: {}, l: {}".format(facing, data.front_wall, data.right_wall, data.left_wall))
			if locked and not previous_locked:
				facing = facing + 90
			rotating = True
			wait_time = millis() + 10000 # 10 seconds more to rotate
		elif not left_wall:
			print("Locked, rotating left..., facing: {} f: {}, r: {}, l: {}".format(facing, data.front_wall, data.right_wall, data.left_wall))
			if locked and not previous_locked:
				facing = facing - 90
			rotating = True
			wait_time = millis() + 10000

	if agarrando_pelota and not waiting:
		print("agarrando pelota and not waiting")
		piso = line_handler.id_to_color(data.floor_color)
		if piso == "yellow" and not accion_de_piso_ejecutada:
			agarrando_pelota = False
			stop = True
			waiting = True
			wait_time = millis()
			accion_de_piso_ejecutada = True
			new_data = new_data._replace(
				servo_active=False,
				kicker_active=True,
			)
		elif piso == "blue" and not accion_de_piso_ejecutada:
			stop = True
			waiting = True
			wait_time = millis()
			accion_de_piso_ejecutada = True
			new_data = new_data._replace(
				motor_move_form=STOP,
				servo_active=False,
			)
		else:
			accion_de_piso_ejecutada = False
			if not locked:
				new_data, stop, waiting, wait_time, locked = forward(data)

	if stop:
		new_data = new_data._replace(
			motor_move_form = STOP,
			motor_speed_target = 0,
			motor_facing_target = facing
		)

		if previous_distance == new_data.motor_distance:
			soft_stop = True

		if soft_stop:
			new_data = new_data._replace(
				motor_move_form = ROTATE,
				motor_speed_target = 0,
				motor_facing_target = facing
			)

	if print_data:
		# print(new_data)
		print_data = False
	previous_locked = locked
	previous_distance = new_data.motor_distance
	return new_data