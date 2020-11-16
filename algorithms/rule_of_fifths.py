#!/usr/bin/env python

'''
Take in a face image and evaluate how well it fits the rule of fifths:
    "A proportionate face may be divided vertically into fifths, each approximately the width
    of one eye."
'''

import cv2

def percent_error(experimental, theoretical):
    if theoretical != 0:
        return (abs(experimental-theoretical)/abs(theoretical))*100
    else:
        print('Mayday! Cannot divide by zero')
        return 0

def evaluate(face_img, landmarks):
    # Get face image shape
    h, w, c = face_img.shape

    # Find the average width of the two eyes, this is our theoretical width of each 1/5 section
    right_eye_width = landmarks[39,0]-landmarks[36,0]
    left_eye_width = landmarks[45,0]-landmarks[42,0]
    theoretical_section_width = (right_eye_width+left_eye_width)//2

    # Get the width of the contestant's face, this is our experimental width of each 1/5 section
    experimental_section_width = w//5

    # Evaluate percent error
    p_error = percent_error(experimental_section_width, theoretical_section_width)
    return p_error
