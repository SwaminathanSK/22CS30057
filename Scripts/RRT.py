from random import choice
import random
import math
import numpy as np
import os
import cv2

class RRT():
    def __init__(self, starting_point, ending_point, max_number, step):
        self.starting_point = starting_point
        self.ending_point = ending_point
        self.max_number = max_number
        self.graph = {starting_point:[]}
        self.image = np.array([[]])
        self.height = 0
        self.width = 0
        self.black = (0,0,0)
        self.red = (0,0,255)
        self.white = (255,255,255)
        self.step = step

    def read_image(self, image):
        self.image = cv2.imread(image)
        self.height = self.image.shape[0]
        self.width = self.image.shape[1]

    def distance(self, point1, point2):
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def nearest_pixel(self, image, graph, point):
        nearest_pixel = None
        nearest_distance = None
        for vertex in graph:
            if nearest_pixel == None:
                nearest_pixel = vertex
                nearest_distance = self.distance(point, vertex)
            elif self.distance(point, vertex) < nearest_distance:
                nearest_pixel = vertex
                nearest_distance = self.distance(point, vertex)
        return nearest_pixel

    def allowed(self, image, graph, point0, point1):
        x0 = point0[0]
        x1 = point1[0]
        y0 = point0[1]
        y1 = point1[1]
        if (image[point1[1], point1[1]] == (0, 0, 255)).all() or (point1[0], point1[1]) == (point0[0], point0[1]):
            return False
        elif (x1 - x0) == 0:
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
        D = (2*dy) - dx
        y = y0
        for x in range(x0, x1+1):
            if (image[y, x] == (0, 0, 255)).all():
                return False
            if D > 0:
                y = y + yi
                D = D + 2*(dy - dx)
            else:
                D = D + 2*dy
        return True

    def plotLineHigh(self, x0, y0, x1, y1, image):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0:
            xi = -1
            dx = -dx
        D = (2 * dx) - dy
        x = x0
        for y in range(y0, y1+1):
            if (image[y, x] == (0, 0, 255)).all():
                return False
            if D > 0:
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                D = D + 2 * dx
        return True

    def plotVer(self, x0, y0, x1, y1, image):
        x = x0
        for y in range(y0, y1+1):
            if (image[y, x] == (0, 0, 255)).all():
                return False
        return True

    def plotHor(self, x0, y0, x1, y1, image):
        y = y0
        for x in range(x0, x1+1):
            if (image[y, x] == (0, 0, 255)).all():
                return False
        return True

    def new_point(self, random, nearest, image, step):
        dist = self.distance(random, nearest)
        if dist < step:
            return random
        else:
            vector = (random[0] - nearest[0], random[1] - nearest[0])
            magnitude = (vector[0]**2 + vector[1]**2)**0.5
            if magnitude < 1:
                return random
            direction = (vector[0]/magnitude, vector[1]/magnitude)
            newx = nearest[0] + int(direction[0]*step)
            newy = nearest[1] + int(direction[0]*step)
            return (newx, newy)

    def draw_line(self, point0, point1, image):
        x0 = point0[0]
        x1 = point1[0]
        y0 = point0[1]
        y1 = point1[1]
        if (x1 - x0) == 0:
            if y0 > y1:
                self.drawVer(x1, y1, x0, y0, image)
            else:
                self.drawVer(x0, y0, x1, y1, image)
        elif (y1 - y0) == 0:
            if x0 > x1:
                self.drawHor(x1, y1, x0, y0, image)
            else:
                self.drawHor(x0, y0, x1, y1, image)
        else:
            if abs(y1 - y0) < abs(x1 - x0):
                if x0 > x1:
                    self.drawLineLow(x1, y1, x0, y0, image)
                else:
                    self.drawLineLow(x0, y0, x1, y1, image)
            else:
                if y0 > y1:
                    self.drawLineHigh(x1, y1, x0, y0, image)
                else:
                    self.drawLineHigh(x0, y0, x1, y1, image)

    def drawLineLow(self, x0, y0, x1, y1, image):
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy
        D = (2*dy) - dx
        y = y0
        for x in range(x0, x1+1):
            self.image[y, x] = (0, 255, 0)
            if D > 0:
                y = y + yi
                D = D + 2*(dy - dx)
            else:
                D = D + 2*dy
        cv2.imshow("plot", self.image)
        cv2.waitKey(5)
        return True

    def drawLineHigh(self, x0, y0, x1, y1, image):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0:
            xi = -1
            dx = -dx
        D = (2 * dx) - dy
        x = x0
        for y in range(y0, y1+1):
            self.image[y, x] = (0, 255, 0)
            if D > 0:
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                D = D + 2 * dx
        cv2.imshow("plot", self.image)
        cv2.waitKey(5)
        return True

    def drawVer(self, x0, y0, x1, y1, image):
        x = x0
        for y in range(y0, y1+1):
            self.image[y, x] = (0, 255, 0)
        cv2.imshow("plot", self.image)
        cv2.waitKey(5)
        return True

    def drawHor(self, x0, y0, x1, y1, image):
        y = y0
        for x in range(x0, x1+1):
            self.image[y, x] = (0, 255, 0)
        cv2.imshow("plot", self.image)
        cv2.waitKey(5)
        return True

    def make_config_space(self, image):
        list = []
        for i in range(self.width):
            for j in range(self.height):
                if (self.image[j, i] != (0, 0, 255)).any():
                    list.append((i, j))
        return list

    def run_loop(self):
        config_space = self.make_config_space(self.image)
        number = 0
        rand_x = -1
        rand_y = -1
        while number < self.max_number:
            (rand_x, rand_y) = random.choice(config_space)
            point0 = self.nearest_pixel(self.image, self.graph, (rand_x, rand_y))
            if (rand_x, rand_y) in self.graph:
                continue
            point1 = self.new_point((rand_x, rand_y), point0, self.image, self.step)
            if not self.allowed(self.image, self.graph, point0, point1):
                continue
            if point0 in self.graph:
                self.graph[point0].append(point1)
            else:
                self.graph[point0] = [point1]
            self.graph[point1] = []
            self.draw_line(point0, point1, self.image)
            number += 1
        cv2.waitKey(10000)
        cv2.destroyAllWindows()