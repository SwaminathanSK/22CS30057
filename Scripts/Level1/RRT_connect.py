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
        self.graph_prime = {ending_point:[0, -1]}
        self.image = np.array([[]])
        self.height = 0
        self.width = 0
        self.black = (0,0,0)
        self.red = (0,0,255)
        self.white = (255,255,255)
        self.step = step
        self.radius = radius
        self.config_space = []

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
            if self.image[y, x][1] < 50:
                self.image[y, x] = (0, 50, 0)
                if (x, y) in self.config_space:
                    self.config_space.remove((x, y))
            else:
                self.image[y, x] = (0, self.image[y, x][1] + 1, 0)
            if D > 0:
                y = y + yi
                D = D + 2*(dy - dx)
            else:
                D = D + 2*dy
        cv2.imshow("plot", self.image)
        cv2.waitKey(1)
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
            if self.image[y, x][1] < 50:
                self.image[y, x] = (0, 50, 0)
                if (x, y) in self.config_space:
                    self.config_space.remove((x, y))
            else:
                self.image[y, x] = (0, self.image[y, x][1] + 1, 0)
            if D > 0:
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                D = D + 2 * dx
        cv2.imshow("plot", self.image)
        cv2.waitKey(1)
        return True

    def drawVer(self, x0, y0, x1, y1, image):
        x = x0
        for y in range(y0, y1+1):
            if self.image[y, x][1] < 50:
                self.image[y, x] = (0, 50, 0)
                if (x, y) in self.config_space:
                    self.config_space.remove((x, y))
            else:
                self.image[y, x] = (0, self.image[y, x][1] + 1, 0)
        cv2.imshow("plot", self.image)
        cv2.waitKey(1)
        return True

    def drawHor(self, x0, y0, x1, y1, image):
        y = y0
        for x in range(x0, x1+1):
            if self.image[y, x][1] < 50:
                self.image[y, x] = (0, 50, 0)
                if (x, y) in self.config_space:
                    self.config_space.remove((x, y))
            else:
                self.image[y, x] = (0, self.image[y, x][1] + 1, 0)
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

    def make_config_space(self, point):
        list = []
        for i in range(self.width):
            for j in range(self.height):
                if (self.image[j, i] != (0, 0, 255)).any():
                    list.append((i, j))
        return list

    def make_config_space2(self, point):
        threshold = 50
        population = 0
        midpoint = point
        for i in range(point[0] - 2*self.radius, point[0] + 2*self.radius):
            for j in range(point[1] - 2*self.radius, point[1] + 2*self.radius):
                if i in range(0, self.width) and j in range(0, self.height):
                    if (self.image[j, i][1] > 50):
                        midpoint = (int((midpoint[0] + i)/2), int((midpoint[1] + j)/2))

        for i in range(midpoint[0] - 2*self.radius, midpoint[0] + 2*self.radius):
            for j in range(midpoint[1] - 2*self.radius, midpoint[1] + 2*self.radius):
                if i in range(0, self.width) and j in range(0, self.height):
                    if (self.image[j, i] != (0, 0, 255)).any() and (self.image[j, i][1] < 50):
                        self.config_space.append((i, j))

    def run_loop(self):
        self.config_space = self.make_config_space(self.starting_point)
        # self.make_config_space(self.ending_point)
        number = 0
        rand_x = -1
        rand_y = -1
        parent = (-1, -1)
        while number < self.max_number:
            new_node = random.choice(self.config_space)
            (rand_x, rand_y) = new_node
            if (self.image[rand_y][rand_x] == self.red).all():
                continue
            point0 = self.nearest_pixel(self.image, self.graph, (rand_x, rand_y))
            if (rand_x, rand_y) in self.graph:
                continue
            point1 = self.new_point((rand_x, rand_y), point0, self.image, self.step)
            if not self.allowed(self.image, self.graph, point0, point1):
                continue

            parent = point0
            self.graph[point1] = [0, parent]
            self.draw_line(point0, point1, self.image)

            new_random_prime = self.ending_point
            if new_random_prime not in self.graph_prime:
                new_random_prime = random.choice(self.config_space)
                new_near_prime = self.nearest_pixel(self.image, self.graph_prime, new_random_prime)
                new_node_prime = self.new_point(new_random_prime, new_near_prime, self.image, self.step)

                if self.allowed(self.image, self.graph_prime, new_node_prime, new_near_prime):
                    self.graph_prime[new_node_prime] = [0, new_near_prime]
                    self.draw_line(new_node_prime, new_near_prime, self.image)

                    self.config_space = self.make_config_space(new_node_prime)

                    while True:
                        node_new_prim2 = self.new_point(point1, new_node_prime, self.image, self.step)
                        if node_new_prim2 and self.allowed(self.image, self.graph_prime, node_new_prim2, new_node_prime):
                            self.graph_prime[node_new_prim2] = [0, new_node_prime]
                            self.draw_line(new_node_prime, node_new_prim2, self.image)
                            # self.make_config_space(node_new_prim2)
                        else:
                            break

                        if node_new_prim2 == new_node_prime:
                            break

            if len(self.graph_prime) < len(self.graph):
                list_mid = self.graph_prime
                self.graph_prime = self.graph
                self.graph = list_mid
            # self.make_config_space(point1)


            '''for i in range(point1[0] - self.radius, point1[0] + self.radius):
                for j in range(point1[1] - self.radius, point1[1] + self.radius):
                    if (i in range(self.width)) and (j in range(self.height)):
                        if (i, j) in self.graph:
                            if cost > self.graph[(i, j)][0] + int(self.distance(point1, (i, j))):
                                if self.allowed(self.image, self.graph, point1, (i, j)):
                                    cost = self.graph[(i, j)][0] + int(self.distance(point1, (i, j)))
                                    parent = (i, j)'''

            '''for i in range(point1[0] - self.radius, point1[0] + self.radius):
                for j in range(point1[1] - self.radius, point1[1] + self.radius):
                    if (i in range(self.width)) and (j in range(self.height)):
                        if (i, j) in self.graph and (i, j) != point1:
                            if self.graph[(i, j)][0] > self.graph[point1][0] + int(self.distance(point1, (i, j))):
                                if self.allowed(self.image, self.graph, point1, (i, j)):
                                    self.erase_line((i, j), self.graph[(i, j)][1], self.image)
                                    self.graph[(i, j)] = [self.graph[point1][0] + int(self.distance(point1, (i, j))), point1]
                                    self.draw_line((i, j), point1, self.image)'''

            number += 1
        # cv2.imshow("plot", self.image)
        cv2.waitKey(10000)
        cv2.destroyAllWindows()