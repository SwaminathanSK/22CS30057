from random import choice
import random
import math
import numpy as np
import os
import cv2

class RRT_star():
    def __init__(self, starting_point, ending_point, max_number, step, radius):
        self.starting_point = starting_point
        self.ending_point = ending_point
        self.max_number = max_number
        self.graph = {starting_point:[0, -1]}
        self.image = np.array([[]])
        self.height = 0
        self.width = 0
        self.black = (0,0,0)
        self.red = (0,0,255)
        self.white = (255,255,255)
        self.step = step
        self.radius = radius
        self.config_space = {}
        self.path = []
        self.complete_space = []
        self.ending_list = [self.starting_point]

    def bomb(self, green_point, rad):
        for i in range(green_point[0] - rad, green_point[0] + rad):
            for j in range(green_point[1] - rad, green_point[1] + rad):
                return 0

    def make_complete_space(self):
        list = []
        for i in range(self.width):
            for j in range(self.height):
                list.append((i, j))
        return list

    def mid_point(self, pointa, pointb):
        mp = (int((pointa[0]+pointb[0])/2), int((pointa[1]+pointb[1])/2))
        return mp

    def gaussian_sampling(self, mean_point, cov = np.array([[500, 0], [0, 500]])):
        rand = np.random.multivariate_normal(mean_point, cov)
        rand = (int(rand[0]), int(rand[1]))
        return rand

    def uniform_sampling(self):
        rand = random.choices(self.complete_space, k = 1)[0]
        return rand

    def combined_choice(self, weight1, weight2):
        choice = [0, 1]
        return random.choices(choice, (weight1, weight2), k = 1)[0]

    def bridge_test(self):
        pointa = random.choice(self.complete_space)
        if pointa not in self.config_space:
            pointb = self.gaussian_sampling(pointa)
            if pointb not in self.config_space:
                pointc = self.mid_point(pointa, pointb)
                return pointc
        return False

    def combined_sampling(self, list):
        if len(self.ending_list) > 100:
            self.ending_list = self.ending_list[-100:]
        list = self.ending_list
        rand_list = []
        for point in list:
            rand_list.append(self.gaussian_sampling(point))
        pointc = random.choice(rand_list)
        return pointc

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
        if x1 not in range(self.width) or y1 not in range(self.height):
            return False
        if (image[point1[1], point1[1]] == (0, 0, 255)).all() or (point1[0], point1[1]) == (point0[0], point0[1]) or point1 in self.graph:
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
                image = self.drawVer(x1, y1, x0, y0, image)
            else:
                image = self.drawVer(x0, y0, x1, y1, image)
        elif (y1 - y0) == 0:
            if x0 > x1:
                image = self.drawHor(x1, y1, x0, y0, image)
            else:
                image = self.drawHor(x0, y0, x1, y1, image)
        else:
            if abs(y1 - y0) < abs(x1 - x0):
                if x0 > x1:
                    image = self.drawLineLow(x1, y1, x0, y0, image)
                else:
                    image = self.drawLineLow(x0, y0, x1, y1, image)
            else:
                if y0 > y1:
                    image = self.drawLineHigh(x1, y1, x0, y0, image)
                else:
                    image = self.drawLineHigh(x0, y0, x1, y1, image)
        return self.image

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
            if image[y, x][1] < 50:
                image[y, x] = (0, 50, 0)
                if (x, y) in self.config_space:
                    self.config_space.remove((x, y))
            else:
                image[y, x] = (0, image[y, x][1] + 1, 0)
            if D > 0:
                y = y + yi
                D = D + 2*(dy - dx)
            else:
                D = D + 2*dy
        self.image = image
        cv2.imshow("plot", self.image)
        cv2.waitKey(1)
        return image

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
            if image[y, x][1] < 50:
                image[y, x] = (0, 50, 0)
                if (x, y) in self.config_space:
                    self.config_space.remove((x, y))
            else:
                image[y, x] = (0, image[y, x][1] + 1, 0)
            if D > 0:
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                D = D + 2 * dx
        self.image = image
        cv2.imshow("plot", self.image)
        cv2.waitKey(1)
        return image

    def drawVer(self, x0, y0, x1, y1, image):
        x = x0
        for y in range(y0, y1+1):
            if image[y, x][1] < 50:
                image[y, x] = (0, 50, 0)
                if (x, y) in self.config_space:
                    self.config_space.remove((x, y))
            else:
                image[y, x] = (0, image[y, x][1] + 1, 0)
        self.image = image
        cv2.imshow("plot", self.image)
        cv2.waitKey(1)
        return image

    def drawHor(self, x0, y0, x1, y1, image):
        y = y0
        for x in range(x0, x1+1):
            if image[y, x][1] < 50:
                image[y, x] = (0, 50, 0)
                if (x, y) in self.config_space:
                    self.config_space.remove((x, y))
            else:
                image[y, x] = (0, image[y, x][1] + 1, 0)
        self.image = image
        cv2.imshow("plot", self.image)
        cv2.waitKey(1)
        return True

    def erase_line(self, point0, point1, image):
        x0 = point0[0]
        x1 = point1[0]
        y0 = point0[1]
        y1 = point1[1]
        if (x1 - x0) == 0:
            if y0 > y1:
                self.eraseVer(x1, y1, x0, y0, image)
            else:
                self.eraseVer(x0, y0, x1, y1, image)
        elif (y1 - y0) == 0:
            if x0 > x1:
                self.eraseHor(x1, y1, x0, y0, image)
            else:
                self.eraseHor(x0, y0, x1, y1, image)
        else:
            if abs(y1 - y0) < abs(x1 - x0):
                if x0 > x1:
                    self.eraseLineLow(x1, y1, x0, y0, image)
                else:
                    self.eraseLineLow(x0, y0, x1, y1, image)
            else:
                if y0 > y1:
                    self.eraseLineHigh(x1, y1, x0, y0, image)
                else:
                    self.eraseLineHigh(x0, y0, x1, y1, image)
    def eraseLineLow(self, x0, y0, x1, y1, image):
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy
        D = (2*dy) - dx
        y = y0
        for x in range(x0, x1+1):
            if self.image[y, x][1] == 50:
                self.image[y, x] = (0, 0, 0)
            else:
                self.image[y, x] = (0, self.image[y, x][1]  - 1, 0)
            if D > 0:
                y = y + yi
                D = D + 2*(dy - dx)
            else:
                D = D + 2*dy
        cv2.imshow("plot", self.image)
        return True

    def eraseLineHigh(self, x0, y0, x1, y1, image):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0:
            xi = -1
            dx = -dx
        D = (2 * dx) - dy
        x = x0
        for y in range(y0, y1+1):
            if self.image[y, x][1] == 50:
                self.image[y, x] = (0, 0, 0)
            else:
                self.image[y, x] = (0, self.image[y, x][1] - 1, 0)
            if D > 0:
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                D = D + 2 * dx
        cv2.imshow("plot", self.image)
        return True

    def eraseVer(self, x0, y0, x1, y1, image):
        x = x0
        for y in range(y0, y1+1):
            if self.image[y, x][1] == 50:
                self.image[y, x] = (0, 0, 0)
            else:
                self.image[y, x] = (0, self.image[y, x][1] - 1, 0)
        cv2.imshow("plot", self.image)
        return True

    def eraseHor(self, x0, y0, x1, y1, image):
        y = y0
        for x in range(x0, x1+1):
            if self.image[y, x][1] == 50:
                self.image[y, x] = (0, 0, 0)
            else:
                self.image[y, x] = (0, self.image[y, x][1] - 1, 0)
        cv2.imshow("plot", self.image)
        return True

    def make_config_space(self, image):
        list = dict()
        for i in range(self.width):
            for j in range(self.height):
                if (self.image[j, i] != (0, 0, 255)).any():
                    list[(i, j)] = 50
        return list

    def make_path(self, point):
        path = []
        point = point
        while self.graph[point][1] != -1:
            path.append(point)
            point = self.graph[point][1]
        return path

    def send_path(self):
        return self.path

    def make_image(self, image):
        img1 = cv2.imread(image)
        path = self.send_path()
        for i in range(len(path) - 1):
            img1 = model.draw_line(path[i], path[i + 1], img1)

        return img1

    def run_loop(self):
        self.config_space = self.make_config_space(self.image)
        self.complete_space = self.make_complete_space()
        number = 0
        rand_x = -1
        rand_y = -1
        parent = (-1, -1)
        while number < self.max_number:
            (rand_x, rand_y) = self.combined_sampling(self.ending_list)
            point0 = self.nearest_pixel(self.image, self.graph, (rand_x, rand_y))
            if (rand_x, rand_y) in self.graph:
                continue
            point1 = self.new_point((rand_x, rand_y), point0, self.image, self.step)
            if not self.allowed(self.image, self.graph, point0, point1):
                continue

            parent = point0
            if parent in self.ending_list:
                self.ending_list.remove(parent)
            self.ending_list.append(point1)

            self.graph[point1] = [self.graph[point0][0] + int(self.distance(point0, point1)), parent]
            cost = self.graph[point0][0] + int(self.distance(point0, point1))
            b = int((np.log(len(self.config_space))/len(self.config_space))**0.5)
            b = 1
            for i in range(point1[0] - self.radius*b, point1[0] + self.radius*b):
                for j in range(point1[1] - self.radius*b, point1[1] + self.radius*b):
                    if (i in range(self.width)) and (j in range(self.height)):
                        if (i, j) in self.graph:
                            if cost > self.graph[(i, j)][0] + int(self.distance(point1, (i, j))):
                                if self.allowed(self.image, self.graph, point1, (i, j)):
                                    cost = self.graph[(i, j)][0] + int(self.distance(point1, (i, j)))
                                    parent = (i, j)

            self.graph[point1] = [cost, parent]
            self.draw_line(point1, parent, self.image)

            for i in range(point1[0] - self.radius*b, point1[0] + self.radius*b):
                for j in range(point1[1] - self.radius*b, point1[1] + self.radius*b):
                    if (i in range(self.width)) and (j in range(self.height)):
                        if (i, j) in self.graph and (i, j) != point1:
                            if self.graph[(i, j)][0] > self.graph[point1][0] + int(self.distance(point1, (i, j))):
                                if self.allowed(self.image, self.graph, point1, (i, j)):
                                    self.erase_line((i, j), self.graph[(i, j)][1], self.image)
                                    self.graph[(i, j)] = [self.graph[point1][0] + int(self.distance(point1, (i, j))), point1]
                                    self.draw_line((i, j), point1, self.image)

            if self.distance(point1, self.ending_point) == 0:
                return (point1, self.graph)

            number += 1
        # cv2.imshow("plot", self.image)
        cv2.destroyAllWindows()