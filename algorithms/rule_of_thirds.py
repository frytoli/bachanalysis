#!/usr/bin/env python

'''
Take in a face image and evaluate how well it fits the rule of thirds:
    "A well proportioned face will be divided into equal thirds when horizontal lines are drawn
    through the forehead hairline, the brow, the base of the nose, and the edge of the chin"
'''

import cv2

def percent_error(experimental, theoretical):
    if theoretical != 0:
        return (abs(experimental-theoretical)/abs(theoretical))*100
    else:
        print('Mayday! Cannot divide by zero')
        return 0

def evaluate(face_img, landmarks):
    # Save measurement of three equal parts of face
    h, w, c = face_img.shape
    theoretical_h = h//3

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
    right_center = ((right_top_right[0]+right_bottom_left[0])//2, (right_top_right[1]+right_bottom_left[1])//2)
    left_center = ((left_top_right[0]+left_bottom_left[0])//2, (left_top_right[1]+left_bottom_left[1])//2)
    # Get height distance from top of image to eyebrow midpoint
    third1 = (right_center[1]+left_center[1])//2

    # Get height distance from eyebrows to bottom of nose
    third2 = landmarks[33,1]-third1

    # Get height distance from bottom of nose to chin (bottom of image)
    third3 = h-landmarks[33,1]

    # Evaluate the percent error of each part
    percent_errors = [percent_error(third, theoretical_h) for third in [third1, third2, third3]]
    # Return
    return percent_errors
