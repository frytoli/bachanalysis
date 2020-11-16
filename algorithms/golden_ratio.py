#!/usr/bin/env python

'''
Take in a face image and evaluate how well it fits the golden ratio as defined by the
"Meisner Beauty Guide"

CITATIONS:
Meisner, G. B., & Araujo, R. (2018). The Golden Ratio: The Divine Beauty of Mathematics
    (Illustrated ed.).Race Point Publishing.
Meisner, G. (2020, September 28). Meisner Beauty Guide for Golden Ratio Facial Analysis.
    The Golden Ratio: Phi, 1.618.
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

def find_ratio(m1, m2):
    # Golden ratio is 1:1.68
    # Divide greater measurement by smaller
    if m1 > m2:
        # Don't divide by zero
        if m2 > 0:
            return m1/m2
        else:
            return 0
    else:
        # Don't divide by zero
        if m1 > 0:
            return m2/m1
        else:
            return 0

def evaluate(face_img, landmarks):
    # Get contestant
    golden_ratio = (1+math.sqrt(5))/2
    # Create ratio variable
    ratios = {
        'hw_ratio': 0.0,
        'v1_ratio': 0.0,
        'v2_ratio': 0.0,
        'v3_ratio': 0.0,
        'v4_ratio': 0.0,
        'v5_ratio': 0.0,
        'v6_ratio': 0.0,
        'v7_ratio': 0.0,
        'h1_ratio': 0.0,
        'h2_ratio': 0.0,
        'h3_ratio': 0.0,
        'h4_ratio': 0.0,
        'h5_ratio': 0.0,
        'h6_ratio': 0.0,
        'h7_ratio': 0.0
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
    eye_right_center = ((right_top_left[0] + right_bottom_right[0])/2, (right_top_left[1] + right_bottom_right[1])/2)
    eye_left_center = ((left_top_left[0] + left_bottom_right[0])/2, (left_top_left[1] + left_bottom_right[1])/2)
    eyes_center = ((eye_right_center[0]+eye_left_center[0])/2, (eye_right_center[1]+eye_left_center[1])/2)
    # Top of eyebrows
    eyebrows_top = ((landmarks[19,0]+landmarks[24,0])/2, (landmarks[19,1]+landmarks[24,1])/2)
    # Top of eyes
    eyes_top_right = (eye_right_center[0], right_top_left[1])
    eyes_top_left = (eye_left_center[0], left_top_left[1])
    eyes_top = ((eyes_top_right[0]+eyes_top_left[0])/2, (eyes_top_right[1]+eyes_top_left[1])/2)
    # Bottom of eyes
    eyes_bottom_right = (eye_right_center[0], right_bottom_right[1])
    eyes_bottom_left = (eye_left_center[0], left_bottom_right[1])
    eyes_bottom = ((eyes_bottom_right[0]+eyes_bottom_left[0])/2, (eyes_bottom_right[1]+eyes_bottom_left[1])/2)

    # * Lips
    # Get top left and bottom right points of lips
    if landmarks[51,1] < landmarks[53,1]:
        y = landmarks[51,1]
    else:
        y = landmarks[53,1]
    lips_top_left = (landmarks[48,0], y)
    lips_bottom_right = (landmarks[54,0], landmarks[57,1])
    # Center of lips
    lips_center = ((lips_top_left[0]+lips_bottom_right[0])/2, (lips_top_left[1]+lips_bottom_right[1])/2)
    # Top of lips
    lips_top = (lips_center[0], y)
    # Bottom of lips
    lips_bottom = (lips_center[0], lips_bottom_right[1])

    # * Nose
    # Get average height of two sides of nose at nostrils
    nostrils = ((landmarks[31,0]+landmarks[35,0])/2, (landmarks[31,1]+landmarks[35,1])/2)
    # Top of nose bulb
    nose_bulb = (landmarks[30,0], landmarks[30,1])
    # Bottom of nose
    nose_bottom = (landmarks[33,0], landmarks[33,1])

    # HEAD RATIO
    ratios['hw_ratio'] = float(find_ratio(h, w))
    # VERTICAL RATIOS
    ratios['v1_ratio'] = float(find_ratio(abs(eyes_center[1]-lips_center[1]), abs(lips_center[1]-h)))
    ratios['v2_ratio'] = float(find_ratio(abs(eyes_center[1]-nostrils[1]), abs(nostrils[1]-h)))
    ratios['v3_ratio'] = float(find_ratio(abs(eyes_center[1]-nose_bulb[1]), abs(nose_bulb[1]-nose_bottom[1])))
    ratios['v4_ratio'] = float(find_ratio(abs(eyebrows_top[1]-eyes_top[1]), abs(eyes_top[1]-eyes_bottom[1])))
    ratios['v5_ratio'] = float(find_ratio(abs(eyes_center[1]-nostrils[1]), abs(nostrils[1]-lips_center[1])))
    ratios['v6_ratio'] = float(find_ratio(abs(lips_top[1]-lips_center[1]), abs(lips_center[1]-lips_bottom[1])))
    ratios['v7_ratio'] = float(find_ratio(abs(nostrils[1]-lips_top[1]), abs(lips_top[1]-lips_center[1])))
    # HORIZONTAL RATIOS
    ratios['h1_ratio'] = float(find_ratio(landmarks[39,0], abs(landmarks[39,0]-w)))
    ratios['h2_ratio'] = float(find_ratio(landmarks[39,0], abs(landmarks[39,0]-landmarks[42,0])))
    ratios['h3_ratio'] = float(find_ratio(abs((w/2)-landmarks[36,0]), landmarks[36,0]))
    ratios['h4_ratio'] = float(find_ratio(landmarks[36,0], abs(landmarks[36,0]-landmarks[39,0])))
    ratios['h5_ratio'] = float(find_ratio(landmarks[17,0], abs(landmarks[17,0]-landmarks[36,0])))
    ratios['h6_ratio'] = float(find_ratio(abs((w/2)-landmarks[35,0]), abs(landmarks[35,0]-landmarks[54,0])))
    ratios['h7_ratio'] = float(find_ratio(abs(landmarks[48,0]-landmarks[52,0]), abs(landmarks[52,0]-landmarks[54,0])))

    return ratios
