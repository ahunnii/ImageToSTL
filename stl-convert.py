from csdt_stl_converter import image2stl
from numpy import asarray
from PIL import Image
import numpy as np
import cv2 # Python bindings for OpenCV
from scipy.ndimage import gaussian_filter
import trimesh
from csdt_stl_tools import numpy2stl


def convert_to_stl(img_array, output_file_directory, base=False, output_scale=0.1):

    make_it_solid = True  # Change this False to make it hollow; True to make the image solid
    exclude_gray_shade_darker_than = 1.0  # Change this to change what colors should be excluded

    python_only = False

    if base:
        return numpy2stl(img_array, output_file_directory,
                scale=output_scale,
                solid=make_it_solid,
                force_python=python_only)
    else:
        return numpy2stl(img_array, output_file_directory,
                scale=output_scale,
                solid=make_it_solid,
                max_height=50,
                mask_val=exclude_gray_shade_darker_than,
                force_python=python_only)




def convert_image_to_stl(input_name="./input/horns.png", output_name="./output/horns.stl"):
    with open(output_name, 'wb') as f:
        f.write(convert_adinkra(input_image_directory=input_name))


def convert_adinkra(input_image_directory='./Stage (19).png',
                      output_stl_directory='./test.stl',

                      include_base=False,
                      smooth=True,
                      negative=True,
                      size=[480, 360],
                      scale=0.5,
                      cookie_raft=[0,255, 255, 255]
                      
                      ):

    # image = Image.open(input_image_directory)

    # img_array = np.array(image)

    # if img_array.shape == 4:
    #     white_pixel = [255, 255, 255]
    #     whitened_img_array = image2stl.convert_transparent_to(img_array, white_pixel)
    # else:
    #     whitened_img_array = img_array

    # resized_image = image2stl.convert_to_standard_size(whitened_img_array, size)
    # grayscaled_image = image2stl.grayscale(resized_image)

    # if smooth is True:
    #     smoothed_image = image2stl.smooth_image(grayscaled_image, 0.5)
    # else:
    #     smoothed_image = grayscaled_image

    # if negative is True:
    #     inverted_image = smoothed_image
    # else:
    #     inverted_image = image2stl.grayscale_negative(smoothed_image)

    # if include_base is True:
    #     print("Adding a base: Enabled")
    # else:
    #     print("Adding a base: Disabled")

    # print("Generating the corresponding STL file")

    # Load the image and convert it to grayscale
    img = Image.open(input_image_directory).convert('RGBA')

    # Convert the image to a numpy array
    img_array = np.array(img)

    # Define the scaling factor for all dimensions
    scale = 0.1

    # Define the color thresholds for setting pixel heights
    black_thresh = 0.6
    white_thresh = 0.2
    red_thresh = 0.3
    red_color = np.array(cookie_raft) / 255.0

    # Convert the image to grayscale
    gray_img = img.convert('L')

    # Rescale the pixel values from [0, 255] to [0, 1]
    gray_array = np.array(gray_img) / 255.0

    # Compute the distance between each pixel value and black
    black_dist = np.abs(gray_array - 0)

    # Compute the distance between each pixel color value and red
    red_dist = np.linalg.norm(img_array - red_color, axis=-1)

    # Create a mask for black pixels
    black_mask = black_dist < black_thresh

    # Create a mask for white pixels
    white_mask = gray_array > 1.0 - white_thresh

    # Create a mask for red pixels
    red_mask = red_dist < red_thresh

    # Create a mask for all other pixels
    other_mask = ~(black_mask | white_mask | red_mask)


    smoothed_array = gaussian_filter(gray_array, sigma=1.5)

    # Set the height of black pixels to 100
    smoothed_array[black_mask] = 500

    # Set the height of white pixels to 0
    smoothed_array[white_mask] = 0

    # Set the height of red pixels to 25
    smoothed_array[red_mask] = 25

    # Set the height of all other pixels to 50
    smoothed_array[other_mask] = 50

    
    stl_data = convert_to_stl(smoothed_array, output_stl_directory, include_base, scale)

    return stl_data


convert_image_to_stl()


# Load the mesh from the STL file
mesh = trimesh.load_mesh('./output/horns.stl')


# Make a copy of the original vertices for later use
original_vertices = mesh.vertices.copy()

# Perform Laplacian smoothing
smoothed_mesh = mesh.copy()
smoothed_mesh = trimesh.smoothing.filter_humphrey(smoothed_mesh, alpha=1, beta=1, iterations=10)

# Project the smoothed vertices back to their original height
heights = original_vertices[:, 2]  # assuming Z-axis represents the height
smoothed_vertices = smoothed_mesh.vertices
smoothed_vertices[:, 2] = heights

# Update the mesh with the modified vertices
smoothed_mesh.vertices = smoothed_vertices

# Save the smoothed mesh as an STL file
smoothed_mesh.export('./output/horns_smoothed.stl')