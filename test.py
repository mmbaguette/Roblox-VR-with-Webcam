import math
import threading
import cv2
import mediapipe as mp
import numpy as np
import requests as rq
import time
import calcs

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

uploading = True # are we uploading to the server or still testing?
username = "AerodynamicRocket" # roblox username of player
upload_url = f"https://mmbaguette.pythonanywhere.com/upload_pose/{username}"
roblox_rotations = None
roblox_landmarks = None
sequence_num = 1

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# takes names of two vectors/landmarks from the human body, calculates and assigns their rotation to roblox_rotations
def assign_angles(vector1: str, vector2: str, repeat_side: bool = False):
	v1_coords = roblox_landmarks[vector1] # assign x,y,z coordinates of this landmark
	v2_coords = roblox_landmarks[vector2]
	
	# calculate rotation matrix
	orient = calcs.look_at(np.array([v1_coords["x"], v1_coords["y"], v1_coords["z"]]),np.array([v2_coords["x"], v2_coords["y"], v2_coords["z"]]))
	roll, pitch, yaw = calcs.angles(orient) # retrieve roll, pitch, yaw or x,y,z rotations from matrix
	
	roblox_rotations[vector1] = { 
		"x": roll,
		"y": pitch,
		"z": yaw,
		"visibility": v1_coords["visibility"]
	}
	
	if repeat_side: # repeat the same operation but on the right side of the body
		assign_angles(vector1.replace("left", "right"), vector2.replace("left", "right"))

# allow pose landmark to be uploaded without interrupting pose processing
def keep_uploading():
	last_sequence_num = 1

	while True:
		if sequence_num == 0: # stop program
			break
		elif sequence_num > last_sequence_num:
			r = rq.post(url=upload_url, json=roblox_rotations)

			if r.status_code == 200: # success
				last_sequence_num = sequence_num 
				#print(f"Updated #{last_sequence_num}")
			else: # failure
				print(f"Status code: {r.status_code}")
				print(f"Response body: {r.text}")
		else:
			time.sleep(0.01) # give the loop a break

upload_process = threading.Thread(target=keep_uploading)
upload_process.start() 

with mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as pose:

	while cap.isOpened():
		success, image = cap.read()

		if not success:
			print("Ignoring empty camera frame.")
			continue

		imageToDisplay = cv2.flip(image, 1) # flip the image so it appears as a mirror when we view it
		imageToProcess = cv2.cvtColor(imageToDisplay, cv2.COLOR_BGR2RGB) # convert from BGR color scheme (used by OpenCV engine) to RGB (for processing)

		imageToProcess.flags.writeable = False
		results = pose.process(imageToProcess)

		mp_drawing.draw_landmarks(
			imageToDisplay,
			results.pose_landmarks,
			mp_pose.POSE_CONNECTIONS,
			landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

		world_landmarks = results.pose_world_landmarks

		if world_landmarks:
			roblox_landmarks = { # map each value pose landmark into new dictionary
				"left_shoulder": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
				"right_shoulder": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
				"left_elbow": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW],
				"right_elbow": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW],
				"left_wrist": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST],
				"right_wrist": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST],
				"left_hip": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP],
				"right_hip": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP],
				"left_knee": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE],
				"right_knee": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE],
				"left_ankle": world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE],
				"right_ankle": world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE],
				"nose": world_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
			}

			for body_part in roblox_landmarks: # copy each pose landmark into a new dictionary with different landmark names
				body_part_value = roblox_landmarks[body_part]
				body_part_json = {
					"x": body_part_value.x,
					"y": body_part_value.y,
					"z": body_part_value.z,
					"visibility": body_part_value.visibility,
				}
				roblox_landmarks[body_part] = body_part_json
			roblox_rotations = {} # assign/reset the dictionary storing the rotations of each joint 
			
			# find where v1 (limb 1) has to turn to look at v2 (limb 2) for each joint in the body
			assign_angles("left_shoulder", "left_elbow", repeat_side=True)
			assign_angles("left_elbow", "left_wrist", repeat_side=True)
			assign_angles("left_hip", "left_knee", repeat_side=True)
			assign_angles("left_knee", "left_ankle", repeat_side=True)

			# calculate neck-head rotation
			lf_sh = roblox_landmarks["left_shoulder"]
			rt_sh = roblox_landmarks["right_shoulder"]
			nose = roblox_landmarks["nose"]
			shoulder_midpoint = { # the neck is located between the two shoulders
				"x": (lf_sh["x"] + rt_sh["x"]) / 2,
				"y": (lf_sh["y"] + rt_sh["y"]) / 2,
				"z": (lf_sh["z"] + rt_sh["z"]) / 2
			}

			neck_matrix = calcs.look_at( # find rotation matrix of shoulders' midpoint to nose
				np.array([shoulder_midpoint["x"], shoulder_midpoint["y"], shoulder_midpoint["z"]]),
				np.array([nose["x"], nose["y"], nose["z"]]))
			nk_x, nk_y, nk_z = calcs.angles(neck_matrix) # find rotation angles of neck
			
			roblox_rotations["neck"] = { # assign x,y,z rotations of neck rotation
				"x": nk_x,
				"y": nk_y,
				"z": nk_z
			}
			
			if uploading: # if program is updating angles in the server, otherwise we're just testing
				sequence_num+=1

		cv2.imshow("Webcam Pose", imageToDisplay) # display the image on the "Webcam Pose" window
		time.sleep(0.05) # cooldown

		if cv2.waitKey(1) == 27: # esc
			sequence_num = 0
			break

cap.release()
cv2.destroyAllWindows()
upload_process.join()