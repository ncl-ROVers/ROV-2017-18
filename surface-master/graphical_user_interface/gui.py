from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.graphics.texture import Texture
# noinspection PyUnresolvedReferences
from kivy.garden.mapview import MapView
# noinspection PyUnresolvedReferences
from kivy.garden.mapview import MapMarker
# noinspection PyUnresolvedReferences
from kivy.garden.mapview import MarkerMapLayer

from communication_software.surface_udp import Connection
from flight_data_software import crash_zone_calculator
from vision_software.camera_view import CameraView
from vision_software.shape_recognition import detect as recognise_shape
from vision_software.text_recognition import detect as recognise_text
from cv2 import flip
from cv2 import approxPolyDP
from cv2 import arcLength
from sys import exit

TIME_INTERVAL = 0.01


class Joystick:

    def __init__(self):
        # Set max/min boundaries for the axis
        self.axis_min = -1000
        self.axis_max = 1000

        # Set starting value for the joystick
        self.axis_mid = (self.axis_max + self.axis_min) // 2

        # Store axis information
        self.x = self.axis_mid
        self.y = self.axis_mid
        self.z = self.axis_mid

        # Set max/min boundaries for the hat
        self.hat_min = 1100
        self.hat_max = 1900

        # Set starting value for the hat
        self.hat_mid = (self.hat_max + self.hat_min) // 2

        # Store hat information
        self.hat = [self.hat_mid, self.hat_mid]

        # Store buttons information
        self.jaws_up = False
        self.jaws_down = False

    def normalise_axis_value(self, value):
        # Define variables
        axis_min = -32768
        axis_max = 32767

        # Normalise the output
        output = self.axis_min + (value - axis_min) * (self.axis_max - self.axis_min) / (axis_max - axis_min)

        # Cast it to an integer
        output = int(output)

        # Return the value
        return output

    def set_hat_value(self, x, y):
        # Normalise and set the values
        if x == -1:
            self.hat[0] = self.hat_max
        elif x == 1:
            self.hat[0] = self.hat_min
        else:
            self.hat[0] = self.hat_mid

        if y == -1:
            self.hat[1] = self.hat_max
        elif y == 1:
            self.hat[1] = self.hat_min
        else:
            self.hat[1] = self.hat_mid

    def set_axis_value(self, axis_id, value):
        # Normalise and set the values, x-axis at index 0, y-axis at index 1, z-axis at index 4
        if axis_id == 0:
            self.x = self.normalise_axis_value(value)
        elif axis_id == 1:
            self.y = self.normalise_axis_value(value)
        elif axis_id == 4:
            self.z = self.normalise_axis_value(value)

    def set_button_value(self, button_id):
        # Set the jaws' values
        if button_id == 0:
            self.jaws_up = not self.jaws_up
        elif button_id == 1:
            self.jaws_down = not self.jaws_down

    def get_hat_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update the hat information
        text += "Hat X: " + str(self.hat[0]) + '\n'
        text += "Hat Y: " + str(self.hat[1]) + '\n'

        # Return the string
        return text

    def get_axis_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update the axis information
        text += "Axis X: " + str(self.x) + '\n'
        text += "Axis Y: " + str(self.y) + '\n'
        text += "Axis Z: " + str(self.z) + '\n'

        # Return the string
        return text


class Controller:

    def __init__(self):
        # Initialise value cap for the controller to not use thrusters full power
        self.cap = 200

        # Set max/min boundaries for the axis
        self.axis_min = 1100 + self.cap
        self.axis_max = 1900 - self.cap

        # Set starting value for the controller
        self.axis_mid = (self.axis_max + self.axis_min) // 2

        # Store axis information
        self.left_x = self.axis_mid
        self.left_y = self.axis_mid
        self.right_x = self.axis_mid
        self.right_y = self.axis_mid
        self.lt = self.axis_min
        self.rt = self.axis_min

        # Store hat state information
        self.arrow_up = False
        self.arrow_down = False
        self.arrow_right = False
        self.arrow_left = False

        # Store buttons information
        self.button_a = False
        self.button_b = False
        self.button_y = False
        self.button_x = False

    def normalise_axis_value(self, value):
        # Define variables
        axis_min = -32768
        axis_max = 32767

        # Normalise the output
        output = self.axis_min + (value - axis_min) * (self.axis_max - self.axis_min) / (axis_max - axis_min)

        # Cast it to an integer
        output = int(output)

        # Return the value
        return output

    def set_axis_value(self, axis_id, value):
        # Normalise and set the values, x-axis at indexes 0, 3 y-axis at indexes 1, 4, LT at 2, RT at 5
        if axis_id == 0:
            self.left_x = self.normalise_axis_value(value)
        elif axis_id == 1:
            self.left_y = self.normalise_axis_value(value)
        elif axis_id == 3:
            self.right_x = self.normalise_axis_value(value)
        elif axis_id == 4:
            self.right_y = self.normalise_axis_value(value)
        elif axis_id == 2:
            self.lt = self.normalise_axis_value(value)
        elif axis_id == 5:
            self.rt = self.normalise_axis_value(value)

    def set_hat_value(self, x, y):
        if x == 1:
            self.arrow_left = False
            self.arrow_right = not self.arrow_right
        elif x == -1:
            self.arrow_right = False
            self.arrow_left = not self.arrow_left
        if y == 1:
            self.arrow_down = False
            self.arrow_up = not self.arrow_up
        elif y == -1:
            self.arrow_up = False
            self.arrow_down = not self.arrow_down

    def set_button_value(self, button_id):
        if button_id == 0:
            self.button_y = False
            self.button_a = not self.button_a
        elif button_id == 3:
            self.button_a = False
            self.button_y = not self.button_y
        if button_id == 2:
            self.button_b = False
            self.button_x = not self.button_x
        elif button_id == 1:
            self.button_x = False
            self.button_b = not self.button_b

    def get_axis_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update the axis information
        text += "Left axis X: " + str(self.left_x) + '\n'
        text += "Left axis Y: " + str(self.left_y) + '\n'
        text += "Right axis X: " + str(self.right_x) + '\n'
        text += "Right axis Y: " + str(self.right_y) + '\n'
        text += "LT: " + str(self.lt) + '\n'
        text += "RT: " + str(self.rt) + '\n'

        # Return the string
        return text

    def get_hat_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update the axis information
        text += "Left arrow: " + str(self.arrow_left) + '\n'
        text += "Right arrow: " + str(self.arrow_right) + '\n'
        text += "Up arrow: " + str(self.arrow_up) + '\n'
        text += "Down arrow: " + str(self.arrow_down) + '\n'

        # Return the string
        return text


class Camera:

    def __init__(self, joystick):
        # Create a camera object
        self.camera = CameraView()

        # Set assigned joystick
        self.joy = joystick

        # Initialise the frame field
        self.frame = None

        # Initialise camera position
        self.x = self.joy.hat_mid
        self.y = self.joy.hat_mid

        # Initialise camera rotation speed
        self.speed = 10

        # Keep updating the frame
        Clock.schedule_interval(self.update, TIME_INTERVAL)

    def get_texture(self, frame):
        # Reference: Answer to "Python/Kivy camera widget error with opencv" by arnav Jul 27 '16 at 20:42
        #[https://stackoverflow.com/questions/30294385/python-kivy-camera-widget-error-with-opencv/38622827#38622827}

        # Convert frame to texture
        #buf1 = flip(frame, 0)
        #buf = buf1.tostring()
        #image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        #image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        buf1 = flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]))
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        return image_texture

    def update(self, dt):
        # Update the frame
        self.update_frame()

        # Update the position
        self.update_position()

    def update_frame(self):
        # Capture the frame and assign it to the field
        self.frame = self.camera.capture_frame()

    def update_position(self):
        # Change the position using preset camera rotation speed
        if self.joy.hat[0] == self.joy.hat_max and self.x < self.joy.hat_max:
            self.x += self.speed
        elif self.joy.hat[0] == self.joy.hat_min and self.x > self.joy.hat_min:
            self.x -= self.speed

        if self.joy.hat[1] == self.joy.hat_max and self.y < self.joy.hat_max:
            self.y += self.speed
        elif self.joy.hat[1] == self.joy.hat_min and self.y > self.joy.hat_min:
            self.y -= self.speed

    def reset_position(self):
        self.x = self.joy.hat_mid
        self.y = self.joy.hat_mid

    def get_position_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update the camera position information
        text += "Camera position X: " + str(self.x) + '\n'
        text += "Camera position Y: " + str(self.y) + '\n'

        # Return the string
        return text


class Thrusters:

    def __init__(self, controller):
        # Set assigned controller
        self.con = controller

        # Initialise each thruster's state
        self.aft_left = self.con.axis_mid
        self.aft_right = self.con.axis_mid
        self.for_left = self.con.axis_mid
        self.for_right = self.con.axis_mid
        self.hor_left = self.con.axis_mid
        self.hor_right = self.con.axis_mid

        # Keep updating the thrusters
        Clock.schedule_interval(self.update, TIME_INTERVAL)

    def update(self, dt):
        # Update the thrusters using axis values
        self.hor_right = self.con.left_y
        self.hor_left = self.con.left_y
        self.aft_left = self.con.right_y
        self.aft_right = self.con.right_y
        self.for_left = self.con.right_x
        self.for_right = self.con.right_x

        # Update the thrusters using controller's arrows
        if self.con.arrow_up:
            self.hor_right = self.con.axis_max
            self.hor_left = self.con.axis_max
        elif self.con.arrow_down:
            self.hor_right = self.con.axis_min
            self.hor_left = self.con.axis_min
        if self.con.arrow_right:
            self.aft_right = self.con.axis_max
            self.aft_left = self.con.axis_min
            self.for_right = self.con.axis_max
            self.for_left = self.con.axis_min
        elif self.con.arrow_left:
            self.aft_right = self.con.axis_min
            self.aft_left = self.con.axis_max
            self.for_right = self.con.axis_min
            self.for_left = self.con.axis_max

        # Update the thrusters using controller's buttons:
        if self.con.button_y:
            self.aft_right = self.con.axis_max
            self.aft_left = self.con.axis_max
        elif self.con.button_a:
            self.aft_right = self.con.axis_min
            self.aft_left = self.con.axis_min
        if self.con.button_b:
            self.for_right = self.con.axis_max
            self.for_left = self.con.axis_max
        elif self.con.button_x:
            self.for_right = self.con.axis_min
            self.for_left = self.con.axis_min

        # Update the thrusters using LT, RT
        if self.con.lt == self.con.axis_max:
            self.hor_left = self.con.axis_mid
        if self.con.rt == self.con.axis_max:
            self.hor_right = self.con.axis_mid

    def get_thrusters_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update thrusters' states
        text += "Aft left: " + str(self.aft_left) + '\n'
        text += "Aft right: " + str(self.aft_right) + '\n'
        text += "For left: " + str(self.for_left) + '\n'
        text += "For right: " + str(self.for_right) + '\n'
        text += "Horizontal left: " + str(self.hor_left) + '\n'
        text += "Horizontal right: " + str(self.hor_right) + '\n'

        # Return the string
        return text


class Arm:

    def __init__(self, joystick):
        # Set assigned joystick
        self.joy = joystick

        # Initialise arm rotation speed
        self.speed = 1

        # Initialise jaws speed multiplier
        self.multiplier = 10

        # Initialise arm's threshold turn
        self.threshold = 10

        # Initialise step helpers
        self.delta_y = 0
        self.delta_z = 0

        # Initialise each motor's state
        self.y = self.joy.axis_mid
        self.z = self.joy.axis_mid
        self.jaws = self.joy.axis_mid

        # Keep updating the arm
        Clock.schedule_interval(self.update, TIME_INTERVAL)

    def update(self, dt):
        # Update the step helpers using axis values
        if self.joy.y == self.joy.axis_max:
            self.delta_y += self.speed
        elif self.joy.y == self.joy.axis_min:
            self.delta_y -= self.speed
        if self.joy.z == self.joy.axis_max:
            self.delta_z += self.speed
        elif self.joy.z == self.joy.axis_min:
            self.delta_z -= self.speed

        # Update the positions using deltas of y and z axis
        if self.delta_y > self.threshold:
            self.y += self.threshold
            self.delta_y -= self.threshold
        elif self.delta_y < self.threshold*-1:
            self.y -= self.threshold
            self.delta_y += self.threshold
        if self.delta_z > self.threshold:
            self.z += self.threshold
            self.delta_z -= self.threshold
        elif self.delta_z < self.threshold*-1:
            self.z -= self.threshold
            self.delta_z += self.threshold

        # Update the jaws using buttons
        if self.joy.jaws_up:
            self.jaws += self.speed * self.multiplier
        elif self.joy.jaws_down:
            self.jaws -= self.speed * self.multiplier

    def get_arm_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update arm's state
        text += "Delta Y: " + str(self.delta_y) + '\n'
        text += "Delta Z: " + str(self.delta_z) + '\n'
        text += "Axis Y: " + str(self.y) + '\n'
        text += "Axis Z: " + str(self.z) + '\n'
        text += "Jaws: " + str(self.jaws) + '\n'

        # Return the string
        return text


# These variables are here temporarily
# TODO: Figure out how to have them in the GUI class and access from other classes
joy = Joystick()
con = Controller()
cam = Camera(joy)
thr = Thrusters(con)
arm = Arm(joy)


# TODO: Fix Application leaving in progress issue when X button pressed to close the app
# TODO: Implement good for users windows behaviour, resizing, jumping to other input fields on enter etc.

class WelcomeScreen(Screen):

    def __init__(self):
        super(WelcomeScreen, self).__init__()


class VideoStreamScreen(Screen):

    def __init__(self):
        super(VideoStreamScreen, self).__init__()

        # Keep updating the screen
        Clock.schedule_interval(self.update, TIME_INTERVAL)

    def update(self, dt):
        # Update the frame
        self.update_frame()

        # Update the displayed information
        self.update_text()

    def update_frame(self):
        # Pull the texture from camera
        try:
            self.ids.vs.texture = cam.get_texture(cam.frame)
        except AttributeError:
            print("Invalid video stream frame passed.")

    def update_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update the camera position information
        text += cam.get_position_text()

        # Update the arm information
        text += arm.get_arm_text()

        # Update thrusters information
        text += thr.get_thrusters_text()

        # Update the textual representation of system data
        self.ids.data.text = text


class ShapeRecognitionScreen(Screen):

    def __init__(self):
        super(ShapeRecognitionScreen, self).__init__()

        # Initialise different shape recognition panels
        self.red, self.yellow, self.blue = None, None, None

        # Keep updating the screen
        Clock.schedule_interval(self.update, TIME_INTERVAL)

    def update(self, dt):
        # Update the frame
        self.update_frames()

        # Update the text
        self.update_text()

    def update_frames(self):
        # Update the recognition shapes
        self.red, self.yellow, self.blue = recognise_shape(cam.camera)

        # Pull the textures from camera
        try:
            self.ids.vs.texture = cam.get_texture(cam.frame)
        except AttributeError:
            print("Invalid video stream frame passed.")
        try:
            self.ids.red.texture = cam.get_texture(self.red.frame)
        except AttributeError:
            print("Invalid red-colour recognition frame passed.")
        try:
            self.ids.yellow.texture = cam.get_texture(self.yellow.frame)
        except AttributeError:
            print("Invalid yellow-colour recognition frame passed.")
        try:
            self.ids.blue.texture = cam.get_texture(self.blue.frame)
        except AttributeError:
            print("Invalid blue-colour recognition frame passed.")

    def update_text(self):
        if self.red.contour is not False:
            # Get number of contours' edges
            approx_red = len(approxPolyDP(self.red.contour, 0.01 * arcLength(self.red.contour, True), True))
        else:
            approx_red = 0

        if self.yellow.contour is not False:
            approx_yellow = len(approxPolyDP(self.yellow.contour, 0.01 * arcLength(self.yellow.contour, True), True))
        else:
            approx_yellow = 0

        if self.blue.contour is not False:
            approx_blue = len(approxPolyDP(self.blue.contour, 0.01 * arcLength(self.blue.contour, True), True))
        else:
            approx_blue = 0

        # Check if a triangle or a quadrangle were detected for each shape, update shape recognition output
        try:
            if approx_red == 3:
                self.ids.red_text.text = "Shape recognised:\nRed triangle"
            elif approx_red == 4:
                self.ids.red_text.text = "Shape recognised:\nRed trapezium"
            else:
                self.ids.red_text.text = "No red shape recognised\nNumber of contours: " + str(approx_red)
        except AttributeError:
            print("Invalid red-colour recognition frame passed")

        try:
            if approx_yellow == 3:
                self.ids.yellow_text.text = "Shape recognised\nYellow triangle"
            elif approx_yellow == 4:
                self.ids.yellow_text.text = "Shape recognised\nYellow trapezium"
            else:
                self.ids.yellow_text.text = "No yellow shape recognised\nNumber of contours: " + str(approx_yellow)
        except AttributeError:
            print("Invalid yellow-colour recognition frame passed")

        try:
            if approx_blue == 3:
                self.ids.blue_text.text = "Shape recognised:\nBlue triangle"
            elif approx_blue == 4:
                self.ids.blue_text.text = "Shape recognised:\nBlue trapezium"
            else:
                self.ids.blue_text.text = "No blue shape recognised\nNumber of contours: " + str(approx_blue)
        except AttributeError:
            print("Invalid blue-colour recognition frame passed")


class TextRecognitionScreen(Screen):

    def __init__(self):
        super(TextRecognitionScreen, self).__init__()

        # Initialise custom object that stores recognition steps and detected text
        self.object = None

    def update(self):
        # Update the frame
        self.update_frames()

        # Update the text
        self.update_text()

    def update_frames(self):
        # Update the recognition steps, detect text
        self.object = recognise_text(cam.camera)

        # Pull the textures from the object
        try:
            self.ids.frame.texture = cam.get_texture(self.object.frame)
            self.ids.gray.texture = cam.get_texture(self.object.gray)
            self.ids.bitwise.texture = cam.get_texture(self.object.bitwise)
            self.ids.thresh.texture = cam.get_texture(self.object.thresh)
            self.ids.rotated.texture = cam.get_texture(self.object.rotated)
            self.ids.kernel.texture = cam.get_texture(self.object.kernel)
        except AttributeError:
            print("Invalid video stream frame passed.")

    def update_text(self):
        # Initialise a dictionary with results
        results = {
            "L6R": 0,
            "AX2": 0,
            "UH8": 0,
            "G7C": 0,
            "S1P": 0,
            "JW3": 0
        }

        # Add the score result based on input
        if "L" in self.object.text:
            results["L6R"] += 1
        if "6" in self.object.text:
            results["L6R"] += 1
        if "R" in self.object.text:
            results["L6R"] += 1

        if "A" in self.object.text:
            results["AX2"] += 1
        if "2" in self.object.text:
            results["AX2"] += 1
        if "X" in self.object.text:
            results["AX2"] += 1

        if "U" in self.object.text:
            results["UH8"] += 1
        if "H" in self.object.text:
            results["UH8"] += 1
        if "8" in self.object.text:
            results["UH8"] += 1

        if "G" in self.object.text:
            results["G7C"] += 1
        if "7" in self.object.text:
            results["G7C"] += 1
        if "C" in self.object.text:
            results["G7C"] += 1

        if "J" in self.object.text:
            results["JW3"] += 1
        if "W" in self.object.text:
            results["JW3"] += 1
        if "3" in self.object.text:
            results["JW3"] += 1

        if "S" in self.object.text:
            results["S1P"] += 1
        if "1" in self.object.text:
            results["S1P"] += 1
        if "P" in self.object.text:
            results["S1P"] += 1

        # Update the recognised text
        try:
            self.ids.recognised_text.text = "Text recognised:\n" + self.object.text

            # Get the maximum score from the dictionary
            result = max(results, key=results.get)

            # Update the text accordingly
            if results[result] == 0:
                self.ids.result.text = "Recognition failure"
            else:
                self.ids.result.text = "Recognised: " + result

        except AttributeError:
            print("Invalid video stream frame passed")


class VehicleControlsScreen(Screen):

    def __init__(self):
        super(VehicleControlsScreen, self).__init__()

        # Keep updating the screen
        Clock.schedule_interval(self.update, TIME_INTERVAL)

    def update(self, dt):
        # Update displayed information
        self.update_text()

    def update_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update the controller's axis information
        text += con.get_axis_text()

        # Update the controller's arrows information
        text += con.get_hat_text()

        # Update thrusters information
        text += thr.get_thrusters_text()

        # Update the textual representation of vehicle controlling data
        self.ids.data.text = text


class ArmControlsScreen(Screen):

    def __init__(self):
        super(ArmControlsScreen, self).__init__()

        # Schedule an interval to update joystick's axis' information
        Clock.schedule_interval(self.update, TIME_INTERVAL)  # Was 0.001

    def update(self, dt):
        # Update displayed information
        self.update_text()

    def update_text(self):
        # Initialise an empty string to add to it later
        text = ""

        # Update the joystick axis information
        text += joy.get_axis_text()

        # Update the joystick hat information
        text += joy.get_hat_text()

        # Update arm information
        text += arm.get_arm_text()

        # Update the textual representation of vehicle controlling data
        self.ids.data.text = text


class FlightDataScreen(Screen):

    def __init__(self):
        super(FlightDataScreen, self).__init__()

    def update(self):
        # Try to display the calculations
        try:
            # Initialise an empty string to add to it later
            data = ""

            # Fetch the values from input boxes
            location = self.ids.location.text
            plane_angle = int(self.ids.plane_angle.text)
            ascent_speed = int(self.ids.ascent_speed.text)
            ascent_rate = int(self.ids.ascent_rate.text)
            time = int(self.ids.time.text)
            descent_speed = int(self.ids.descent_speed.text)
            descent_rate = int(self.ids.descent_rate.text)
            wind_angle = int(self.ids.wind_angle.text)
            wind_equation = self.ids.wind_equation.text

            # Calculate the output
            output = crash_zone_calculator.calculate_coordinates(location, plane_angle, ascent_speed, ascent_rate, time,
                                                                 descent_speed, descent_rate, wind_angle, wind_equation)

            # Get the coordinates to change the map's focus and put markers
            start_coords = output[1]
            crash_coords = output[2]

            # Update the map view
            self.ids.map_view.center_on(start_coords[0], start_coords[1])
            self.ids.map_view.zoom = 11

            # Create a start location marker
            start_marker = MapMarker(lat=start_coords[0], lon=start_coords[1])

            # Create a crash location marker
            crash_marker = MapMarker(lat=crash_coords[0], lon=crash_coords[1])

            # Put the start location marker
            self.ids.map_view.add_marker(start_marker)

            # Put the crash location marker
            self.ids.map_view.add_marker(crash_marker)

            '''
            # Create a new mapmarkerlayer
            m = MarkerMapLayer()

            # Put the start location marker
            self.ids.map_view.add_marker(start_marker, layer=m)

            # Put the crash location marker
            self.ids.map_view.add_marker(crash_marker, layer=m)
            '''
            # Clear the text
            self.ids.data.text = ""

            # Update the displayed information
            for s in output[0]:
                self.ids.data.text += s
        except:
            print("Error while doing the calculations")


class GUI(App):

    def __init__(self):
        super(GUI, self).__init__()

        try:
            pass
            # Create the connection with PI
            # self.connection = Connection()

            # Connect to the PI
            # self.connection.connect()

            # Begin console output for debug
            # self.connection.begin_console_output()

            # Keep sending the data
            # Clock.schedule_interval(self.update_data, TIME_INTERVAL/2)

        except OSError:
            print("OSError, check connection credentials + cable")

        # Load the base layout
        self.base = Builder.load_file("graphical_user_interface/layouts/base.kv")

        # Load other screens
        self.welcome = Builder.load_file("graphical_user_interface/layouts/welcome.kv")
        self.vehicle_controls = Builder.load_file("graphical_user_interface/layouts/vehicle_controls.kv")
        self.arm_controls = Builder.load_file("graphical_user_interface/layouts/arm_controls.kv")
        self.flight_data = Builder.load_file("graphical_user_interface/layouts/flight_data.kv")
        self.video_stream = Builder.load_file("graphical_user_interface/layouts/video_stream.kv")
        self.shape_recognition = Builder.load_file("graphical_user_interface/layouts/shape_recognition.kv")
        self.text_recognition = Builder.load_file("graphical_user_interface/layouts/text_recognition.kv")

        # Create a list to store the information about previous screens
        self.links = []

    def build(self):
        # Disable the multitouch
        Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

        # Bind the joystick axis
        Window.bind(on_joy_axis=self.on_joy_axis)

        # Bind the hat
        Window.bind(on_joy_hat=self.on_joy_hat)

        # Bind the buttons
        Window.bind(on_joy_button_down=self.on_joy_button_down)
        Window.bind(on_joy_button_up=self.on_joy_button_up)

        # Load the welcome screen on build
        self.base.ids.sm.switch_to(self.welcome)

        # Add the welcome screen to links
        self.links.append(self.welcome)

        # Return the base screen
        return self.base

    def switch_to(self, screen):
        # Avoid overloading screens
        if not self.links[-1] == screen:

            # Switch to a different screen (for example on an action bar button press)
            self.root.ids.sm.switch_to(screen)

            # Add the screen to links list
            self.links.append(screen)

    def switch_back(self):
        # Check if there is a screen to change to
        if len(self.links) > 1:

            # Pop the current screen
            self.links.pop()

            # Load the previous screen
            self.root.ids.sm.switch_to(self.links[-1])

    def update_data(self, dt):

        # Send the vertical thrusters' data
        self.connection.set_output_value(1, thr.aft_left)
        self.connection.set_output_value(2, thr.aft_right)
        self.connection.set_output_value(3, thr.for_left)
        self.connection.set_output_value(4, thr.for_right)

        # Send the horizontal thrusters' data
        self.connection.set_output_value(5, thr.hor_left)
        self.connection.set_output_value(6, thr.hor_right-100)

        # Send the camera position data
        self.connection.set_output_value(7, cam.x)
        self.connection.set_output_value(8, cam.y)

        # Send the arm rotation data
        self.connection.set_output_value(9, arm.y)
        self.connection.set_output_value(11, arm.z)
        self.connection.set_output_value(12, arm.jaws)

        # Update the data
        self.connection.iterate()

    def on_joy_axis(self, _, stick_id, axis_id, value):
        # If stick id is 0, then it's arm's joystick
        if stick_id == 0:

            # Update the arm's axis' values
            if axis_id == 0 or axis_id == 4:
                joy.set_axis_value(axis_id, value)
            # If this is the Y-axis, swap the value's sign (aka multiply by -1)
            elif axis_id == 1:
                joy.set_axis_value(axis_id, (value*-1)-1)

        # If stick id is 1, then it's vehicle's controller
        elif stick_id == 1:

            # Update the vehicle axis' values
            if axis_id == 0 or axis_id == 2 or axis_id == 3 or axis_id == 5 or axis_id == 6:
                con.set_axis_value(axis_id, value)
            # If this is the second Y-axis, swap the value's sign (aka multiply by -1)
            elif axis_id == 4 or axis_id == 1:
                con.set_axis_value(axis_id, value*-1)

    def on_joy_hat(self, _, stick_id, ball_id, value):
        # If stick id is 0, then it's arm's joystick
        if stick_id == 0:

            # Set the hat values
            joy.set_hat_value(value[0], value[1])

        # If stick id is 1, then it's the controller
        elif stick_id == 1:

            # Set the hat values
            con.set_hat_value(value[0], value[1])

    def on_joy_button_down(self, _, stick_id, button_id):
        # If stick id is 0, then it's arm's joystick
        if stick_id == 0:

            # Reset the camera position
            if button_id == 2:
                cam.reset_position()

            # Move the arm more TODO: Change it in a proper place (arm class)
            if button_id == 7:
                arm.y -= 100
            if button_id == 9:
                arm.y += 100
            if button_id == 8:
                arm.z -= 100
            if button_id == 10:
                arm.z += 100

            # Pass the button id to the joystick
            joy.set_button_value(button_id)

        # If stick id is 1, then it's the controller
        if stick_id == 1:

            con.set_button_value(button_id)

    def on_joy_button_up(self, _, stick_id, button_id):
        # If stick id is 0, then it's arm's joystick
        if stick_id == 0:
            # Pass the button id to the joystick
            joy.set_button_value(button_id)
