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
    # Return a list of the sizes of the three horizontal parts of the face
    # Save measurement of three equal parts of face
    h, w, c = face_img.shape
    theoretical_h = h//3

    # Get height of face from hairline (top of image) to eyebrows
    # Get midpoint of eyebrows
    right_center = ((landmarks[18,0]+landmarks[20,0])//2, (landmarks[18,1]+landmarks[20,1])//2)
    left_center = ((landmarks[23,0]+landmarks[25,0])//2, (landmarks[23,1]+landmarks[25,1])//2)
    # Get height distance from top of image to eyebrow midpoint
    third1 = (right_center[1]+left_center[1])//2

    # Get height distance from eyebrows to bottom of nose
    third2 = landmarks[33,1]-third1

    # Get height distance from bottom of nose to chin (bottom of image)
    third3 = h-landmarks[33,1]

    cv2.circle(face_img, (50, third1), 1, (255,0,0), 1)
    cv2.circle(face_img, (50, landmarks[33,1]), 1, (0,255,0), 1)
    cv2.circle(face_img, (50, h), 1, (0,0,255), 1)
    cv2.imwrite('temp.jpeg', face_img)

    # Evaluate the percent error of each part
    percent_errors = [percent_error(third, theoretical_h) for third in [third1, third2, third3]]
    # Return
    return percent_errors
