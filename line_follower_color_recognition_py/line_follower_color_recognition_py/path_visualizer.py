import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from std_msgs.msg import Int32, ColorRGBA
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

class PathVisualizer(Node):
    def __init__(self):
        super().__init__('path_visualizer')

        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            10
        )

        self.color_sub = self.create_subscription(
            Int32,
            'line_color',
            self.color_callback,
            10
        )

        # Publisher
        self.marker_pub = self.create_publisher(
            Marker,
            'path_marker',
            10
        )

        self.current_color = 0
        self.previous_point = None

        # Marker
        self.marker = Marker()
        self.marker.header.frame_id = "odom"
        self.marker.ns = "path"
        self.marker.id = 0
        self.marker.type = Marker.LINE_LIST
        self.marker.action = Marker.ADD
        self.marker.scale.x = 0.05
        self.marker.pose.orientation.w = 1.0

    def color_callback(self, msg):
        self.current_color = msg.data

        self.get_logger().info(f"Current line color_idx: {self.current_color}")

    def odom_callback(self, msg):
        current_point = Point()
        current_point.x = msg.pose.pose.position.x
        current_point.y = msg.pose.pose.position.y
        current_point.z = msg.pose.pose.position.z

        if self.previous_point is not None:
            self.marker.points.append(self.previous_point)
            self.marker.points.append(current_point)

            color = self.get_color(self.current_color)
            self.marker.colors.append(color)
            self.marker.colors.append(color)

            self.marker_pub.publish(self.marker)
        
        self.previous_point = current_point

    def get_color(self, color_idx):
        if color_idx == 0: # Red
            return ColorRGBA(r=1.0, g=0.0, b=0.0, a=1.0)
        if color_idx == 1: # Green
            return ColorRGBA(r=0.0, g=1.0, b=0.0, a=1.0)
        if color_idx == 2: # Blue
            return ColorRGBA(r=0.0, g=0.0, b=1.0, a=1.0)

def main(args=None):
    rclpy.init(args=args)

    node = PathVisualizer()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()