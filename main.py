from flask import Flask, request, jsonify, render_template, Response, send_from_directory
import requests
import base64
import cv2
import numpy as np
import os
from webcam_manager import WebcamManager
from event_manager import AppEventManager

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__, template_folder="src", static_folder="src")
        self.app.config['UPLOAD_FOLDER'] = 'uploads'
        self.app.config['PORT'] = 5000

        self.webcam_manager = WebcamManager()
        self.event_manager = AppEventManager()

        # Register routes
        self.register_routes()

        # Register event handlers
        self.register_event_handlers()

        # Remove all remaining files in 'uploads' from the last session
        self.cleanup_upload_folder()

    def cleanup_upload_folder(self):
        """Remove all files in the uploads folder."""
        folder_path = self.app.config['UPLOAD_FOLDER']

        # Check if the uploads folder exists
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                # Only remove files, not subdirectories
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed: {file_path}")

    def register_event_handlers(self):
        def on_button_click(data):
            print(f"Button clicked! Data: {data}")

        def on_data_received(data):
            print(f"Data received: {data}")

        # Subscribe to events
        self.event_manager.button_clicked += on_button_click
        self.event_manager.data_received += on_data_received

    def upload_file(self):
        """Save PDF file into uploads directoty."""
        if 'pdf' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Invalid file type'}), 400

        file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        return jsonify({'message': 'File processed', 'result': file_path})

    def serve_file(self, filename):
        file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)

        # Check if the file exists
        if not os.path.exists(file_path):
            return jsonify({'error': f'File "{filename}" not found.'}), 404

        # Serve the file if it exists
        return send_from_directory(self.app.config['UPLOAD_FOLDER'], filename)

    def encode_frame(self, frame: np.ndarray) -> bytes:
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()

    def image(self):
        """No longer used"""
        uploaded_files = cv2.imread("src/pics/loyd.jpeg")
        return Response(self.encode_frame(uploaded_files), mimetype='image/jpeg')

    def generate_frames(self):
        """Generator for video streaming"""
        while True:
            frame = self.webcam_manager.get_frame()
            if frame is None:
                break

            # Convert the frame to bytes
            frame_bytes = self.encode_frame(frame)

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def process_image(self):
        """Endpoint to receive image and ID to post it onto the target element."""
        data = request.json

        if not data or 'image' not in data or 'element_id' not in data:
            return jsonify({'error': 'Missing image or element_id'}), 400

        # Decode the base64 image data
        try:
            image_data = base64.b64decode(data['image'])
            np_arr = np.frombuffer(image_data, dtype=np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        except Exception as e:
            return jsonify({'error': f'Error decoding image: {str(e)}'}), 400

        # Get the element ID
        element_id = data['element_id']

        # Here you can process the image, e.g., save it or do other operations
        image_path = os.path.join(self.app.config['UPLOAD_FOLDER'], f"{element_id}.jpg")
        cv2.imwrite(image_path, img)

        # Respond with the saved image path (or any other info)
        return jsonify({'message': 'Image processed and saved', 'image_path': image_path})

    def send_image_to_server(self, mat_image, element_id):
        """Function for users to send their Mat image and ID directly."""
        _, img_buffer = cv2.imencode('.jpg', mat_image)
        img_bytes = img_buffer.tobytes()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        # Define the URL of the Flask API endpoint
        url = f"http://localhost:{self.app.config['PORT']}/process_image"

        # Create the payload with the base64 image and element ID
        payload = {'image': img_base64, 'element_id': element_id}

        # Send POST request to the Flask server
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': 'Failed to process image', 'details': response.json()}

    def get_image_path(self, element_id):
        """Return the image path based on the element_id."""
        image_path = os.path.join(self.app.config['UPLOAD_FOLDER'], f"{element_id}.jpg")

        # Check if the image exists
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404

        return jsonify({'image_path': f"/uploads/{element_id}.jpg"})

    def video_feed(self):
        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def trigger_button(self):
        data = request.json
        self.event_manager.trigger_event("button_clicked", data)
        return jsonify({"status": "success"})

    def finetune_viewer(self):
        return render_template('finetune.html')

    def pdf_viewer(self):
        return render_template('pdf.html')

    def manual(self):
        return render_template('manual.html')

    def table(self):
        return render_template('table.html')

    def register_routes(self):
        """Main routes""" 
        self.app.route('/')(self.pdf_viewer)
        self.app.route('/table')(self.table)
        self.app.route('/ft')(self.finetune_viewer)
        self.app.route('/image')(self.image)
        self.app.route('/video_feed')(self.video_feed)
        self.app.route('/upload', methods=['POST'])(self.upload_file)
        self.app.route('/uploads/<filename>')(self.serve_file)
        self.app.route('/trigger_button', methods=['POST'])(self.trigger_button)
        self.app.route('/process_image', methods=['POST'])(self.process_image)
        self.app.route('/get_image_path/<element_id>', methods=['GET'])(self.get_image_path)
        self.app.route('/manual')(self.manual)

    def run(self, debug=False):
        self.app.run(host="0.0.0.0", debug=debug, port=self.app.config['PORT'])

if __name__ == '__main__':
    flask_app = FlaskApp()

    # Clear the 'uploads' directory upon exit.
    import atexit
    atexit.register(flask_app.cleanup_upload_folder)

    # Start the server
    flask_app.run(debug=True)

