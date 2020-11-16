#!/usr/bin/env python

'''
Take in a face image and evaluate how well it fits the rule of fifths:
    "A proportionate face may be divided vertically into fifths, each approximately the width
    of one eye."
'''

import cv2

def evaluate(face_img, landmarks):
    # Create fifths variable
    fifths = {
        'theoretical_fifths': 0.0,
        'experimental_fifths1': 0.0,
        'experimental_fifths2': 0.0,
        'experimental_fifths3': 0.0,
        'experimental_fifths4': 0.0,
        'experimental_fifths5': 0.0
    }

    # Get face image shape
    h, w, c = face_img.shape

    # Find the average width of the two eyes, this is our theoretical width of each 1/5 section
    right_eye_width = landmarks[39,0]-landmarks[36,0]
    left_eye_width = landmarks[45,0]-landmarks[42,0]
    fifths['theoretical_fifths'] = float((right_eye_width+left_eye_width)/2)

    # Get the widths of the five sections of the contestant's face (left to right)
    fifths['experimental_fifths1'] = float(landmarks[36,0])
    fifths['experimental_fifths2'] = float(abs(landmarks[36,0]-landmarks[39,0]))
    fifths['experimental_fifths3'] = float(abs(landmarks[39,0]-landmarks[42,0]))
    fifths['experimental_fifths4'] = float(abs(landmarks[42,0]-landmarks[45,0]))
    fifths['experimental_fifths5'] = float(abs(landmarks[45,0]-w))

    # Return results
    return fifths
