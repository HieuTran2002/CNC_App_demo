from main import FlaskApp
import cv2

app = FlaskApp()

def theFunction(data):
    image = cv2.imread("src/pics/loyd2.jpg")
    app.send_matlike(image, 'result1')


app.event_manager.button_clicked += theFunction
app.run()

