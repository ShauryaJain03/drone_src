import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from uav_msgs.msg import DetectedObject #type: ignore
from builtin_interfaces.msg import Time
from ultralytics import YOLO

class Detection(Node):
    def __init__(self):
        super().__init__("detection_node")
        self.subscription = self.create_subscription(Image,"/camera/image_raw",self.image_callback,10)
        
        self.detection_publisher = self.create_publisher(DetectedObject,"/uav/detections",10)
        
        self.bridge = CvBridge()
        self.model = YOLO('yolov8s.pt')
        self.get_logger().info("Detection node started")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        
        results = self.model.predict(frame, classes=[0, 2])
        images = results[0]

        current_time = self.get_clock().now().to_msg()

        for det in images.boxes:
            cls_id = int(det.cls)
            class_name = self.model.names[cls_id]
            conf = float(det.conf)
            xmin, ymin, xmax, ymax = map(int, det.xyxy[0].tolist())
            
            self.get_logger().info(f"Detected: {class_name} ({conf:.2f})")
            
            detection_msg = DetectedObject()
            detection_msg.class_name = class_name
            detection_msg.confidence = conf
            detection_msg.xmin = xmin
            detection_msg.ymin = ymin
            detection_msg.xmax = xmax
            detection_msg.ymax = ymax
            detection_msg.stamp = current_time
            
            self.detection_publisher.publish(detection_msg)

        cv2.imshow("detections", images.plot())
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = Detection()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()