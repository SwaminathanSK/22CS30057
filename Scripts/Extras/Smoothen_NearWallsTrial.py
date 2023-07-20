import cv2
import numpy as np
import RRT_star

class check_dynamics():
    def __init__(self):
        self.none = None

    def check(self, image, graph, point0, point1):
        x0 = point0[0]
        x1 = point1[0]
        y0 = point0[1]
        y1 = point1[1]
        if (x1 - x0) == 0:
            if y0 > y1:
                return self.plotVer(x1, y1, x0, y0, image)
            else:
                return self.plotVer(x0, y0, x1, y1, image)
        elif (y1 - y0) == 0:
            if x0 > x1:
                return self.plotHor(x1, y1, x0, y0, image)
            else:
                return self.plotHor(x0, y0, x1, y1, image)
        else:
            if abs(y1 - y0) < abs(x1 - x0):
                if x0 > x1:
                    return self.plotLineLow(x1, y1, x0, y0, image)
                else:
                    return self.plotLineLow(x0, y0, x1, y1, image)
            else:
                if y0 > y1:
                    return self.plotLineHigh(x1, y1, x0, y0, image)
                else:
                    return self.plotLineHigh(x0, y0, x1, y1, image)
    def plotLineLow(self, x0, y0, x1, y1, image):
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy
        D = (2 * dy) - dx
        y = y0
        for x in range(x0, x1 + 1):
            if (image[y-1, x] == (0, 0, 255)).all():
                return (0, (x, y+1))
            if (image[y+1, x] == (0, 0, 255)).all():
                return (1, (x, y-1))
            if (image[y, x-1] == (0, 0, 255)).all():
                return (2, (x+1, y))
            if (image[y, x+1] == (0, 0, 255)).all():
                return (3, (x-1, y))
            if D > 0:
                y = y + yi
                D = D + 2 * (dy - dx)
            else:
                D = D + 2 * dy
        return (4, -1)


    def plotLineHigh(self, x0, y0, x1, y1, image):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0:
            xi = -1
            dx = -dx
        D = (2 * dx) - dy
        x = x0
        for y in range(y0, y1 + 1):
            if (image[y - 1, x] == (0, 0, 255)).all():
                return (0, (x, y + 1))
            if (image[y + 1, x] == (0, 0, 255)).all():
                return (1, (x, y - 1))
            if (image[y, x-1] == (0, 0, 255)).all():
                return (2, (x + 1, y))
            if (image[y, x + 1] == (0, 0, 255)).all():
                return (3, (x - 1, y))
            if D > 0:
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                D = D + 2 * dx
        return (4, -1)


    def plotVer(self, x0, y0, x1, y1, image):
        x = x0
        for y in range(y0, y1 + 1):
            if (image[y - 1, x] == (0, 0, 255)).all():
                return (0, (x, y + 1))
            if (image[y + 1, x] == (0, 0, 255)).all():
                return (1, (x, y - 1))
            if (image[y, x - 1] == (0, 0, 255)).all():
                return (2, (x + 1, y))
            if (image[y, x + 1] == (0, 0, 255)).all():
                return (3, (x - 1, y))
        return (4, -1)


    def plotHor(self, x0, y0, x1, y1, image):
        y = y0
        for x in range(x0, x1 + 1):
            if (image[y - 1, x] == (0, 0, 255)).all():
                return (0, (x, y + 1))
            if (image[y + 1, x] == (0, 0, 255)).all():
                return (1, (x, y - 1))
            if (image[y, x - 1] == (0, 0, 255)).all():
                return (2, (x + 1, y))
            if (image[y, x + 1] == (0, 0, 255)).all():
                return (3, (x - 1, y))
        return (4, -1)

path = [(504, 369), (443, 363), (414, 363), (405, 359), (397, 359), (377, 359), (331, 356), (282, 364), (256, 353), (216, 357), (172, 351), (170, 331), (207, 293), (247, 300), (281, 292), (289, 258), (290, 237), (297, 234), (345, 232), (346, 202), (373, 200), (376, 199), (385, 190), (384, 173), (399, 169), (403, 168), (450, 175), (449, 178), (451, 180), (446, 201), (450, 211), (452, 213)]
path = path[::-1]

image = cv2.imread("final2.png")

checker = check_dynamics()

for i in range(len(path)-1):
    check = checker.check(image, [], path[i], path[i+1])
    if check[0] != 4:
        path = path[:i+1] + [check[1]] + path[i+1:]

print(path)

