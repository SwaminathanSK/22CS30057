import cv2
import numpy as np

image = cv2.imread("processed_map.png")
cv2.imwrite("processed_map.png", image)

def make_config_space(image, width, height):
    list = []
    for i in range(width):
        for j in range(height):
            if (image[j, i] != (0, 0, 255)).any():
                for x in range(i-1, i+2):
                    for y in range(j-1, j+2):
                        if x in range(width) and y in range(height) and (image[y, x] == (0, 0, 255)).all():
                            list.append((i, j))
    return list

config_space = make_config_space(image, image.shape[1], image.shape[0])
width = image.shape[1]
height = image.shape[0]
for x in config_space:
    if (image[x[1], x[0]] != (255, 255, 255)).any() and (image[x[1], x[0]] != (255, 0, 0)).any():
        image[x[1], x[0]] = (0, 0, 255)

cv2.imshow("image", image)
cv2.imwrite("processed_map2.png", image)
if cv2.waitKey(0) == 'q':
    cv2.destroyAllWindows()