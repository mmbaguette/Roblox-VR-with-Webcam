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

	# convert from radians to degrees
	# roll = math.degrees(roll)
	# pitch = math.degrees(pitch)
	# yaw = math.degrees(yaw)
	return roll, pitch, yaw
'''
def angles(matrix: np.matrix):
	# epsilon for testing whether a number is close to zero
	_EPS = np.finfo(float).eps * 5.0

	# axis sequences for Euler angles
	_NEXT_AXIS = [1, 2, 0, 1]
	firstaxis, parity, repetition, frame = (1, 1, 0, 0) # ''

	i = firstaxis
	j = _NEXT_AXIS[i+parity]
	k = _NEXT_AXIS[i-parity+1]

	M = np.array(matrix, dtype='float', copy=False)[:3, :3]
	if repetition:
		sy = np.sqrt(M[i, j]*M[i, j] + M[i, k]*M[i, k])
		if sy > _EPS:
			ax = np.arctan2( M[i, j],  M[i, k])
			ay = np.arctan2( sy,       M[i, i])
			az = np.arctan2( M[j, i], -M[k, i])
		else:
			ax = np.arctan2(-M[j, k],  M[j, j])
			ay = np.arctan2( sy,       M[i, i])
			az = 0.0
	else:
		cy = np.sqrt(M[i, i]*M[i, i] + M[j, i]*M[j, i])
		if cy > _EPS:
			ax = np.arctan2( M[k, j],  M[k, k])
			ay = np.arctan2(-M[k, i],  cy)
			az = np.arctan2( M[j, i],  M[i, i])
		else:
			ax = np.arctan2(-M[j, k],  M[j, j])
			ay = np.arctan2(-M[k, i],  cy)
			az = 0.0

	if parity:
		ax, ay, az = -ax, -ay, -az
	if frame:
		ax, az = az, ax
	return ax, ay, az
'''