import rclpy 
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

class CamSub(Node):
    def __init__(self):
        super().__init__("cam_sub")
        self.get_logger().info("camera subscriber node activated")
        self.bridge = CvBridge()
        self.detection_subscription = self.create_subscription(Image,"/camera/image_raw",self.detection_callback,10)
        self.image_center_x = None

    def detection_callback(self,msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        
        if self.image_center_x is None:
            height, width = cv_image.shape[:2]
            self.image_center_x = width // 2
            self.image_width = width
            self.image_height = height
            self.get_logger().info(f"Image dimensions: {width}x{height}")

    
def main(args=None):
    rclpy.init(args=args)
    node = CamSub()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()