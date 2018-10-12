import math


def calculate_coordinates(location, plane_angle, ascent_speed, ascent_rate, time, descent_speed, descent_rate,
                          wind_angle, wind_equation):

    # Try to calculate the values
    try:
        # Initialise a list to store the values to print
        strings = []

        # Return longitude/latitude depending on the take-off location
        start_lat, start_long = get_initial_coordinates(location)
        strings.append("Initial geographic coordinates: " + str(start_lat) + ", " + str(start_long) + '\n')

        # Calculate the height reached before the engine failure
        height = get_height(ascent_rate, time)
        strings.append("Height reached: " + str(height) + '\n')

        # Calculate diagonal distance before the engine failure to extract X-axis and Y-axis distances
        ascent_distance = get_plane_distance(ascent_speed, time)
        strings.append("Diagonal distance before the engine failure: " + str(ascent_distance) + '\n')

        # Convert the angle so it meets extraction requirements
        plane_angle = convert_angle(plane_angle, 0)

        # Extract X-axis and Y-axis distances for ascent
        ascent_x, ascent_y = extract_distance(plane_angle, ascent_distance)
        strings.append("Ascent in X-axis: " + str(ascent_x) + "\nAscent in Y-axis: " + str(ascent_y) + '\n')

        # Calculate time after which the plane reached the ground
        crash_time = get_crash_time(height, descent_rate)
        strings.append("Crash time after the engine failure: " + str(crash_time) + '\n')

        # Calculate diagonal distance after the engine failure to extract X-axis and Y-axis distances
        descent_distance = get_plane_distance(descent_speed, crash_time)
        strings.append("Diagonal distance before the engine failure: " + str(descent_distance) + '\n')

        # Extract X-axis and Y-axis distances for descent
        descent_x, descent_y = extract_distance(plane_angle, descent_distance)
        strings.append("Descent in X-axis: " + str(descent_x) + "\nDescent in Y-axis: " + str(descent_y) + '\n')

        # Calculate diagonal distance of the wind
        wind_distance = get_wind_distance(wind_equation, crash_time)
        strings.append("Diagonal distance of the wind: " + str(wind_distance) + '\n')

        # Convert the angle so it meets extraction requirements, additional 180 because of the "wind blows from" sentence
        wind_angle = convert_angle(wind_angle + 180, 0)

        # Extract X-axis and Y-axis distances for wind
        wind_x, wind_y = extract_distance(wind_angle, wind_distance)
        strings.append("Wind in X-axis: " + str(wind_x) + "\nWind in Y-axis: " + str(wind_y) + '\n')

        strings.append("----------------------------" + '\n')

        # Calculate total X-axis and Y-axis movements
        total_x = ascent_x + descent_x + wind_x
        total_y = ascent_y + descent_y + wind_y
        strings.append("Total in X-axis: " + str(total_x) + "\nTotal in Y-axis: " + str(total_y) + '\n')

        # Calculate the diagonal distance of the flight
        total_distance = get_diagonal_distance(total_x, total_y)
        strings.append("Total diagonal distance: " + str(total_distance) + '\n')

        # Calculate the angle of the flight
        final_angle = convert_angle(get_angle(total_x, total_y), 1)
        strings.append("Flight angle: " + str(final_angle) + '\n')

        # Return the crash coordinates
        crash_x, crash_y = get_crash_coordinates(start_lat, start_long, total_x, total_y)
        strings.append("Crash geographical coordinates: " + str(crash_x) + ", " + str(crash_y) + '\n')

        # Return the strings, start and crash coordinates
        return strings, (start_lat, start_long), (crash_x, crash_y)
    except:
        return "Failed to calculate the coordinates"


def get_initial_coordinates(location):
    # Return latitude, longitude of the location
    if location == "Naval Air Station Sand Point":
        return 47.682000, -122.246000
    elif location == "Renton Airfield":
        return 47.500000, -122.216000
    else:
        print("Wrong location, returning (0, 0) geographical coordinates.")
        return 0, 0


def get_height(rate, time):
    return rate*time


def get_plane_distance(speed, time):
    return speed*time


def convert_angle(angle, mode):
    # Standard to Compass
    if mode == 0:
        # Angle 0 on Y-axis (for North) is 90 degrees from angle 0 on X-axis (standard)
        return (90 - angle) % 360
    # Compass to standard
    elif mode == 1:
        # Angle 0 on X-axis (standard) is 90 degrees from angle 0 on Y-axis (for North)
        return (90 + angle) % 360
    else:
        print("Wrong mode, returning input angle.")
        return angle


def extract_distance(angle, distance):

    # If angle is on one of the axis, return the distances directly, to avoid rounding
    if angle == 0:
        return distance, 0
    elif angle == 270:
        return 0, -distance
    elif angle == 180:
        return -distance, 0
    elif angle == 90:
        return 0, distance

    # Calculate the distance from the angle, where angle 0 is on positive X-axis
    x = distance * math.cos(math.radians(angle))
    y = distance * math.sin(math.radians(angle))

    # Return the components
    return x, y


def get_crash_time(height, descent_rate):
    return height/descent_rate


def get_wind_distance(equation, time):
    # Do some splitting or enter values manually

    # Manually:
    speed = 25
    acceleration = -1/720
    power = 2

    # Split:
    split = equation.split("+")
    speed = int(split[1])

    split = split[0].split("*")
    power = int(split[1].split("^")[1])

    split = split[0].split("/")
    acceleration = int(split[0])/int(split[1])

    # Return the value (using integral of velocity to calculate position)
    return acceleration*(1/(power+1))*math.pow(time, power+1) + speed*time


def get_diagonal_distance(x, y):
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2))


def get_angle(x, y):
    # Calculate tangent of the angle
    tan = y/x

    # Calculate the angle itself (using arcus tangent)
    angle = math.degrees(math.atan(math.fabs(tan)))

    # Return the angle
    return angle


def get_crash_coordinates(lat, long, x, y):
    # Constant for calculations
    VAL = 111300

    # Calculate the latitude
    lat = lat + y/VAL

    # Calculate the longitude
    long = long + x / (VAL * math.cos(long))

    # Return the values
    return lat, long
