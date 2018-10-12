import cv2
import numpy as np

# Constants for filtering adequate contours (represented as a fraction of the image area)
CONTOUR_SIZE_BOUND = 1 / 40


# Define constants for red hsv ranges
RED_MIN_LOW = np.array([0, 100, 40], np.uint8)
RED_MAX_LOW = np.array([8, 255, 255], np.uint8)
RED_MIN_HIGH = np.array([172, 100, 40], np.uint8)
RED_MAX_HIGH = np.array([180, 255, 255], np.uint8)

# Define constants for yellow hsv ranges
YELLOW_MIN = np.array([15,60, 60], np.uint8)
YELLOW_MAX = np.array([35, 255, 255], np.uint8)

# Define constants for blue hsv ranges
BLUE_MIN = np.array([90, 120, 80], np.uint8)
BLUE_MAX = np.array([130, 255, 255], np.uint8)


class Shape:

    def __init__(self, frame, contour):
        self.frame = frame
        self.contour = contour


def detect(camera):
    # Crop the frame
    frame = crop_frame(camera.frame, camera.rect)

    # Threshold the image to extract specific colours
    red, yellow, blue = extract_colours(frame)

    # Detect the contours
    red_con, yellow_con, blue_con = detect_shape(red), detect_shape(yellow), detect_shape(blue)

    # Reuse red, yellow and blue variables to draw contours on an actual image
    red = frame.copy()
    yellow = frame.copy()
    blue = frame.copy()

    # Draw the contours if a valid contour is present
    if red_con is not False:
        cv2.drawContours(red, red_con, -1, (255, 0, 255), 2)

    if yellow_con is not False:
        cv2.drawContours(yellow, yellow_con, -1, (255, 0, 255), 2)

    if blue_con is not False:
        cv2.drawContours(blue, blue_con, -1, (255, 0, 255), 2)

    # Display the frames
    # cv2.imshow("Red", red)
    # cv2.imshow("Yellow", yellow)
    # cv2.imshow("Blue", blue)

    # Create new Shape objects
    red = Shape(red, red_con)
    yellow = Shape(yellow, yellow_con)
    blue = Shape(blue, blue_con)

    # Return the frames with colour and shape recognised, as well as the contours
    return red, yellow, blue


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


def extract_colours(frame):

    # Convert the frame to hsv
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Thresh the frame to find colours, using defined ranges
    blue = cv2.inRange(hsv, BLUE_MIN, BLUE_MAX)
    yellow = cv2.inRange(hsv, YELLOW_MIN, YELLOW_MAX)

    # Thresh red colour using combined ranges
    red_low = cv2.inRange(hsv, RED_MIN_LOW, RED_MAX_LOW)
    red_high = cv2.inRange(hsv, RED_MIN_HIGH, RED_MAX_HIGH)
    red = cv2.addWeighted(red_low, 1.0, red_high, 1.0, 0.0)

    # Display the frames with colours extracted
    # cv2.imshow("Red thresh", red)
    # cv2.imshow("Yellow thresh", yellow)
    # cv2.imshow("Blue thresh", blue)

    # Return new frames with extracted colours
    return red, yellow, blue


def detect_shape(frame):
    # Store the resolution
    res = frame.shape

    # Store the area of the window to use it when filtering the contours
    area = res[0] * res[1]

    # Find contours inside the frame
    contours = cv2.findContours(frame, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[1]

    # Initialise the contour to be displayed
    contour = 0

    # Iterate through each contour in the threshed image
    for cnt in contours:

        # Calculate the area of the shape
        cnt_area = cv2.contourArea(cnt)

        # Do not consider any areas smaller than the fraction of the image
        if not cnt_area < area * CONTOUR_SIZE_BOUND:
            # If important contour is empty (is int), assign a contour to the field
            if type(contour) == int:
                contour = cnt
            # If important contour is a contour, then calculate the areas and put the bigger one in the field
            elif cnt_area > cv2.contourArea(contour):
                contour = cnt

    # Return the contour if a valid one was detected, otherwise return False
    if type(contour) != int:
        return contour
    else:
        return False
