#!/usr/bin/env python

'''
Take in a face image and evaluate how well it fits the golden ratio
https://www.goldennumber.net/meisner-beauty-guide-golden-ratio-facial-analysis/

+-----------+------------------+-----------------------+------------------------+
| Reference | Start            | Ratio                 | End                    |
+-----------+------------------+-----------------------+------------------------+
| HW        | Face height      | height:width          | Face width             |
+-----------+------------------+-----------------------+------------------------+
| V1        | Center of pupils | Center of lips        | Bottom of chin         |
+-----------+------------------+-----------------------+------------------------+
| V2        | Center of pupils | Nose at nostrils      | Bottom of chin         |
+-----------+------------------+-----------------------+------------------------+
| V3        | Center of pupils | Nose bulb top         | Bottom of nose         |
+-----------+------------------+-----------------------+------------------------+
| V4        | Top of eyebrows  | Top of eyes           | Bottom of eyes         |
+-----------+------------------+-----------------------+------------------------+
| V5        | Center of pupils | Nose at nostrils      | Center of lips         |
+-----------+------------------+-----------------------+------------------------+
| V6        | Top of lips      | Center of lips        | Bottom of lips         |
+-----------+------------------+-----------------------+------------------------+
| V7        | Nose at nostrils | Top of lips           | Center of lips         |
+-----------+------------------+-----------------------+------------------------+
| H1        | Side of face     | Inside of nearest eye | Opposite side of face  |
+-----------+------------------+-----------------------+------------------------+
| H2        | Side of face     | Inside of nearest eye | Inside of opposite eye |
+-----------+------------------+-----------------------+------------------------+
| H3        | Center of face   | Outside edge of eye   | Side of face           |
+-----------+------------------+-----------------------+------------------------+
| H4        | Side of face     | Outside edge of eye   | Inside edge of eye     |
+-----------+------------------+-----------------------+------------------------+
| H5        | Side of face     | Outside of eye brow   | Outside edge of eye    |
+-----------+------------------+-----------------------+------------------------+
| H6        | Center of face   | Width of nose         | Width of mouth         |
+-----------+------------------+-----------------------+------------------------+
| H7        | Side of mouth    | Cupid's bow           | Opposite side of mouth |
+-----------+------------------+-----------------------+------------------------+
'''

import math
import cv2

def percent_error(experimental, theoretical):
    if theoretical != 0:
        return (abs(experimental-theoretical)/abs(theoretical))*100
    else:
        print('Mayday! Cannot divide by zero')
        return 0

def evaluate(face_img, landmarks):
    # Get contestant
    golden_ratio = (1+math.sqrt(5))/2
    # Create ratio variable
    ratios = {
        'hw': 0.0,
        'v1': 0.0,
        'v2': 0.0,
        'v3': 0.0,
        'v4': 0.0,
        'v5': 0.0,
        'v6': 0.0,
        'v7': 0.0,
        'h1': 0.0,
        'h2': 0.0,
        'h3': 0.0,
        'h4': 0.0,
        'h5': 0.0,
        'h6': 0.0,
        'h7': 0.0
    }

    # Get face image shape
    h, w, c = face_img.shape

    # Perform useful calculations for ratio evaluation:
    # * Center of eyes:
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
    eye_right_center = ((right_top_left[0] + right_bottom_right[0])//2, (right_top_left[1] + right_bottom_right[1])//2)
    eye_left_center = ((left_top_left[0] + left_bottom_right[0])//2, (left_top_left[1] + left_bottom_right[1])//2)
    eyes_center = ((eye_right_center[0]+eye_left_center[0])//2, (eye_right_center[1]+eye_left_center[1])//2)
    # Top of eyebrows
    eyebrows_top = ((landmarks[19,0]+landmarks[24,0])//2, (landmarks[19,1]+landmarks[24,1])//2)
    # Top of eyes
    eyes_top_right = (eye_right_center[0], right_top_left[1])
    eyes_top_left = (eye_left_center[0], left_top_left[1])
    eyes_top = ((eyes_top_right[0]+eyes_top_left[0])//2, (eyes_top_right[1]+eyes_top_left[1])//2)
    # Bottom of eyes
    eyes_bottom_right = (eye_right_center[0], right_bottom_right[1])
    eyes_bottom_left = (eye_left_center[0], left_bottom_right[1])
    eyes_bottom = ((eyes_bottom_right[0]+eyes_bottom_left[0])//2, (eyes_bottom_right[1]+eyes_bottom_left[1])//2)

    # * Lips
    # Get top left and bottom right points of lips
    if landmarks[51,1] < landmarks[53,1]:
        y = landmarks[51,1]
    else:
        y = landmarks[53,1]
    lips_top_left = (landmarks[48,0], y)
    lips_bottom_right = (landmarks[54,0], landmarks[57,1])
    # Center of lips
    lips_center = ((lips_top_left[0]+lips_bottom_right[0])//2, (lips_top_left[1]+lips_bottom_right[1])//2)
    # Top of lips
    lips_top = (lips_center[0], y)
    # Bottom of lips
    lips_bottom = (lips_center[0], lips_bottom_right[1])

    # * Nose
    # Get average height of two sides of nose at nostrils
    nostrils = ((landmarks[31,0]+landmarks[35,0])//2, (landmarks[31,1]+landmarks[35,1])//2)
    # Top of nose bulb
    nose_bulb = (landmarks[30,0], landmarks[30,1])
    # Bottom of nose
    nose_bottom = (landmarks[33,0], landmarks[33,1])

    # Eval ratios
    ratios['hw'] = percent_error(h/w, golden_ratio)
    ratios['v1'] = percent_error((lips_center[1]-eyes_center[1])/(h-lips_center[1]), golden_ratio)
    ratios['v2'] = percent_error((nostrils[1]-eyes_center[1])/(h-nostrils[1]), golden_ratio)
    ratios['v3'] = percent_error((nose_bulb[1]-eyes_center[1])/(nose_bottom[1]-nose_bulb[1]), golden_ratio)
    ratios['v4'] = percent_error((eyes_top[1]-eyebrows_top[1])/(eyes_bottom[1]-eyes_top[1]), golden_ratio)
    ratios['v5'] = percent_error((nostrils[1]-eyes_center[1])/(lips_center[1]-nostrils[1]), golden_ratio)
    ratios['v6'] = percent_error((lips_center[1]-lips_top[1])/(lips_bottom[1]-lips_center[1]), golden_ratio)
    ratios['v7'] = percent_error((lips_top[1]-nostrils[1])/(lips_center[1]-lips_top[1]), golden_ratio)
    print(ratios)
