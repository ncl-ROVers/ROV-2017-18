# Vision software

### *camera.py*
Provides video stream and functions to complete the tail recognition task at the [MATE](https://www.marinetech.org/) competition.

#### Usage
To use the camera, instantiate the `Camera` object and use its `stream()` function. This will open a new window with a video stream from webcam connected to the raspberry PI. To view the video from a different source, comment out `self.cap.open("http://169.254.116.33:8081/?action=stream")` section. The area selection type for frame processing is stored in `MANUAL` boolean.

Functions provided by the `Camera` object:
- *stream()*
- *capture_frame()*
- *get_rectangle()*

Both `capture_frame()` and `get_rectangle()` should not be used on their own, they are linked with each other and the `stream()` function. Consider them private to the class. Only the `stream()` function should be used externally.

#### Functions' description

`stream()` is a simple `while` loop that keeps capturing the frame while the camera is streaming.

`get_rectangle()` returns coordinates (calculated using frame size) needed to draw a recangle on the screen. It's called only once, in `__init__()`.

`capture_frame()` feature is used to read current frame from the `VideoCapture` object, and process it. Precisely, if not in manual mode, it draws a rectangle on the screen to mark the crop area for later image processing. On button press, it launches new processes with other modules' functions.

### *colour_recognition.py*
### *shape_recognition.py*
### *text_recognition.py*
