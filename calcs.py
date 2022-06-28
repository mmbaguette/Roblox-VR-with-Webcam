from math import *
import numpy as np

def vec_length(v: np.array):
    return np.sqrt(sum(i**2 for i in v))

def normalize(v):
	norm = np.linalg.norm(v)

	if norm == 0: 
		return v
	return v / norm

def look_at(eye: np.array, target: np.array):
	"Calculates a numpy rotation matrix from two 3D vectors."
	axis_z = normalize((eye - target))

	if vec_length(axis_z) == 0:
		axis_z = np.array((0, -1, 0))

	axis_x = np.cross(np.array((0, 0, 1)), axis_z)
    
	if vec_length(axis_x) == 0:
		axis_x = np.array((1, 0, 0))
    
	axis_y = np.cross(axis_z, axis_x)
	rot_matrix = np.matrix([axis_x * 360, axis_y * 360, axis_z * 360]).transpose()
	
	return rot_matrix

def angles(rot_matrix: np.matrix): # https://stackoverflow.com/a/64336115
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
	return roll, pitch, yaw