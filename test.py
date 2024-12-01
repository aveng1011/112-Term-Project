import cv2
import numpy as np
from PIL import Image, ImageOps
import os


from PIL import Image
import os

# Path to your GIF
gif_path = "assets/heart.gif"

# Directory to save frames
output_directory = "assets/heart_animation/"
os.makedirs(output_directory, exist_ok=True)

# Open the GIF
with Image.open(gif_path) as gif:
    frame_number = 0
    while True:
        # Save the current frame as a PNG file
        frame_path = os.path.join(output_directory, f"frame_{frame_number}.png")
        gif.save(frame_path)
        print(f"Saved {frame_path}")
        
        frame_number += 1
        try:
            # Move to the next frame
            gif.seek(frame_number)
        except EOFError:
            # No more frames
            break

print("All frames have been extracted and saved.")


# def overLayImage(maskPath, imagePath, outputPath):
#     mask = Image.open(maskPath)
#     image = Image.open(imagePath)

#     maskW, maskH = mask.size

#     image = image.resize(mask.size)
#     image = image.convert('RGBA')

#     mask_pixels = mask.load()
#     image_pixels = image.load()
#     for y in range(maskH):
#         for x in range(maskW):
#             if mask_pixels[x,y] == 0:
#                 image_pixels[x,y] = (255, 255, 255, 0)
#     image.save(outputPath)


# overLayImage('shirt_mask.png', 'captured_image.jpg', 'result.png')

