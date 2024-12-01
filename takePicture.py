import cv2
from cmu_graphics import *
import numpy as np

def overlay_image_alpha(img, overlay, x, y, alpha_mask=None):
    h, w = overlay.shape[:2]
    roi = img[y:y+h, x:x+w]
    if overlay.shape[2] == 4: 
        alpha_mask = overlay[:, :, 3] / 255.0 
        overlay = overlay[:, :, :3]  
    overlay_resized = cv2.resize(overlay, (roi.shape[1], roi.shape[0]))
    alpha_mask_resized = cv2.resize(alpha_mask, (roi.shape[1], roi.shape[0]))
    alpha_mask_resized = np.dstack([alpha_mask_resized] * 3)
    img[y:y+h, x:x+w] = (roi * (1 - alpha_mask_resized) + overlay_resized * alpha_mask_resized).astype(np.uint8)


def takePicture(app):
    camera = cv2.VideoCapture(0)

    guide = cv2.imread('assets/templates/shirt.png', cv2.IMREAD_UNCHANGED)

    if guide.shape[2] == 4:
        guideRGB = guide[:, :, 3]
        guideA = guide[:,:,3] / 255


    if not camera.isOpened():
        print("Error: Could not access the camera.")
        exit()

    cv2.namedWindow("Camera Feed")

    while True:
        ret, frame = camera.read()
        width, height, __ = frame.shape
        gWidth, gHeight, ___ = guide.shape

        if not ret:
            print("Error: Could not capture image.")
            break

        guideX = (width-gWidth) //2
        guideY = (height-gHeight) //2

        overlay_image_alpha(frame, guide, guideX, guideY, guideA)
        frame = cv2.flip(frame, 1)
        cv2.imshow("Camera Feed", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):  
            cv2.imwrite("captured_image.jpg", frame)
            print("Image saved successfully.")
            app.capturedImage = "captured_image.jpg"
            break

        elif key == ord('q'):
            print("Exiting without saving image.")
            break

    camera.release()
    cv2.destroyAllWindows()

def onAppStart(app):
    app.capturedImage = None

def onKeyPress(app, key):
    if key == 't':
        takePicture(app)

def redrawAll(app):
    drawLabel('press t to open camera and press space to take picture', app.width/2, 20)
    drawLabel('press q to close camera', app.width/2, 40)
    
    if app.capturedImage != None:
        drawImage(app.capturedImage, app.width/2, app.height/2, width=150, height=80, align='center')

def main():
    runApp()

main()
