import time
import serializer as serializer
import line_handler as line_handler
import math
import angle as angle

STOP = 0
ROTATE = 1
FORWARD = 2

WIDTH = 320
HEIGHT = 240

def millis():
	return time.time_ns() // 1000000

previous_time = 0
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

def value_map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def follow_line(data: serializer._BinaryDataTuple, line_centroid):
	new_data = data

	cx = line_centroid[0]
	cy = line_centroid[1]

	if cx == -1 or cy == -1:
		return new_data

	x = (cx - (WIDTH // 2))
	y = HEIGHT - cy + 100

	theta = (math.atan2(int(y), int(x))*180/math.pi-90)*-1

	speed = 18
	angle = int(data.yaw + theta)
	new_data = new_data._replace(
		motor_move_form = FORWARD,
		motor_facing_target = angle,
		motor_speed_target = speed
	)
	print("Following line at ({} rps, {}°)°".format(speed, angle))
	return new_data, angle

def challenge(data: serializer._BinaryDataTuple, line_centroid):
	global previous_time, facing, waiting, wait_time, rotating, stop, soft_stop, \
		previous_locked, locked, previous_distance, print_data

	new_data = data
	cx = line_centroid[0]
	cy = line_centroid[1]
	line_visible = (not (cx == -1) and not (cy == -1))

	if not angle.threshold(data.yaw, facing, 30) and not waiting and not rotating:
		print("Robot is facing {}°, target is {}°. Not within range".format(data.yaw, facing))
		waiting = True
		wait_time = millis()

	if line_visible and not waiting and not rotating:
		new_data, facing = follow_line(data, line_centroid)

	if rotating and not waiting:
		print("Rotating: currently at {}°, target is {}°".format(data.yaw, facing))
		new_data = new_data._replace(
			motor_move_form = ROTATE,
			motor_facing_target = facing,
			motor_speed_target = 0
		)
		if (angle.threshold(data.yaw, facing, 10)):
			rotating = False
			print("Finished rotating to {}°".format(facing))

	if waiting and not rotating:
		print("Waiting at {}° for 500ms".format(facing))
		new_data = new_data._replace(
			motor_move_form = STOP,
			motor_facing_target = facing,
			motor_speed_target = 0
		)
		if (millis() - wait_time) > 500:
			waiting = False
			rotating = True
			print("Finished waiting")

	return new_data