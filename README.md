# CNC_App_demo

# Demo
```
from main import FlaskApp
import cv2

def theFunction(data):
    image = cv2.imread("./src/pics/loyd.jpeg")
    app.send_image_to_server(image, 'result1')

app = FlaskApp()
app.event_manager.button_clicked += theFunction


app.run()
```

## Run with camera and port binding.
```
sudo nerdctl run -p 5000:5000 --device=/dev/video0:/dev/video0 flask-cnc-app

```
