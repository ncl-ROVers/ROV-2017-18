from flight_data_software.crash_zone_calculator import calculate_coordinates

if __name__ == '__main__':
    strings = calculate_coordinates("Renton Airfield", 184, 93, 10, 43, 64, 6, 270, "-1/720*t^2+25")

    # Print the strings
    for s in strings:
        print(s, end="")
