#!/usr/bin/env python

'''
Take in a face image and evaluate how well it fits the rule of thirds:
    "A well proportioned face will be divided into equal thirds when horizontal lines are drawn
    through the forehead hairline, the brow, the base of the nose, and the edge of the chin"
'''

import cv2

def evaluate(face_img, landmarks):
    # Create thirds variable
    thirds = {
        'theoretical_thirds': 0.0,
        'experimental_thirds1': 0.0,
        'experimental_thirds2': 0.0,
        'experimental_thirds3': 0.0
    }

    # Save measurement of three equal parts of face
    h, w, c = face_img.shape
    thirds['theoretical_thirds'] = h/3

    # Get height of face from hairline (top of image) to eyebrows
    # Get midpoint of eyebrows
    right_top_right = (landmarks[17,0], landmarks[19,1])
    if landmarks[17,1] > landmarks[21,1]:
        right_bottom_left = (landmarks[21,0], landmarks[17,1])
    else:
        right_bottom_left = (landmarks[21,0], landmarks[17,1])
    left_top_right = (landmarks[22,0], landmarks[24,1])
    if landmarks[22,1] > landmarks[26,1]:
        left_bottom_left = (landmarks[26,0], landmarks[22,1])
    else:
        left_bottom_left = (landmarks[26,0], landmarks[26,1])
    right_center = ((right_top_right[0]+right_bottom_left[0])/2, (right_top_right[1]+right_bottom_left[1])/2)
    left_center = ((left_top_right[0]+left_bottom_left[0])/2, (left_top_right[1]+left_bottom_left[1])/2)
    # Get height distance from top of image to eyebrow midpoint
    thirds['experimental_thirds1'] = float((right_center[1]+left_center[1])/2)

    # Get height distance from eyebrows to bottom of nose
    thirds['experimental_thirds2'] = float(landmarks[33,1]-thirds['experimental_thirds1'])

    # Get height distance from bottom of nose to chin (bottom of image)
    thirds['experimental_thirds3'] = float(h-landmarks[33,1])

    # Return results
    return thirds
