import RRT_star as RRT_star
import RRT as RRT
import RRT_star2
import RRT_connect
import cv2

# model = RRT_connect.RRT_star((473, 365), (452, 213), 300, 50, 30)
model = RRT_connect.RRT_star((347, 195), (452, 213), 3000, 100, 30)
model.read_image("processed_map.png")
model.run_loop()
