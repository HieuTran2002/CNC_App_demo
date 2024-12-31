from main import FlaskApp
import cv2

app = FlaskApp()

def theFunction():
    image = cv2.imread("src/pics/loyd2.jpg")
    app.send_matlike(image, 'result1')
    print("upload")


app.upload += theFunction
app.run()

