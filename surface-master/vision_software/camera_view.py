import cv2


class CameraView:

    def __init__(self):
        # Create new VideoCapture object
        self.cap = cv2.VideoCapture(0)

        # Get the camera stream from the PI
        # self.cap.open("http://169.254.116.33:8081/?action=stream")

        while self.cap.read()[1] is None:
            # Catch the initial frame
            self.frame = self.cap.read()[1]

        # Save the rectangle values
        self.rect = self.get_rectangle()

    def capture_frame(self):

        # Check if the successfully read new frame
        if self.cap.read()[1] is not None:
            # Capture frame-by-frame
            self.frame = self.cap.read()[1]
        else:
            pass

        # Assign a copy of frame, to not draw the rectangle on the original one
        frame_copy = self.frame.copy()

        # Draw the rectangle
        cv2.rectangle(frame_copy, self.rect[0], self.rect[1], (0, 0, 255), 3)

        # Wait the shortest possible value to update the frame correctly
        cv2.waitKey(1)

        # Return the frame with the rectangle to use it in the GUI
        return frame_copy

    # Stream function is called only when running the camera in a separate window
    def stream(self):
        # Keep streaming
        while True:
            # Update the frame
            self.capture_frame()

    def get_rectangle(self):
        # Get the width and height of the frame
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # Calculate rectangle boundaries
        rect = (int(width//2 - width//4), int(height//2 - height//4)),\
               (int(width//2 + width//4), int(height//2 + height//4))

        # Return the rectangle
        return rect
