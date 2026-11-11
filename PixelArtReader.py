from copy import deepcopy
import csv
import cv2
import json
import math
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import re
import shutil
import signal
import sys
import tempfile
import textwrap
import traceback


#The function "get_terminal_dimensions()" will return the number of columns 
#and rows in the console, to allow to properly format the text and dividers.
def get_terminal_dimensions():
    #Detect columns (width) and lines (height)
    #Returns a named tuple; default fallback is (80, 24)
    size = shutil.get_terminal_size(fallback=(80, 24))
    return int(size.columns * 0.75), int(size.lines)
    
#The function "is_valid_positive_non_zero_int_or_float" will validate the data 
#stored in the dictionary obtained from the "json_settings.json" file to make 
#sure it is not "NaN" or "Infinity" (not "math.isfinite(number)") and make sure 
#that the number either an integer or a float and also exclude negative and zero 
#numbers "number <= 0". It will return "True" if the number is a valid
#("else" statement) integer and "False" otherwise ("if" statement).
def is_valid_positive_non_zero_int_or_float(number):
    if not math.isfinite(number) or not isinstance(number, (int, float)) or number <= 0: 
        return False
    else:
        return True

#The function "is_valid_positive_int_or_float" will validate the data stored 
#in the dictionary obtained from the "json_settings.json" file to make sure 
#it is not "NaN" or "Infinity" (not "math.isfinite(number)") and make sure 
#that the number is either a positive integer or a float. It will return 
#"True" if the number is a valid ("else" statement) integer and "False" 
#otherwise ("if" statement).   
def is_valid_positive_int_or_float(number):
    if not math.isfinite(number) or not isinstance(number, (int, float)) or number < 0:
        return False
    else:
        return True

#The function "is_valid_int_or_float" will validate the data stored 
#in the dictionary obtained from the "json_settings.json" file to make sure 
#it is not "NaN" or "Infinity" (not "math.isfinite(number)") and make sure 
#that the number is either an integer or a float. It will return "True" if 
#the number is a valid ("else" statement) integer and "False" otherwise 
#("if" statement).   
def is_valid_int_or_float(number):
    if not math.isfinite(number) or not isinstance(number, (int, float)):
        return False
    else:
        return True

#The function "atomic_save()" will create a temporary JSON file with the updated changes.
#If the files is created successfully, then the files will be swapped. If a problem is 
#encountered, the temp file will be unlinked and an error log will be reported.
def atomic_save(json_settings_dictionary, json_settings_file_path_name):
    #Create a temp file in the same directory
    temp_dir = os.path.dirname(json_settings_file_path_name) or "."
    json_file_descriptor, temp_path = tempfile.mkstemp(dir=temp_dir, text=True)

    try:
        with os.fdopen(json_file_descriptor, "w", encoding="utf-8") as f:
            #Write the default values found in "json_settings_dictionary" in the empty JSON file, 
            #with four space indentations to make it more human-readable.
            json.dump(json_settings_dictionary, f, indent=4)
            #Ensure the data is flushed to hardware.
            f.flush()
            #"os.fsync(f.fileno())" is required to force the OS to physically commit
            #every bit of information to the hardware storage right now, preventing 
            #a situation where an empty file might be created if the computer crashed
            #before the OS finished waiting before committing the file to memory. 
            os.fsync(f.fileno())

        #Swap the files only if the temp file was successfully generated (Atomic security)
        os.replace(temp_path, json_settings_file_path_name)
    except Exception as e:
        #Clean up temp file if something goes wrong BEFORE the swap
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        #The function "write_entry_in_error_log()" will write 
        #the full technical traceback error to the error log.
        write_entry_in_error_log()

        #The function "get_terminal_dimensions()" will return the number of columns 
        #and rows in the console, to allow to properly format the text and dividers.
        columns, lines = get_terminal_dimensions()

        print("\n" + "=" * columns)
        print("CRITICAL ERRROR ENCOUNTERED")
        print("\nDetails:", e)
        print("\n" + "=" * columns)

        #Exit with error code
        sys.exit(1)

#The "clear_screen()" function will clear the CLI screen
#using the appropriate command depending on the operating system.
def clear_screen():
    #'nt' is for Windows, 'posix is for Linux/Raspberry Pi/macOS (else statement)
    os.system('cls' if os.name == 'nt' else 'clear')

#The Signal Interrupt (SIGINT) handler will
#call the "signal_interrupt_signal_handler()" function 
#when the user presses on CTRL + C to exit the app.

#The function "signal_interrupt_signal_handler()" will call
#"sys.exit(0)" to exit the program normally.
def signal_interrupt_signal_handler(sig, frame):
    sys.exit(0)

#The function "write_entry_in_error_log()" will write 
#the full technical traceback error to the error log.
def write_entry_in_error_log():
    with open("ERROR LOG.txt", "a", encoding="utf-8") as error_log:
        error_log.write(f"\n--- Error at {datetime.now()} ---\n")
        traceback.print_exc(file=error_log)

#The function "textwrap_action_strings_in_menu_action_dict()", which takes in 
#a menu action dictionary comprised of one character keys and values made up
#of a three-member tuple (action string, function, function arguments).
#The action strings ("value[0]") will be textwrapped and the modified
#dictionary will be returned.
def textwrap_action_strings_in_menu_action_dict(menu_action_dict):

    #The function "get_terminal_dimensions()" will return the number of columns 
    #and rows in the console, to allow to properly format the text and dividers.
    columns, lines = get_terminal_dimensions()

    for key, value in menu_action_dict.items():
        value[0] = textwrap.fill(value[0], columns)
    return menu_action_dict

#The function "quit_function()" will call
#"sys.exit()" with the exit code "1" meaning
#"success".
def quit_function():
    sys.exit(1)
    
#The function "back_to_main_menu_function()"
#will set the Boolean flags "is_in_submenu" and 
#"is_in_sub_submenu" to "False", which will break the submenu
#"while" loops and return to the main menu.
def back_to_main_menu_function(json_settings_dictionary):
    global is_in_submenu 
    global is_in_sub_submenu
    global is_in_sub_sub_submenu
    is_in_submenu = False
    is_in_sub_submenu = False
    is_in_sub_sub_submenu = False    
    return json_settings_dictionary

def back_to_submenu_function(json_settings_dictionary):
    global is_in_sub_submenu
    is_in_sub_submenu = False  
    return json_settings_dictionary

#The "invalid_menu_choice()" function will be called when the
#user enters invalid input in one of the functions called by
#the "run_menu()" function.
def invalid_menu_choice(json_settings_dictionary):
    input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The function "run_menu" will retrieve and call the function
#at the appropriate choice key in the "menu_actions_dict"
def run_menu(menu_actions_dict, json_settings_dictionary):

    for key, (label, _, _) in menu_actions_dict.items():
        print(f"[{key}] {label}")

    choice = input("\nSelect an option: ").strip().lower()

    #In case the user just pressed "Enter",
    #"json_settings_dictionary" will be returned
    #(no action, this will avoid an error message).
    if choice == "":
        return json_settings_dictionary

    #If you can successfully access the "menu_actions_dict" dictionary
    #with the value of "choice", you then have access to the tuple containing
    #(function label, function, args). Indexing the tuple at the position one
    #gives the function itself, and indexing it at the position 2 gives you the
    #arguments for that function as a list, which must be unpacked with the "*" operator. 
    nested_list = menu_actions_dict.get(choice, [None, invalid_menu_choice, (json_settings_dictionary,)]) 
    return nested_list[1](*nested_list[2])

#The "reset_to_default_setting()" function will reset the setting to its default value
#found while accessing the value of the "json_default_settings_dictionary" dictionary 
#with the key "setting_label_key".
def reset_to_default_setting(setting_label_key, json_settings_dictionary, 
json_default_settings_dictionary, json_settings_file_path_name):
    json_settings_dictionary[setting_label_key] = json_default_settings_dictionary[setting_label_key]
    #The function "atomic_save()" will create a temporary JSON file with the updated changes.
    #If the files is created successfully, then the files will be swapped. If a problem is 
    #encountered, the temp file will be unlinked and an error log will be reported.
    atomic_save(json_settings_dictionary, json_settings_file_path_name)   
    return json_settings_dictionary

#The "toggle_boolean_setting()" function will set the Boolean setting found while accessing
#the "json_settings_dictionary" dictionary with the key "setting_label_key" to the opposite
#value of the current setting ("True" if the current setting is "False" and vice-versa). 
def toggle_boolean_setting(setting_label_key, json_settings_dictionary, 
json_settings_file_path_name):
    if json_settings_dictionary[setting_label_key]:
        json_settings_dictionary[setting_label_key] = False
    else:
        json_settings_dictionary[setting_label_key] = True 
    #The function "atomic_save()" will create a temporary JSON file with the updated changes.
    #If the files is created successfully, then the files will be swapped. If a problem is 
    #encountered, the temp file will be unlinked and an error log will be reported.
    atomic_save(json_settings_dictionary, json_settings_file_path_name)    
    return json_settings_dictionary

#The "set_numeric_setting()" function will set the value of the setting found while accessing
#the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
#value ("setting_value"). 
def set_numeric_setting(setting_value, setting_label_key, json_settings_dictionary, 
json_settings_file_path_name):
    json_settings_dictionary[setting_label_key] = setting_value
    #The function "atomic_save()" will create a temporary JSON file with the updated changes.
    #If the files is created successfully, then the files will be swapped. If a problem is 
    #encountered, the temp file will be unlinked and an error log will be reported.
    atomic_save(json_settings_dictionary, json_settings_file_path_name)   
    return json_settings_dictionary

#The function "return_file_name_suffix_integer()" will extract any sequences 
#of one or more digit characters preceding the ".jpg" file extension and return 
#their integer-casted value. If there were no such digit sequences in the file name,
#then the function will return zero, as the file name must then be the first file 
#name without a numbered suffix ("my_file-.jpg" vs "my_file-0001.jpg").
#This will allow the "sorted()" method to sort padded 
#(e.g., "my_file-0001.jpg") or non-padded (e.g., "my_file-1") file names,
#provided that the numbering pattern is uniform throughout the files.
#This will prevent "my_file-10.jpg" from appearing before "my_file-2.jpg"
#in the sorted list.
def return_file_name_suffix_integer(file_name):
    digit_string_list = re.findall(r"([\d]+).jpg$", file_name)
    if digit_string_list != []:
        return int(digit_string_list[0])
    else:
        return 0

#If the tilt rotation angle (in degrees) isn't equal to zero, meaning that there was a tilt 
#angle, then the "x,y" coordinates of the center of the black squares will be updated using 
#the "get_new_point_coordinates_after_rotation()" function, which does the matrix multiplication 
#between the [2x3] rotation matrix around the center of the canvas, obtained by the 
#"cv2.getRotationMatrix2D" method, and the [x, y, 1]T [1x3] matrix, where T means 
#the transposed matrix ([3x1] instead of [1x3]).          
def get_point_new_coordinates_after_rotation(x, y, cols, rows, angle_degrees):
    #Rotate the image according to OpenCV's documentation,
    #where cols-1 and rows-1 are the coordinate limits (zero-indexed)

    #1. Generate the original rotation matrix around the true center, 
    #where clockwise rotations have a negative angle in mathematics
    M = cv2.getRotationMatrix2D(((cols-1)/2.0, (rows-1)/2.0), angle_degrees, 1.0)
    #The new coordinates are obtained by matrix multiplication of the 
    #rotation matrix M by [[x], [y], [1]] with a shape (3, 1), according 
    #to the following link: https://docs.opencv.org/2.4.13.7/doc/tutorials/imgproc/imgtrans/warp_affine.html.
    new_coordinates = np.matmul(M, np.array([x, y, 1]).reshape((3, 1)))
    
    # #The "x" and "y" coordinates are obtained by accessing the indices 
    # #zero and one of the [2x1] matrix "new_coordinates", respectively,
    # #followed by accessing the matrix element (last "[0]").
    return round(new_coordinates[0][0]), round(new_coordinates[1][0])

#The function "rotate_image()" will rotate the "img"
#numpy array using the "getRotationMatrix2D()" and 
#"warpAffine()" OpenCV methods. 
def rotate_image(img, cols, rows, angle_degrees):
    #Rotate the image according to OpenCV's documentation,
    #where cols-1 and rows-1 are the coordinate limits (zero-indexed)

    #1. Generate the original rotation matrix around the true center, 
    #where clockwise rotations have a negative angle in mathematics
    M = cv2.getRotationMatrix2D(((cols-1)/2.0, (rows-1)/2.0), angle_degrees, 1.0)

    #3. The "warpAffine()" method will apply the rotation transformation to every pixel 
    #of the image. "BORDER_CONSTANT" will fill newly exposed background area with white (255,255,255).
    #"INTER_CUBIC" will allow better results with floating point rotation angles.
    img = cv2.warpAffine(img, M, (cols, rows),  
        borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255),
        flags=cv2.INTER_CUBIC)

    return img

#The function "find_black_squares()" will locate the coordinates 
#of the black squares at the upper corners of the pages and calculate 
#the tilt angle and printing rescaling in order to properly segment 
#the grid cells in the "segment_scan()" function. 
def find_black_squares(
    scan_image,
    JPEG_file_name,
    scans_folder_path,
    excluded_border_pixels,
    bottom_y_coordinate_for_scanning_for_black_squares,
    template_pixel_width_at_300_dpi,
    scan_dpi_correction_factor,
    black_square_side_dimension_in_template,
    horizontal_pixel_distance_between_center_of_the_black_squares_template,
    vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template,
    percentage_of_cell_dimension_that_is_cropped,
    grid_cell_side_dimension_in_template,
    number_of_cells_per_side_of_grid,
    is_grayscale_mode_on):

    #The height and width of the image are stored in 
    #the "rows" and "cols" variables, respectively.
    rows=scan_image.shape[0]
    cols=scan_image.shape[1]
    
    #If the grayscale mode is on, then the JPEG scan 
    #will have been loaded in grayscale mode already, so 
    #no conversion to grayscale will be required.
    #A simple view of the original array will use 
    #the same memory buffer for efficiency, as 
    #the array will not be modified while detecting 
    #the black squares.
    if is_grayscale_mode_on:
        scan_image_gray = scan_image.view()
    else:
        #Convert image from RGB to grayscale (This will be used in 
        #the detection of the black squares at the top of the pages.
        scan_image_copy = scan_image.copy()
        scan_image_gray = cv2.cvtColor(scan_image_copy, cv2.COLOR_RGB2GRAY)

    #The image's numpy array is filtered using the np.where() function to convert pixels
    #lighter than 100 on the grayscale scale to 0 and darker pixels to 1. The rows are added up
    #(summation along the 1 axis) to determine how many non-white pixels there are for a given
    #y coordinate. The same is done for the columns, with a summation along the 0 axis.
    #The first 25 pixels from the edges of the image ("excluded_border_pixels") are 
    #skipped over in order to avoid shadows along these scan edges. The horizontal 
    #center of the page ("round(cols/2)") is used as a right threshold for the 
    #area where the left square is detected, as both squares are located in 
    #the upper outer edges of the page.    
    image_filtered = np.where(scan_image_gray>100, 0, 1)
    
    y_pixels_left_square = np.sum(image_filtered[excluded_border_pixels:bottom_y_coordinate_for_scanning_for_black_squares,
    excluded_border_pixels:round(cols/2)], axis=1)
    
    x_pixels_left_square = np.sum(image_filtered[excluded_border_pixels:bottom_y_coordinate_for_scanning_for_black_squares,
    excluded_border_pixels:round(cols/2)], axis=0)

    #Only the "y" pixels where there are more than 10 "x" pixels under a grayscale value of 100
    #(which amounts to "0.2*black_square_side_dimension_in_template * scan_dpi_correction_factor"
    #when factoring in the dpi resolution correction factor) are retained in "y_pixels_left_square". 
    #The difference between the index of the first and last "y" pixels meeting these requirements 
    #will give the height of the square: (y_pixels_left_square[-1]-y_pixels_left_square[0])
    y_pixels_left_square = np.where(y_pixels_left_square > 0.2*black_square_side_dimension_in_template * scan_dpi_correction_factor)[0]

    #In order to reach the center of the square on the "y" axis, we have to add the amount of pixels needed
    #to reach the topmost coordinate of the "image_filtered" slicing used in the "np.sum()" operation
    #("excluded_border_pixels"), then add the amount of pixels within that slice to reach the topmost 
    #side of the square (y_pixels_left_square[0]), and finally add the half-height of the square
    #(y_pixels_left_square[-1]-y_pixels_left_square[0])/2).
    y_center_left_square = round(excluded_border_pixels + y_pixels_left_square[0] + (y_pixels_left_square[-1]-y_pixels_left_square[0])/2)
    
    x_pixels_left_square = np.where(x_pixels_left_square > 0.2*black_square_side_dimension_in_template * scan_dpi_correction_factor)[0]

    #In order to reach the center of the square on the "x" axis, we have to add the amount of pixels needed
    #to reach the leftmost coordinate of the "image_filtered" slicing used in the "np.sum()" operation
    #("excluded_border_pixels"), then add the amount of pixels within that slice to reach the leftmost 
    #vertical side of the square (x_pixels_left_square[0]), and finally add the half-width of
    #the square (x_pixels_left_square[-1]-x_pixels_left_square[0])/2).
    x_center_left_square = round(excluded_border_pixels + x_pixels_left_square[0] + (x_pixels_left_square[-1]-x_pixels_left_square[0])/2)

    #The equivalent code to the one above is used for the black square in the top right corner.  
    y_pixels_right_square = np.sum(image_filtered[excluded_border_pixels:bottom_y_coordinate_for_scanning_for_black_squares,
    round(cols/2) + 1: cols - excluded_border_pixels], axis=1)
    
    x_pixels_right_square =  np.sum(image_filtered[excluded_border_pixels:bottom_y_coordinate_for_scanning_for_black_squares,
    round(cols/2) + 1: cols - excluded_border_pixels], axis=0)

    y_pixels_right_square = np.where(y_pixels_right_square > 0.2*black_square_side_dimension_in_template * scan_dpi_correction_factor)[0]

    y_center_right_square = round(excluded_border_pixels + y_pixels_right_square[0] + (y_pixels_right_square[-1]-y_pixels_right_square[0])/2)
    
    x_pixels_right_square = np.where(x_pixels_right_square > 0.2*black_square_side_dimension_in_template * scan_dpi_correction_factor)[0]

    #In order to reach the center of the square on the "x" axis, we have to add the amount
    #of pixels needed to reach the leftmost coordinate of the "image_filtered" slicing used
    #in the "np.sum()" operation ("round(cols/2 + 1"), then add the amount of pixels
    #within that slice to reach the leftmost vertical side of the square
    #("x_pixels_right_square[0]"), and finally add the half-width of
    #the square (x_pixels_right_square[-1]-x_pixels_right_square[0])/2).
    x_center_right_square = round(cols/2 + 1 + x_pixels_right_square[0] + (x_pixels_right_square[-1]-x_pixels_right_square[0])/2)

    #The slope (delta y/ deltax) of the line connecting center of the two corner squares is 
    #calculated and will be used to determine the angle used in rotating the canvas and 
    #calculated the corrected "x, y" coordinates for the center of the black squares 
    #when accounted for the rotation around the center of the canvas.
    
    #If the two dots represent the center coordinate of both squares in the tilted image: 
    #       delta x
    #  .------------------  
    #                    | delta y
    #                    .  
    #Then the tangent of the tilt angle theta of the smallest 
    #angle of the right angle triangle would be equal to:
    #tan theta = delta y / delta x
    #theta = arctan(delta y / delta x)
    center_of_black_squares_delta_y = (y_center_right_square - y_center_left_square)
    center_of_black_squares_delta_x = (x_center_right_square-x_center_left_square)
    tilt_angle_radians = np.arctan2(center_of_black_squares_delta_y, center_of_black_squares_delta_x)
    tilt_angle_degrees = np.rad2deg(tilt_angle_radians)
    
    #If the tilt rotation angle (in degrees) isn't equal to zero, meaning that there was a tilt 
    #angle, then the "x,y" coordinates of the center of the black squares will be updated using 
    #the "get_new_point_coordinates_after_rotation()" function, which does the matrix multiplication 
    #between the [2x3] rotation matrix around the center of the canvas, obtained by the 
    #"cv2.getRotationMatrix2D" method, and the [x, y, 1]T [1x3] matrix, where T means 
    #the transposed matrix ([3x1] instead of [1x3]).  
    if tilt_angle_degrees != 0:
        x_center_left_square, y_center_left_square = get_point_new_coordinates_after_rotation(x_center_left_square, y_center_left_square, cols, rows, tilt_angle_degrees)
        x_center_right_square, y_center_right_square = get_point_new_coordinates_after_rotation(x_center_right_square, y_center_right_square, cols, rows, tilt_angle_degrees)
    
    #The scaling factor is calculated with the updated values of "x_center_right_square" and 
    #"x_center_left_square" (if applicable), by dividing the difference between these by the 
    #original pixel horizontal distance between these points in the original template at 300 dpi,
    #times the "scan_dpi_correction_factor" to factor in the scan resolution when calculating the 
    #scaling factor only due to rescaling when printing the page.
    print_scaling_factor = ((x_center_right_square - x_center_left_square)/  
        (horizontal_pixel_distance_between_center_of_the_black_squares_template * scan_dpi_correction_factor))
     
    return (print_scaling_factor, x_center_left_square, y_center_left_square, cols, rows, tilt_angle_degrees, 
        x_pixels_left_square[0], x_pixels_left_square[-1], y_pixels_left_square[0], y_pixels_left_square[-1],
        x_pixels_right_square[0], x_pixels_right_square[-1], y_pixels_right_square[0], y_pixels_right_square[-1])
  
#The function "segment_scan()" will use the coordinates of the black squares 
#obtained from the "find_black_squares()" function to populate the list of 
#65x65 grid "x, y" coordinates of the slicing area at the center of each 
#grid cell "list_of_x_y_cell_segmentation_coordinates".
def segment_scan(scan_image,
    scan_dpi_correction_factor,
    print_scaling_factor, 
    x_center_left_square, 
    y_center_left_square, 
    cols, 
    rows, 
    tilt_angle_degrees, 
    left_x_left_square, 
    right_x_left_square, 
    top_y_left_square, 
    bottom_y_left_square,
    left_x_right_square, 
    right_x_right_square, 
    top_y_right_square, 
    bottom_y_right_square, 
    list_of_x_y_cell_segmentation_coordinates,
    pixel_art_canvas_size_width_number_of_cells,
    pixel_art_canvas_size_height_number_of_cells,
    grid_cell_side_dimension_in_template,
    percentage_of_cell_dimension_that_is_cropped,
    bottom_y_coordinate_for_scanning_for_black_squares,
    vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template,
    is_color_key_being_processed):
        
    #Left black square: A red rectangle is 
    #drawn so as to outline the black square
    cv2.rectangle(scan_image, 
    (left_x_left_square + excluded_border_pixels, top_y_left_square + excluded_border_pixels), 
    (right_x_left_square + excluded_border_pixels, bottom_y_left_square + excluded_border_pixels), 
    (0,0,255),
    3)
    
    #Left black square: A blue rectangle is drawn so as to outline the
    #slicing region of the original "image_filtered" for the "np.sum" operation
    cv2.rectangle(scan_image, 
    (excluded_border_pixels, excluded_border_pixels), 
    (round(cols/2), bottom_y_coordinate_for_scanning_for_black_squares), 
    (255,0,0),
    3)
    
    #Right black square: A red rectangle is 
    #drawn so as to outline the black square
    cv2.rectangle(scan_image, 
    (left_x_right_square + round(cols/2) + 1, top_y_right_square + excluded_border_pixels), 
    (right_x_right_square + round(cols/2) + 1, bottom_y_right_square + excluded_border_pixels), 
    (0,0,255),
    3)
    
    #Right black square: A blue rectangle is drawn so as to outline the
    #slicing region of the original "image_filtered" for the "np.sum" operation
    cv2.rectangle(scan_image, 
    (round(cols/2) + 1, excluded_border_pixels), 
    (cols-excluded_border_pixels, bottom_y_coordinate_for_scanning_for_black_squares), 
    (255,0,0),
    3)
 
    #The left "x" coordinate of the first cell of the 65 x 65 grid is calculated by 
    #subtracting half the black square dimension (corrected for scan dpi resolution
    #and print scaling) from the center "x" coordinate of the left black square.
    left_x_first_cell = (x_center_left_square - 
        (black_square_side_dimension_in_template * scan_dpi_correction_factor * print_scaling_factor)/2)
    #The top "y" coordinate of the first cell of the 65 x 65 grid is calculated by 
    #adding the value of "vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template",
    #(corrected for scan dpi resolution and print scaling) to the center "y" coordinate of the left black square.
    top_y_first_cell = (y_center_left_square + 
        vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template * 
        scan_dpi_correction_factor * print_scaling_factor)    
     
    #The cell dimension corrected for the scan dpi resolution and the print scaling factor 
    #is calculated by multiplying the value of "grid_cell_side_dimension_in_template" by 
    #"scan_dpi_correction_factor" and "print_scaling_factor", respectively.
    corrected_cell_dimension = (grid_cell_side_dimension_in_template * 
        scan_dpi_correction_factor * print_scaling_factor)
    #The width and height of the square area that will be cropped at the center of every 
    #cell is calculated by multiplying the corrected cell dimension by the percentage of 
    #the cell dimension that is cropped ("percentage_of_cell_dimension_that_is_cropped").
    cell_cropping_area_pixel_dimension = corrected_cell_dimension * percentage_of_cell_dimension_that_is_cropped/100
    #The horizontal and vertical spacer required to reach the top-left coordinate of the 
    #cropping area in a given cell is calculated by halving the difference between the 
    #corrected cell dimension and the cell cropping area pixel dimension.
    spacer_until_cell_cropping_point = (corrected_cell_dimension - cell_cropping_area_pixel_dimension)/2

    #The following nested "for" loops will loop over each row of the 65 x 65 grid (outer "i" loop)
    #and then over each cell (columns) of each of these rows (inner "j" loop) and populate the nested 
    #list of cell segmentation coordinates "list_of_x_y_cell_segmentation_coordinates". 
    
    #The nested list of the cell segmentation coordinates 
    #"list_of_x_y_cell_segmentation_coordinates" has the following structure: 
    #[[[[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],    #row 1, scan 1
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],     #row 2, scan 1
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]]],    #row n, scan 1

    # [[[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],    #row 1, scan 2
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],     #row 2, scan 2
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]]]]    #row n, scan 2
    
    #The value of "current_y" is initialized to the top "y" coordinate 
    #of the first cell in the 65x65 grid, and will be incremented by 
    #the value of "corrected_cell_dimension" upon reaching the last 
    #pixel of every line.
    current_y = top_y_first_cell
    cumulative_height_cell_index = 0
    for i in range(number_of_cells_per_side_of_grid):
        #The value of "current_x" is reinitialized to the left "x" coordinate 
        #of the first cell in the 65x65 grid at the start of every new line, 
        #and will be incremented by the value of "corrected_cell_dimension" 
        #at every iteration of the inner "for" loop that travels through 
        #each cell of the given row at the index "i".
        current_x = left_x_first_cell
        cumulative_width_cell_index = 0
        #At the start of every new row of cells, a new empty list is 
        #appended to the current scan at the last index of the list 
        #"list_of_x_y_cell_segmentation_coordinates" to represent 
        #the start of the new row being iterated over in the 
        #inner "for" loop.
        list_of_x_y_cell_segmentation_coordinates[-1].append([])
        for j in range(number_of_cells_per_side_of_grid):
            #The left "x" coordinate of the slice area is calculated by 
            #adding the horizontal spacer between the left edge of the 
            #cell and the cropping area ("spacer_until_cell_cropping_point")
            #to the left "x" coordinate of the current cell.
            left_x = round(current_x + spacer_until_cell_cropping_point)
            #The top "y" coordinate of the slice area is calculated by 
            #adding the vertical spacer between the top edge of the 
            #cell and the cropping area ("spacer_until_cell_cropping_point")
            #to the top "y" coordinate of the current cell.
            top_y = round(current_y + spacer_until_cell_cropping_point)
            #The right "x" coordinate of the slice area is calculated by 
            #adding the number of pixels of the square cropping area dimension
            #("round(cell_cropping_area_pixel_dimension)") to the value of 
            #"left_x" that was calculated above.
            right_x = left_x + round(cell_cropping_area_pixel_dimension)
            #The bottom "y" coordinate of the slice area is calculated by 
            #adding the number of pixels of the square cropping area dimension
            #("round(cell_cropping_area_pixel_dimension)") to the value of 
            #"top_y" that was calculated above.
            bottom_y = top_y + round(cell_cropping_area_pixel_dimension)
            #The top-left and bottom-right "x, y" coordinate tuple list 
            #is appended to the current scan (first "[-1]") of the 
            #current row (second "[-1]") of the nested list 
            #"list_of_x_y_cell_segmentation_coordinates".
            list_of_x_y_cell_segmentation_coordinates[-1][-1].append(
            [(left_x, top_y), (right_x, bottom_y)])
            #If the color key is currently being processed 
            #("is_color_key_being_processed == True") and 
            #the current row being processed is the first one 
            #"cumulative_height_cell_index == 0" and the current 
            #cell isn't the last one on the first row 
            #("cumulative_width_cell_index < number_of_cells_per_side_of_grid - 1"),
            #then the "current_x" value will be incremented by the value of 
            #"corrected_cell_dimension" and the cumulative with cell index 
            #will be incremented by one to move on to the next cell to the right.
            if (is_color_key_being_processed and cumulative_height_cell_index == 0 and
            cumulative_width_cell_index < number_of_cells_per_side_of_grid - 1):
               current_x += corrected_cell_dimension
               cumulative_width_cell_index += 1
            #If the current cell isn't the last one in the current row of the 65x65 grid and it also 
            #isn't the last column in the pixel art canvas, meaning that there are remaining pixels 
            #to be processed on the current row, then the "current_x" value will be incremented by 
            #the value of "corrected_cell_dimension" and the cumulative with cell index will be 
            #incremented by one to move on to the next cell to the right.
            elif (cumulative_width_cell_index < number_of_cells_per_side_of_grid - 1 and         
            cumulative_width_cell_index < pixel_art_canvas_size_width_number_of_cells - 1):
               current_x += corrected_cell_dimension
               cumulative_width_cell_index += 1
            #Otherwise, the code will increment the value of "current_y" by the value of 
            #"corrected_cell_dimension" and the cumulative height cell index will be 
            #incremented by one, provided that the current row isn't the last one in 
            #the 65 x 65 grid nor the pixel art canvas, in which case the value of 
            #"list_of_x_y_cell_segmentation_coordinates" will be returned instead,
            #as there are no more rows to be processed on this scan.
            else:
                if (cumulative_height_cell_index == number_of_cells_per_side_of_grid - 1 or 
                cumulative_height_cell_index == pixel_art_canvas_size_height_number_of_cells - 1):
                    return list_of_x_y_cell_segmentation_coordinates 

                current_y += corrected_cell_dimension
                cumulative_height_cell_index += 1
                break

#The function "find_squares_and_segment_scan()" will first find the
#coordinates of the black squares by calling the "find_black_squares()"
#function. The canvas will be rotated if a tilt was detected, and then 
#the slicing area in each square cell of the 65x65 grid will be appended 
#to the "list_of_x_y_cell_segmentation_coordinates" list in the "segment_scan()"
#function. Finally, the segmentation results will be drawn onto a copy of the scans 
#to convey the results to the user.
def find_squares_and_segment_scan(
    scan_image,
    JPEG_file_name,
    scans_folder_path,
    excluded_border_pixels, 
    bottom_y_coordinate_for_scanning_for_black_squares,
    template_pixel_width_at_300_dpi,
    scan_dpi_correction_factor,
    black_square_side_dimension_in_template,
    horizontal_pixel_distance_between_center_of_the_black_squares_template,
    vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template,
    percentage_of_cell_dimension_that_is_cropped,
    grid_cell_side_dimension_in_template,
    number_of_cells_per_side_of_grid,
    list_of_x_y_cell_segmentation_coordinates,
    pixel_art_canvas_size_width_number_of_cells,
    pixel_art_canvas_size_height_number_of_cells,
    is_grayscale_mode_on,
    brightness_level,
    contrast_level,
    paper_color_filter_threshold,
    is_color_key_being_processed = False):
        
    #The function "find_black_squares()" will locate the coordinates 
    #of the black squares at the upper corners of the pages and calculate 
    #the tilt angle and printing rescaling in order to properly segment 
    #the grid cells in the "segment_scan()" function. 
    (print_scaling_factor, x_center_left_square, y_center_left_square, cols, rows, 
    tilt_angle_degrees, left_x_left_square, right_x_left_square, top_y_left_square, bottom_y_left_square,
    left_x_right_square, right_x_right_square, top_y_right_square, bottom_y_right_square) = find_black_squares(
            scan_image,
            JPEG_file_name,
            scans_folder_path,
            excluded_border_pixels, 
            bottom_y_coordinate_for_scanning_for_black_squares,
            template_pixel_width_at_300_dpi,
            scan_dpi_correction_factor,
            black_square_side_dimension_in_template,
            horizontal_pixel_distance_between_center_of_the_black_squares_template,
            vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template,
            percentage_of_cell_dimension_that_is_cropped,
            grid_cell_side_dimension_in_template,
            number_of_cells_per_side_of_grid,
            is_grayscale_mode_on)
    
    #If the value of "tilt_angle_degrees" isn't zero, meaning that the 
    #canvas needs to be rotated to correct the tilt, then the "if" 
    #statement below will run.
    if tilt_angle_degrees != 0:
        
        #The slice coordinates for the pixels at the center of the page 
        #(excluding those from the left, right, top and bottom margins)
        #are stored in the variable "slice_center_of_page" through the
        #use of the NumPy "np.s_" indexing routine.
        slice_center_of_page = np.s_[
            excluded_border_pixels : rows - excluded_border_pixels,
            excluded_border_pixels : cols - excluded_border_pixels]
            
        #Select everything except the center of the page by
        #creating a Boolean mask initialized to "True" (1) in 
        #every position.
        spatial_mask_margins_of_page = np.ones(scan_image.shape, dtype = bool)
        #Set the values of the indices in the center of the page
        #to "False".
        spatial_mask_margins_of_page[slice_center_of_page] = False
        
        #A new array filled with light gray pixels ("rgb(222, 222, 222)")
        #will be used to replace all pixels found in the excluded margin 
        #of the unrotated image with light gray pixels that will not interfere 
        #with the detection of the black squares, as the grayscale threshold 
        #for the detection of the black squares is 100 (vs 222). This way,
        #the user will know whether the image was rotated, and which pixels 
        #in the excluded border were lost.
        light_gray_array = np.full_like(scan_image, [222])
        #The "scan_image" is sliced to replace the margins by 
        #the corresponding pixels in the light gray array.
        scan_image[spatial_mask_margins_of_page] = light_gray_array[spatial_mask_margins_of_page]
        
        #The function "rotate_image()" will rotate the "img"
        #numpy array using the "getRotationMatrix2D()" and 
        #"warpAffine()" OpenCV methods. 
        scan_image = rotate_image(scan_image, cols, rows, tilt_angle_degrees)
        
        #The function "find_black_squares()" will locate the coordinates 
        #of the black squares at the upper corners of the pages and calculate 
        #the tilt angle and printing rescaling in order to properly segment 
        #the grid cells in the "segment_scan()" function. 
        
        #The function is called once again to locate the 
        #black squares in the rotated canvas.
        (print_scaling_factor, x_center_left_square, y_center_left_square, cols, rows, 
        tilt_angle_degrees, left_x_left_square, right_x_left_square, top_y_left_square, bottom_y_left_square,
        left_x_right_square, right_x_right_square, top_y_right_square, bottom_y_right_square) = find_black_squares(
            scan_image,
            JPEG_file_name,
            scans_folder_path,
            excluded_border_pixels, 
            bottom_y_coordinate_for_scanning_for_black_squares,
            template_pixel_width_at_300_dpi,
            scan_dpi_correction_factor,
            black_square_side_dimension_in_template,
            horizontal_pixel_distance_between_center_of_the_black_squares_template,
            vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template,
            percentage_of_cell_dimension_that_is_cropped,
            grid_cell_side_dimension_in_template,
            number_of_cells_per_side_of_grid,
            is_grayscale_mode_on)
    
    #In order to give as much headspace above the darkest hue to separate 
    #the darkest gray, lighter gray and paper color during the contrast step,
    #it is recommended to bring the brightness level down such that the darkest 
    #hue has an RGB value slightly above true black "rgb(0, 0, 0)" (to avoid 
    #overly darkening the image and reducing the spread between the dark and 
    #light gray colors). When scanning the images drawn with HB lead at the 
    #normal (+0) lightness setting, a brightness level setting of -50 seemed 
    #optimal.
    if brightness_level != 0:
        scan_image = np.clip(scan_image.astype(np.float32) + brightness_level, 0, 255).astype(np.uint8)

    #Possible values to increase contrast: >1 to about 3
    #A contrast level of 1.1-1.2 seemed optimal in increasing 
    #the gap between the darkest gray, the lighter gray and 
    #the page color, after bringing the brightness down by 
    #about 50 to bring the darkest gray close to zero (thus 
    #creating more headspace to spread out the colors).
    if contrast_level != 1 and contrast_level >= 0:
        #In order to change the contrast without affecting the overall brightness, 
        #we need to scale the pixel values around a midpoint (128 for 8-bit images 
        #with values comprised between 0-255). This pushes light pixels closer to 
        #white (255) and dark pixels closer to black (0).
        midpoint = 128.0
        scan_image = np.clip(midpoint + (scan_image.astype(np.float32) - midpoint) * contrast_level, 0, 255).astype(np.uint8)
    
    #Apply a cutoff value that is equal to or slightly lower than the 
    #average RGB value for the page color, after the brightness and contrast 
    #adjustments have been made. This way, the white page color will be set 
    #to 255 and will be much lighter than the darkened light HB lead strokes. 
    #In my case, a cutoff value of 210 worked well.
    if paper_color_filter_threshold != 255:
        scan_image = np.where(scan_image > paper_color_filter_threshold, 245, scan_image)
    
    #The function "segment_scan()" will use the coordinates of the black squares 
    #obtained from the "find_black_squares()" function to populate the list of 
    #65x65 grid "x, y" coordinates of the slicing area at the center of each 
    #grid cell "list_of_x_y_cell_segmentation_coordinates".
    list_of_x_y_cell_segmentation_coordinates = segment_scan(
        scan_image,
        scan_dpi_correction_factor,
        print_scaling_factor, 
        x_center_left_square, 
        y_center_left_square, 
        cols, 
        rows, 
        tilt_angle_degrees, 
        left_x_left_square, 
        right_x_left_square, 
        top_y_left_square, 
        bottom_y_left_square,
        left_x_right_square, 
        right_x_right_square, 
        top_y_right_square, 
        bottom_y_right_square, 
        list_of_x_y_cell_segmentation_coordinates,
        pixel_art_canvas_size_width_number_of_cells,
        pixel_art_canvas_size_height_number_of_cells,
        grid_cell_side_dimension_in_template,
        percentage_of_cell_dimension_that_is_cropped,
        bottom_y_coordinate_for_scanning_for_black_squares,
        vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template,
        is_color_key_being_processed)
     
    #A green square is drawn in the middle of every cell of 
    #the current scan being processed at the last index of 
    #the list "list_of_x_y_cell_segmentation_coordinates" to 
    #indicate the area where the colored pixel information 
    #will be extracted.
    scan_image_copy = scan_image.copy()
    for line in list_of_x_y_cell_segmentation_coordinates[-1]:
        for cell in line:
            cv2.rectangle(scan_image_copy, 
            cell[0], 
            cell[1], 
            (0,255,0),
            2)
    
    JPEG_images_with_rectangles_folder_name = "JPEG images with rectangles"    
    if not os.path.exists(os.path.join(scans_folder_path, JPEG_images_with_rectangles_folder_name)):
        os.makedirs(os.path.join(scans_folder_path, JPEG_images_with_rectangles_folder_name))
   
    (cv2.imwrite(os.path.join(scans_folder_path, JPEG_images_with_rectangles_folder_name, JPEG_file_name.removesuffix(".jpg") +
    ' (segmentation results).jpg'), scan_image_copy))
    
    return list_of_x_y_cell_segmentation_coordinates, scan_image

#The function "populate_list_predicted_colors_for_segmented_cells()"
#will populate the list "list_of_PNG_images" with  all of the predicted 
#RGBA values for each pixels in the final canvas. To do this, it will 
#collate the data from each scan into one cohesive final canvas. 
def populate_list_predicted_colors_for_segmented_cells(
    list_of_PNG_images,
    list_predicted_colors_for_segmented_cells,
    number_of_scans_in_width_of_pixel_art_canvas,
    number_of_scans_in_height_of_pixel_art_canvas,
    number_of_cells_per_side_of_grid,
    pixel_art_canvas_size_width_number_of_cells,
    pixel_art_canvas_size_height_number_of_cells):

    #A new empty list is appended to "list_of_PNG_images"
    #before adding the pixel values for the new image.
    list_of_PNG_images.append([])
    #The "rows_of_scans_index" and "cols_of_scans_index"
    #variables, both initialized to zero, will keep track 
    #of which scan is currently being processed in the grid 
    #of scans making up the final pixel art canvas.
    rows_of_scans_index = 0
    cols_of_scans_index = 0

    #The nested list of predicted color key color tuples for each cell 
    #"list_predicted_colors_for_segmented_cells" has the following structure:

    #[[[(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 1, scan 1
    #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 2, scan 1
    #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)]],  #row n, scan 1 

    # [[(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 1, scan 2
    #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 2, scan 2
    #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)]]], #row n, scan 2 
    
    #Iterate over the different scan indices ("i") in the
    #nested list "list_predicted_colors_for_segmented_cells".
    for i in range(len(list_predicted_colors_for_segmented_cells)):
        #If the current scan index "i" is a multiple of 
        #the number of scans in the pixel art canvas width 
        #("number_of_scans_in_width_of_pixel_art_canvas"),
        #Then it means that the current scan is in the leftmost 
        #column of scans in our grid of scans making up the entire 
        #pixel art canvas.
        
        #Leftmost column of scans
        #0                          1
        #2                          3
        
        #The value of "cols_of_scans_index" will be reset to zero,
        #as this is now the first column of scans.
        if i % number_of_scans_in_width_of_pixel_art_canvas == 0:
            cols_of_scans_index = 0
            #The value of "rows_of_scans_index" shouldn't be incremented 
            #at the first 65x65 grid, as its value is already set to zero 
            #(the first column of scans). The value of "rows_of_scans_index" 
            #is then only incremented after the first scan ("i > 0").
            if i > 0:
                rows_of_scans_index += 1
        #Otherwise, the index of the scan column in the grid of scans 
        #making up the entire pixel art canvas will be incremented by 
        #one, as we are moving to the next scan in the same row of 
        #scans.
        else:
            cols_of_scans_index += 1
        #Iterate over the row indices ("j") of the current scan at the  
        #index ("i") of the nested list "list_predicted_colors_for_segmented_cells".
        for j in range(len(list_predicted_colors_for_segmented_cells[i])):                         
            #The cumulative row index in the pixel art canvas is calculated by adding 
            #the current row index "j" in the current scan to the product of the 
            #number of cells per grid "number_of_cells_per_side_of_grid" by the 
            #current row of scans index ("rows_of_scans_index").
            cumulative_row_index = j + number_of_cells_per_side_of_grid * rows_of_scans_index
            #If the zero-indexed value of "cumulative_row_index" is equal to the 
            #height of the pixel art canvas, then it means that we need to break 
            #out of the "for j" loop, as we are now below the lower edge of the 
            #pixel art canvas (the artist's pixel art creation final canvas size
            #is not necessarily a multiple of 65, which is the number of squares 
            #on each side of the 65x65 grid).
            if cumulative_row_index == pixel_art_canvas_size_height_number_of_cells:
                break
            #If the current scan index "i" is a multiple of 
            #the number of scans in the pixel art canvas width 
            #("number_of_scans_in_width_of_pixel_art_canvas"),
            #Then it means that the current scan is in the leftmost 
            #column of scans in our grid of scans making up the entire 
            #pixel art canvas.
            
            #Leftmost column of scans
            #0                          1
            #2                          3
            
            #A new empty list will be appended to the current image of 
            #the "list_of_PNG_images" at the index "-1" to represent the 
            #new row of pixels in the current row of scans.
            elif i % number_of_scans_in_width_of_pixel_art_canvas == 0:
                list_of_PNG_images[-1].append([])
            #Iterate over each row in the current line.
            for k in range(len(list_predicted_colors_for_segmented_cells[i][j])):
                #The cumulative column index in the pixel art canvas is calculated by adding 
                #the current column index "k" in the current scan to the product of the 
                #number of cells per grid "number_of_cells_per_side_of_grid" by the 
                #current column of scans index ("cols_of_scans_index").
                cumulative_column_index = k + number_of_cells_per_side_of_grid * cols_of_scans_index
                #The current pixel under investigation at the index "[i][j][k]" of the list 
                #of predicted colors for the segmented cells is appended to the current image 
                #at current row ("cumulative_row_index") the index "-1" of the list of pixel 
                #information for the final PNG image ("list_of_PNG_images")
                list_of_PNG_images[-1][cumulative_row_index].append(list_predicted_colors_for_segmented_cells[i][j][k])
                #If the zero-indexed value of "cumulative_column_index" is equal to the 
                #width of the pixel art canvas minus one, then it means that we need to 
                #break out of the "for k" loop, as we have just included the rightmost 
                #pixel for that row of the final pixel art canvas (the artist's pixel 
                #art creation final canvas size is not necessarily a multiple of 65, 
                #which is the number of squares on each side of the 65x65 grid).
                if cumulative_column_index == pixel_art_canvas_size_width_number_of_cells - 1:
                    break
            #If the values of both "cumulative_row_index" and "cumulative_column_index"
            #match those of the last indices in the height and width of the pixel art 
            #canvas, respectively, then it means that we have just finished processing 
            #the last pixel of the last row of pixels of the pixel art image and we 
            #may now return the value of "list_of_PNG_images".
            if (cumulative_row_index == pixel_art_canvas_size_height_number_of_cells - 1 and 
            cumulative_column_index == pixel_art_canvas_size_width_number_of_cells - 1):
                return list_of_PNG_images

#The function "hex_2_rgba_tuple()" extracts a 
#color Hex code from a string argument and returns 
#the corresponding RGBA tuple, where an A channel 
#value of 255 (fully opaque) being included if there 
#was no transparency information in the hex code string.
def hex_2_rgb_tuple(hex_input_string):
    #A search result with a pattern of three or more consecutive characters 
    #that are either a digit 0-9 or a letter among A-F (upper or lowercase) 
    #is captured in the "hex_search_result" variable. If the result wasn't 
    #"None", then the "if" statement below would run. 
    hex_search_result = re.search(r"[a-fA-F0-9]{3,}", hex_input_string)
    if hex_search_result:
        #The string from the group zero of "hex_search_result" is stored in "hex_string"
        hex_string = hex_search_result.group(0)
        #If a 3- or 4-digit shorthand hex form is used, then all of the digits will be duplicated.
        #If the 3- or 6-character hex form has been provided, then the full transparency A channel 
        #"FF" will be suffixed to the end of the hex code.
        if len(hex_string) == 3:
            hex_string = 2 * hex_string[0] + 2 * hex_string[1] + 2 * hex_string[2] + "FF"
        elif len(hex_string) == 4:
            hex_string = 2 * hex_string[0] + 2 * hex_string[1] + 2 * hex_string[2] + 2 * hex_string[3]
        elif len(hex_string) == 6:
            hex_string += "FF"
        #The "hex_string" is sliced in three sections of two characters starting
        #at the index zero and each two-character slice is casted to an integer
        #in base 16, giving the RGB values that are stored in the list "rgb_list".
        rgba_tuple = (int(hex_string[0:2], 16), int(hex_string[2:4], 16), int(hex_string[4:6], 16), int(hex_string[6:8], 16))
        return rgba_tuple

#The function "get_dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values()"
#will extract the RGB colors mapping to the original RGB colors found in the 
#"dict_of_color_key_index_keys_to_rgba_tuple_values". It will return a dictionary 
#of scanned color key tuple keys in string form to values made up of tuples 
#of rgba values corresponding to the colors specified in the CSV file for 
#each color row of the scanned color key, with the last row of the CSV file 
#corresponding to the color mapping to the page color.
def get_dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values(
    cwd,
    press_any_key_string,
    dict_of_color_key_index_keys_to_rgba_tuple_values):
    
    #The following code will populate the dictionary
    #"dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values" 
    #with the RGBA colors for each color found in the CSV color key, 
    #with 1 being the first row of the color key and 65 being the last 
    #possible row of the color key (as the grid only contains 65 rows), 
    #and the color number mapping to the page color (empty cells), being 
    #equal to the last color number plus one. The user can either specify 
    #the colors as RGBA values (one "R", "G", "B" or "A" value per cell 
    #after the color label) or as hex codes.
    
    #For example:
    
    #1,0,0,0,255
    #2,255,0,0,255
    #3,0,255,0,255
    #4,#0000FFFF
    #5,255,255,255,0
    
    #Would indicate:
    
    #1:Black (100% opaque)
    #2:Red (100% opaque)
    #3:Green (100% opaque)
    #4:Blue (100% opaque)
    #5:(100% transparent white color (what was originally the page color)
    dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values = {}
    
    #The list "csv_file_paths" is populated with the CSV file 
    #paths that are found in the current working directory.
    csv_file_paths = ([os.path.join(cwd, file_name) for file_name in os.listdir(cwd) if file_name[-4:] == ".csv"])
        
    csv_file_error_string = "\nPlease create a Comma-Separated Values (CSV) file with \"UTF-8\" encoding, \",\" as a field delimiter, and '\"' as a string delimiter in the same folder as the executable file.\n\nThe CSV file should contain the color key number (1-64) and page color (a color number equal to your last color number plus one) categories in the first column, and then the RGBA values (one R, G, B or A value per cell) or Hex codes afterwards for the color categories that you will be using.\n\nFor example:\n\n1,0,0,0,255\n2,255,0,0,255\n3,0,255,0,255\n4,#0000FFFF\n5,255,255,255,0\n\nWould indicate:\n\n1:Black (100% opaque)\n2:Red (100% opaque)\n3:Green (100% opaque)\n4:Blue (100% opaque)\n5 (page color):(100% transparent white color)\n"

    if len(csv_file_paths) > 1:
        print("\nPlease only include a single Comma-Separated Values (CSV) file with \"UTF-8\" encoding, \",\" as a field delimiter, and '\"' as a string delimiter in the same folder as the executable file.\n\nThe CSV file should contain the color key number (1-64) and page color (a color number equal to your last color number plus one) categories in the first column, and then the RGBA values (one R, G, B or A value per cell) or Hex codes afterwards for the color categories that you will be using.\n\nFor example:\n\n1,0,0,0,255\n2,255,0,0,255\n3,0,255,0,255\n4,#0000FFFF\n5,255,255,255,0\n\nWould indicate:\n\n1:Black (100% opaque)\n2:Red (100% opaque)\n3:Green (100% opaque)\n4:Blue (100% opaque)\n5 (page color):(100% transparent white color)\n")
        input(press_any_key_string)
        sys.exit() 
    elif len(csv_file_paths) == 1:
        with open(csv_file_paths[0], "r", encoding="UTF-8") as f:
            reader = csv.reader(f)
            csv_rows = [row for row in reader]
        try:
            for row in csv_rows:
                #Empty strings are filtered out, as the number of cells containing digits will 
                #allow the code to tell if the provided color was entered as an RGB value or a 
                #hex code.
                row = [element for element in row if element != ""]
                #As the CSV color key index is found in the first column, 
                #we want the length of the row when empty cells have been 
                #filtered out to be at least 2 for them to be included, as 
                #they would then contain RGB or Hex code color information
                #instead of only containing the CSV color index.
                if len(row) > 1 and row[1] != "":
                    #The string form of the RGB tuple for the scanned color key 
                    #at the color index found in the first column at ("[0]") of 
                    #"row" will be stored in the "tuple_string" variable and will 
                    #be used as the key for the new RGB tuple extracted from the 
                    #CSV file when populating the dictionary 
                    #"dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values".
                    #As the CSV color key index ("row[0]") is one-indexed, one must 
                    #be subtracted from it in order to acces the dictionary 
                    #"dict_of_color_key_index_keys_to_rgba_tuple_values".
                    tuple_string = str(dict_of_color_key_index_keys_to_rgba_tuple_values[int(row[0]) - 1])
                    #If the length of the row that where empty strings 
                    #have been filtered out is equal to five, then it 
                    #means that R, G, B, and A values have been provided 
                    #in sequence after the first column.
                    if len(row) == 5:
                        dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values[tuple_string] = (int(row[1]), int(row[2]), int(row[3]), int(row[4]))
                    #If the length of the row that where empty strings 
                    #have been filtered out is equal to four, then it 
                    #means that R, G, and B values have been provided 
                    #in sequence after the first column, so the A value 
                    #will be set to full opacity at 255.
                    elif len(row) == 4:
                        dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values[tuple_string] = (int(row[1]), int(row[2]), int(row[3]), 255)
                    #If the user has input a hexadecimal string, it would likely be at least 3 characters
                    #- 3-digit shorthand where each character is doubled (e.g., "F0C" becomes "FF00CC", which in turn becomes (255, 0, 204)),
                    #- 4-digit shorthand including the alpha channel at the end (e.g., "F0C00" becomes "FF00CC00", which in turn becomes (255, 0, 204, 0)),
                    #- 6-digit normal hex code,
                    #- 8-digit hex code with 2 alpha digits at the end
                    elif len(row) == 2:
                        #The function "hex_2_rgba_tuple()" extracts a 
                        #color Hex code from a string argument and returns 
                        #the corresponding RGBA tuple, where an A channel 
                        #value of 255 (fully opaque) being included if there 
                        #was no transparency information in the hex code string.
                        rgba_tuple = hex_2_rgb_tuple(row[1])
                        #If the "hex_2_rgb_tuple()" function was able to extract 
                        #the RGBA information from the Hex code input string "row[1]",
                        #then the tuple will be added to the dictionary of color key 
                        #tuple strings to CSV file rgb color values.
                        if rgba_tuple:
                            dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values[tuple_string] = rgba_tuple
                            
                        else:
                            #The function "get_terminal_dimensions()" will return the number of columns 
                            #and rows in the console, to allow to properly format the text and dividers.
                            columns, lines = get_terminal_dimensions()
                            error_string = textwrap.fill(f"There was a problem while processing the following color mapping in your CSV file:{str(row)[1:-1]}\n", width=columns)
                            print("")
                            print(error_string)
                            print(csv_file_error_string)
                            input(press_any_key_string)
                            sys.exit()
                    else:
                        #The function "get_terminal_dimensions()" will return the number of columns 
                        #and rows in the console, to allow to properly format the text and dividers.
                        columns, lines = get_terminal_dimensions()
                        error_string = textwrap.fill(f"There was a problem while processing the following color mapping in your CSV file:{str(row)[1:-1]}\n", width=columns)
                        print("")
                        print(error_string)
                        print(csv_file_error_string)
                        input(press_any_key_string)
                        sys.exit()
            return dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values
        except:
            print(csv_file_error_string)
            input(press_any_key_string)
            sys.exit() 

#The function "get_user_settings()" will retrieve the current settings from the 
#"json_settings_dictionary" and store them into some variables that will be returned.
#If any of these values are invalid, the default setting found in the dictionary 
#"json_default_settings_dictionary" will be used instead.
def get_user_settings(json_settings_dictionary, json_default_settings_dictionary):    
       
    scan_dpi = json_settings_dictionary["Scan Resolution in DPI"]
    #Reset dpi to the default value of 200 if 
    #the JSON data is invalid or under 100.
    if not (is_valid_positive_int_or_float(scan_dpi) and scan_dpi >= 100):
        scan_dpi = int(json_default_settings_dictionary["Scan Resolution in DPI"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        scan_dpi = int(scan_dpi)

    brightness_level = json_settings_dictionary["Brightness Level"]
    #Reset brightness level to the default value of 0 
    #(no changes) if the JSON data is invalid. The value 
    #will be casted to an integer in case it was a float value.
    if not is_valid_int_or_float(brightness_level):
        brightness_level = int(json_default_settings_dictionary["Brightness Level"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        brightness_level = int(brightness_level)
        
    contrast_level = json_settings_dictionary["Contrast Level"]
    #Reset contrast level to the default value of 1.0 
    #(no changes) if the JSON data is invalid or negative. 
    if not (is_valid_positive_int_or_float(contrast_level)):
        contrast_level = float(json_default_settings_dictionary["Contrast Level"])
    #Otherwise its value will be casted to an float in case it was a integer value.
    else:
        contrast_level = float(contrast_level)
       
    paper_color_filter_threshold = json_settings_dictionary["Paper Color Filter Threshold"]
    #Reset paper color threshold level to the default value of 255 
    #(no changes) if the JSON data is invalid or negative. The value 
    #will be casted to an integer in case it was a float value.
    if not (is_valid_positive_int_or_float(paper_color_filter_threshold)):
        paper_color_filter_threshold = int(json_default_settings_dictionary["Paper Color Filter Threshold"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        paper_color_filter_threshold = int(paper_color_filter_threshold)

    current_US_Letter_or_A4_format_string = json_settings_dictionary["A4 or US Letter Format Selection"]
    #If the lowercased and stripped value of 
    #"current_US_Letter_or_A4_format_string"
    #isn't in the list '["us letter", "a4"]',
    #then its value will be set to "US Letter".
    if current_US_Letter_or_A4_format_string.lower().strip() not in ["us letter", "a4"]:
        current_US_Letter_or_A4_format_string = json_default_settings_dictionary["A4 or US Letter Format Selection"]
    
    graph_line_pixel_width = json_settings_dictionary["Graph Line Pixel Width"]
    
    #If the value of "graph_line_pixel_width" is invalid, or lesser than or 
    #equal to zero, then the default value of 3 px will be used instead. 
    #The value will be casted to an integer in case it was a float value.
    if not is_valid_positive_non_zero_int_or_float(graph_line_pixel_width):
        graph_line_pixel_width = int(json_default_settings_dictionary["Graph Line Pixel Width"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        graph_line_pixel_width = int(graph_line_pixel_width)

    thicker_graph_line_pixel_width = json_settings_dictionary["Thicker Graph Line Pixel Width"]
    #If the value of "thicker_graph_line_pixel_width" is invalid, or lesser than or 
    #equal to zero, then the default value of 5 px will be used instead. 
    #The value will be casted to an integer in case it was a float value.
    if not is_valid_positive_non_zero_int_or_float(thicker_graph_line_pixel_width):
        thicker_graph_line_pixel_width = int(json_default_settings_dictionary["Thicker Graph Line Pixel Width"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        thicker_graph_line_pixel_width = int(thicker_graph_line_pixel_width)

    thicker_line_every_n_squares = json_settings_dictionary["Number of Squares Between Thicker Lines"]
    #If the value of "thicker_line_every_n_squares" is invalid, or lesser 
    #than zero, then the default value of 5 will be used instead. 
    #The value will be casted to an integer in case it was a float value.
    if not is_valid_positive_int_or_float(thicker_line_every_n_squares):  
        thicker_line_every_n_squares = int(json_default_settings_dictionary["Number of Squares Between Thicker Lines"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        thicker_line_every_n_squares = int(thicker_line_every_n_squares)
      
    graph_line_color_rgb_tuple_string = json_settings_dictionary["Graph Line RGB or Hex Code Color"].lower().strip()
    #The search pattern is comprised of "rgb(", followed by one to three digits, a comma,
    #the presence of zero or one space, a sequence of one to three digits, a comma, the 
    #presence of zero or one space and a final series of one to three digits, followed 
    #by a closing parenthesis.
    rgb_tuple_string_search_hits = re.findall(r"rgb[(]\d{1,3},[ ]?\d{1,3},[ ]?\d{1,3}[)]", 
        graph_line_color_rgb_tuple_string)
    #If the value of "graph_line_color_rgb_tuple_string" wasn't 
    #a properly formatted rgb tuple string (e.g., "rgb(0, 0, 0)"),
    #then the default value of "rgb(200, 200, 200)" will be used 
    #instead.
    if not rgb_tuple_string_search_hits:
        graph_line_color_rgb_tuple_string = json_default_settings_dictionary["Graph Line RGB or Hex Code Color"].lower().strip()

    percentage_of_cell_dimension_that_is_cropped = json_settings_dictionary["Percentage of Cell Dimension that is Cropped"]
    #If the value of "percentage_of_cell_dimension_that_is_cropped" 
    #is invalid, greater than one (100%) or lesser than or equal to 
    #zero, then the default value of 50 (50%) will be used instead. 
    if (not is_valid_positive_non_zero_int_or_float(percentage_of_cell_dimension_that_is_cropped) or 
    percentage_of_cell_dimension_that_is_cropped < 1 or
    percentage_of_cell_dimension_that_is_cropped > 100):
        percentage_of_cell_dimension_that_is_cropped = json_default_settings_dictionary["Percentage of Cell Dimension that is Cropped"]
        
    pixel_art_canvas_size_width_number_of_cells = json_settings_dictionary["Number of Squares in Pixel Art Drawing Width"]
    #If the value of "pixel_art_canvas_size_width_number_of_cells" is invalid, 
    #or lesser than or equal to zero, then the default value of 65 square cells 
    #will be used instead. The value will be casted to an integer in case it 
    #was a float value.
    if not is_valid_positive_non_zero_int_or_float(pixel_art_canvas_size_width_number_of_cells):
        pixel_art_canvas_size_width_number_of_cells = int(json_default_settings_dictionary["Number of Squares in Pixel Art Drawing Width"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        pixel_art_canvas_size_width_number_of_cells = int(pixel_art_canvas_size_width_number_of_cells)

    pixel_art_canvas_size_height_number_of_cells = json_settings_dictionary["Number of Squares in Pixel Art Drawing Height"]
    #If the value of "pixel_art_canvas_size_height_number_of_cells" is invalid, 
    #or lesser than or equal to zero, then the default value of 65 square cells 
    #will be used instead. The value will be casted to an integer in case it 
    #was a float value.
    if not is_valid_positive_non_zero_int_or_float(pixel_art_canvas_size_height_number_of_cells):
        pixel_art_canvas_size_height_number_of_cells = int(json_default_settings_dictionary["Number of Squares in Pixel Art Drawing Height"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        pixel_art_canvas_size_height_number_of_cells = int(pixel_art_canvas_size_height_number_of_cells)

    scaling_factor = json_settings_dictionary["Scaling Factor"]
    #If the value of "scaling_factor" is invalid, or lesser than one, 
    #then the default value of 1 (100% scale) will be used instead. 
    #The value will be casted to an integer in case it was a float value.
    if (not is_valid_positive_non_zero_int_or_float(scaling_factor) or 
    scaling_factor < 1):
        scaling_factor = int(json_default_settings_dictionary["Scaling Factor"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        scaling_factor = int(scaling_factor)
    
    number_of_colors_in_color_key_excluding_white = json_settings_dictionary["Number of Colors Excluding White in Pixel Art Drawing"]
    #If the value of "pixel_art_canvas_size_height_number_of_cells" is invalid, 
    #or lesser than or equal to zero, then the default value of 2 will be used 
    #instead. The value will be casted to an integer in case it was a float value.
    if not is_valid_positive_non_zero_int_or_float(number_of_colors_in_color_key_excluding_white):
        number_of_colors_in_color_key_excluding_white = int(json_default_settings_dictionary["Number of Colors Excluding White in Pixel Art Drawing"])
    #Otherwise its value will be casted to an integer in case it was a float value.
    else:
        number_of_colors_in_color_key_excluding_white = int(number_of_colors_in_color_key_excluding_white)
    
    is_grayscale_mode_on = json_settings_dictionary["Grayscale Mode"]
    #If the value of "is_grayscale_mode_on" isn't a Boolean, 
    #then it will be set to its default value of "False".
    if not isinstance(is_grayscale_mode_on, bool):
        is_grayscale_mode_on = json_default_settings_dictionary["Grayscale Mode"]  
    #If the lowercased and stripped value of 
    #"current_US_Letter_or_A4_format_string" 
    #is equal to "a4", then the value of 
    #"is_A4_format_selected" will be set 
    #to "True" and the template pixel 
    #dimensions will be set to those of 
    #an A4 page at 300 dpi.    
    if current_US_Letter_or_A4_format_string.lower().strip() == "a4":
        is_A4_format_selected = True
        template_pixel_width_at_300_dpi = 2480
        template_pixel_height_at_300_dpi = 3508   
    #Otherwise, the value of "current_US_Letter_or_A4_format_string"
    #will be set to "US Letter" (in case it didn't correspond to 
    #A4 nor US Letter), the value of "is_A4_format_selected"
    #will be set to "False" and the template pixel dimensions 
    #will be set to those of a US Letter page at 300 dpi.
    else:
        current_US_Letter_or_A4_format_string = "US Letter"
        is_A4_format_selected = False
        template_pixel_width_at_300_dpi = 2550
        template_pixel_height_at_300_dpi = 3300

    #The variable "scan_dpi_correction_factor" will hold the 
    #correction factor to deal with cases where the pages 
    #were scanned at a resolution other than 300 dpi, as 
    #all of the pixel measurements in the template were 
    #done at 300 dpi. It is calculated by dividing the 
    #user's scanning resolution in dpi by the default 
    #300.
    scan_dpi_correction_factor = scan_dpi/300

    #The variable "bottom_y_coordinate_for_scanning_for_black_squares" will hold 
    #the bottom "y" coordinate representing the lower boundary where the black 
    #squares will be screened for in the scans. Setting this value to a higher 
    #pixel value will allow more flexibility when detecting the black squares 
    #on scans of pages that were scaled down while printing, resulting in the 
    #black squares to be pushed down on the page. 
    bottom_y_coordinate_for_scanning_for_black_squares = round(
        0.1 *  template_pixel_height_at_300_dpi  * scan_dpi_correction_factor)

    #===================================================================================
    #TEMPLATE DIMENSIONS CALCULATION
    #===================================================================================    
    #The left "x" coordinate of the left black square in the template is set to the 
    #value of the quarter inch margin in pixels (at 300 dpi, this means 75 pixels).
    left_x_left_black_square_in_template = quarter_inch_margin_pixels_at_300_dpi
    #The right "x" coordinate of the left black square in the template is set to the 
    #sum of the left "x" coordinate of the black square, plus the black square dimension 
    #in pixels in the template.
    right_x_left_black_square_in_template =  (left_x_left_black_square_in_template + 
        black_square_side_dimension_in_template)
    #The left "x" coordinate of the right black square in the template is calculated 
    #by subtracting the quarter inch margins in pixels (at 300 dpi) and the black 
    #square dimension in pixels in the template from the total width of the canvas 
    #at 300 dpi.
    left_x_right_black_square_in_template = (template_pixel_width_at_300_dpi - 
        quarter_inch_margin_pixels_at_300_dpi - black_square_side_dimension_in_template)
    #The right "x" coordinate of the right black square in the template is set to the 
    #sum of the left "x" coordinate of the black square, plus the black square dimension 
    #in pixels in the template.
    right_x_right_black_square_in_template = (left_x_right_black_square_in_template + 
        black_square_side_dimension_in_template)
    #The top "y" coordinate of the left black square in the template is set to the
    #value of the quarter inch margin in pixels (at 300 dpi, this means 75 pixels).  
    top_y_black_squares_in_template = quarter_inch_margin_pixels_at_300_dpi
    bottom_y_black_squares_in_template = (quarter_inch_margin_pixels_at_300_dpi + 
        black_square_side_dimension_in_template)

    #The total side dimension for the 65x65 grid is calculated by subtracting two 
    #times the quarter inch margins at 300 dpi (75 px * 2 == 150 px) from the 
    #template canvas width at 300 dpi. This way, the grid occupies the maximum 
    #available width, while allowing sufficient margins for conveniently printing 
    #the grids.
    total_grid_side_dimension_in_template = (template_pixel_width_at_300_dpi - 
        2*quarter_inch_margin_pixels_at_300_dpi)

    #The grid cell size dimension in the template (the side dimension of each 
    #of the squares making up the 65x65 grid) is calculated by dividing the 
    #value of "total_grid_side_dimension_in_template" by the number of cells 
    #in the grid (65).
    grid_cell_side_dimension_in_template = total_grid_side_dimension_in_template/number_of_cells_per_side_of_grid

    #The left "x" coordinate of the first cell in the 65x65 grid is set to 
    #the value of "left_x_left_black_square_in_template", which is itself 
    #equal to the quarter inch margins in the template (at 300 dpi, this is 75 px).
    grid_left_x_in_template = left_x_left_black_square_in_template

    #The top "y" coordinate of the 65x65 grid in the template is calculated by 
    #subtracting the quarter inch margin at 300 dpi (75 px) and the side dimension 
    #of the 65x65 grid itself ("total_grid_side_dimension_in_template") from the 
    #canvas height in the template at 300 dpi ("template_pixel_height_at_300_dpi").
    #The grid is placed at the lowest point on the page to allow the users more 
    #flexibility in setting a value of "bottom_y_coordinate_for_scanning_for_black_squares"
    #that is low enough to accomodate any scaling down of the pages when printing, thus 
    #allowing the black squares to still be detected with the same settings.
    grid_top_y_in_template = (template_pixel_height_at_300_dpi - 
        quarter_inch_margin_pixels_at_300_dpi - total_grid_side_dimension_in_template)
    #The horizontal distance between the center of the two black squares is calculated 
    #by subtracting two times the quarter-inch margin (75 px * 2 = 150 px) and the width 
    #of one black square (as we are measuring from the center of the squares, thereby 
    #excluding the outer halves of the squares) from the width of the canvas.
    horizontal_pixel_distance_between_center_of_the_black_squares_template = (
        template_pixel_width_at_300_dpi - 2*quarter_inch_margin_pixels_at_300_dpi - 
        black_square_side_dimension_in_template)
    #The center "y" coordinate of the black squares on the template is calculated by 
    #adding half the black square side dimension to the top "y" coordinate of the 
    #black squares.
    black_squares_center_y_template = top_y_black_squares_in_template + black_square_side_dimension_in_template/2
    #The vertical pixel distance between the center "y" coordinate of the black squares 
    #and the top of the 65x65 grid is calculated by subtracting the center "y" coordinate 
    #of the black squares ("black_squares_center_y_template") from the grid top "y" 
    #coordinate ("grid_top_y_in_template").
    vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template = (
        grid_top_y_in_template - black_squares_center_y_template)

    return (
        is_A4_format_selected,
        graph_line_pixel_width,
        thicker_graph_line_pixel_width,
        thicker_line_every_n_squares,
        graph_line_color_rgb_tuple_string,
        percentage_of_cell_dimension_that_is_cropped,
        pixel_art_canvas_size_width_number_of_cells,
        pixel_art_canvas_size_height_number_of_cells,
        scaling_factor,
        number_of_colors_in_color_key_excluding_white,
        is_grayscale_mode_on,
        scan_dpi,
        template_pixel_width_at_300_dpi,
        template_pixel_height_at_300_dpi,
        current_US_Letter_or_A4_format_string,
        scan_dpi_correction_factor,
        bottom_y_coordinate_for_scanning_for_black_squares,
        brightness_level,
        contrast_level,
        paper_color_filter_threshold,
        left_x_left_black_square_in_template,
        right_x_left_black_square_in_template,
        left_x_right_black_square_in_template,
        right_x_right_black_square_in_template,
        top_y_black_squares_in_template,
        bottom_y_black_squares_in_template,
        total_grid_side_dimension_in_template,
        grid_cell_side_dimension_in_template,
        grid_left_x_in_template,
        grid_top_y_in_template,
        horizontal_pixel_distance_between_center_of_the_black_squares_template,
        black_squares_center_y_template,
        vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template,
    )

#The function "generate_grid_pdf()" will 
#generate the printable 65x65 graph paper 
#PDF template.
def generate_grid_pdf(json_settings_dictionary, 
        json_default_settings_dictionary):
    #The function "get_user_settings()" will retrieve the current settings from the 
    #"json_settings_dictionary" and store them into some variables that will be returned.
    #If any of these values are invalid, the default setting found in the dictionary 
    #"json_default_settings_dictionary" will be used instead.
    (is_A4_format_selected,
    graph_line_pixel_width,
    thicker_graph_line_pixel_width,
    thicker_line_every_n_squares,
    graph_line_color_rgb_tuple_string,
    percentage_of_cell_dimension_that_is_cropped,
    pixel_art_canvas_size_width_number_of_cells,
    pixel_art_canvas_size_height_number_of_cells,
    scaling_factor,
    number_of_colors_in_color_key_excluding_white,
    is_grayscale_mode_on,
    scan_dpi,
    template_pixel_width_at_300_dpi,
    template_pixel_height_at_300_dpi,
    current_US_Letter_or_A4_format_string,
    scan_dpi_correction_factor,
    bottom_y_coordinate_for_scanning_for_black_squares,
    brightness_level,
    contrast_level,
    paper_color_filter_threshold,
    left_x_left_black_square_in_template,
    right_x_left_black_square_in_template,
    left_x_right_black_square_in_template,
    right_x_right_black_square_in_template,
    top_y_black_squares_in_template,
    bottom_y_black_squares_in_template,
    total_grid_side_dimension_in_template,
    grid_cell_side_dimension_in_template,
    grid_left_x_in_template,
    grid_top_y_in_template,
    horizontal_pixel_distance_between_center_of_the_black_squares_template,
    black_squares_center_y_template,
    vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template) = (
        get_user_settings(json_settings_dictionary, 
        json_default_settings_dictionary))

    #===================================================================================
    #DRAWING TEMPLATE BLACK SQUARES
    #===================================================================================
    grid_template = Image.new(mode="RGB", 
        size=(template_pixel_width_at_300_dpi, template_pixel_height_at_300_dpi),
        color="rgb(255, 255, 255)")

    grid_template_editable = ImageDraw.Draw(grid_template)

    #Black squares are drawn in the top corners of the page, for the segmentation
    #code to be able to align the pages accurately. As such, the outer vertical 
    #edges of the corner squares line up with the center "x" coordinate of the 
    #first and last vertical lines of the grid.
    grid_template_editable.rectangle([(left_x_left_black_square_in_template, top_y_black_squares_in_template),
    (right_x_left_black_square_in_template, bottom_y_black_squares_in_template)], fill="Black")

    grid_template_editable.rectangle([(left_x_right_black_square_in_template, top_y_black_squares_in_template), 
    (right_x_right_black_square_in_template, bottom_y_black_squares_in_template)], fill="Black")

    #===================================================================================
    #DRAWING TEMPLATE GRID
    #===================================================================================
    current_line_x_template = grid_left_x_in_template
    current_line_y_template = grid_top_y_in_template
    line_x_coordinates_template = []
    line_y_coordinates_template = []
    #The list of "x" coordinates where the vertical lines will 
    #be drawn is stored in the "line_x_coordinates_template" list.
    for i in range(number_of_cells_per_side_of_grid + 1):
        line_x_coordinates_template.append(current_line_x_template)
        line_y_coordinates_template.append(current_line_y_template)
        current_line_x_template += grid_cell_side_dimension_in_template
        current_line_y_template += grid_cell_side_dimension_in_template
      
    #Thicker lines are drawn whenever the current line number is a multiple of 
    #"thicker_line_every_n_squares" (if it isn't equal to zero).
    for i in range(len(line_x_coordinates_template)):    
        #If the variable "thicker_line_every_n_squares" isn't set to zero and if the
        #current line number is a multiple of "thicker_line_every_n_squares" (remainder
        #of zero after a modulus operation), then a thicker horizontal line is drawn,
        #with a line width equal to "thicker_graph_line_pixel_width".
        if thicker_line_every_n_squares != 0 and i%thicker_line_every_n_squares == 0:
            grid_template_editable.line([(line_x_coordinates_template[i], line_y_coordinates_template[0]),
            (line_x_coordinates_template[i], line_y_coordinates_template[-1])], 
            fill = graph_line_color_rgb_tuple_string,
            width = thicker_graph_line_pixel_width)
        #If there are to be no thicker lines every certain number of squares
        #("thicker_line_every_n_squares == 0") or if the current line isn't one
        #of them (i%thicker_line_every_n_squares != 0), then a horizontal line
        #with a normal line width ("graph_line_pixel_width") is drawn.
        elif thicker_line_every_n_squares == 0 or i%thicker_line_every_n_squares != 0:
            grid_template_editable.line([(line_x_coordinates_template[i], line_y_coordinates_template[0]),
            (line_x_coordinates_template[i], line_y_coordinates_template[-1])], 
            fill = graph_line_color_rgb_tuple_string,
            width = graph_line_pixel_width)
    #Similar code is applied for the horizontal lines of the grid.
    for i in range(len(line_y_coordinates_template)):
        #If the variable "thicker_line_every_n_squares" isn't set to zero and if the
        #current line number is a multiple of "thicker_line_every_n_squares" (remainder
        #of zero after a modulus operation), then a thicker horizontal line is drawn,
        #with a line width equal to "thicker_graph_line_pixel_width".
        if thicker_line_every_n_squares == 0 or i%thicker_line_every_n_squares != 0:
            grid_template_editable.line([(line_x_coordinates_template[0], line_y_coordinates_template[i]),
            (line_x_coordinates_template[-1], line_y_coordinates_template[i])],
            fill = graph_line_color_rgb_tuple_string, 
            width = graph_line_pixel_width)
        #If there are to be no thicker lines every certain number of squares
        #("thicker_line_every_n_squares == 0") or if the current line isn't one
        #of them (i%thicker_line_every_n_squares != 0), then a horizontal line
        #with a normal line width ("graph_line_pixel_width") is drawn.
        elif thicker_line_every_n_squares != 0 and i%thicker_line_every_n_squares == 0:
            grid_template_editable.line([(line_x_coordinates_template[0], line_y_coordinates_template[i]),
            (line_x_coordinates_template[-1], line_y_coordinates_template[i])],
            fill = graph_line_color_rgb_tuple_string, 
            width = thicker_graph_line_pixel_width)
          
    grid_template.save(os.path.join(cwd, f"Grid Template ({current_US_Letter_or_A4_format_string}).pdf"), 
        quality=100, resolution=300)
     
    #The function "get_terminal_dimensions()" will return the number of columns 
    #and rows in the console, to allow to properly format the text and dividers.
    columns, lines = get_terminal_dimensions()
    
    print("\n" + textwrap.fill(f"Successfully generated your {current_US_Letter_or_A4_format_string} graph paper PDF document in the 'PixelArtReader' folder.", width = columns))
    
    input(press_any_key_string)
    
    return json_settings_dictionary

#The "generate_png_images()" function will generate 
#pixel art PNG images from the hand-drawn scans.
def generate_png_images(json_settings_dictionary, 
        json_default_settings_dictionary):
    #The function "get_user_settings()" will retrieve the current settings from the 
    #"json_settings_dictionary" and store them into some variables that will be returned.
    #If any of these values are invalid, the default setting found in the dictionary 
    #"json_default_settings_dictionary" will be used instead.
    (is_A4_format_selected,
    graph_line_pixel_width,
    thicker_graph_line_pixel_width,
    thicker_line_every_n_squares,
    graph_line_color_rgb_tuple_string,
    percentage_of_cell_dimension_that_is_cropped,
    pixel_art_canvas_size_width_number_of_cells,
    pixel_art_canvas_size_height_number_of_cells,
    scaling_factor,
    number_of_colors_in_color_key_excluding_white,
    is_grayscale_mode_on,
    scan_dpi,
    template_pixel_width_at_300_dpi,
    template_pixel_height_at_300_dpi,
    current_US_Letter_or_A4_format_string,
    scan_dpi_correction_factor,
    bottom_y_coordinate_for_scanning_for_black_squares,
    brightness_level,
    contrast_level,
    paper_color_filter_threshold,
    left_x_left_black_square_in_template,
    right_x_left_black_square_in_template,
    left_x_right_black_square_in_template,
    right_x_right_black_square_in_template,
    top_y_black_squares_in_template,
    bottom_y_black_squares_in_template,
    total_grid_side_dimension_in_template,
    grid_cell_side_dimension_in_template,
    grid_left_x_in_template,
    grid_top_y_in_template,
    horizontal_pixel_distance_between_center_of_the_black_squares_template,
    black_squares_center_y_template,
    vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template) = (
        get_user_settings(json_settings_dictionary, 
        json_default_settings_dictionary))

    #===================================================================================
    #SEGMENTATION CODE
    #===================================================================================
    #The function "get_terminal_dimensions()" will return the number of columns 
    #and rows in the console, to allow to properly format the text and dividers.
    columns, lines = get_terminal_dimensions()

    #If either the "Scans" subfolder is missing, or if it doesn't contain any JPEG scans,
    #then the folder will be created if needed and the code will exit the application while 
    #printing the "missing_scans_string" on-screen.
    missing_scans_string = "\n" + textwrap.fill("Please add one or more JPEG scans in the 'Scans' subfolder of the PixelArtReader folder and launch the application again.", width=columns) + "\n"     

    if not os.path.exists(scans_folder_path):
        os.mkdir(scans_folder_path) 
        print(missing_scans_string)
        input(press_any_key_string)
        sys.exit(1)
            
    #The list "JPEG_file_names" is populated with the ".jpg" file names in
    #the "Scans" folder.The list is sorted in ascending order using the 
    #key provided by the function "return_file_name_suffix_integer()",
    #which returns the integer-casted value of the sequence of one or more digits 
    #preceding the ".jpg" file extension, or zero if there are no such sequences
    #in the file name. This will allow the "sorted()" method to sort padded 
    #(e.g., "my_file-0001.jpg") or non-padded (e.g., "my_file-1") file names,
    #provided that the numbering pattern is uniform throughout the files.
    #This will prevent "my_file-10.jpg" from appearing before "my_file-2.jpg"
    #in the sorted list.
    JPEG_file_names = ([file_name for file_name in sorted(os.listdir(scans_folder_path), 
        key=return_file_name_suffix_integer) if file_name[-4:] == ".jpg"])

    if JPEG_file_names == []:
        print(missing_scans_string)
        input(press_any_key_string)
        sys.exit(1)

    #If either the "Color Key" subfolder within the "Scans" subfolder is missing, or 
    #if it doesn't contain any JPEG scans, then the folder will be created if needed 
    #and the code will exit the application while printing the "missing_color_key_string" 
    #on-screen.
    missing_color_key_string = "\n" + textwrap.fill("Please add a single JPEG scan of your color key (up to 65 colors, one per row, with the five first cells in each row being colored in with your chosen color) in the 'Color Key' subfolder of the 'Scans' subfolder of the PixelArtReader folder and launch the application again.", width=columns) + "\n"     

    if not os.path.exists(color_key_folder_path):
        os.makedirs(color_key_folder_path) 
        print(missing_color_key_string)
        input(press_any_key_string)
        sys.exit(1)
            
    #The list "color_key_JPEG_file_names" is populated with the ".jpg" file names in
    #the "Color Key" subfolder of the "Scans" subfolder.The list is sorted in ascending 
    #order using the key provided by the function "return_file_name_suffix_integer()",
    #which returns the integer-casted value of the sequence of one or more digits 
    #preceding the ".jpg" file extension, or zero if there are no such sequences
    #in the file name. This will allow the "sorted()" method to sort padded 
    #(e.g., "my_file-0001.jpg") or non-padded (e.g., "my_file-1") file names,
    #provided that the numbering pattern is uniform throughout the files.
    #This will prevent "my_file-10.jpg" from appearing before "my_file-2.jpg"
    #in the sorted list.
    color_key_JPEG_file_names = ([file_name for file_name in sorted(os.listdir(color_key_folder_path), 
        key=return_file_name_suffix_integer) if file_name[-4:] == ".jpg"])

    if len(color_key_JPEG_file_names) != 1:
        print(missing_color_key_string)
        input(press_any_key_string)
        sys.exit(1)

    #If there are insufficient JPEG scans in the "Scans" folder to make up the entire 
    #pixel art canvas, then the code will exit the application while printing the 
    #"insufficient_JPEG_scans_string" on-screen.

    #The number of scans required to make up the width of the pixel art canvas is calculated by 
    #dividing the total number of pixels in the width of the pixel art canvas by the number of 
    #cells in each side of the 65x65 grid (which each represent one pixel), and then rounding 
    #up the result, as even partially filling a grid will require an entire grid.
    number_of_scans_in_width_of_pixel_art_canvas = math.ceil(pixel_art_canvas_size_width_number_of_cells/number_of_cells_per_side_of_grid)
    number_of_scans_in_height_of_pixel_art_canvas = math.ceil(pixel_art_canvas_size_height_number_of_cells/number_of_cells_per_side_of_grid)
    example_pixel_width = 170
    example_pixel_height = 96
    insufficient_JPEG_scans_string = "\n" + textwrap.fill(f"There are not enough 65x65 grid scans to make up the entire {pixel_art_canvas_size_width_number_of_cells}x{pixel_art_canvas_size_height_number_of_cells} pixel art canvas. Please add all of the scans to the 'Scans' subfolder of the PixelArtReader folder and launch the application again.", width=columns) + "\n"     
    order_of_pixel_art_canvas_scans_string = textwrap.fill(f"You need to number the JPEG scans in a sequential way, with the {number_of_cells_per_side_of_grid}x{number_of_cells_per_side_of_grid} grids making up the width being scanned first, before moving on to the next row of panels. For example, for a {example_pixel_width}x{example_pixel_height} pixel art canvas, the files would be ordered as follows:", width=columns) + "\n" 
    canvas_scans_order_example_string = f"""Pixel At Canvas Width:\t\t{example_pixel_width} squares\t({int(math.ceil(example_pixel_width/number_of_cells_per_side_of_grid))} {number_of_cells_per_side_of_grid}x{number_of_cells_per_side_of_grid} grids)
    Pixel At Canvas Height:\t\t{example_pixel_height} squares\t({int(math.ceil(example_pixel_height/number_of_cells_per_side_of_grid))} {number_of_cells_per_side_of_grid}x{number_of_cells_per_side_of_grid} grids)

    Here is the order in which the scans will 
    be processed by the code to make up your 
    complete pixel art image: 

    1 2 3
    4 5 6

    So the file numbering would be as follows, 
    when scanned sequentially by your scanner:

    Scan.jpg        Scan-0001.jpg       Scan-0002.jpg
    Scan-0003.jpg   Scan-0004.jpg       Scan-0005.jpg"""
    if (len(JPEG_file_names) < number_of_scans_in_width_of_pixel_art_canvas * 
    number_of_scans_in_height_of_pixel_art_canvas):     
        print(insufficient_JPEG_scans_string)
        print(order_of_pixel_art_canvas_scans_string)
        print(canvas_scans_order_example_string)
        input(press_any_key_string)
        sys.exit(1)

    #The nested list of the cell segmentation coordinates 
    #"list_of_x_y_cell_segmentation_coordinates" has the following structure: 
    #[[[[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],    #row 1, scan 1
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],     #row 2, scan 1
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]]],    #row n, scan 1

    #An extra empty list needs to be added here, even though there will only be one color key scan 
    #being processed, as the function "find_squares_and_segment_scan()" will be called for both 
    #the color key and the pixel art scans themselves, which may span many individual scans, 
    #hence the presence of an extra nesting level in the list.
    color_key_list_of_x_y_cell_segmentation_coordinates = [[]]

    #The image is loaded using the "cv2.imread" method.
    if is_grayscale_mode_on:
        color_key_scan_image = cv2.imread(os.path.join(color_key_folder_path, color_key_JPEG_file_names[0]), flags=cv2.IMREAD_GRAYSCALE)  
    else:
        color_key_scan_image = cv2.imread(os.path.join(color_key_folder_path, color_key_JPEG_file_names[0]), flags=cv2.IMREAD_COLOR_BGR)  

    #The function "find_squares_and_segment_scan()" will first find the
    #coordinates of the black squares by calling the "find_black_squares()"
    #function. The canvas will be rotated if a tilt was detected, and then 
    #the slicing area in each square cell of the 65x65 grid will be appended 
    #to the "list_of_x_y_cell_segmentation_coordinates" list in the "segment_scan()"
    #function. Finally, the segmentation results will be drawn onto a copy of the scans 
    #to convey the results to the user.
    color_key_list_of_x_y_cell_segmentation_coordinates, color_key_scan_image = find_squares_and_segment_scan(
        color_key_scan_image,
        color_key_JPEG_file_names[0],
        color_key_folder_path,
        excluded_border_pixels, 
        bottom_y_coordinate_for_scanning_for_black_squares,
        template_pixel_width_at_300_dpi,
        scan_dpi_correction_factor,
        black_square_side_dimension_in_template,
        horizontal_pixel_distance_between_center_of_the_black_squares_template,
        vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template,
        percentage_of_cell_dimension_that_is_cropped,
        grid_cell_side_dimension_in_template,
        number_of_cells_per_side_of_grid,
        color_key_list_of_x_y_cell_segmentation_coordinates,
        #As only the first five cells per row will be 
        #segmented for extracting the RGB values of the 
        #scanned color key, a value of 5 is passed in.
        5,
        #Up to 65 color key colors may be included 
        #in the scanned color key (one per row), 
        #hence the value of  "number_of_cells_per_side_of_grid"
        #being passed in, which is the number of rows in the 
        #65x65 grid.        
        number_of_cells_per_side_of_grid,
        is_grayscale_mode_on,
        brightness_level,
        contrast_level,
        paper_color_filter_threshold,
        #The Boolean argument of the "find_squares_and_segment_scan()"
        #function, default initialized to "False" will allow the cells 
        #of the sixth column onwards of the last row of the color key 
        #to be sliced in order to include some white page color to the 
        #color key. 
        True
    )

    #The dictionary of color key index keys to RGB tuple values 
    #"dict_of_color_key_index_keys_to_rgba_tuple_values" will hold
    #the color palette that was extracted from the first five cells 
    #of each row from the color key scan, with the final color at the 
    #last index corresponding to the page color the sixth cell onwards 
    #on the first row.
    dict_of_color_key_index_keys_to_rgba_tuple_values = {}
    #The dictionary of color key index keys to nested list of average R, G, and B
    #values extracted from each of the five cells of each color from the color key,
    #with the exception of the paper color that was extracted from the sixth cell 
    #onwards on the first row.  
    dict_of_color_key_index_keys_to_nested_list_of_average_r_g_b_values = {}
    #The outer loop in the nested "for" loop below will run for a total number of times 
    #equal to the number of colors in the color key, minus the page color that will be 
    #extracted from the first row of cells as well.
    for i in range(number_of_colors_in_color_key_excluding_white):
        #The number of cells to slice in the current row is calculated by 
        #measuring the length of the nested list "color_key_list_of_x_y_cell_segmentation_coordinates",
        #which is first indexed with zero to indicate the first and only color key scan in the nested 
        #list, then at the index "i" to indicate the current row index in the color key scan.
        number_of_cells_to_slice_in_current_color_key_row = len(color_key_list_of_x_y_cell_segmentation_coordinates[0][i])
        #The inner "for" loop will iterate over all of the cells that are to be sliced.
        for j in range(number_of_cells_to_slice_in_current_color_key_row):
            #If the current color key row is the first one at the index zero 
            #and the current cell is the sixth one onwards, then the dictionary 
            #key will be the total number of colors (excluding white).
            #This way, the page color will always be the last color, since the 
            #user didn't need to color it in.
            if i == 0 and j > 4:
                dictionary_key = number_of_colors_in_color_key_excluding_white
            #Otherwise, the dictionary key is set to the value of 
            #the current color key row index "i".
            else:
                dictionary_key = i

            #The slice coordinates for the pixels at the center of the current cell 
            #are stored in the variable "slice_center_of_current_cell" through the
            #use of the NumPy "np.s_" indexing routine.
            
            #The indexing of "color_key_list_of_x_y_cell_segmentation_coordinates" works as follows:
            #"[0]": The first scan data in the nested list (there is only one color key, so the first index zero is selected)
            #"[i]": The outer loop iteration index cycling over all of the rows.
            #"[j]": The inner loop iteration index cycling over all of the cells in the current row.
            #The two last indices determine which coordinate is taken when indexing the sublist of two 
            #"x, y" coordinate tuples: [(left_x_1, top_y_1), (right_x_1, bottom_y_1)]
            slice_center_of_current_cell = np.s_[
                color_key_list_of_x_y_cell_segmentation_coordinates[0][i][j][0][1] : color_key_list_of_x_y_cell_segmentation_coordinates[0][i][j][1][1],
                color_key_list_of_x_y_cell_segmentation_coordinates[0][i][j][0][0] : color_key_list_of_x_y_cell_segmentation_coordinates[0][i][j][1][0]]        
            
            #If the grayscale mode is on, then the JPEG scan 
            #will have been loaded in grayscale mode, with only 
            #one grayscale channel per pixel. Therefore, the same 
            #grayscale value will be included in the R, B, and G
            #channels in order for the color key colors to be 
            #displayed to the user in RGB format regardless of 
            #grayscale versus RGB image mode.
            if is_grayscale_mode_on:
                average_cell_b_value = int(np.average(color_key_scan_image[slice_center_of_current_cell]))
                average_cell_g_value = average_cell_b_value
                average_cell_r_value = average_cell_b_value 
            #The OpenCV colorspace is BGR, so the order of B and R is inverted.
            #The "np.average()" method is called on the slice of the current cell,
            #which is itself sliced such as to include all rows and columns, yet 
            #only one RGB color channel at a time ("[:, :, 0]" for b in the bgr 
            #OpenCV colorspace, for example). The value is then converted into 
            #an integer.
            else:
                average_cell_b_value = int(np.average(color_key_scan_image[slice_center_of_current_cell][:, :, 0]))
                average_cell_g_value = int(np.average(color_key_scan_image[slice_center_of_current_cell][:, :, 1]))
                average_cell_r_value = int(np.average(color_key_scan_image[slice_center_of_current_cell][:, :, 2]))      

            #Upon starting a new color key row (the cell index would then be zero 
            #for that new row) or if the code is processing the first row and the 
            #sixth cell at the index 5 is being processed, then a new nest list of 
            #three empty lists is added for that dictionary key, as average R, G, 
            #and B values for the cells will be appended to those for each color 
            #in the color key.
            if j == 0 or i == 0 and j == 5:
                dict_of_color_key_index_keys_to_nested_list_of_average_r_g_b_values[dictionary_key] = [[], [], []]
            
            #The average values of R, G, and B channels of each cell are appended to 
            #the appropriate sublists in the list value at the current dictionary key 
            #of "dict_of_color_key_index_keys_to_nested_list_of_average_r_g_b_values".
            dict_of_color_key_index_keys_to_nested_list_of_average_r_g_b_values[dictionary_key][0].append(average_cell_r_value)
            dict_of_color_key_index_keys_to_nested_list_of_average_r_g_b_values[dictionary_key][1].append(average_cell_g_value)
            dict_of_color_key_index_keys_to_nested_list_of_average_r_g_b_values[dictionary_key][2].append(average_cell_b_value)

    #Once all of the average R, G, and B channel values have been gathered for each cell 
    #of the color key scan, the average R, G, and B values across all five cells of each 
    #color (except the page color, which spans more cells on the first row) will be 
    #calculated, and the resulting RGBA tuple (with complete opacity at an A channel 
    #value of 255) tuple will be stored in the dictionary 
    #"dict_of_color_key_index_keys_to_rgba_tuple_values" 
    #at the same key.
    for key, value in dict_of_color_key_index_keys_to_nested_list_of_average_r_g_b_values.items():
        #If the grayscale mode is on, then the JPEG scan 
        #will have been loaded in grayscale mode, with only 
        #one grayscale channel per pixel. Therefore, the same 
        #grayscale value will be included in the R, B, and G
        #channels in order for the color key colors to be 
        #displayed to the user in RGB format regardless of 
        #grayscale versus RGB image mode.
        if is_grayscale_mode_on:
            average_r = int(np.average(value[0]))
            average_g = average_r
            average_b = average_r
        else:
            average_r = int(np.average(value[0]))
            average_g = int(np.average(value[1]))
            average_b = int(np.average(value[2]))
        dict_of_color_key_index_keys_to_rgba_tuple_values[key] = (average_r, average_g, average_b, 255)

    #The contents of the dictionary of colors in the color key scan will 
    #be outputted on-screen.   
    print("\nHere are the colors extracted from your color key")
    print("(row number in color key, RGB value, Sum or R+G+B, then Hex code):\n")
    #+1 is added to the range in order to include the key of the page 
    #color, which is equal to "number_of_colors_in_color_key_excluding_white + 1".
    for i in range(number_of_colors_in_color_key_excluding_white + 1):
        r = dict_of_color_key_index_keys_to_rgba_tuple_values[i][0]
        g = dict_of_color_key_index_keys_to_rgba_tuple_values[i][1]
        b = dict_of_color_key_index_keys_to_rgba_tuple_values[i][2]
        #Displays only two hexadecimal ("x") characters per RGB channel.
        #The string "(page color)" is only written after the last color, 
        #which was extracted from the sixth cell onwards on the first row
        #and thus these cells shouldn't contain any color.
        print(f"{i+1}\tRGB: ({r}, {g}, {b}),\tSum RGB: {r+g+b}, \tHex: #{r:02x}{g:02x}{b:02x}{'\t(page color)'*(i == number_of_colors_in_color_key_excluding_white)}")

    print("\nCurrently processing your pixel art scans.\nThis could take a few seconds.")

    #The nested list of the cell segmentation coordinates 
    #"list_of_x_y_cell_segmentation_coordinates" has the following structure: 
    #[[[[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],    #row 1, scan 1
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],     #row 2, scan 1
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]]],    #row n, scan 1

    # [[[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],    #row 1, scan 2
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]],     #row 2, scan 2
    # [[(left_x_1, top_y_1), (right_x_1, bottom_y_1)], [(left_x_2, top_y_2), (right_x_2, bottom_y_2)], ... , [(left_x_n, top_y_n), (right_x_n, bottom_y_n)]]]]    #row n, scan 2
    list_of_x_y_cell_segmentation_coordinates = []
    #The nested list of predicted color key color tuples for each cell 
    #"list_predicted_colors_for_segmented_cells" has the following structure:

    #[[[(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 1, scan 1
    #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 2, scan 1
    #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)]],  #row n, scan 1 

    # [[(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 1, scan 2
    #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 2, scan 2
    #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)]]], #row n, scan 2 
    list_predicted_colors_for_segmented_cells = []
    #The following "for" loop will loop through each JPEG file in the 
    #"JPEG_file_names" list in order to process each scan in turn.
    for i in range(len(JPEG_file_names)):
        #An empty list is appended to the nested 
        #list of the cell segmentation coordinates 
        #"list_of_x_y_cell_segmentation_coordinates"
        #to mark the start of a new scan being processed.
        list_of_x_y_cell_segmentation_coordinates.append([])
        #An empty list is appended to the nested 
        #list of the predicted color key color tuples for 
        #each cell "list_predicted_colors_for_segmented_cells"
        #to mark the start of a new scan being processed.
        list_predicted_colors_for_segmented_cells.append([])
        #The image is loaded using the "cv2.imread" method.
        if is_grayscale_mode_on:
            scan_image = cv2.imread(os.path.join(scans_folder_path, JPEG_file_names[i]), flags=cv2.IMREAD_GRAYSCALE)  
        else:
            scan_image = cv2.imread(os.path.join(scans_folder_path, JPEG_file_names[i]), flags=cv2.IMREAD_COLOR_BGR)  
        
        #The function "find_squares_and_segment_scan()" will first find the
        #coordinates of the black squares by calling the "find_black_squares()"
        #function. The canvas will be rotated if a tilt was detected, and then 
        #the slicing area in each square cell of the 65x65 grid will be appended 
        #to the "list_of_x_y_cell_segmentation_coordinates" list in the "segment_scan()"
        #function. Finally, the segmentation results will be drawn onto a copy of the scans 
        #to convey the results to the user.
        list_of_x_y_cell_segmentation_coordinates, scan_image = find_squares_and_segment_scan(
            scan_image,
            JPEG_file_names[i],
            scans_folder_path,
            excluded_border_pixels, 
            bottom_y_coordinate_for_scanning_for_black_squares,
            template_pixel_width_at_300_dpi,
            scan_dpi_correction_factor,
            black_square_side_dimension_in_template,
            horizontal_pixel_distance_between_center_of_the_black_squares_template,
            vertical_pixel_distance_between_center_of_the_black_squares_and_top_of_grid_template,
            percentage_of_cell_dimension_that_is_cropped,
            grid_cell_side_dimension_in_template,
            number_of_cells_per_side_of_grid,
            list_of_x_y_cell_segmentation_coordinates,
            pixel_art_canvas_size_width_number_of_cells,
            pixel_art_canvas_size_height_number_of_cells,
            is_grayscale_mode_on,
            brightness_level,
            contrast_level,
            paper_color_filter_threshold,
        )

        #The outer loop in the nested "for" loop below will run for a total number of times 
        #equal to the number of rows that were segmented in the scanned image at the index 
        #"i" of "JPEG_file_names".    
        len_list_of_x_y_cell_segmentation_coordinates = len(list_of_x_y_cell_segmentation_coordinates[i])
        for j in range(len_list_of_x_y_cell_segmentation_coordinates):
            #A new empty list is appended at the end of the current scan 
            #being processed at the last index ("[-1]") of the list 
            #"list_of_x_y_cell_segmentation_coordinates" at the 
            #start of every new row of pixels. 
            list_predicted_colors_for_segmented_cells[-1].append([])
            #The number of cells to slice in the current row is calculated by 
            #measuring the length of the nested list "list_of_x_y_cell_segmentation_coordinates",
            #which is first indexed with the current scanned file index "i", then at the index "j" 
            #to indicate the current row index in the scan's 65x65 grid.
            number_of_cells_to_slice_in_current_row = len(list_of_x_y_cell_segmentation_coordinates[i][j])
            #The inner "for" loop will iterate over all of the cells of that row that are to be sliced.
            for k in range(number_of_cells_to_slice_in_current_row):
                #The nested list of sums of absolute values of each delta r, 
                #delta g and delta b channels between the average values determined 
                #above for the current cell under investigation and each of the color keys colors
                #"nested_list_of_color_distance_values_and_color_key_indices"
                #is initialized as an empty list.
                nested_list_of_color_distance_values_and_color_key_indices = []
                
                #The slice coordinates for the pixels at the center of the current cell 
                #are stored in the variable "slice_center_of_current_cell" through the
                #use of the NumPy "np.s_" indexing routine.
                
                #The indexing of "list_of_x_y_cell_segmentation_coordinates" works as follows:
                #"[i]": The scan file index in the nested list
                #"[j]": The outer loop iteration index cycling over all of the rows.
                #"[k]": The inner loop iteration index cycling over all of the cells in the current row.
                #The two last indices determine which coordinate is taken when indexing the sublist of two 
                #"x, y" coordinate tuples: [(left_x_1, top_y_1), (right_x_1, bottom_y_1)]
                slice_center_of_current_cell = np.s_[
                    list_of_x_y_cell_segmentation_coordinates[i][j][k][0][1] : list_of_x_y_cell_segmentation_coordinates[i][j][k][1][1],
                    list_of_x_y_cell_segmentation_coordinates[i][j][k][0][0] : list_of_x_y_cell_segmentation_coordinates[i][j][k][1][0]]        

                #If the grayscale mode is on, then the JPEG scan 
                #will have been loaded in grayscale mode, with only 
                #one grayscale channel per pixel. Therefore, only the 
                #grayscale value for the pixels of the slice needs to 
                #be average, instead of the R, G and B values for 
                #color images.
                if is_grayscale_mode_on:
                    #The "np.average()" method is called on the slice of the current cell,
                    #to get the average grayscale value for all the pixels of the slice,
                    #which is then converted into an integer.
                    average_cell_grayscale_value = int(np.average(scan_image[slice_center_of_current_cell]))
                    
                    #The dictionary of color key index keys to RGB tuple values 
                    #"dict_of_color_key_index_keys_to_rgba_tuple_values" will hold
                    #the color palette that was extracted from the first five cells 
                    #of each row from the color key scan, with the final color at the 
                    #last index corresponding to the page color the sixth cell onwards 
                    #on the first row. When the grayscale mode is turned on, the same 
                    #grayscale values are included in the R, G and B channels of the 
                    #color key colors, in order for the same information to be displayed 
                    #to the user regardless of the grayscale versus color mode.

                    #Each color in the dictionary will be iterated over, and the absolute 
                    #value of the difference between the dictionary color and the detected 
                    #color in the current cell under investigation will be appended to the 
                    #list "nested_list_of_color_distance_values_and_color_key_indices",
                    #along with the current key, which will allow retrieval of the color 
                    #key index that has the lowest absolute delta grayscale value (and thus
                    #is closest to the detected color of the cell under investigation) in
                    #the sorted list. As the same grayscale values are stored in the R, G 
                    #and B channels of each color key in the dictionary, only the first 
                    #channel (R) will be used when calculating the delta grayscale value.
                    for key, value in dict_of_color_key_index_keys_to_rgba_tuple_values.items():
                        abs_delta_grayscale = abs(average_cell_grayscale_value - value[0])
                     
                        nested_list_of_color_distance_values_and_color_key_indices.append([abs_delta_grayscale, key])
                else:
                    #The OpenCV colorspace is BGR, so the order of B and R is inverted.
                    #The "np.average()" method is called on the slice of the current cell,
                    #which is itself sliced such as to include all rows and columns, yet 
                    #only one RGB color channel at a time ("[:, :, 0]" for b in the bgr 
                    #OpenCV colorspace, for example). The value is then converted into 
                    #an integer.
                    average_cell_b_value = int(np.average(scan_image[slice_center_of_current_cell][:, :, 0]))
                    average_cell_g_value = int(np.average(scan_image[slice_center_of_current_cell][:, :, 1]))
                    average_cell_r_value = int(np.average(scan_image[slice_center_of_current_cell][:, :, 2]))      
         
                    #The dictionary of color key index keys to RGB tuple values 
                    #"dict_of_color_key_index_keys_to_rgba_tuple_values" will hold
                    #the color palette that was extracted from the first five cells 
                    #of each row from the color key scan, with the final color at the 
                    #last index corresponding to the page color the sixth cell onwards 
                    #on the first row.

                    #Each color in the dictionary will be iterated over, and the square values 
                    #of the delta r, delta g and delta b values will be calculated between the 
                    #dictionary color and the detected color in the current cell under investigation. 
                    #The square root of the sum of these will be stored in the variable 
                    #"rgb_euclidian_distance", which will itself be appended to the list 
                    #"nested_list_of_color_distance_values_and_color_key_indices",
                    #along with the current key, which will allow retrieval of the color key index that 
                    #has the lowest sum (and thus is closest to the detected color of the cell under 
                    #investigation) in the sorted list.
                    for key, value in dict_of_color_key_index_keys_to_rgba_tuple_values.items():
                        delta_r_squared = (average_cell_r_value - value[0])**2
                        delta_g_squared = (average_cell_g_value - value[1])**2
                        delta_b_squared = (average_cell_b_value - value[2])**2
                        rgb_euclidian_distance = (delta_r_squared + delta_g_squared + delta_b_squared)**0.5
                                        
                        nested_list_of_color_distance_values_and_color_key_indices.append([rgb_euclidian_distance, key])
                    
                #The nested list of sums of absolute values of each delta r, 
                #delta g and delta b channels between the average values determined 
                #for the current cell under investigation and each of the color keys colors
                #will be sorted in ascending order along the first element of each sublist 
                #(sum of absolute values), such that the element at the index zero after 
                #sorting will represent the predicted color, for which the color key's index 
                #may be accessed at the second element of this first sublist ("[0][1]").             
                nested_list_of_color_distance_values_and_color_key_indices.sort(key=lambda x:x[0])
                predicted_color_rgb_tuple = (dict_of_color_key_index_keys_to_rgba_tuple_values[nested_list_of_color_distance_values_and_color_key_indices[0][1]])
                #The value of "predicted_color_rgb_tuple" for the current JPEG scan (first "[-1]" index)
                #and for the current row (second "[-1]" index) will be appended to the nested list of 
                #predicted color key color tuples for each cell "list_predicted_colors_for_segmented_cells".
                list_predicted_colors_for_segmented_cells[-1][-1].append(predicted_color_rgb_tuple)

    #Once all of the JPEG images have been scanned, a composite PNG image will be 
    #generated in the "if" statement below if any of the dimensions of the pixel 
    #art canvas exceeds the number of squares making up the width or height of 
    #the 65x65 grid found on a single page. 

    #Otherwise, if the pixel art canvas dimensions are at most those of the 
    #65x65 grid found on a single page, then each JPEG image will result in 
    #the generation of a separate PNG pixel art image in the "else" statement 
    #that follows the "if" statement below.

    #In any case, the list will hold the RGB pixel information 
    #for each PNG image that will need to be generated.
    list_of_PNG_images = [] 
                              
    if (pixel_art_canvas_size_width_number_of_cells > number_of_cells_per_side_of_grid or 
    pixel_art_canvas_size_height_number_of_cells > number_of_cells_per_side_of_grid):
        #The function "populate_list_predicted_colors_for_segmented_cells()"
        #will populate the list "list_of_PNG_images" with  all of the predicted 
        #RGBA values for each pixels in the final canvas. To do this, it will 
        #collate the data from each scan into one cohesive final canvas. 
        list_of_PNG_images = populate_list_predicted_colors_for_segmented_cells(
        list_of_PNG_images,
        list_predicted_colors_for_segmented_cells,
        number_of_scans_in_width_of_pixel_art_canvas,
        number_of_scans_in_height_of_pixel_art_canvas,
        number_of_cells_per_side_of_grid,
        pixel_art_canvas_size_width_number_of_cells,
        pixel_art_canvas_size_height_number_of_cells
        )
        
    #Otherwise, if the pixel art canvas dimensions are at most those of the 
    #65x65 grid found on a single page, then each JPEG image will result in 
    #the generation of a separate PNG pixel art image.
    else:
        #The nested list of predicted color key color tuples for each cell 
        #"list_predicted_colors_for_segmented_cells" has the following structure:

        #[[[(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 1, scan 1
        #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 2, scan 1
        #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)]],  #row n, scan 1 

        # [[(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 1, scan 2
        #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)],   #row 2, scan 2
        #  [(r_1, g_1, b_1, a_1), (r_2, g_2, b_2, a_2), ... , (r_n, g_n, b_n, a_n)]]], #row n, scan 2 
        
        #The value of "list_of_PNG_images" is set to the value of 
        #"list_predicted_colors_for_segmented_cells"
        list_of_PNG_images = list_predicted_colors_for_segmented_cells 
     
    #The "for" loop below cycles through all of the image pixel RGBA values in "list_of_PNG_images"
    #and generates a numpy array with "np.uint8" data type that is required to generate a Pillow 
    #Image object. The Image object is then exported as a PNG image.
    for i in range(len(list_of_PNG_images)):
        #The file name is extracted from the parallel list of JPEG file names,
        #with the ".jpg" file extension being removed, as the ".png" file extension 
        #will be added to the new file name.
        PNG_file_name = JPEG_file_names[i].removesuffix(".jpg")
        
        if not os.path.exists(generated_png_pixel_art_files_folder_path):
            os.mkdir(generated_png_pixel_art_files_folder_path)
        #The list "list_of_image_data_nested_lists", initialized to 
        #the value of the current image's RGB tuple pixel color 
        #data for every row of pixels ("list_of_PNG_images[i]"),
        #will be appended with the corresponding list of remapped 
        #color pixel data "csv_image_data" in order to generate 
        #two PNG files: 1- with detected colors (adjusted for 
        #brightness, contrast and page color cutoff value) and 
        #2- with remapped colors (if the number of remapped 
        #colors corresponds to the initial number of colors 
        #in the scanned color key).
        list_of_image_data_nested_lists = [list_of_PNG_images[i]]
        #The function "get_dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values()"
        #will extract the RGB colors mapping to the original RGB colors found in the 
        #"dict_of_color_key_index_keys_to_rgba_tuple_values". It will return a dictionary 
        #of scanned color key tuple keys in string form to values made up of tuples 
        #of rgba values corresponding to the colors specified in the CSV file for 
        #each color row of the scanned color key, with the last row of the CSV file 
        #corresponding to the color mapping to the page color.
        dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values = (
            get_dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values(
            cwd,
            press_any_key_string,
            dict_of_color_key_index_keys_to_rgba_tuple_values))
        #If the number of remapped colors in the dictionary 
        #"dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values"
        #matches the number of colors in the initial scanned color key,
        #then the "csv_image_data" list will be populated with every 
        #remaped pixel of every row. To get the remapped color, the 
        #original scanned color key's color rgb tuple in string form 
        #will be used to index the dictionary, which will return the 
        #rgb tuple of the remapped color.
        if (dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values and 
        len(dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values) == 
        len(dict_of_color_key_index_keys_to_rgba_tuple_values)):
            csv_image_data = []
            for row in list_of_PNG_images[i]:
                #A new empty list is appended 
                #at the start of every row of 
                #pixels.
                csv_image_data.append([])
                for rgb_tuple in row:
                    #The remapped pixel RGB tuple 
                    #is appended to the end of the 
                    #current row at the index "[-1]"
                    #of the "csv_image_data" list.
                    csv_image_data[-1].append(dict_of_color_key_tuple_string_keys_to_csv_rgb_color_values[str(rgb_tuple)])
            #The list "list_of_image_data_nested_lists", initialized to 
            #the value of the current image's RGB tuple pixel color 
            #data for every row of pixels ("list_of_PNG_images[i]"),
            #will be appended with the corresponding list of remapped 
            #color pixel data "csv_image_data" in order to generate 
            #two PNG files: 1- with detected colors (adjusted for 
            #brightness, contrast and page color cutoff value) and 
            #2- with remapped colors (if the number of remapped 
            #colors corresponds to the initial number of colors 
            #in the scanned color key).
            list_of_image_data_nested_lists.append(csv_image_data)
        #The list "list_of_image_data_nested_lists", initialized to 
        #the value of the current image's RGB tuple pixel color 
        #data for every row of pixels ("list_of_PNG_images[i]"),
        #will be appended with the corresponding list of remapped 
        #color pixel data "csv_image_data" in order to generate 
        #two PNG files: 1- with detected colors (adjusted for 
        #brightness, contrast and page color cutoff value) and 
        #2- with remapped colors (if the number of remapped 
        #colors corresponds to the initial number of colors 
        #in the scanned color key).
        for i in range(len(list_of_image_data_nested_lists)):
            image_array = np.array(list_of_image_data_nested_lists[i], dtype=np.uint8)
            #If a scaling factor integer greater than one 
            #was specified, then the dimensions of the original 
            #pixel art numpy array will be stored in "png_height"
            #and "png_width", then multiplied by the value of 
            #"scaling_factor" to get the scaled PNG image 
            #dimensions, which will be passed in when calling 
            #the "cv2.resize()" function. The "INTER_NEAREST"
            #interpolation method preserves the crisp edges 
            #of the pixel art, as it does not average out 
            #pixel values.
            if scaling_factor > 1:
                png_height, png_width = image_array.shape[:2]
                scaled_png_width = scaling_factor*png_width
                scaled_png_height = scaling_factor*png_height
                image_array = cv2.resize(image_array, (scaled_png_width, scaled_png_height), interpolation = cv2.INTER_NEAREST)
            
            #A Pillow "Image" object is instantiated 
            #from the "image_array" numpy array 
            pillow_image = Image.fromarray(image_array)
            #If the image already exists, it will first be 
            #deleted before outputting the updated image.
            PNG_image_path = os.path.join(generated_png_pixel_art_files_folder_path, PNG_file_name + f"{(i == 1)*" (Remapped Colors)"}.png")
            if os.path.exists(PNG_image_path):
                os.remove(PNG_image_path)
            #Output the PNG image with maximal compression level of 9,
            #which won't affect the image quality as it is a lossless format.
            pillow_image.save(PNG_image_path, optimize=True, compress_level=9)
        
    number_of_generated_PNG_images = len(list_of_PNG_images)
    print("\n" + textwrap.fill(f"Successfully generated your {number_of_generated_PNG_images} PNG image{"s" * (number_of_generated_PNG_images > 1)} in the '{generated_png_pixel_art_files_folder_name}' subfolder of the 'PixelArtReader' folder.", width = columns))
    
    input(press_any_key_string)
    
    return json_settings_dictionary

#The "set_pixel_art_canvas_size_width_number_of_cells()" function 
#will set the canvas size width in number of cells.
def set_pixel_art_canvas_size_width_number_of_cells(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Number of Squares in Pixel Art Drawing Width ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(pixel_art_canvas_size_width_number_of_cells_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the number of squares (integer greater than or equal to one), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Pixel Art Scale and Color Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 1:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_pixel_art_canvas_size_height_number_of_cells()" function 
#will set the canvas size height in number of cells.
def set_pixel_art_canvas_size_height_number_of_cells(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Number of Squares in Pixel Art Drawing Height ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(pixel_art_canvas_size_height_number_of_cells_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the number of squares (integer greater than or equal to one), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Pixel Art Scale and Color Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 1:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_scaling_factor()" function 
#will set the scaling factor integer.
def set_scaling_factor(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Scaling Factor ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(scaling_factor_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the scaling factor (integer greater than or equal to one), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Pixel Art Scale and Color Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 1:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_number_of_colors_in_color_key_excluding_white()" function 
#will set the number of colors used in the color key, excluding the 
#white page color.
def set_number_of_colors_in_color_key_excluding_white(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Number of Colors Excluding White in Pixel Art Drawing ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(number_of_colors_in_color_key_excluding_white_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the number of colors (integer greater than or equal to one), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Pixel Art Scale and Color Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 1:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "pixel_art_scale_and_color_settings_menu()" function will run a "while is_in_submenu"
#loop that will allow the user to navigate the menu, and the loop will 
#be broken out of when they select the "Quit" option.
def pixel_art_scale_and_color_settings_menu(json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_submenu
    is_in_submenu = True

    while is_in_submenu:
        #The "clear_screen()" function will clear the CLI screen
        #using the appropriate command depending on the operating system.
        clear_screen()

        pixel_art_scale_and_color_settings_menu_actions_dict = {
        "1": [f"Number of Squares in Pixel Art Drawing Width ({json_settings_dictionary["Number of Squares in Pixel Art Drawing Width"]})", set_pixel_art_canvas_size_width_number_of_cells, ("Number of Squares in Pixel Art Drawing Width", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "2": [f"Number of Squares in Pixel Art Drawing Height ({json_settings_dictionary["Number of Squares in Pixel Art Drawing Height"]})", set_pixel_art_canvas_size_height_number_of_cells, ("Number of Squares in Pixel Art Drawing Height", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)], 
        "3": [f"Scaling Factor ({json_settings_dictionary["Scaling Factor"]})", set_scaling_factor, ("Scaling Factor", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "4": [f"Number of Colors Excluding White in Pixel Art Drawing ({json_settings_dictionary["Number of Colors Excluding White in Pixel Art Drawing"]})", set_number_of_colors_in_color_key_excluding_white, ("Number of Colors Excluding White in Pixel Art Drawing", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "m": ["Main Menu", back_to_main_menu_function, (json_settings_dictionary,)],
        "q": ["Quit", quit_function, ()]}

        #The function "textwrap_action_strings_in_menu_action_dict()", which takes in 
        #a menu action dictionary comprised of one character keys and values made up
        #of a three-member tuple (action string, function, function arguments).
        #The action strings ("value[0]") will be textwrapped and the modified
        #dictionary will be returned.
        pixel_art_scale_and_color_settings_menu_actions_dict = textwrap_action_strings_in_menu_action_dict(pixel_art_scale_and_color_settings_menu_actions_dict)

        print("=== Pixel Art Scale and Color Settings Menu ===\n\n")

        #The function "get_terminal_dimensions()" will return the number of columns 
        #and rows in the console, to allow to properly format the text and dividers.
        columns, lines = get_terminal_dimensions()

        print(textwrap.fill("This menu will allow you to specify the settings for the scale of your pixel art drawing and set the number of different colors used in its creation. Further details are available in the submenu options, or in the 'README.txt' file.", width=columns) + "\n")

        #The function "run_menu" will retrieve and call the function
        #at the appropriate choice key in the "menu_actions_dict"
        json_settings_dictionary = run_menu(pixel_art_scale_and_color_settings_menu_actions_dict, json_settings_dictionary)
    return json_settings_dictionary 

#The "set_current_US_Letter_or_A4_format()" function 
#will set the current page format (US Letter or A4).
def set_current_US_Letter_or_A4_format(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== A4 or US Letter Format Selection ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(current_US_Letter_or_A4_format_string_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the page format ('A4' or 'US Letter'), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Graph Paper Grid Layout Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = choice.strip()
            if user_input.lower() in ["a4", "us letter"]:
                #The value of the "A4 or US Letter Format Selection" 
                #key is updated with that of "user_input" in 
                #"json_settings_dictionary" and the changes 
                #are then saved.
                
                #In case the user has entered a lowercased 
                #value for the paper format, these will be 
                #stored in capitalized form.
                if user_input.lower() == "a4":
                    user_input = "A4"
                else:
                    user_input = "US Letter"
                json_settings_dictionary[json_settings_key] = user_input
                #The function "atomic_save()" will create a temporary JSON file with the updated changes.
                #If the files is created successfully, then the files will be swapped. If a problem is 
                #encountered, the temp file will be unlinked and an error log will be reported.
                atomic_save(json_settings_dictionary, json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_graph_line_pixel_width()" function 
#will set the line width of the lines in the 
#graph paper grid.
def set_graph_line_pixel_width(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Graph Line Pixel Width ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(graph_line_pixel_width_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the width of the lines in pixels (integer value 1 or above), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Graph Paper Grid Layout Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 1:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_thicker_graph_line_pixel_width()" function 
#will set the line width of the bold lines in the 
#graph paper grid.
def set_thicker_graph_line_pixel_width(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Thicker Graph Line Pixel Width ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(thicker_graph_line_pixel_width_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the width of the lines in pixels (integer value 1 or above), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Graph Paper Grid Layout Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 1:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_thicker_line_every_n_squares()" function 
#will set the number of squares between thicker lines 
#in the graph paper grid.
def set_thicker_line_every_n_squares(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Number of Squares Between Thicker Lines ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(thicker_line_every_n_squares_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the number of squares between thicker lines (integer value 1 or above), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Graph Paper Grid Layout Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 1:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_graph_line_color_rgb_tuple()" function 
#will set the color of the lines in the graph paper 
#grid.
def set_graph_line_color_rgb_tuple(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Graph Line RGB or Hex Code Color ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(graph_line_color_rgb_tuple_string_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the line color (RGB values or hex code), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Graph Paper Grid Layout Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = choice.strip()
            
            #The user input is screened for the presence of RGB information, 
            #which would take the form of three 1-3 digit channel values (0-255), 
            #each separated by a comma with or without some spaces after the comma.
            rgb_search_hits = re.findall(r"[\d]{1,3},[ ]*[\d]{1,3},[ ]*[\d]{1,3}", user_input)
            if rgb_search_hits:
                rgb_values_list = [channel.strip() for channel in rgb_search_hits[0].split(",")]
                rgb_tuple_string = "rgb(" + ", ".join(rgb_values_list) + ")"
                #The value of the "Graph Line RGB or Hex Code Color"
                #key of "json_settings_dictionary" is set to the value 
                #of "rgb_tuple_string" and the changes are then saved.                    
                json_settings_dictionary[json_settings_key] = rgb_tuple_string
                #The function "atomic_save()" will create a temporary JSON file with the updated changes.
                #If the files is created successfully, then the files will be swapped. If a problem is 
                #encountered, the temp file will be unlinked and an error log will be reported.
                atomic_save(json_settings_dictionary, json_settings_file_path_name)
            else:
                #The function "hex_2_rgba_tuple()" extracts a 
                #color Hex code from a string argument and returns 
                #the corresponding RGBA tuple, where an A channel 
                #value of 255 (fully opaque) being included if there 
                #was no transparency information in the hex code string.
                rgba_tuple = hex_2_rgb_tuple(user_input)
                if rgba_tuple:
                    rgb_tuple_string = "rgb" + str(tuple([rgba_tuple[i] for i in range(len(rgba_tuple)) if i != len(rgba_tuple) - 1]))
                    #The value of the "Graph Line RGB or Hex Code Color"
                    #key of "json_settings_dictionary" is set to the value 
                    #of "rgb_tuple_string" and the changes are then saved.                    
                    json_settings_dictionary[json_settings_key] = rgb_tuple_string
                    #The function "atomic_save()" will create a temporary JSON file with the updated changes.
                    #If the files is created successfully, then the files will be swapped. If a problem is 
                    #encountered, the temp file will be unlinked and an error log will be reported.
                    atomic_save(json_settings_dictionary, json_settings_file_path_name)
                else:
                    input("\nInvalid choice, press any key to continue.")  
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "graph_paper_grid_layout_settings_menu()" function will run a "while is_in_submenu"
#loop that will allow the user to navigate the menu, and the loop will 
#be broken out of when they select the "Quit" option.
def graph_paper_grid_layout_settings_menu(json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_submenu
    is_in_submenu = True

    while is_in_submenu:
        #The "clear_screen()" function will clear the CLI screen
        #using the appropriate command depending on the operating system.
        clear_screen()

        graph_paper_grid_layout_settings_menu_actions_dict = {
        "1": [f"A4 or US Letter Format Selection ({json_settings_dictionary["A4 or US Letter Format Selection"]})", set_current_US_Letter_or_A4_format, ("A4 or US Letter Format Selection", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "2": [f"Graph Line Pixel Width ({json_settings_dictionary["Graph Line Pixel Width"]})", set_graph_line_pixel_width, ("Graph Line Pixel Width", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)], 
        "3": [f"Thicker Graph Line Pixel Width ({json_settings_dictionary["Thicker Graph Line Pixel Width"]})", set_thicker_graph_line_pixel_width, ("Thicker Graph Line Pixel Width", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "4": [f"Number of Squares Between Thicker Lines ({json_settings_dictionary["Number of Squares Between Thicker Lines"]})", set_thicker_line_every_n_squares, ("Number of Squares Between Thicker Lines", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "5": [f"Graph Line RGB or Hex Code Color ({json_settings_dictionary["Graph Line RGB or Hex Code Color"]})", set_graph_line_color_rgb_tuple, ("Graph Line RGB or Hex Code Color", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "m": ["Main Menu", back_to_main_menu_function, (json_settings_dictionary,)],
        "q": ["Quit", quit_function, ()]}

        #The function "textwrap_action_strings_in_menu_action_dict()", which takes in 
        #a menu action dictionary comprised of one character keys and values made up
        #of a three-member tuple (action string, function, function arguments).
        #The action strings ("value[0]") will be textwrapped and the modified
        #dictionary will be returned.
        graph_paper_grid_layout_settings_menu_actions_dict = textwrap_action_strings_in_menu_action_dict(graph_paper_grid_layout_settings_menu_actions_dict)

        print("=== Graph Paper Grid Layout Settings Menu ===\n\n")

        #The function "get_terminal_dimensions()" will return the number of columns 
        #and rows in the console, to allow to properly format the text and dividers.
        columns, lines = get_terminal_dimensions()

        print(textwrap.fill("This menu will allow you to specify the settings that will format the graph paper PDF template. Further details are available in the submenu options, or in the 'README.txt' file.", width=columns) + "\n")

        #The function "run_menu" will retrieve and call the function
        #at the appropriate choice key in the "menu_actions_dict"
        json_settings_dictionary = run_menu(graph_paper_grid_layout_settings_menu_actions_dict, json_settings_dictionary)
    return json_settings_dictionary  

#The "set_dpi()" function will set the 
#resolution at which the scans were made.
def set_dpi(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Scan Resolution in DPI ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(dpi_setting_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the DPI resolution of the scans (integer value 100 or above), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Scan Processing Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 100:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_percentage_of_cell_dimension_that_is_cropped()" 
#function will set the width of the cropping slice in each 
#cell for the segmentation step.
def set_percentage_of_cell_dimension_that_is_cropped(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Percentage of Cell Dimension that is Cropped ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(percentage_of_cell_dimension_that_is_cropped_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the percentage (integer value between 1 and 100), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Scan Processing Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 1 and user_input <= 100:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_brightness_level()" function will set 
#the number of RGB units that will be applied to 
#each channel during the brightness transformation.
def set_brightness_level(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Brightness Level ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(brightness_level_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the brightness level (integer value between -255 and 255, with a value of zero resulting in no brightness adjustments), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Scan Processing Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= -255 and user_input <= 255:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_contrast_level()" function will set 
#the number of RGB units that will be applied to 
#each channel during the brightness transformation.
def set_contrast_level(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Contrast Level ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(contrast_level_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the contrast level (zero and above, with 1.0 resulting in no contrast adjustments), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Scan Processing Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = float(choice)
            if user_input >= 0:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "set_paper_color_grayscale_filter_threshold()" function will set 
#the RGB channel value above which it will be set to 255.
def set_paper_color_grayscale_filter_threshold(json_settings_key, json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_sub_submenu
    is_in_sub_submenu = True

    while is_in_sub_submenu:
        try:
            #The "clear_screen()" function will clear the CLI screen
            #using the appropriate command depending on the operating system.
            clear_screen()

            print("=== Set the Paper Color Filter Threshold ===\n\n")

            #The function "get_terminal_dimensions()" will return the number of columns 
            #and rows in the console, to allow to properly format the text and dividers.
            columns, lines = get_terminal_dimensions()

            print(f"Current Setting: {json_settings_dictionary[json_settings_key]} | Default: {json_default_settings_dictionary[json_settings_key]}.\n")

            textwrapped_instructions_string = textwrap.fill(paper_color_filter_threshold_comment_string, width=columns)
            textwrapped_input_string = textwrap.fill("Enter the threshold value (integer between 0 and 255, with 255 resulting in no filter adjustments), or select one of the above options:", width=columns)

            print(textwrapped_instructions_string + " ")
            print(f"\n[r] Reset to the Default Setting\n[b] Scan Processing Settings Menu\n[m] Main Menu\n[q] Quit\n")
            choice = input(textwrapped_input_string + " ").strip().lower()

            if choice == "":
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("").
                continue
            elif choice == "m":
                #The function "back_to_main_menu_function()"
                #will set the Boolean flags "is_in_submenu" and 
                #"is_in_sub_submenu" to "False", which will break the submenu
                #"while" loops and return to the main menu.
                back_to_main_menu_function(json_settings_dictionary)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("m").
                continue
            elif choice == "b":
                is_in_sub_submenu = False
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("b").
                continue
            elif choice == "r":
                #The "reset_to_default_setting()" function will reset the setting to its default value
                #found while accessing the value of the "json_default_settings_dictionary" dictionary 
                #with the key "setting_label_key". 
                #The "True" return value (if used) will break the submenu
                #loop and allow to return to the main menu or
                #the nested menu.
                json_settings_dictionary = reset_to_default_setting(json_settings_key, json_settings_dictionary, 
                    json_default_settings_dictionary, json_settings_file_path_name)
                #A continue needs to be used, as we don't want 
                #the code below the "elif" statements to run,
                #which would cause a ValueError on int("r").
                continue
            elif choice == "q":
                quit_function()
            user_input = int(choice)
            if user_input >= 0 and user_input <= 255:
                #The "set_numeric_setting()" function will set the value of the setting found while accessing
                #the "json_settings_dictionary" dictionary with the key "setting_label_key" to the provided
                #value ("setting_value"). 
                json_settings_dictionary = set_numeric_setting(user_input, json_settings_key, json_settings_dictionary, 
                json_settings_file_path_name)
            else:
                input("\nInvalid choice, press any key to continue.") 
        except ValueError:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary

#The "scan_processing_settings_menu()" function will run a "while is_in_submenu"
#loop that will allow the user to navigate the menu, and the loop will 
#be broken out of when they select the "Quit" option.
def scan_processing_settings_menu(json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_submenu
    is_in_submenu = True

    while is_in_submenu:
        #The "clear_screen()" function will clear the CLI screen
        #using the appropriate command depending on the operating system.
        clear_screen()

        #The function "get_terminal_dimensions()" will return the number of columns 
        #and rows in the console, to allow to properly format the text and dividers.
        columns, lines = get_terminal_dimensions()

        textwrapped_toggle_string = textwrap.fill(is_grayscale_mode_on_comment_string, width=columns)

        if (json_settings_dictionary["Grayscale Mode"]):
            grayscale_mode_state = "ON"
        else:
            grayscale_mode_state = "OFF"

        scan_processing_settings_menu_actions_dict = {
        "1": [f"Scan Resolution in DPI ({json_settings_dictionary["Scan Resolution in DPI"]})", set_dpi, ("Scan Resolution in DPI", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "2": [f"Percentage of Cell Dimension that is Cropped ({json_settings_dictionary["Percentage of Cell Dimension that is Cropped"]})", set_percentage_of_cell_dimension_that_is_cropped, ("Percentage of Cell Dimension that is Cropped", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)], 
        "3": [f"Brightness Level ({json_settings_dictionary["Brightness Level"]})", set_brightness_level, ("Brightness Level", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "4": [f"Contrast Level ({json_settings_dictionary["Contrast Level"]})", set_contrast_level, ("Contrast Level", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "5": [f"Paper Color Filter Threshold ({json_settings_dictionary["Paper Color Filter Threshold"]})", set_paper_color_grayscale_filter_threshold, ("Paper Color Filter Threshold", json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "t": ["Toggle Grayscale Mode On/Off (Increases the processing speed for grayscale scans)", toggle_boolean_setting, ("Grayscale Mode", json_settings_dictionary, json_settings_file_path_name)],
        "m": ["Main Menu", back_to_main_menu_function, (json_settings_dictionary,)],
        "q": ["Quit", quit_function, ()]}

        #The function "textwrap_action_strings_in_menu_action_dict()", which takes in 
        #a menu action dictionary comprised of one character keys and values made up
        #of a three-member tuple (action string, function, function arguments).
        #The action strings ("value[0]") will be textwrapped and the modified
        #dictionary will be returned.
        scan_processing_settings_menu_actions_dict = textwrap_action_strings_in_menu_action_dict(scan_processing_settings_menu_actions_dict)

        print("=== Scan Processing Settings Menu ===\n\n")

        #The function "get_terminal_dimensions()" will return the number of columns 
        #and rows in the console, to allow to properly format the text and dividers.
        columns, lines = get_terminal_dimensions()

        print(f"Grayscale mode is currently turned {grayscale_mode_state}{" (Default value)" * (not json_settings_dictionary["Grayscale Mode"])}.\n")

        print(textwrapped_toggle_string + "\n")

        print(textwrap.fill("This menu will allow you to specify the settings that will help the code locate the graph paper square cells and detect the colors in them. Further details are available in the submenu options, or in the 'README.txt' file.", width=columns) + "\n")

        #The function "run_menu" will retrieve and call the function
        #at the appropriate choice key in the "menu_actions_dict"
        json_settings_dictionary = run_menu(scan_processing_settings_menu_actions_dict, json_settings_dictionary)
    return json_settings_dictionary     

#The "reset_all_settings()" function will set the value "json_settings_dictionary"
#to that of "json_default_settings_dictionary" and save the changes to the JSON file.
def reset_all_settings(json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name):

    global is_in_submenu
    is_in_submenu = True

    while is_in_submenu:

        #The "clear_screen()" function will clear the CLI screen
        #using the appropriate command depending on the operating system.
        clear_screen()

        print("=== Reset All Settings ===\n\n")

        #The function "get_terminal_dimensions()" will return the number of columns 
        #and rows in the console, to allow to properly format the text and dividers.
        columns, lines = get_terminal_dimensions()
        textwrapped_input_string = textwrap.fill("Are you sure you want to reset all of the settings? Enter (y/n), or select one of the above options: ", width=columns)

        print(f"[m] Main Menu\n[q] Quit\n")

        choice = input(textwrapped_input_string + " ").strip().lower()
        if choice in ["", "n"]:
            #A continue needs to be used, as we don't want 
            #the code below the "elif" statements to run,
            #which would cause a ValueError on int("").
            continue
        elif choice == "m":
            #The function "back_to_main_menu_function()"
            #will set the Boolean flags "is_in_submenu" and 
            #"is_in_sub_submenu" to "False", which will break the submenu
            #"while" loops and return to the main menu.
            return json_settings_dictionary
        elif choice == "q":
            quit_function()
        elif choice == "y":           
            #A deep copy (since it contains a list of deleted pages) of 
            #"json_default_settings_dictionary" is made so as to avoid having
            #both "json_settings_dictionary" and "json_default_settings_dictionary"
            #pointing to the same address.
            json_settings_dictionary = deepcopy(json_default_settings_dictionary)
            #The function "atomic_save()" will create a temporary JSON file with the updated changes.
            #If the files is created successfully, then the files will be swapped. If a problem is 
            #encountered, the temp file will be unlinked and an error log will be reported.
            atomic_save(json_settings_dictionary, json_settings_file_path_name)
            print("\nAll settings have successfully been reset to their default values.")
            input("\nPress any key continue.")
        else:
            input("\nInvalid choice, press any key to continue.")
    return json_settings_dictionary   
   
#The "main_menu()" function will run a "while True"
#loop that will allow the user to navigate the menu, and the
#loop will be broken out of when they select the "Quit" option,
#or when they press Ctrl+C (SIGINT, Signal Interrupt).
def main_menu(json_settings_dictionary, json_default_settings_dictionary, cwd, json_settings_file_path_name):

    while True:
        #The "clear_screen()" function will clear the CLI screen
        #using the appropriate command depending on the operating system.
        clear_screen()

        menu_actions_dict = {
        "1": ["Generate PNG Files with Current Settings", generate_png_images, (json_settings_dictionary, json_default_settings_dictionary)],
        "2": ["Generate PDF Graph Paper Template With Current Settings", generate_grid_pdf, (json_settings_dictionary, json_default_settings_dictionary)],
        "3": ["Pixel Art Scale and Color Settings Menu", pixel_art_scale_and_color_settings_menu, (json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "4": ["Graph Paper Grid Layout Settings Menu", graph_paper_grid_layout_settings_menu, (json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "5": ["Scan Processing Settings Menu (Settings that help the code locate the squares and detect the colors)", scan_processing_settings_menu, (json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "r": ["Reset Defaults", reset_all_settings, (json_settings_dictionary, json_default_settings_dictionary, json_settings_file_path_name)],
        "q": ["Quit", quit_function, ()]}

        #The function "textwrap_action_strings_in_menu_action_dict()", which takes in 
        #a menu action dictionary comprised of one character keys and values made up
        #of a three-member tuple (action string, function, function arguments).
        #The action strings ("value[0]") will be textwrapped and the modified
        #dictionary will be returned.
        menu_actions_dict = textwrap_action_strings_in_menu_action_dict(menu_actions_dict)

        print(" PixelArtReader")
        print("=== Main Menu ===\n\n")

        #The function "run_menu" will retrieve and call the function
        #at the appropriate choice key in the "menu_actions_dict"
        json_settings_dictionary = run_menu(menu_actions_dict, json_settings_dictionary)

#The function "load_json_data()" will load the JSON data from file
#and store them in the "json_settings_dictionary", or initialize the
#dictionary based on the values of "json_default_settings_dictionary".
def load_json_data(json_settings_file_path_name): 

    json_default_settings_dictionary = {
        "_comment_1" : dpi_setting_comment_string,
        "Scan Resolution in DPI" : 200,

        "_comment_2" : brightness_level_comment_string,
        "Brightness Level" : 0,

        "_comment_3" : contrast_level_comment_string,
        "Contrast Level" : 1.0,

        "_comment_4" : paper_color_filter_threshold_comment_string,
        "Paper Color Filter Threshold" : 255,

        "_comment_5" : current_US_Letter_or_A4_format_string_comment_string,
        "A4 or US Letter Format Selection": "US Letter",

        "_comment_6" : graph_line_pixel_width_comment_string,
        "Graph Line Pixel Width" : 3,

        "_comment_7" : thicker_graph_line_pixel_width_comment_string,
        "Thicker Graph Line Pixel Width" : 5,
        
        "_comment_8" : thicker_line_every_n_squares_comment_string,
        "Number of Squares Between Thicker Lines" : 5,

        "_comment_9" : graph_line_color_rgb_tuple_string_comment_string,
        "Graph Line RGB or Hex Code Color" :  "rgb(200, 200, 200)",

        "_comment_10" : percentage_of_cell_dimension_that_is_cropped_comment_string,
        "Percentage of Cell Dimension that is Cropped" : 50,

        "_comment_11" : pixel_art_canvas_size_width_number_of_cells_comment_string,
        "Number of Squares in Pixel Art Drawing Width" : 65,
        
        "_comment_12" : pixel_art_canvas_size_height_number_of_cells_comment_string,
        "Number of Squares in Pixel Art Drawing Height" : 65,
        
        "_comment_13" : scaling_factor_comment_string,
        "Scaling Factor" : 1,

        "_comment_14" : number_of_colors_in_color_key_excluding_white_comment_string,
        "Number of Colors Excluding White in Pixel Art Drawing" : 2, 

        "_comment_15" : is_grayscale_mode_on_comment_string,
        "Grayscale Mode" : False,
    }

    need_to_generate_new_json_file = False
    if os.path.isfile(json_settings_file_path_name):
        #A try-except statement is used in case
        #the JSON file is malformed or empty,
        #in which case the Boolean variable
        #"need_to_generate_new_json_file" will
        #be set to "True" and the "if" statement
        #below this one would run.
        try:
            #The "utf-8-sig" encoding handles files with or without a BOM automatically
            with open(json_settings_file_path_name, "r", encoding="utf-8-sig") as f:
                json_settings_dictionary = json.load(f)
        except json.JSONDecodeError:
            need_to_generate_new_json_file = True
    else:
        need_to_generate_new_json_file = True

    if need_to_generate_new_json_file:
        #A deep copy (since it contains a list of deleted pages) of 
        #"json_default_settings_dictionary" is made so as to avoid having
        #both "json_settings_dictionary" and "json_default_settings_dictionary"
        #pointing to the same address.
        json_settings_dictionary = deepcopy(json_default_settings_dictionary)

        #Create a low-level file descriptor (used for atomic saves)
        #The two access flags "os.O_RDWR" and "os.O_CREAT" allow for the file to be 
        #read and written to and created if it doesn't already exist, respectively.
        file_descriptor = os.open(json_settings_file_path_name, os.O_RDWR | os.O_CREAT)
        with os.fdopen(file_descriptor, "w+", encoding="utf-8") as f:
            #Write the default values found in "json_settings_dictionary" in the empty JSON file, 
            #with four space indentations to make it more human-readable.
            json.dump(json_settings_dictionary, f, indent=4)
            #Ensure the data is flushed to hardware.
            f.flush()
            #"os.fsync(f.fileno())" is required to force the OS to physically commit
            #every bit of information to the hardware storage right now, preventing 
            #a situation where an empty file might be created if the computer crashed
            #before the OS finished waiting before committing the file to memory. 
            os.fsync(f.fileno())
    return json_default_settings_dictionary, json_settings_dictionary

#The "main()" function will initialize the path variables and the "json_settings_dictionary" and 
#"json_default_settings_dictionary" dictionaries by calling the "load_json_data()" function.
#It will then initiate the main menu loop by calling the "main_menu()" function.
def main():
    #Register the Signal Interrupt (SIGINT) handler that will
    #call the "signal_interrupt_signal_handler()" function 
    #when the user presses on CTRL + C to exit the app.

    #The function "signal_interrupt_signal_handler()" will call
    #"sys.exit(0)" to exit the program normally.
    signal.signal(signal.SIGINT, signal_interrupt_signal_handler)

    cwd = os.getcwd()

    json_settings_file_path_name = os.path.join(cwd, "settings.json")

    #The function "load_json_data()" will load the JSON data from file
    #and store them in the "json_settings_dictionary", or initialize the
    #dictionary based on the values of "json_default_settings_dictionary".
    json_default_settings_dictionary, json_settings_dictionary = load_json_data(json_settings_file_path_name)

    #The "main_menu()" function will run a "while True"
    #loop that will allow the user to navigate the menu, and the
    #loop will be broken out of when they select the "Quit" option,
    #or when they press Ctrl+C (SIGINT, Signal Interrupt).
    main_menu(json_settings_dictionary, json_default_settings_dictionary, cwd, json_settings_file_path_name)

if __name__ == '__main__':

    # README_STRING = """"""

    # LICENSE_STRING = """"""

    # #Delete any mention of "README_STRING" and "LICENSE_STRING"
    # #and "SOURCE_CODE_STRING" from "SOURCE_CODE_STRING", as you 
    # #only want the Python code in there. Also, make sure to use
    # #a raw string (r''' ''') in order to avoid interpreting 
    # #backslashes ("\") as escape characters. Finally, the raw 
    # #string needs to be with single quotes in PixelArtReader,
    # #as there is a format string using (f""" """) in the code.
    # SOURCE_CODE_STRING = textwrap.dedent(r'''''')


    # #Comment out these three "with open("txt_file.txt", "w", encoding="utf-8") as f:" statements 
    # #in the code hosted on GitHub, as you will not be including the "README_STRING", "LICENSE_STRING"
    # #nor "SOURCE_CODE_STRING" on GitHub, only in the compiled version of the code so that these 
    # #would automatically get generated upon running the application.
    # with open("README.txt", "w", encoding="utf-8") as f:
        # f.write(README_STRING)

    # with open("LICENSE.txt", "w", encoding="utf-8") as f:
        # f.write(LICENSE_STRING)

    # with open("source_code.py", "w", encoding="utf-8") as f:
        # f.write(SOURCE_CODE_STRING)

    try:
        #=================================================================================== 
        #GLOBAL VARIABLES 
        #===================================================================================
        press_any_key_string = "\nPress any key to continue.\n"
        cwd = os.getcwd()
        scans_folder_name = "Scans"
        scans_folder_path = os.path.join(cwd, scans_folder_name)
        generated_png_pixel_art_files_folder_name = "Generated PNG Pixel Art Files"
        generated_png_pixel_art_files_folder_path = os.path.join(cwd, generated_png_pixel_art_files_folder_name)
        color_key_folder_path = os.path.join(scans_folder_path, "Color Key")
        black_square_side_dimension_in_template = 50
        quarter_inch_margin_pixels_at_300_dpi = 75
        excluded_border_pixels = 25
        number_of_cells_per_side_of_grid = 65 

        dpi_setting_comment_string = f"The 'Scan Resolution in DPI', with possible values of 100 and above, corresponds to the resolution, in dots per inch (DPI), of the scanned scoresheet JPEG files located in the '{scans_folder_name}' subfolder. A scan resolution of 200 DPI gives small file sizes and works reasonably well in terms of accuracy. You might want to scan your drawings at a higher DPI setting to potentially increase the accuracy of the color prediction (default setting: 200)."
        brightness_level_comment_string = "The 'Brightness Level' corresponds to the extent to which the R, G and B values (each between 0 and 255) will be lightened or darkened (for negative brightness values). It can be useful to bring the brightness down, such as to bring the darkest gray value close to zero, thus creating more headspace to spread out the remaining colors during the contrast step (default setting: 0, or no changes)."
        contrast_level_comment_string = "The 'Contrast Level' setting will adjust the contrast level of the JPEG scan images, with a contrast level of one resulting in no changes, a value less than one and greater than zero decreasing the contrast, and a value above one increasing the contrast. Increasing the contrast using a setting of around 1.1-1.2 can spread out the colors to make them easier to distinguish (default setting: 1.0, or no changes)."
        paper_color_filter_threshold_comment_string = "The 'Paper Color Filter Threshold', with possible values spanning from 0 to 255, inclusively, will determine the R, G and B value cutoff point above which the pixels on the brightness- and contrast-adjusted image will be set to 255, with the other pixels remaining the same. For example, a threshold of 245 would set all the R, G and B pixel values lighter than it (greater than 245) to 255 and the other R, G and B pixel values would be unchanged (default setting: 255, or no changes)."
        current_US_Letter_or_A4_format_string_comment_string = "The 'A4 or US Letter Format Selection' will indicate which paper format, A4 or US Letter, is to be used when generating the graph paper PDF template and when processing your scans (default setting: US Letter)."
        graph_line_pixel_width_comment_string = "The 'Graph Line Pixel Width', with possible values of 1 or above, will determine the line width in pixels of the lines making up the graph paper grid of the PDF template, at a resolution of 300 dpi (default setting 3)."
        thicker_graph_line_pixel_width_comment_string = "The 'Thicker Graph Line Pixel Width', with possible values of 1 or above, will determine the line width in pixels of the bold lines drawn at a regular interval in the graph paper grid of the PDF template, at a resolution of 300 dpi (default setting 5)."
        thicker_line_every_n_squares_comment_string = "The 'Number of Squares Between Thicker Lines', with possible values of 0 (no bold lines) or above, will determine the number of squares between bold lines in the graph paper grid of the PDF template (default setting: 5)."
        graph_line_color_rgb_tuple_string_comment_string= "The 'Graph Line RGB or Hex Code Color' will set the color of the lines of the graph paper grid of the PDF template. The color needs to either be specified as an RGB value (e.g., '255, 0, 0' for red) or a hex code (e.g., 'ff0000' for red) (default setting: 200, 200, 200)."
        percentage_of_cell_dimension_that_is_cropped_comment_string = "The 'Percentage of Cell Dimension that is Cropped' setting, with possible values between 1 and 100, will determine the width of the square cell cropping area that will be used to predict the color in every cell, expressed as a percentage of the square graph paper cell dimension. For example, a value of 50 would represent 50% of the square cell width or height. A setting between 25 and 75 works best, to ensure that enough pixels are included, while preventing the crop area from overspilling into neighboring cells. (default setting: 50)."
        pixel_art_canvas_size_width_number_of_cells_comment_string = f"The 'Number of Squares in Pixel Art Drawing Width', of which the value needs to be greater than zero, represents the total width of your final pixel art drawing, after the code automatically merges the individual {number_of_cells_per_side_of_grid}x{number_of_cells_per_side_of_grid} grids together, if applicable. For example, an image spanning two full grids in width would have a total width of {2*number_of_cells_per_side_of_grid} pixels in the unscaled PNG image (default setting: 65)."
        pixel_art_canvas_size_height_number_of_cells_comment_string = f"The 'Number of Squares in Pixel Art Drawing Height', of which the value needs to be greater than zero, represents the total height of your final pixel art drawing, after the code automatically merges the individual {number_of_cells_per_side_of_grid}x{number_of_cells_per_side_of_grid} grids together, if applicable. For example, an image spanning two full grids in height would have a total height of {2*number_of_cells_per_side_of_grid} pixels in the unscaled PNG image (default setting: 65)." 
        scaling_factor_comment_string = "The 'Scaling Factor', expressed in integer values above zero (e.g., 1, 2, 10, 20, etc.), represents the number of times that the pixel art will be scaled by to generate the final PNG image, with a scaling factor of one yielding the original size. For example, a scaling factor of 10 would convert an initial drawing of 65 x 65 graph paper squares to a 650 x 650 pixel PNG image (default value: 1)."
        number_of_colors_in_color_key_excluding_white_comment_string = "The 'Number of Colors Excluding White in Pixel Art Drawing', of which the value needs to be at least one, represents the number of colors used in the pixel art drawing and in the scanned color key, excluding white, which is the page color. For example, should the drawing include blue, red, green, and black colors and some squares that were left in the white paper color, a value of 4 would be used (default setting: 2)."
        is_grayscale_mode_on_comment_string = "The 'Grayscale Mode' will determine whether or not the Grayscale Mode is enabled, which leads to faster computation times if your drawing was either drawn or scanned in grayscale (default setting: False, or OFF)."
        
        main()

    except Exception as e:
        #The function "get_terminal_dimensions()" will return the number of columns 
        #and rows in the console, to allow to properly format the text and dividers.
        columns, lines = get_terminal_dimensions()
        troubleshooting_step_1_string = textwrap.fill("1. Please manually back up 'settings.json' if you need to salvage your user settings.", width=columns)
        troubleshooting_step_2_string = textwrap.fill("2. Once backed up, you can delete the original copy of 'settings.json' in the root folder to reset to the default settings and launch the app again.", width=columns)

        print("\n" + "=" * columns)
        print("CRITICAL ERRROR ENCOUNTERED")
        print("\nDetails:", e)
        print("\n" + "=" * columns)

        print("\nTroubleshooting Steps:\n")
        print(troubleshooting_step_1_string)
        print(troubleshooting_step_2_string)

        #The function "write_entry_in_error_log()" will write 
        #the full technical traceback error to the error log.
        write_entry_in_error_log()

        #Exit with error code
        sys.exit(1)
