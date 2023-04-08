import cv2
from PIL import Image, ImageChops
import numpy as np

import cairosvg

# Load the PNG image
img = cv2.imread('Stage (14).png')

# ## (1) Convert to gray, and threshold
# gray_alt = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# th, threshed = cv2.threshold(gray_alt, 240, 255, cv2.THRESH_BINARY_INV)

# ## (2) Morph-op to remove noise
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
# morphed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, kernel)

# ## (3) Find the max-area contour
# cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
# cnt = sorted(cnts, key=cv2.contourArea)[-1]

# (x,y),radius = cv2.minEnclosingCircle(cnt)
# center = (int(x),int(y))
# radius = int(radius)
# cv2.circle(img,center,radius,(0,255,0),2)


# ## (4) Crop and save it
# x,y,w,h = cv2.boundingRect(cnt)
# dst = img[y:y+h, x:x+w]
# cv2.imwrite("001.png", dst)



# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Perform Canny edge detection
edges = cv2.Canny(gray, 100, 200)

# Find contours in the edges
contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

cv2.imwrite("001.png", edges)

print(len(contours))
# Create an SVG file and write the contours to it
with open('output.svg', 'w') as f:
    f.write('<?xml version="1.0" standalone="no"?>\n')
    f.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n')
    f.write('  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    f.write('<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg">\n'.format(img.shape[1], img.shape[0]))
   
    # Write the outer contour to the SVG file
    outer_contour_idx = -1

    #deconstruct size of image 
    x, y, z = img.shape

    # Define the circle parameters
    cx, cy, r = x/2 , y/2, (max(x, y) /2 -50)
    fill_color = 'rgba(255, 118, 96, 255)'


    # Construct the circle path string
    path_str = f'M {cx - r}, {cy} a {r},{r} 0 1,0 {r * 2},0 a {r},{r} 0 1,0 -{r * 2},0'

    f.write(f'<path d="{path_str}" fill="{fill_color}" />\n')
    for i, contour in enumerate(contours):
        if hierarchy[0][i][3] == -1: # Outer contour
            outer_contour_idx = i
            path_data = 'M '
            for j in range(len(contour)):
                x, y = contour[j][0]
                if j == 0:
                    path_data += '{} {} '.format(x, y)
                else:
                    path_data += 'L {} {} '.format(x, y)
            path_data += 'Z'
            f.write('<path d="{}" fill="white" stroke="black" stroke-width="5"/>\n'.format(path_data))

    # Write the inner contours to the SVG file
    for i, contour in enumerate(contours):
        if hierarchy[0][i][3] == outer_contour_idx: # Inner contour
            path_data = 'M '
            for j in range(len(contour)):
                x, y = contour[j][0]
                if j == 0:
                    path_data += '{} {} '.format(x, y)
                else:
                    path_data += 'L {} {} '.format(x, y)
            path_data += 'Z'
            f.write('<path d="{}" fill="white" stroke="black" stroke-width="5"/>\n'.format(path_data))

    # Write the contours around the holes to the SVG file
    for i, contour in enumerate(contours):
        if hierarchy[0][i][3] != -1 and hierarchy[0][hierarchy[0][i][3]][3] == outer_contour_idx: # Hole contour
            path_data = 'M '
            for j in range(len(contour)):
                x, y = contour[j][0]
                if j == 0:
                    path_data += '{} {} '.format(x, y)
                else:
                    path_data += 'L {} {} '.format(x, y)
            path_data += 'Z'
            f.write('<path d="{}" fill="white" stroke="black" stroke-width="5"/>\n'.format(path_data))
    
    f.write('</svg>\n')


width = 480
height = 480
cairosvg.svg2png(url='output.svg', write_to='final_form.png', output_width=width, output_height=height, dpi=700)


# Open the PNG image
im = Image.open("./final_form.png")

# Create a new image with a white background
rgb_im = Image.new("RGB", im.size, (255, 255, 255))

# Paste the PNG image onto the new image, making any transparent pixels white
rgb_im.paste(im, mask=im.convert("RGBA").split()[-1])

# Save the new image as a JPEG
rgb_im.save("./final_form.jpg", "JPEG")