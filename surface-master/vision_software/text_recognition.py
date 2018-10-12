from PIL import Image
import os
import numpy as np
import pytesseract
import cv2


class TextRecognitionDataHolder:

    def __init__(self, frame, gray, bitwise, thresh, rotated, kernel, text):
        self.frame = frame
        self.gray = gray
        self.bitwise = bitwise
        self.thresh = thresh
        self.rotated = rotated
        self.kernel = kernel
        self.text = text


def detect(camera):
    # Crop the frame
    frame = crop_frame(camera.frame, camera.rect)

    # Rotate the text to enhance recognition, assign all outputs to different variables
    gray, bitwise, thresh, rotated = rotate_text(frame)
    # cv2.imshow("Step 4: Rotation", rotated)

    # Apply a custom kernel to enhance it further
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    kernel = cv2.filter2D(rotated, -1, kernel)
    # cv2.imshow("Step 5: Kernel", kernel)

    # TODO: Test different kernels, result for [[0, -1, 0], [-1, 5, -1], [0, -1, 0]] for L6R - [6R

    '''
    Unused filter, to be tested with other samples, result for L6R - [BR

    # Apply blur to enhance it further
    blur = cv2.medianBlur(rotated, 5)
    cv2.imshow("Step 6: Blur", cv2.resize(blur, (0, 0), fx=3, fy=3))

    '''
    # Create a temporary path to store the image
    filename = "tmp_text_to_recognise.png"

    # Save the image to later open it with PIL
    cv2.imwrite(filename, kernel)

    # Recognise the text
    text = pytesseract.image_to_string(Image.open(filename))

    # Delete the temporary image
    os.remove(filename)

    # Return a new Text object, convert all gray-scale items to bgr to be ocrrectly displayed by kivy
    return TextRecognitionDataHolder(frame, cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), cv2.cvtColor(bitwise, cv2.COLOR_GRAY2BGR),
                            cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR), cv2.cvtColor(rotated, cv2.COLOR_GRAY2BGR),
                            cv2.cvtColor(kernel, cv2.COLOR_GRAY2BGR), text)


def rotate_text(frame):

    # Apply gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Step 1: Grayscale", gray)

    # Swap the colours, text should be white, background black
    bitwise = cv2.bitwise_not(gray)
    # cv2.imshow("Step 2: Colour swap", bitwise)

    # Apply the threshold
    thresh = cv2.threshold(bitwise, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # cv2.imshow("Step 3: Threshold", thresh)

    # Get the coordinates of the text block
    coords = np.column_stack(np.where(thresh > 0))

    # Get the rotation angle of the block wrapped in a rectangle
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Find the center and store it in a tuple
    (h, w) = frame.shape[:2]
    center = (w // 2, h // 2)

    # Create a rotation matrix
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Rotate the text
    rotated = cv2.warpAffine(thresh, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Return the all steps
    return gray, bitwise, thresh, rotated


def crop_frame(frame, rect):
    # Divide the rectangle into parts
    y1 = rect[0][1]
    y2 = rect[1][1]
    x1 = rect[0][0]
    x2 = rect[1][0]

    # Crop the frame
    frame = frame[y1:y2, x1:x2]

    # Return the cropped frame
    return frame
