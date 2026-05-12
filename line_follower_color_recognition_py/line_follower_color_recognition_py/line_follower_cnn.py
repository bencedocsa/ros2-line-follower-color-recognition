import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32
from ament_index_python.packages import get_package_share_directory

from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.compat.v1 import InteractiveSession
from tensorflow.compat.v1 import ConfigProto
from tensorflow.keras import __version__ as keras_version
import tensorflow as tf
import h5py
import zipfile
import json

import cv2
import numpy as np
import threading
import time

class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('image_subscriber')

        # Set image size
        self.image_size = 24

        # Initialize Tensorflow session
        self.config = ConfigProto()
        self.config.gpu_options.allow_growth = True
        self.session = InteractiveSession(config=self.config)

        pkg_line_follower_color_recognition_py = get_package_share_directory('line_follower_color_recognition_py')
        model_path = pkg_line_follower_color_recognition_py + "/network_model/model.best.keras"

        print("Tensorflow version: %s" % tf.__version__)
        keras_version_str = str(keras_version)
        print("Keras version: %s" % keras_version_str)
        print("CNN model: %s" % model_path)

        # Fetch the saved Keras version used to produce the file
        model_version = self.get_keras_version_from_keras_file(model_path)
        print("Model's Keras version:", model_version)

        if model_version != keras_version_str:
            print('You are using Keras version', keras_version_str, ', but the model was built using', model_version)
            exit()

        # Finally load model:
        self.model = load_model(model_path, custom_objects=None, compile=True, safe_mode=True)
        self.model.summary()

        self.last_time = time.time()

        self.subscription = self.create_subscription(
            CompressedImage,
            'image_raw/compressed',  # topic name
            self.image_callback,
            1  # Queue size of 1
        )

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        self.color_publisher = self.create_publisher(Int32, 'line_color', 10)
        
        # Initialize CvBridge
        self.bridge = CvBridge()
        
        # Variable to store the latest frame
        self.latest_frame = None
        self.frame_lock = threading.Lock()  # Lock to ensure thread safety
        
        # Flag to control the display loop
        self.running = True

        # Start a separate thread for spinning (to ensure image_callback keeps receiving new frames)
        self.spin_thread = threading.Thread(target=self.spin_thread_func)
        self.spin_thread.start()

    def spin_thread_func(self):
        """Separate thread function for rclpy spinning."""
        while rclpy.ok() and self.running:
            rclpy.spin_once(self, timeout_sec=0.05)

    def image_callback(self, msg):
        """Callback function to receive and store the latest frame."""
        # Convert ROS Image message to OpenCV format and store it
        with self.frame_lock:
            #self.latest_frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.latest_frame = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding="bgr8")

    def display_image(self):
        # Create a single OpenCV window
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("frame", 800,600)

        while rclpy.ok():
            # Check if there is a new frame available
            if self.latest_frame is not None:
                # Process the current image
                self.process_image(self.latest_frame)

                # Show the latest frame
                cv2.imshow("frame", self.latest_frame)
                self.latest_frame = None  # Clear the frame after displaying

            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_robot()
                self.running = False
                break

        # Close OpenCV window after quitting
        cv2.destroyAllWindows()
        self.running = False

    def process_image(self, img):
        msg = Twist()
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.0

        color_msg = Int32()

        image = cv2.resize(img, (self.image_size, self.image_size))
        image = img_to_array(image)
        image = np.array(image, dtype="float") / 255.0

        image = image.reshape(-1, self.image_size, self.image_size, 3)
        
        with tf.device('/gpu:0'):
            prediction = self.model.predict(image)

            direction_pred = prediction[0]
            color_pred = prediction[1]

            direction_idx = np.argmax(direction_pred)
            color_idx = np.argmax(color_pred)

        directions = [
            "forward",
            "right",
            "left"
        ]
        colors = [
            "red",
            "green",
            "blue"
        ]

        if color_idx == 0: # Red
            colorSpeedFactor = 1.0
        elif color_idx == 1: # Green
            colorSpeedFactor = 0.9
        elif color_idx == 2: # Blue
            colorSpeedFactor = 1.1

        color_msg.data = int(color_idx)

        if direction_idx == 0: # Forward
            msg.angular.z = 0.0
            msg.linear.x = 0.08 * colorSpeedFactor
        elif direction_idx == 1: # Right
            msg.angular.z = -0.3
            msg.linear.x = 0.05 * colorSpeedFactor
        elif direction_idx == 2: # Left
            msg.angular.z = 0.3
            msg.linear.x = 0.05 * colorSpeedFactor

        print("Prediction: %s %s, colorSpeedFactor: %.1f, elapsed time: %.3f" % (colors[color_idx], directions[direction_idx], colorSpeedFactor, time.time()-self.last_time))
        self.last_time = time.time()

        # Publish cmd_vel
        self.publisher.publish(msg)
        self.color_publisher.publish(color_msg)

    # Helper to read the .keras file's metadata
    def get_keras_version_from_keras_file(self, path):
        with zipfile.ZipFile(path, 'r') as archive:
            # Look for metadata.json (exact filename may vary in future versions)
            if 'metadata.json' in archive.namelist():
                with archive.open('metadata.json') as f:
                    metadata = json.load(f)
                    return metadata.get('keras_version', 'Unknown')
            return 'Unknown'

    def stop_robot(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.0

        self.publisher.publish(msg)

    def stop(self):
        """Stop the node and the spin thread."""
        self.running = False
        self.spin_thread.join()

def main(args=None):

    print("OpenCV version: %s" % cv2.__version__)

    rclpy.init(args=args)
    node = ImageSubscriber()
    
    try:
        node.display_image()  # Run the display loop
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()  # Ensure the spin thread and node stop properly
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()