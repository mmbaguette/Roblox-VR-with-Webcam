from math import asin, pi, atan2, cos 
from pprint import pprint as pp
import time

import cv2
import mediapipe as mp
import numpy as np
import requests as rq

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

uploading = False # are we uploading to the server or still testing?
username = "AerodynamicRocket" # roblox username of player
upload_url = f"https://mmbaguette.pythonanywhere.com/upload_pose/{username}"

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

def vec_length(v: np.array):
    return np.sqrt(sum(i**2 for i in v))

def normalize(v):
	norm = np.linalg.norm(v)

	if norm == 0: 
		return v
	return v / norm

def look_at(eye: np.array, target: np.array):
	axis_z = normalize((eye - target))

	if vec_length(axis_z) == 0:
		axis_z = np.array((0, -1, 0))

	axis_x = np.cross(np.array((0, 0, 1)), axis_z)
    
	if vec_length(axis_x) == 0:
		axis_x = np.array((1, 0, 0))
    
	axis_y = np.cross(axis_z, axis_x)
	rot_matrix = np.matrix([axis_x * 360, axis_y * 360, axis_z * 360]).transpose()
	
	return rot_matrix

def euler_angles(rot_matrix: np.matrix): # https://stackoverflow.com/a/64336115
	"Returns the roll, pitch and yaw from a given numpy rotation matrix."
	rot_array = np.squeeze(np.asarray(rot_matrix))
	R11, R12, R13 = rot_array[0]
	R21, R22, R23 = rot_array[1]
	R31, R32 , R33 = rot_array[2]

	if R31 != 1 and R31 != -1: 
		pitch_1 = -1*asin(R31)
		pitch_2 = pi - pitch_1 
		roll_1 = atan2( R32 / cos(pitch_1) , R33 /cos(pitch_1) ) 
		roll_2 = atan2( R32 / cos(pitch_2) , R33 /cos(pitch_2) ) 
		yaw_1 = atan2( R21 / cos(pitch_1) , R11 / cos(pitch_1) )
		yaw_2 = atan2( R21 / cos(pitch_2) , R11 / cos(pitch_2) ) 

		pitch = pitch_2 
		roll = roll_2
		yaw = yaw_2
	else: 
		yaw = 0 # anything (we default this to zero)
		if R31 == -1: 
			pitch = pi/2 
			roll = yaw + atan2(R12,R13) 
		else: 
			pitch = -pi/2 
			roll = -1*yaw + atan2(-1*R12,-1*R13) 

	# convert from radians to degrees
	roll = roll*180/pi 
	pitch = pitch*180/pi
	yaw = yaw*180/pi 
	return roll, pitch, yaw

with mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as pose:

	while cap.isOpened():
		success, image = cap.read()

		if not success:
			print("Ignoring empty camera frame.")
			continue

		imageToDisplay = cv2.flip(image, 1)
		imageToProcess = cv2.cvtColor(imageToDisplay, cv2.COLOR_BGR2RGB)

		imageToProcess.flags.writeable = False
		results = pose.process(imageToProcess)

		mp_drawing.draw_landmarks(
			imageToDisplay,
			results.pose_landmarks,
			mp_pose.POSE_CONNECTIONS,
			landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

		world_landmarks = results.pose_world_landmarks

		if world_landmarks:
			roblox_landmarks = {
				"left_shoulder": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
				"left_elbow": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW],
				"right_shoulder": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
				"right_elbow": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW],
				"left_wrist": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST],
				"right_wrist": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST],
				"left_knee": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE],
				"right_knee": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE],
				"left_ankle": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE],
				"right_ankle": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE],
			}

			for body_part in roblox_landmarks:
				body_part_value = roblox_landmarks[body_part]
				body_part_json = {
					"x": body_part_value.x,
					"y": body_part_value.y,
					"z": body_part_value.z,
					"visibility": body_part_value.visibility,
				}
				roblox_landmarks[body_part] = body_part_json
			
			lf_sh = roblox_landmarks["left_shoulder"]
			lf_wr = roblox_landmarks["left_wrist"]
			orient = look_at(np.array([lf_sh["x"], lf_sh["y"], lf_sh["z"]]), np.array([lf_wr["x"], lf_wr["y"], lf_wr["z"]]))
			roll, pitch, yaw = euler_angles(orient)
			print("Roll:", roll, "Pitch:", pitch, "Yaw:", yaw)
			time.sleep(1)

			if uploading:
				r = rq.post(url=upload_url, json=roblox_landmarks)

				if r.status_code != 200:
					print(f"Status code: {r.status_code}")
					print(f"Response body: {r.text}")

		cv2.imshow("Webcam Pose", imageToDisplay)

		if cv2.waitKey(1) == 27: # esc
			break

cap.release()
cv2.destroyAllWindows()
