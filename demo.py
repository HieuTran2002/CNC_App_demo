from main import FlaskApp
import cv2

def theFunction(data):
    image = cv2.imread("./src/pics/loyd.jpeg")
    app.send_image_to_server(image, 'result1')

app = FlaskApp()
app.event_manager.button_clicked += theFunction


app.run()

