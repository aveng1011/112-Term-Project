import cv2
from cmu_graphics import *

def takePicture(app):
    camera = cv2.VideoCapture(0)
    app.capturedImage

    if not camera.isOpened():
        print("Error: Could not access the camera.")
        exit()

    cv2.namedWindow("Camera Feed")

    while True:
        ret, frame = camera.read()

        if not ret:
            print("Error: Could not capture image.")
            break

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
# import cv2
# from cmu_graphics import *

# def onAppStart(app):
#     app.camera = cv2.VideoCapture(0)
#     app.frame = None
#     app.cameraMode = False
#     takePicture(app)
    

# def takePicture(app):
#     app.camera = cv2.VideoCapture(0)
#     app.cameraMode = True 

#     if not app.camera.isOpened():
#         print("Error: Could not access the camera.")
#         exit()

#     cv2.namedWindow("Camera Feed")

#     while app.cameraMode == True:
#         ret, app.frame = app.camera.read()
#         if not ret:
#             print("Error: Could not capture image.")
#             break
#         cv2.imshow("Camera Feed", app.frame)

#         key = cv2.waitKey(1) & 0xFF


# def onKeyPress(app, key):
#     if key == 't':
#         cv2.imwrite("captured_image.jpg", app.frame)
#         print("Image saved successfully.")
#         closeCamera()
#     elif key == 'q':
#         print("Exiting without saving image.")
#         closeCamera()


# def closeCamera(app):
#     app.cameraMode = False
#     app.camera.release()
#     cv2.destroyAllWindows()


# def redrawAll(app):
#     drawCircle(20, 20, 3, fill='black')

# def main():
#     runApp()

# main()