import cv2

image = cv2.imread("processed_map.png")
cv2.imshow("image", image)

if cv2.waitKey(0) == 'q':
    cv2.destroyAllWindows