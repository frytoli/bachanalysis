#!/usr/bin/env python

'''
Create a new dataset by
	1. Extracting physical features from images
	2. Applying attractiveness algorithms to images
		- Rule of thirds
		- Rule of fifths
		- Golden ratio
	3. Aggregate relevant data points from all data sets
'''

from multiprocessing import Pool
from algorithms import *
import numpy as np
import argparse
import base64
import data
import dlib
import math
import json
import cv2
import db
import os

# Global var for path to volume within container
PATH_TO_VOLUME = os.path.join(os.getcwd(), 'local')
# Global var for path to database
PATH_TO_DB = os.path.join(PATH_TO_VOLUME, 'thebach.db')

'''
Helper functions
'''
def b64_to_img(uri):
	encoded_data = uri.split(',')[1]
	nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
	img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	return img

def euclidean_distance(a, b):
	x1 = a[0]; y1 = a[1]
	x2 = b[0]; y2 = b[1]
	return math.sqrt(((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)))

def rotate_img(img, angle):
	img_center = tuple(np.array(img.shape[1::-1]) / 2)
	rot_mat = cv2.getRotationMatrix2D(img_center, angle, 1.0)
	result = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
	return result

def detect_landmarks(x, y, w, h, img):
	# Read-in dlib shape predictor from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
	predictor = dlib.shape_predictor('/usr/bin/shape_predictor_68_face_landmarks.dat')
	# Convert the cv2 rectangle coordinates to Dlib rectangle
	dlib_rect = dlib.rectangle(x, y, x+w, y+h)
	# Detect landmarks
	detected_landmarks = predictor(img, dlib_rect).parts()
	# Convert landmarks to np matrix (containes indices of landmarks)
	landmarks = np.matrix([[p.x,p.y] for p in detected_landmarks])
	return landmarks

'''
Rotate a contestant's photo so that their face is straight
Guidance from: https://sefiks.com/2020/02/23/face-alignment-for-face-recognition-in-python-within-opencv/
'''
def get_face_rotation(img):
	# Load pre-trained classifiers
	face_cascade = cv2.CascadeClassifier(f'{cv2.data.haarcascades}haarcascade_frontalface_default.xml')
	eye_cascade = cv2.CascadeClassifier(f'{cv2.data.haarcascades}haarcascade_eye.xml')

	# Convert to grayscale
	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	# Apply a Gaussian blur with a 3 x 3 kernel to help remove high frequency noise
	img_gauss = cv2.GaussianBlur(img_gray,(3,3), 0)

	# Detect contestant's face
	# https://stackoverflow.com/questions/20801015/recommended-values-for-opencv-detectmultiscale-parameters
	faces = face_cascade.detectMultiScale(img_gauss, scaleFactor=1.05, minNeighbors=6, minSize=(20,20), flags=cv2.CASCADE_SCALE_IMAGE)
	face_index = 0
	for face in faces:
		(x, y, w, h) = face
		# Get face image
		face_img = img_gauss[y:y+h, x:x+w]
		# Detect eyes JUST for second check that detected face is truly a face
		eyes = eye_cascade.detectMultiScale(face_img)
		# Ensure that at least one eye was detected
		if len(eyes) > 0:
			# Detect landmarks -- NOTE: it seems as if all landmarks are truly at point landmark-1
			landmarks = detect_landmarks(x, y, w, h,img)
			# Get the center point of (midpoint between) each eye
			# Get top left and bottom right points of right eye
			if landmarks[37, 1] > landmarks[38, 1]:
				y = landmarks[38, 1]
			else:
				y = landmarks[37, 1]
			right_top_left = (landmarks[36,0], y)
			if landmarks[41, 1] > landmarks[40, 1]:
				y = landmarks[41, 1]
			else:
				y = landmarks[40, 1]
			right_bottom_right = (landmarks[39,0], y)
			# Get top left and bottom right points of left eye
			if landmarks[43, 1] > landmarks[44,1]:
				y = landmarks[44,1]
			else:
				y = landmarks[43,1]
			left_top_left = (landmarks[42,0], y)
			if landmarks[47, 1] > landmarks[46, 1]:
				y = landmarks[47, 1]
			else:
				y = landmarks[46, 1]
			left_bottom_right = (landmarks[45,0], y)
			# Get the center points of each eye (midpoint formula)
			right_x = (right_top_left[0] + right_bottom_right[0])//2
			right_y = (right_top_left[1] + right_bottom_right[1])//2
			right_center = (right_x, right_y)
			left_x = (left_top_left[0] + left_bottom_right[0])//2
			left_y = (left_top_left[1] + left_bottom_right[1])//2
			left_center = (left_x, left_y)

			# Evaluate the location of the horizontal point and direction of rotation (clockwise or counterclockwise)
			if left_y < right_y:
				horiz_point = (right_x, left_y)
				direction = -1 # clockwise
			else:
				horiz_point = (left_x, right_y)
				direction = 1 # counterclockwise

			# Evaluate the edge lengths of the triangle made up of the line between the center of the eyes, a perfectly horizontal line, and a perfectly vertical line (with euclidean distance)
			a = euclidean_distance(left_center, horiz_point)
			b = euclidean_distance(right_center, left_center)
			c = euclidean_distance(right_center, horiz_point)

			# Find the possible angle of rotation with arc cosine (inverse)
			if b > 0 and c > 0: # Ensure no division by 0
				arc_cos = (b*b + c*c - a*a)/(2*b*c)
			else:
				arc_cos = 0
			angle = np.arccos(arc_cos)
			# Convert angle from radians to degrees
			angle = (angle * 180) / math.pi

			# If rotating clockwise, evaluate angle by negative evaluation of 90-angle (sum of all angles of a triangle = 180, we've already created a right 90 degree angle between the horizontal/vertical lines and line between center of the eyes)
			if direction == -1:
				angle = 0-(90 - angle)

			# Return the angle to rotate
			return face_index, angle
		face_index += 1
	return None, None

'''
Crop a contestant's photo to just their face
'''
def process_face(name, b64photo):
	# Initialize sqldb object
	bachdb = db.bachdb(PATH_TO_DB)
	# Initialize data model handler object
	bachdata = data.bachdata()

	# Load pre-trained classifier
	face_cascade = cv2.CascadeClassifier(f'{cv2.data.haarcascades}haarcascade_frontalface_default.xml')

	# Extract image extension
	ext = f'''.{b64photo.split(';base64')[0].split('/')[-1]}'''
	# Convert base64 encoded photo to a cv2 image
	img = b64_to_img(b64photo)

	# Find detected face index and rotation angle for image
	face_index, rotation_angle = get_face_rotation(img)
	# Rotate image
	img_straight = rotate_img(img, rotation_angle)

	# Many thanks to https://github.com/rajendra7406-zz/FaceShape -->
	# Make a copy of the original (straightened) image
	img_original = img_straight.copy()
	# Convert to grayscale
	img_gray = cv2.cvtColor(img_straight, cv2.COLOR_BGR2GRAY)
	# Apply a Gaussian blur with a 3 x 3 kernel to help remove high frequency noise
	img_gauss = cv2.GaussianBlur(img_gray,(3,3), 0)

	# Detect contestant's face
	# https://stackoverflow.com/questions/20801015/recommended-values-for-opencv-detectmultiscale-parameters
	faces = face_cascade.detectMultiScale(img_gauss, scaleFactor=1.05, minNeighbors=6, minSize=(20,20), flags=cv2.CASCADE_SCALE_IMAGE)
	if len(faces) > 0:
		# Handle the case that a face is not detected this time around or face_index is null
		if not face_index or len(faces) <= face_index:
			face_index = 0

		# Use face at face_index (from rotation angle evaluation)
		(x, y, w, h) = faces[face_index]

		# Detect landmarks
		landmarks = detect_landmarks(x, y, w, h, img_straight)

		# Save left and right cheek points
		cheek_left = (landmarks[1,0],landmarks[1,1])
		cheek_right = (landmarks[15,0],landmarks[15,1])
		# Save left and right jaw points (only in the case that the distance between these two points is larger than the distance between the two cheek points)
		jaw_left = (landmarks[3,0],landmarks[3,1])
		jaw_right = (landmarks[13,0],landmarks[13,1])
		# Save top (of forehead) and bottom (of chin) face points
		face_bottom = (landmarks[8,0],landmarks[8,1])
		face_top = (landmarks[8,0],y)
		# Find top right and bottom left points of rectangle around face
		if cheek_left[0] < jaw_left[0]:
			top_left = (cheek_left[0], face_top[1])
		else:
			top_left = (jaw_left[0], face_top[1])
		if cheek_right[0] > cheek_right[0]:
			bottom_right = (cheek_right[0], face_bottom[1])
		else:
			bottom_right = (jaw_right[0], face_bottom[1])

		# Crop photo to just contestant's face
		img_cropped = img_original[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

		# Resize image to height == 200 (for standardization)
		resize_height = 200
		# Calculate the ratio of the height and construct the dimensions
		h, w, c = img_cropped.shape
		ratio = resize_height / h
		dimensions = (int(w * ratio), resize_height)
		try:
			img_resized = cv2.resize(img_cropped, dimensions, interpolation=cv2.INTER_AREA)
		except Exception as e:
			print(f'Mayday! {e}')
			img_resized = np.array([])

		if img_resized.size > 0:
			# Encode resized, cropped image as base64 string
			b64face = f'''data:image/jpeg;base64,{base64.b64encode(cv2.imencode(ext, img_resized)[1]).decode()}'''

			# Lastly, detect new landmarks
			h, w, c = img_resized.shape
			landmarks = detect_landmarks(0, 0, w, h, img_resized).tolist()

			# Model the data
			record = {
				'name': name,
				'dlib_landmarks': json.dumps(landmarks), # Json dump nested list as a string
				'face_photo': b64face
			}
		else:
			record = {}
	else:
		record = {}
	if len(record) > 0:
		modeled_record = bachdata.model_one(5, record)
		# Add the modeled data to ds5 table
		bachdb.insert_doc('ds5', modeled_record)
	# Explicity remove record from memory
	del record

def eval_rule_of_thirds(name):
	# Initialize sqldb object
	bachdb = db.bachdb(PATH_TO_DB)
	# Retrieve contestants' names (id), cropped face photos, and dlib landmarks
	contestants = bachdb.get_docs('ds5', column='name, face_photo, dlib_landmarks', filters=[{'key':'name', 'operator':'==', 'comparison':name}])
	if len(contestants) > 0:
		for contestant in contestants:
			percent_error = rule_of_thirds.evaluate(b64_to_img(contestant[1]), np.array(json.loads(contestant[2])))
			# Update record in database
			bachdb.update_doc('ds5', {'key':'rule_of_thirds','operator':'=','comparison':json.dumps(percent_error)}, {'key':'name','operator':'==','comparison':name})
	# Clean memory
	del contestants

def eval_rule_of_fifths(name):
	# Initialize sqldb object
	bachdb = db.bachdb(PATH_TO_DB)
	# Retrieve contestants' names (id), cropped face photos, and dlib landmarks
	contestants = bachdb.get_docs('ds5', column='name, face_photo, dlib_landmarks', filters=[{'key':'name', 'operator':'==', 'comparison':name}])
	if len(contestants) > 0:
		for contestant in contestants:
			percent_error = rule_of_fifths.evaluate(b64_to_img(contestant[1]), np.array(json.loads(contestant[2])))
			# Update record in database
			bachdb.update_doc('ds5', {'key':'rule_of_fifths','operator':'=','comparison':json.dumps(percent_error)}, {'key':'name','operator':'==','comparison':name})
	# Clean memory
	del contestants

def eval_golden_ratio(name):
	# Initialize sqldb object
	bachdb = db.bachdb(PATH_TO_DB)
	# Retrieve contestants' names (id), cropped face photos, and dlib landmarks
	contestants = bachdb.get_docs('ds5', column='name, face_photo, dlib_landmarks', filters=[{'key':'name', 'operator':'==', 'comparison':name}])
	if len(contestants) > 0:
		for contestant in contestants:
			percent_error = golden_ratio.evaluate(b64_to_img(contestant[1]), np.array(json.loads(contestant[2])))
			# Update record in database
			bachdb.update_doc('ds5', {'key':'golden_ratio','operator':'=','comparison':json.dumps(percent_error)}, {'key':'name','operator':'==','comparison':name})
	# Clean memory
	del contestants

def main():
	# Retrieve args
	parser = argparse.ArgumentParser(description='Process contestant data')
	parser.add_argument('--preprocess', dest='preprocess', action='store_true', help='preprocess the data (rotate, crop, and identify dlib landmarks) for data set 5')
	parser.add_argument('--algorithm', dest='algorithm', type=str, nargs='+', default=['thirds', 'fifths', 'golden', 'features'], help='a string algorithm name to perform (thirds, fifths, golden, and/or features)')
	parser.add_argument('--contestant', dest='contestant', type=str, nargs='+', default=[], help='a string contestant first and last name separated by "_" (i.e. joelle_fletcher)')
	parser.add_argument('--overwrite', dest='overwrite', action='store_true', help='overwrite table ds5 in the database. Only applicable with preprocess flag')
	args = parser.parse_args()

	# Initialize multiprocessing pool with 5 threads
	pool = Pool(processes=5)

	# Initialize sqldb object
	bachdb = db.bachdb(PATH_TO_DB)
	# Initialize data model handler object
	bachdata = data.bachdata()

	# If the user wants to preprocess the data
	if args.preprocess:
		# Drop and create new data source tables, if applicable
		if args.overwrite:
			bachdb.create_table('ds5', bachdata.get_sql_table_values(5), drop_existing=True)

		# If no contestants are given by the user, process every contestant from data set 3 in the database
		if len(args.contestant) == 0:
			# Retrieve contestants' names (id) and photos
			contestants = bachdb.get_docs('ds3', column='name, photo')
			if len(contestants) == 0:
				print(f'Mayday! Unable to compile data set 5. Has data set 3 been collected and stored?')
		else:
			contestants = []
			for contestant in args.contestant:
				names = contestant.lower().split('_')
				name = f'''{names[0][0].upper()}{names[0][1:].lower()} {names[1][0].upper()}{names[1][1:].lower()}'''
				contestant = bachdb.get_docs('ds3', column='name, photo', filters=[{'key':'name', 'operator':'==', 'comparison':name}])
				if len(contestant) > 0:
					contestants += contestant
		# Multiprocess rotating, cropping, and finding facial landmarks of contestants' faces via their photos
		pool_resp = pool.starmap_async(process_face, contestants)
		pool_resp.get()

	# Perform algorithms if specified
	if len(args.algorithm) > 0:
		# Rule of thirds
		if 'thirds' in args.algorithm:
			# If no contestants are given by the user, retrieve all pre-processed document ids (contestant names) from the database
			if len(args.contestant) == 0:
				# Retrieve contestants' names (id)
				contestants = [contestant[0] for contestant in bachdb.get_docs('ds5', column='name')]
				if len(contestants) == 0:
					print(f'Mayday! Unable to evaluate rule of thirds. Has data set 5 been collected, preprocessed, and stored?')
			else:
				contestants = []
				for contestant in args.contestant:
					names = contestant.lower().split('_')
					name = f'''{names[0][0].upper()}{names[0][1:].lower()} {names[1][0].upper()}{names[1][1:].lower()}'''
					contestants.append(name)
			# Multiprocess evaluating rule of thirds
			pool_resp = pool.map(eval_rule_of_thirds, contestants)
		# Rule of fifths
		if 'fifths' in args.algorithm:
			print('fifths')
		# Golden ratio
		if 'golden' in args.algorithm:
			print('golden')
		# Feature measurement
		if 'features' in args.algorithm:
			print('features')
		# Let 'er rip!
		pool_resp.get()

if __name__ == '__main__':
	main()
