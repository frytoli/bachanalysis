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

import numpy as np
import base64
import data
import dlib
import cv2
import db
import os

# Global var for path to volume within container
PATH_TO_VOLUME = os.path.join(os.getcwd(), 'local')
# Global var for path to database
PATH_TO_DB = os.path.join(PATH_TO_VOLUME, 'thebach.db')

'''
Convert a base64 encoded string to a cv2 image
'''
def b64_to_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

'''
Rotate a contestant's photo so that their face is straight
https://sefiks.com/2020/02/23/face-alignment-for-face-recognition-in-python-within-opencv/
'''
def align_face(img):
    # Load pre-trained classifier
    eye_cascade = cv2.CascadeClassifier(f'{cv2.data.haarcascades}haarcascade_eye.xml')

'''
Crop a contestant's photo to just their face
'''
def crop_face(b64photo):
    # Load pre-trained classifier
    face_cascade = cv2.CascadeClassifier(f'{cv2.data.haarcascades}haarcascade_frontalface_default.xml')
    # Read-in dlib shape predictor from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
    predictor = dlib.shape_predictor(os.path.join(PATH_TO_VOLUME, 'shape_predictor_68_face_landmarks.dat'))

    # Extract image extension
    ext = f'''.{b64photo.split(';base64')[0].split('/')[-1]}'''
    # Convert base64 encoded photo to a cv2 image
    img = b64_to_img(b64photo)

    # Many thanks to https://github.com/rajendra7406-zz/FaceShape -->
    # Make a copy of the original image
    img_original = img.copy()
    # Convert to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply a Gaussian blur with a 3 x 3 kernel to help remove high frequency noise
    img_gauss = cv2.GaussianBlur(img_gray,(3,3), 0)

    # Detect contestant's face
    faces = face_cascade.detectMultiScale(img_gauss, scaleFactor=1.05, minNeighbors=5, minSize=(100,100), flags=cv2.CASCADE_SCALE_IMAGE)
    (x, y, w, h) = faces[0]

    # Convert the cv2 rectangle coordinates to Dlib rectangle
    dlib_rect = dlib.rectangle(x, y, x+w, y+h)

    # Detect landmarks
    detected_landmarks = predictor(img, dlib_rect).parts()
    # Convert landmarks to np matrix (containes indices of landmarks)
    landmarks = np.matrix([[p.x,p.y] for p in detected_landmarks])

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

    # Resize image to height == 500 (for standardization)
    resize_height = 500
    # Calculate the ratio of the height and construct the dimensions
    (height, width) = img.shape[:2]
    ratio = resize_height / float(height)
    dimensions = (int(width * ratio), resize_height)
    img_resized = cv2.resize(img_cropped, dimensions, interpolation=cv2.INTER_AREA)

    # Encode resized, cropped image as base64 string
    b64face = base64.b64encode(cv2.imencode(ext, img_resized)[1]).decode()
    # Return base64 string
    return b64face

def main():
    # Retrieve args
    parser = argparse.ArgumentParser(description='Process contestant data')
    parser.add_argument('--contestant', dest='contestant', type=str, nargs='+', default=[], help='a string contestant first and last name separated by "_" (only applicable with data source 5) (i.e. joelle_fletcher)')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true', help='overwrite applicable table(s) in the database')
    args = parser.parse_args()

    # Initialize sqldb object
    bachdb = db.bachdb(PATH_TO_DB)
    # Initialize data model handler object
    bachdata = data.bachdata()

    # Drop and create new data source tables, if applicable
    if args.overwrite:
        bachdb.create_table('ds5', bachdata.get_sql_table_values(ds), drop_existing=True)

    # Retrieve contestants' names (id) and photos
    contestants = bachdb.get_docs('ds3', column='name, photo')
    # Iterate over contestants and create the new dataset
    data = []
    for contestant in contestants:
        record = {
            'name': contestant[0]
        }
        # Crop contestant's face
        record['face_photo'] = crop_face(photo)

    # Model the data
    modeled_data = bachdata.model_many(5, scraped)
    # Add the modeled data to ds5 table
    bachdb.insert_docs('ds5', modeled_data)


if __name__ == '__main__':
    main()
