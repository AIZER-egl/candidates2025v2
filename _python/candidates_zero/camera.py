from picamera2 import Picamera2
import cv2
import time
import numpy as np

def initialize(width, height, frame_rate, save_video):
	picam2 = Picamera2()
	config = picam2.create_preview_configuration(
		main={"size": (width,height), "format": "BGR888"},
		controls={
			"FrameRate": frame_rate,
			"AeEnable": False,
			"ExposureTime": 10000,
			"AnalogueGain": 1.0
		}
	)
	picam2.configure(config)
	picam2.start()
	picam2.save_video = save_video

	print("[{}]: [CAMERA.PY] Camera initialized, adjusting sensor...".format(time.time_ns() // 1000000))
	time.sleep(1)
	print("[{}]: [CAMERA.PY] Camera initialized. Limiting processing to {} FPS.".format(time.time_ns() // 1000000, frame_rate))

	if save_video:
		fourcc = cv2.VideoWriter_fourcc(*'mp4v')
		out = cv2.VideoWriter('output.mp4', fourcc, frame_rate, (width, height))
		picam2.out = out
		print("[{}]: [CAMERA.PY] Video saving enabled.".format(time.time_ns() // 1000000))
	return picam2

def get_ball_preprocessed_frame(picam2):
	frame = picam2.capture_array()
	frame = cv2.flip(frame, 0)
	frame = cv2.flip(frame, 1)

	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	# print("[{}]: [CAMERA.PY] Frame captured and preprocessed.".format(time.time_ns() // 1000000))
	return frame

def nothing():
	pass

def get_ball_centroid(picam, frame):
	mask = cv2.inRange(frame, (100, 127, 127), (120, 255, 255))
	contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	cx = -1
	cy = -1

	if len(contours) > 0:
		largest_contour = max(contours, key=cv2.contourArea)
		area = cv2.contourArea(largest_contour)

		if area > 100:
			x, y, w, h = cv2.boundingRect(largest_contour)
			cx = x + w // 2
			cy = y + h // 2
#			print("[{}]: [CAMERA.PY] Ball detected at ({}, {}) with area".format(time.time_ns() // 1000000, cx, cy))
		else:
			nothing()
#			print("[{}]: [CAMERA.PY] No ball detected (area too small: {}).".format(time.time_ns() // 1000000, area))
	if picam.save_video:
		rgb_frame = cv2.cvtColor(frame, cv2.COLOR_HSV2RGB)
		if cx != -1 and cy != -1:
			rgb_frame = cv2.circle(rgb_frame, (cx, cy), 10, (0, 255, 0), -1)
		picam.out.write(rgb_frame)

	return cx, cy

def get_line_preprocessed_frame(picam2):
	frame = picam2.capture_array()
	frame = cv2.flip(frame, 0)
	frame = cv2.flip(frame, 1)

	height, width, _ = frame.shape
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	frame = cv2.rectangle(frame,(0,height),(30,0),(255,255,255),-1)
	frame = cv2.rectangle(frame,(width - 30,height),(width,0),(255,255,255),-1)
	frame = cv2.rectangle(frame,(0,0),(width,110),(255,255,255),-1)

	frame = cv2.GaussianBlur(frame,(11,11),0)

	cv2.imshow("raw", frame)
	retval,frame = cv2.threshold(frame, 70 ,255,cv2.THRESH_BINARY_INV)

	# kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(15,15))
	# frame = cv2.erode(frame,kernel,iterations = 1)
	# frame = cv2.dilate(frame,kernel,iterations = 1)
#	print("[{}]: [CAMERA.PY] Frame captured and preprocessed.".format(time.time_ns() // 1000000))
	return frame

def get_line_centroid(picam, frame):
	contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	cx = -1
	cy = -1
	if len(contours) > 0:
		largest_contour = max(contours, key=cv2.contourArea)
		M = cv2.moments(largest_contour)
		if M["m00"] != 0:
			cx = int(M["m10"] / M["m00"])
			cy = int(M["m01"] / M["m00"])
		else:
			cx, cy = largest_contour[0][0]

	if picam.save_video:
		print("saving video")
		rgb_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
		if cx != -1 and cy != -1:
			rgb_frame = cv2.circle(rgb_frame, (cx, cy), 10, (0, 255, 0), -1)
		picam.out.write(rgb_frame)
		cv2.imshow("frame", rgb_frame)
		cv2.waitKey(1)


	return cx, cy
