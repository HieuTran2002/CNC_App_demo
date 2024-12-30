from flask import Flask, request, jsonify, render_template, Response, send_from_directory
from flask_socketio import SocketIO
import base64
import cv2
import numpy as np
import os
from webcam_manager import WebcamManager
from event_manager import AppEventManager

class FlaskApp:
    app = Flask(__name__, template_folder="src", static_folder="src")
    # websocket
    socketio = SocketIO(app)
    table_count = 0

    def __init__(self):
        self.app.config['UPLOAD_FOLDER'] = 'uploads'
        self.app.config['SECRET_KEY'] = 'your_secret_key'

        self.app.config['PORT'] = 5000

        self.webcam_manager = WebcamManager()
        self.event_manager = AppEventManager()

        # Register routes
        self.register_routes()

        self.register_websocket_events()

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

    def generate_frames(self):
        """Generator for video streaming"""
        while True:
            frame = self.webcam_manager.get_frame()
            if frame is None:
                break

            # Convert the frame to bytes
            frame_bytes = self.encode_frame(frame)

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def video_feed(self):
        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def trigger_button(self):
        data = request.json
        self.event_manager.trigger_event("button_clicked", data)
        return jsonify({"status": "success"})

    def register_websocket_events(self):
        """Register WebSocket events."""
        @self.socketio.on('request_image')
        def handle_image_request(data):
            print(data['path'], data['id'])
            self.send_image(data['path'], data['id'])

        @self.socketio.on('table/random_row')
        def generate_random_row():
            # Randomly generate data for 6 columns, keeping ID unique
            import random
            from time import sleep
            self.socketio.emit('table/control', {'isEnable': '0'})
            for i in range(10):
                unique_id = str(self.table_count)
                columns = [f"{random.randint(1, 100)}" for i in range(1, 6)]
                self.add_row({'id': unique_id, 'columns': columns})
                self.table_count += 1
                sleep(1)
            self.socketio.emit('table/control', {'isEnable': '1'})

    def add_row(self, row):
        self.socketio.emit('table/add_row', row)

    def send_image(self, image, id):
        image_path = image
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            base64_image = base64.b64encode(img_data).decode('utf-8')

        # Sending the image along with the ID in the message
        response = {'id': id, 'image': base64_image}
        self.socketio.emit('image_data', response)

    def send_matlike(self, image, id):
        # Encode the Mat-like image to JPEG
        success, buffer = cv2.imencode('.jpg', image)
        if not success:
            raise ValueError("Failed to encode image.")

        # Convert the encoded image to base64
        base64_image = base64.b64encode(buffer).decode('utf-8')

        # Prepare the response
        response = {'id': id, 'image': base64_image}

        # Emit the data through the socket
        self.socketio.emit('image_data', response)

    def finetune_viewer(self):
        return render_template('finetune.html')

    def pdf_viewer(self):
        return render_template('pdf.html')

    def manual(self):
        return render_template('manual.html')

    def table(self):
        return render_template('table.html')

    def index(self):
        return render_template('index.html')

    def register_routes(self):
        """Main routes""" 
        self.app.route('/')(self.pdf_viewer)
        self.app.route('/index')(self.index)
        self.app.route('/table')(self.table)
        self.app.route('/ft')(self.finetune_viewer)
        self.app.route('/video_feed')(self.video_feed)
        self.app.route('/upload', methods=['POST'])(self.upload_file)
        self.app.route('/uploads/<filename>')(self.serve_file)
        self.app.route('/trigger_button', methods=['POST'])(self.trigger_button)
        self.app.route('/manual')(self.manual)

    def run(self, debug=False):
        # self.app.run(host="0.0.0.0", debug=debug, port=self.app.config['PORT'])
        self.socketio.run(self.app, host='0.0.0.0', port=self.app.config['PORT'], debug=debug)

if __name__ == '__main__':
    flask_app = FlaskApp()

    # Clear the 'uploads' directory upon exit.
    import atexit
    atexit.register(flask_app.cleanup_upload_folder)

    # Start the server
    flask_app.run(debug=True)

