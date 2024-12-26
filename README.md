# CNC_App_demo

# Demo
```
from main import FlaskApp
import cv2

def pprint(data):
    image = cv2.imread("./src/pics/loyd.jpeg")
    app.send_image_to_server(image, 'result1')

app = FlaskApp()
app.event_manager.button_clicked += pprint


app.run(debug=True)

```
