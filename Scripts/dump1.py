import RRT_star as RRT_star
import RRT as RRT
import cv2

model = RRT_star.RRT_star((473, 365), (100, 100), 20000, 50, 30)
model.read_image("processed_map.png")
model.run_loop()
