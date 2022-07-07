import subprocess
import json
import time
import threading
print("Loading extensions...")  # also called libraries

"-----EDIT THESE VALUES-----"
# Roblox username of player
username = "MyRobloxUsername"
# AUTHORIZATION token (games will ask you for this)
authorization = "CHANGE-ME"
# SERVER OWNERS: move {username} to wherever the player's username should be inserted into the URL. 
# PLAYERS: this value should be given from the roblox game.
upload_url = f"https://www.example.com/upload_pose/{username}" 

# how long in seconds between each pose update (less seconds = more data uploaded to server = lag)
cooldown = 0.2
# are we using the typing input feature (True/False case-sensitive)?
typing_input = False

"-----FOR TYPING FEATURE WITHOUT SERVER ()-----"
# when the program starts, how long does it take for the autoclicker to the send data through the roblox keyboard
start_typing_delay = 2  # seconds
# interval between each key press. lower = faster results, but maybe not all computers can handle it
press_delay = 0.002
# don't use any of the "Magic Characters" as one of the autoclicker's keys.
# https://developer.roblox.com/en-us/articles/string-patterns-reference#magic-characters
key_map = {  # what the autoclicker will press vs. what the actual value of the key is.
    "q": "0",
    "e": "1",
    "r": "2",
    "t": "3",
    "y": "4",
    "u": "5",
    "p": "6",
    "f": "7",
    "g": "8",
    "h": "9",
    "j": ',',
    "k": '[',
    "l": ']',
    "z": "-",
    "v": "."
}

starting_char = 'x'  # charaters that will indicate the start or end of the data
ending_char = 'c'

# -----DO NOT EDIT-----

# are we uploading to the server or only testing the pose tracking?
uploading = True

while True:  # automatically download missing dependencies
    try:
        import requests as rq
        import mediapipe as mp  # mediapipe depends on opencv
        import cv2  # which depends on numpy
        import numpy as np
        import pydirectinput
        import calcs
        pydirectinput.PAUSE = press_delay  # short keypress delay
        break
    except ImportError as e:
        print("Missing 1 or more dependencies.", e)
        print("Downloading dependencies now.")
        subprocess.run("python -m pip install -r requirements.txt", shell=True)

roblox_rotations = {}
roblox_landmarks = {}
sent_data = []
sequence_num = 1

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


def replace_all(string: str):
    for i in key_map:
        v = str(key_map[i])
        string = string.replace(v, i)  # must reassign after replacing strings
    return string


def assign_angles(vector1: str, vector2: str, repeat_side: bool = False):
    """
    Takes names of two vectors/landmarks from the human body, calculates 
    and assigns their rotation to roblox_rotations.
    """
    global roblox_rotations

    # assign x,y,z coordinates of this landmark
    v1_coords = roblox_landmarks[vector1]
    v2_coords = roblox_landmarks[vector2]

    # calculate rotation matrix
    orient = calcs.look_at(np.array([v1_coords["x"], v1_coords["y"], v1_coords["z"]]), np.array(
        [v2_coords["x"], v2_coords["y"], v2_coords["z"]]))
    # retrieve roll, pitch, yaw or x,y,z rotations from matrix
    roll, pitch, yaw = calcs.angles(orient)

    roblox_rotations[vector1] = {
        "x": roll,
        "y": pitch,
        "z": yaw,
        "visibility": v2_coords["visibility"]
    }

    if repeat_side:  # repeat the same operation but on the right side of the body
        assign_angles(vector1.replace("left", "right"),
                      vector2.replace("left", "right"))


def keep_uploading():  # runs on a separate thread
    "Allow pose landmark to be uploaded without interrupting pose processing"
    last_sequence_num = 1
    requests_this_minute = 0
    last_request_count_time = time.time()
    last_request_sent = last_request_count_time
    request_headers = {"authorization": authorization}

    while True:
        if sequence_num == 0:  # stop program
            break

        elif sequence_num > last_sequence_num:
            if (time.time() - last_request_sent >= cooldown):
                if (typing_input):  # if using the typing feature
                    # indicate that this is a new list
                    pydirectinput.press(starting_char)
                    # parse pose data as json string
                    raw_json = json.dumps(sent_data)
                    string_data = replace_all(
                        raw_json.replace(" ", ""))  # remove spaces
                    pydirectinput.write(string_data)  # type it all out
                    # indicate that this is the end of the pose data list
                    pydirectinput.press(ending_char)
                else:  # otherwise upload to server
                    try:
                        r = rq.post(url=upload_url, json=sent_data,
                                    headers=request_headers)
                    except rq.ConnectTimeout as e:
                        print(e)
                        continue

                    requests_this_minute += 1
                    last_request_sent = time.time()

                    if r.status_code == 200:  # success
                        last_sequence_num = sequence_num
                    else:  # failure
                        print(f"Status code: {r.status_code}")
                        print(f"Response body: {r.text}")

            if time.time() - last_request_count_time >= 60:  # every 60 seconds display requests counter
                print(f"Requests this minute: {requests_this_minute}")
                last_request_count_time = time.time()
                requests_this_minute = 0

        else:
            time.sleep(0.01)  # give the loop a break


def main():
    "Main function of the program that handles pose processing"
    global roblox_landmarks
    global roblox_rotations
    global sequence_num
    global sent_data

    print("Opening the webcam...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("Initializing pose detection...")

    with mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7) as pose:
        print("View the new \"Webcam Pose\" window to make sure your webcam can see your pose clearly.")
        while cap.isOpened():
            success, image = cap.read()

            if not success:
                print("Ignoring empty camera frame.")
                continue

            # flip the image so it appears as a mirror when we view it
            imageToDisplay = cv2.flip(image, 1)
            # convert from BGR color scheme (used by OpenCV engine) to RGB (for processing)
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
                roblox_landmarks = {  # map each value pose landmark into new dictionary
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

                for body_part in roblox_landmarks:  # copy each pose landmark into a new dictionary with different landmark names
                    body_part_value = roblox_landmarks[body_part]
                    body_part_json = {
                        "x": body_part_value.x,
                        "y": body_part_value.y,
                        "z": body_part_value.z,
                        "visibility": body_part_value.visibility,
                    }
                    roblox_landmarks[body_part] = body_part_json
                roblox_rotations = {}  # assign/reset the dictionary storing the rotations of each joint

                # find where v1 (limb 1) has to turn to look at v2 (limb 2) for each joint in the body
                assign_angles("left_shoulder", "left_elbow", repeat_side=True)
                assign_angles("left_elbow", "left_wrist", repeat_side=True)
                assign_angles("left_hip", "left_knee", repeat_side=True)
                assign_angles("left_knee", "left_ankle", repeat_side=True)

                # calculate neck-head rotation
                lf_sh = roblox_landmarks["left_shoulder"]
                rt_sh = roblox_landmarks["right_shoulder"]
                nose = roblox_landmarks["nose"]
                shoulder_midpoint = {  # the neck is located between the two shoulders
                    "x": (lf_sh["x"] + rt_sh["x"]) / 2,
                    "y": (lf_sh["y"] + rt_sh["y"]) / 2,
                    "z": (lf_sh["z"] + rt_sh["z"]) / 2
                }

                neck_matrix = calcs.look_at(  # find rotation matrix of shoulders' midpoint to nose
                    np.array([shoulder_midpoint["x"],
                              shoulder_midpoint["y"], shoulder_midpoint["z"]]),
                    np.array([nose["x"], nose["y"], nose["z"]]))
                # find rotation angles of neck
                nk_x, nk_y, nk_z = calcs.angles(neck_matrix)

                roblox_rotations["neck"] = {  # assign x,y,z rotations of neck rotation
                    "x": nk_x,
                    "y": nk_y,
                    "z": nk_z,
                    "visibility": (lf_sh["visibility"] + rt_sh["visibility"]) / 2
                }

                # calculate hips rotation
                # also called the upper legs
                lf_hip = roblox_landmarks["left_hip"]
                rt_hip = roblox_landmarks["right_hip"]
                waist_midpoint = {  # midpoint of waist
                    "x": (lf_hip["x"] + rt_hip["x"]) / 2,
                    "y": (lf_hip["y"] + rt_hip["y"]) / 2,
                    "z": (lf_hip["z"] + rt_hip["z"]) / 2
                }

                waist_matrix = calcs.look_at(  # look-at rotation from hips to the bottom of the neck
                    np.array(
                        [waist_midpoint["x"], waist_midpoint["y"], waist_midpoint["z"]]),
                    np.array([shoulder_midpoint["x"], shoulder_midpoint["y"], shoulder_midpoint["z"]]))
                waist_x, waist_y, waist_z = calcs.angles(waist_matrix)

                roblox_rotations["waist"] = {  # store x,y,z rotations of the waist
                    "x": waist_x,
                    "y": waist_y,
                    "z": waist_z,
                    # avg visibility of hips
                    "visibility": (lf_hip["visibility"] + rt_hip["visibility"]) / 2
                }

                # order of compressed sent data
                landmarks_order = [
                    "neck",
                    "left_shoulder",
                    "right_shoulder",
                    "left_elbow",
                    "right_elbow",
                    "waist",
                    "left_hip",
                    "right_hip",
                    "left_knee",
                    "right_knee",
                ]
                sent_data = []  # the data that will be sent

                # compress data in a an array
                for ln_name in landmarks_order:  # if there's a left or right side to the landmark
                    # retrieve the dictionary containing x,y,z and visibility of landmark rotation
                    ln = roblox_rotations[ln_name]
                    ln_array = [round(ln["x"], 2), round(ln["y"], 2), round(
                        ln["z"], 2), round(ln["visibility"], 2)]
                    sent_data.append(ln_array)

                if uploading:  # if program is updating angles in the server, otherwise we're just testing
                    sequence_num += 1

            # display the image on the "Webcam Pose" window
            cv2.imshow("Webcam Pose", imageToDisplay)

            if cv2.waitKey(1) == 27:  # Esc key
                sequence_num = 0  # set to 0 to indicate to keep_uploading to stop
                cap.release()  # close the camera capture process
                cv2.destroyAllWindows()  # remove any currently open windows
                break


if __name__ == '__main__':
    if typing_input:
        input("Press Enter in the console to begin the program. "
              + f"The script will begin typing on the screen in {start_typing_delay} "
              + "seconds, so make sure Roblox is in focus.")
    time.sleep(start_typing_delay)
    upload_process = threading.Thread(target=keep_uploading)
    upload_process.start()
    main()  # if this function terminates, then stop the other thread below too
    upload_process.join()
