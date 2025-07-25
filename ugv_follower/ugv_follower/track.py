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
        super().__init__("detection_tracking_node")
        self.subscription = self.create_subscription(
            Image, "/camera/image_raw", self.image_callback, 10)
        self.detection_publisher = self.create_publisher(
            DetectedObject, "/uav/detections", 10)
        self.tracked_img_pub = self.create_publisher(
            Image, "/uav/tracked_image", 10)

        self.bridge = CvBridge()
        self.model = YOLO('yolov8s.pt')
        self.get_logger().info("Detection+Tracking node started")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        results = self.model.track(frame, tracker='bytetrack.yaml', classes=[0, 2])
        result = results[0]

        current_time = self.get_clock().now().to_msg()
        for det in result.boxes:
            cls_id = int(det.cls)
            class_name = self.model.names[cls_id]
            conf = float(det.conf)
            xmin, ymin, xmax, ymax = map(int, det.xyxy[0].tolist())
            track_id = int(det.id) if hasattr(det, 'id') and det.id is not None else -1


            msg_out = DetectedObject()
            msg_out.class_name = class_name
            msg_out.confidence = conf
            msg_out.xmin = xmin
            msg_out.ymin = ymin
            msg_out.xmax = xmax
            msg_out.ymax = ymax
            msg_out.stamp = current_time
            msg_out.track_id = track_id 
            self.detection_publisher.publish(msg_out)

        tracked_img = result.plot() 
        tracked_img_msg = self.bridge.cv2_to_imgmsg(tracked_img, encoding="bgr8")
        self.tracked_img_pub.publish(tracked_img_msg)

      
        cv2.imshow("detections+tracking", tracked_img)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = Detection()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()