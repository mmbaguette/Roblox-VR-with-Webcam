# Virtual Reality in Roblox using a Webcam

Control your Roblox character's full body like in VR, but using only a webcam and no headset.

![Roblox_VR_with_Webcam_Good](https://user-images.githubusercontent.com/76597978/177058172-8a5cecb1-5693-42e7-9cfb-2e9d0b853cd0.gif)

Scroll down for setup and instructions.

## Features

- Control your R15 character pose (neck, shoulders, elbows, hips, legs and knees)
- Copies your entire body's movements from reality
- One-dimensional, flat body rotations (for now)
- Side-to-side head movements
- Real-time pose tracking using your webcam
- Open-source, thorough code documentation (read a few lines if you're unsure!)
- Authorization tokens to prevent spam and someone else controlling you

## How it works

A Python script/program on your PC captures your webcam footage. Using an advanced, AI, pose-estimation model from **Google/Mediapipe**, it calculates your 3D rotations for every joint in your body. Next, this pose data is immediately forwarded to a server that anyone can setup. Finally, a Roblox server making up to 500 requests a minute downloads your body pose to move you real time.

![Pose Upload Diagram Roblox VR](https://user-images.githubusercontent.com/76597978/177061058-7f928a18-645c-41b3-a146-7886befbde47.png)

## Pose Estimation

You might be wondering, **how is this possible?** How is a computer capable of tracking someone's pose using just a webcam? 

![pose gif mediapipe](https://user-images.githubusercontent.com/76597978/177061310-efbf795e-42d4-4f07-97b7-9a7236cde33a.gif)

This is where **MediaPipe** comes in, an open-source project from Google that provides several computer vision, machine learning/AI models for anyone to use, including their pose estimation solution. Check out https://google.github.io/mediapipe/solutions/pose for more info. 

## Setup

To get started playing games now, go to **client setup**.
To setup a Roblox game for players to join and use this program, go to **game setup**.

## Client Setup

Start playing on any game that already has the server-side and Roblox game setup.

- Start by downloading the [Python programming language](https://www.python.org)
  - More info: https://www.pythontutorial.net/getting-started/install-python/
- Download this repository: click on the green *Code* button > Download as ZIP
- Open the file `main.py` in a text editor like Notepad or an IDE like [Visual Studio Code](https://code.visualstudio.com)
- Edit the following variables at the top:
  - **username**: Change this to your Roblox username, not your display name
  - **authorization**: A **temporary** access token used by servers to verify your identity. A *3D Roblox* button in supported games will appear and give you instructions to use this (required).
  - **upload_url**: The URL of the HTTP request that will upload the pose data every **cooldown** seconds.
  - **cooldown**: Delay in seconds between each upload request. You don't need to change this.
- Now run the Python script `main.py` by double clicking the file to open with Python, or right click on the file on Windows > Open with > Python or open up a command prompt or terminal, and type `python [FILEPATH TO main.py]`

Make sure your webcam is plugged in and ready. When you run the program, a window will pop up revealing your camera. Position yourself far enough so that the white lines cover your whole body or the part you want to control.

## Game Setup

Allow your players to take advantage of this technology. Two things: Roblox game setup and online server setup.
Roblox model: https://www.roblox.com/library/10129626203/Virtual-Reality-and-3D-Camera

Under Construction 🚧
(too lazy to write rn) 
