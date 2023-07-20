import cv2
import numpy as np
import random

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
        self.config_space = []
        self.path = []
        self.complete_space = []

    def read_image(self, image):
        self.image = cv2.imread(image)
        self.height = self.image.shape[0]
        self.width = self.image.shape[1]

    def make_complete_space(self):
        list = []
        for i in range(self.width):
            for j in range(self.height):
                list.append((i, j))
        return list

    def mid_point(self, pointa, pointb):
        mp = (int((pointa[0]+pointb[0])/2), int((pointa[1]+pointb[1])/2))
        return mp

    def gaussian_sampling(self, mean_point, cov = np.array([[150, 0], [0, 150]])):
        rand = np.random.multivariate_normal(mean_point, cov)
        rand = (int(rand[0]), int(rand[1]))
        return rand

    def uniform_sampling(self):
        rand = random.choices(self.config_space, k = 1)[0]
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
                if pointc in self.config_space:
                    return pointc
        return False

    def combined_sampling(self):
        choice = self.combined_choice(10, 5)
        if choice == 0:
            while True:
                pointc = self.bridge_test()
                if pointc:
                    break
        elif choice == 1:
            while True:
                pointc = self.uniform_sampling()
                if pointc:
                    break
        return pointc

    def make_config_space(self, image):
        list = []
        for i in range(self.width):
            for j in range(self.height):
                if (self.image[j, i] != (0, 0, 255)).any():
                    list.append((i, j))
        return list

    def plot_sample(self):
        list_of_points = []
        self.config_space = self.make_config_space(self.image)
        self.complete_space = self.make_complete_space()
        num = 0

        while num < self.max_number:
            point_plot = self.combined_sampling()
            list_of_points.append(point_plot)
            self.image[point_plot[1], point_plot[0]] = (255, 255, 255)
            num+=1
            cv2.waitKey(1)
            cv2.imshow("image", self.image)

        return (self.image, list_of_points)

model = RRT_star((0, 0), (100, 100), 2000, 10, 10)
model.read_image("processed_map.png")
(image, list_of_points) = model.plot_sample()

print(list_of_points)

cv2.imshow("image", image)
if cv2.waitKey(0) == 'q':
    cv2.destroyAllWindows()