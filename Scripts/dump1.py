import RRT_star as RRT_star
import RRT as RRT
import RRT_star2
import RRT_connect
import cv2

model = RRT_star.RRT_star((452, 213), (473, 365), 1000, 30, 500, "processed_map.png")
# model = RRT_star2.RRT_star((452, 213), (473, 365), 800, 100, 30)
model.run_loop()