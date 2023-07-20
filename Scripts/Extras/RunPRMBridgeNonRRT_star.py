#### Tried using the generated points as connections


import RRT_star as RRT_star
import RRT as RRT
import RRT_star2
import RRT_connect
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

    def allowed(self, image, graph, point0, point1):
        x0 = point0[0]
        x1 = point1[0]
        y0 = point0[1]
        y1 = point1[1]
        if x1 not in range(self.width) or y1 not in range(self.height):
            return False
        if (image[point1[1], point1[0]] == (0, 0, 255)).all() or (point1[0], point1[1]) == (point0[0], point0[1]):
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
        list = []
        for i in range(self.width):
            for j in range(self.height):
                if (self.image[j, i] != (0, 0, 255)).any():
                    list.append((i, j))
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



model = RRT_star((452, 213), (473, 365), 1000, 10, 10)
model.read_image("processed_map.png")

config_space =[model.starting_point, model.ending_point, (263, 134), (301, 196), (544, 99), (492, 207), (520, 176), (481, 102), (298, 360), (457, 394), (229, 124), (533, 209), (289, 320), (101, 298), (538, 106), (435, 328), (347, 206), (235, 124), (234, 297), (593, 157), (514, 180), (497, 98), (474, 107), (387, 103), (258, 362), (387, 111), (517, 212), (175, 171), (353, 355), (382, 190), (422, 297), (345, 160), (300, 197), (176, 200), (589, 117), (451, 103), (285, 165), (475, 105), (186, 103), (207, 151), (294, 232), (223, 121), (98, 291), (308, 100), (523, 195), (422, 170), (346, 163), (290, 259), (380, 276), (486, 330), (466, 225), (578, 95), (531, 97), (497, 115), (450, 171), (283, 93), (300, 97), (374, 140), (515, 155), (174, 184), (252, 295), (619, 112), (297, 123), (383, 136), (308, 311), (538, 99), (372, 361), (554, 200), (217, 297), (249, 120), (512, 181), (550, 99), (219, 120), (285, 256), (345, 280), (470, 373), (289, 193), (291, 265), (289, 254), (347, 160), (449, 182), (67, 297), (285, 147), (384, 199), (464, 286), (245, 302), (443, 101), (368, 362), (351, 221), (287, 167), (346, 151), (594, 191), (591, 198), (348, 147), (313, 99), (469, 203), (291, 265), (449, 263), (349, 260), (507, 390), (574, 198), (276, 360), (459, 216), (290, 272), (453, 402), (317, 194), (401, 132), (235, 119), (285, 168), (384, 113), (597, 95), (176, 177), (244, 357), (215, 296), (323, 231), (419, 360), (531, 128), (283, 281), (283, 240), (623, 113), (337, 98), (379, 144), (514, 143), (506, 92), (351, 236), (439, 380), (166, 233), (229, 295), (319, 320), (285, 161), (390, 140), (259, 295), (497, 368), (245, 121), (287, 262), (353, 95), (376, 196), (233, 358), (461, 397), (635, 104), (302, 119), (405, 359), (595, 186), (207, 362), (287, 251), (202, 103), (400, 131), (383, 191), (369, 137), (164, 294), (286, 251), (399, 80), (512, 168), (594, 142), (175, 195), (588, 161), (364, 140), (175, 356), (211, 364), (333, 96), (47, 277), (517, 165), (351, 212), (233, 298), (212, 117), (258, 297), (308, 93), (460, 297), (306, 298), (182, 155), (387, 155), (176, 174), (294, 95), (323, 229), (162, 234), (454, 240), (234, 121), (499, 129), (477, 344), (450, 241), (385, 291), (517, 154), (522, 215), (146, 247), (274, 320), (449, 110), (175, 248), (203, 358), (346, 267), (284, 186), (325, 97), (403, 361), (285, 153), (285, 190), (612, 108), (174, 185), (308, 363), (22, 281), (543, 198), (342, 156), (383, 109), (291, 250), (324, 232), (228, 122), (549, 98), (435, 328), (423, 357), (438, 167), (348, 273), (514, 155), (291, 249), (192, 246), (28, 300), (204, 149), (576, 201), (340, 164), (195, 304), (171, 240), (466, 350), (388, 359), (340, 150), (363, 143), (278, 359), (285, 185), (283, 184), (454, 143), (232, 298), (190, 300), (3, 327), (447, 196), (70, 299), (301, 354), (288, 259), (562, 99), (304, 133), (247, 122), (338, 93), (491, 108), (241, 297), (341, 162), (603, 122), (443, 128), (417, 360), (593, 156), (315, 230), (323, 200), (588, 148), (450, 253), (285, 159), (307, 235), (448, 113), (305, 131), (68, 297), (470, 103), (467, 271), (442, 402), (345, 270), (172, 343), (380, 126), (443, 137), (239, 304), (288, 217), (287, 164), (195, 318), (356, 280), (497, 112), (582, 202), (450, 182), (453, 266), (173, 200), (441, 397), (269, 358), (368, 137), (83, 296), (236, 117), (452, 141), (438, 280), (179, 132), (518, 137), (250, 126), (362, 197), (314, 200), (304, 234), (314, 278), (464, 270), (342, 139), (500, 109), (590, 153), (25, 321), (232, 121), (478, 107), (365, 360), (555, 198), (311, 232), (517, 159), (455, 229), (325, 231), (286, 175), (401, 358), (215, 299), (247, 294), (346, 170), (361, 95), (495, 397), (348, 304), (315, 194), (444, 138), (510, 194), (204, 298), (174, 196), (144, 248), (452, 247), (476, 106), (448, 177), (452, 247), (344, 179), (144, 215), (353, 226), (301, 236), (581, 97), (379, 106), (395, 168), (343, 157), (465, 105), (318, 274), (493, 92), (600, 150), (269, 362), (444, 190), (196, 361), (531, 97), (465, 107), (373, 124), (207, 302), (217, 124), (601, 190), (449, 159), (333, 358), (245, 124), (174, 342), (242, 303), (531, 97), (291, 140), (464, 223), (373, 201), (435, 196), (256, 296), (599, 132), (195, 361), (301, 194), (456, 105), (464, 292), (364, 80), (456, 106), (235, 363), (455, 243), (400, 147), (591, 178), (463, 106), (323, 362), (483, 365), (386, 104), (178, 142), (213, 360), (156, 319), (359, 194), (283, 119), (448, 347), (279, 120), (91, 300), (175, 183), (284, 145), (194, 248), (167, 340), (187, 357), (198, 299), (172, 186), (248, 122), (579, 202), (108, 295), (515, 175), (383, 114), (431, 277), (449, 142), (366, 194), (41, 310), (63, 302), (230, 352), (590, 158), (348, 258), (290, 98), (281, 120), (304, 355), (345, 137), (552, 196), (176, 182), (284, 196), (342, 137), (184, 224), (139, 300), (509, 387), (384, 306), (357, 279), (449, 107), (364, 291), (344, 146), (257, 126), (315, 289), (149, 291), (331, 231), (293, 124), (313, 320), (47, 320), (170, 159), (292, 198), (174, 189), (147, 218), (334, 185), (383, 171), (296, 232), (194, 360), (346, 236), (441, 340), (357, 363), (180, 121), (625, 134), (466, 271), (618, 141), (201, 293), (314, 99), (421, 172), (42, 273), (346, 216), (350, 267), (209, 102), (410, 171), (177, 200), (511, 154), (382, 92), (136, 302), (464, 103), (385, 281), (345, 137), (315, 309), (283, 364), (342, 170), (589, 124), (379, 282), (515, 134), (378, 364), (193, 321), (249, 296), (346, 234), (297, 291), (423, 298), (515, 210), (124, 292), (212, 122), (316, 317), (259, 359), (625, 105), (452, 249), (352, 142), (162, 286), (222, 123), (446, 145), (580, 202), (514, 174), (451, 184), (255, 118), (384, 150), (341, 135), (353, 143), (429, 358), (458, 249), (287, 190), (174, 188), (397, 166), (494, 129), (536, 195), (389, 199), (451, 234), (271, 117), (245, 304), (581, 196), (374, 281), (333, 232), (477, 372), (190, 358), (352, 355), (284, 217), (349, 254), (210, 298), (380, 114), (285, 256), (167, 328), (395, 86), (540, 201), (351, 241), (465, 107), (385, 137), (174, 165), (631, 97), (348, 189), (452, 232), (234, 358), (380, 276), (349, 309), (445, 130), (447, 129), (435, 327), (342, 172), (343, 155), (287, 175), (473, 107), (169, 280), (347, 135), (322, 91), (288, 110), (637, 106), (288, 241), (315, 313), (509, 344), (453, 121), (601, 105), (73, 292), (153, 228), (424, 156), (90, 295), (346, 145), (170, 183), (436, 171), (518, 152), (435, 402), (287, 148), (477, 204), (573, 195), (301, 200), (167, 365), (472, 208), (516, 123), (375, 306), (401, 147), (421, 361), (114, 295), (289, 184), (359, 354), (234, 360), (477, 111), (48, 327), (302, 97), (286, 138), (441, 107), (300, 229), (345, 267), (446, 138), (285, 258), (465, 301), (588, 192), (51, 332), (175, 101), (208, 157), (434, 217), (153, 299), (283, 188), (34, 295), (287, 138), (302, 233), (108, 295), (446, 195), (362, 134), (374, 88), (214, 293), (616, 95), (198, 234), (447, 186), (227, 121), (302, 356), (495, 360), (503, 402), (272, 295), (447, 122), (332, 235), (394, 364), (312, 100), (532, 219), (182, 108), (402, 150), (283, 355), (530, 215), (253, 126), (439, 350), (431, 273), (274, 274), (527, 125), (472, 106), (0, 330), (509, 223), (508, 367), (531, 128), (387, 109), (272, 353), (394, 82), (436, 399), (337, 357), (365, 92), (193, 324), (399, 82), (58, 296), (385, 104), (223, 122), (43, 319), (489, 207), (283, 290), (16, 316), (386, 111), (400, 99), (372, 358), (562, 100), (173, 174), (365, 200), (346, 267), (448, 125), (400, 166), (593, 120), (441, 347), (475, 375), (475, 344), (372, 198), (516, 182), (354, 210), (517, 172), (229, 297), (461, 400), (319, 361), (340, 357), (354, 96), (168, 360), (339, 96), (465, 224), (263, 293), (628, 124), (331, 233), (434, 191), (253, 362), (468, 109), (600, 188), (145, 226), (177, 195), (426, 354), (288, 175), (335, 231), (347, 248), (516, 179), (337, 193), (291, 173), (594, 195), (604, 135), (383, 313), (443, 136), (421, 292), (298, 311), (341, 183), (467, 272), (453, 161), (357, 94), (520, 104), (383, 175), (431, 158), (228, 119), (400, 127), (556, 196), (481, 349), (174, 180), (378, 127), (534, 97), (290, 248), (313, 90), (387, 187), (225, 122), (227, 300), (329, 230), (595, 174), (209, 302), (299, 132), (399, 167), (304, 116), (416, 360), (302, 362), (118, 293), (200, 356), (355, 91), (513, 133), (172, 347), (175, 349), (242, 121), (284, 219), (514, 185), (467, 280), (573, 103), (285, 219), (213, 302), (349, 265), (144, 292), (346, 220), (106, 296), (319, 317), (512, 151), (390, 194), (124, 296), (469, 108), (384, 358), (341, 189), (624, 139), (541, 96), (288, 173), (264, 359), (32, 290), (349, 267), (173, 348), (425, 272), (287, 190), (603, 110), (188, 354), (287, 203), (467, 301), (448, 195), (256, 301), (533, 220), (285, 154), (5, 331), (347, 215), (352, 140), (466, 387), (349, 215), (463, 201), (384, 315), (242, 297), (284, 110), (278, 310), (343, 176), (169, 344), (259, 359), (356, 363), (338, 189), (388, 184), (226, 123), (356, 357), (511, 328), (319, 320), (571, 202), (438, 224), (370, 85), (287, 208), (375, 352), (520, 198), (48, 332), (497, 123), (198, 294), (516, 184), (160, 279), (375, 199), (309, 312), (513, 160), (236, 118), (508, 111), (404, 165), (373, 352), (385, 112), (308, 321), (293, 134), (300, 282), (379, 125), (289, 362), (251, 121), (507, 327), (400, 143), (525, 124), (289, 259), (452, 236), (308, 95), (323, 202), (248, 302), (520, 139), (144, 218), (233, 295), (517, 146), (302, 199), (284, 91), (487, 378), (176, 193), (605, 111), (233, 299), (350, 237), (20, 289), (360, 303), (399, 125), (436, 401), (304, 99), (265, 122), (512, 189), (316, 276), (580, 203), (450, 243), (434, 357), (316, 198), (522, 194), (463, 355), (311, 234), (293, 132), (385, 311), (365, 288), (513, 132), (367, 139), (179, 352), (384, 199), (211, 365), (317, 273), (447, 110), (232, 358), (639, 92), (345, 254), (234, 365), (363, 365), (467, 224), (386, 106), (529, 223), (447, 233), (174, 171), (391, 359), (379, 112), (448, 245), (438, 401), (302, 230), (596, 167), (3, 312), (401, 81), (472, 337), (259, 122), (445, 282), (600, 169), (182, 321), (554, 200), (231, 122), (593, 198), (328, 357), (377, 358), (318, 291), (451, 131), (385, 186), (443, 146), (533, 129), (444, 370), (549, 106), (349, 247), (639, 149), (176, 328), (82, 302), (457, 107), (409, 182), (309, 232), (347, 90), (347, 217), (207, 156), (291, 220), (424, 285), (45, 328), (453, 242), (289, 211), (376, 80), (246, 119), (410, 362), (213, 362), (470, 211), (526, 194), (336, 98), (347, 288), (322, 228), (287, 220), (237, 125), (390, 361), (419, 353), (476, 327), (350, 143), (208, 361), (437, 401), (378, 83), (175, 204), (354, 355), (487, 107), (492, 209), (273, 357), (352, 275), (287, 263), (236, 126), (285, 147), (461, 279), (172, 191), (463, 191), (476, 107), (223, 121), (181, 360), (408, 169), (500, 347), (224, 297), (173, 153), (220, 304), (549, 100), (265, 294), (480, 395), (220, 298), (452, 238), (360, 141), (512, 401), (440, 332), (564, 102), (287, 265), (322, 232), (287, 260), (428, 183), (334, 209), (380, 360), (387, 186), (236, 298), (23, 283), (305, 198), (171, 280), (285, 268), (242, 121), (174, 197), (283, 163), (454, 236), (127, 292), (284, 145), (291, 252), (353, 235), (49, 287), (290, 222), (310, 230), (108, 296), (372, 195), (276, 320), (283, 199), (171, 186), (442, 101), (351, 259), (513, 178), (374, 288), (178, 340), (201, 214), (491, 212), (495, 379), (441, 284), (402, 131), (380, 365), (408, 359), (242, 301), (480, 202), (220, 125), (461, 367), (345, 312), (346, 242), (150, 242), (239, 120), (514, 121), (509, 189), (208, 358), (445, 349), (28, 287), (315, 235), (512, 223), (250, 125), (291, 129), (288, 161), (302, 94), (577, 97), (381, 298), (508, 364), (252, 301), (264, 122), (360, 143), (533, 105), (346, 242), (264, 134), (247, 301), (507, 206), (112, 295), (510, 166), (530, 105), (373, 361), (379, 307), (193, 284), (461, 387), (638, 93), (401, 125), (285, 154), (234, 297), (287, 258), (284, 256), (633, 103), (303, 200), (181, 125), (322, 95), (238, 303), (349, 138), (616, 147), (345, 142), (167, 223), (216, 126), (599, 177), (290, 247), (153, 288), (513, 176), (448, 117), (369, 358), (413, 358), (519, 140), (212, 357), (432, 155), (516, 144), (341, 138), (315, 91), (281, 286), (288, 226), (306, 230), (367, 85), (451, 139), (171, 364), (177, 208), (52, 299), (84, 292), (210, 300), (228, 119), (386, 181), (19, 331), (355, 141), (236, 359), (382, 178), (338, 360), (407, 160), (243, 122), (385, 174), (452, 107), (514, 143), (460, 336), (522, 225), (287, 219), (253, 364), (3, 323), (177, 163), (349, 221), (448, 350), (439, 225), (287, 178), (209, 359), (284, 111), (417, 179), (245, 364), (536, 94), (206, 299), (217, 123), (452, 184), (489, 212), (286, 143), (581, 97), (442, 386), (284, 214), (284, 107), (466, 288), (508, 358), (297, 94), (567, 194), (288, 185), (260, 298), (289, 269), (18, 272), (319, 234), (512, 152), (212, 122), (598, 161), (484, 108), (346, 146), (578, 197), (500, 120), (518, 143), (206, 134), (387, 189), (173, 106), (154, 220), (445, 163), (287, 262), (384, 192), (442, 402), (380, 278), (150, 243), (584, 195), (342, 96), (69, 297), (282, 273), (91, 301), (505, 336), (202, 300), (285, 163), (145, 222), (465, 103), (10, 284), (253, 299), (366, 357), (525, 224), (579, 98), (252, 359), (148, 293), (225, 353), (462, 199), (325, 198), (607, 102), (385, 169), (318, 321), (434, 192), (494, 367), (385, 360), (513, 145), (326, 93), (167, 218), (45, 279), (383, 113), (389, 188), (414, 158), (286, 263), (609, 93), (164, 221), (224, 123), (334, 358), (518, 136), (205, 112), (284, 106), (94, 298), (27, 290), (442, 341), (168, 214), (285, 246), (21, 295), (290, 178), (346, 150), (307, 291), (285, 179), (499, 112), (384, 146), (441, 223), (170, 328), (306, 228), (159, 317), (425, 176), (453, 231), (284, 174), (612, 139), (285, 186), (600, 203), (592, 162), (470, 330), (248, 304), (436, 213), (442, 328), (347, 162), (113, 296), (489, 358), (448, 112), (264, 134), (636, 99), (284, 313), (346, 357), (517, 184), (450, 157), (100, 298), (13, 310), (445, 120), (29, 329), (244, 360), (304, 126), (288, 293), (449, 127), (460, 281), (170, 183), (384, 175), (16, 289), (339, 134), (312, 236), (190, 115), (348, 365), (502, 388), (276, 134), (421, 271), (391, 165), (173, 124), (286, 359), (354, 209), (372, 139), (56, 292), (540, 199), (194, 356), (146, 230), (270, 357), (438, 327), (176, 208), (4, 290), (206, 134), (140, 296), (620, 133), (393, 169), (2, 292), (548, 199), (544, 199), (268, 358), (454, 119), (256, 363), (168, 304), (16, 302), (176, 183), (302, 194), (275, 321), (209, 296), (499, 355), (290, 162), (246, 124), (198, 248), (287, 157), (240, 299), (582, 100), (388, 184), (287, 180), (368, 138), (452, 172), (601, 106), (399, 101), (542, 103), (346, 233), (222, 294), (205, 106), (114, 292), (323, 231), (240, 122), (85, 296), (348, 272), (340, 364), (237, 123), (214, 295), (338, 228), (397, 363), (51, 270), (171, 166), (190, 115), (385, 276), (317, 277), (173, 198), (637, 93), (121, 303), (465, 366), (446, 103), (306, 303), (132, 296), (187, 312), (448, 131), (157, 283), (309, 93), (176, 326), (454, 103), (387, 177), (574, 201), (593, 186), (507, 217), (201, 142), (446, 155), (287, 189), (310, 318), (170, 323), (289, 259), (440, 371), (174, 206), (592, 189), (599, 180), (269, 119), (303, 196), (366, 196), (383, 182), (528, 115), (388, 182), (68, 301), (330, 198), (635, 148), (508, 332), (286, 287), (155, 323), (352, 270), (3, 300), (246, 118), (436, 271), (352, 138), (452, 260), (287, 216), (516, 196), (453, 105), (248, 123), (46, 321), (47, 294), (313, 97), (375, 88), (168, 364), (345, 295), (178, 224), (170, 132), (175, 185), (304, 235), (537, 201), (595, 194), (539, 106), (344, 173), (434, 221), (307, 95), (340, 230), (261, 297), (533, 124), (428, 179), (200, 298), (175, 355), (452, 179), (130, 294), (316, 313), (401, 95), (285, 242), (176, 200), (350, 239), (287, 189), (551, 195), (384, 162), (287, 357), (382, 156), (167, 219), (201, 141), (472, 207), (170, 346), (490, 329), (383, 112), (384, 159), (595, 180), (328, 197), (503, 402), (494, 128), (511, 107), (476, 348), (315, 96), (386, 202), (302, 116), (536, 100), (446, 183), (597, 166), (310, 231), (163, 290), (452, 257), (313, 89), (473, 382), (170, 187), (456, 235), (155, 295), (452, 243), (174, 361), (483, 210), (319, 360), (224, 124), (524, 110), (453, 294), (205, 297), (547, 102), (387, 156), (344, 170), (212, 299), (363, 136), (340, 166), (271, 358), (32, 327), (387, 111), (394, 357), (480, 106), (538, 202), (86, 297), (345, 258), (311, 202), (456, 226), (358, 140), (257, 298), (584, 199), (427, 163), (341, 89), (348, 156), (203, 299), (285, 126), (442, 114), (127, 297), (447, 297), (326, 362), (312, 200), (421, 295), (464, 339), (465, 284), (358, 185), (595, 171), (340, 141), (442, 101), (176, 327), (175, 179), (283, 149), (145, 238), (566, 200), (517, 162), (390, 186), (143, 293), (495, 207), (319, 277), (150, 243), (153, 222), (2, 292), (514, 192), (366, 98), (555, 203), (182, 106), (494, 214), (66, 299), (422, 354), (379, 126), (344, 180), (553, 95), (341, 172), (180, 124), (362, 195), (344, 229), (175, 159), (177, 351), (177, 179), (275, 357), (512, 136), (285, 307), (189, 363), (361, 141), (444, 125), (596, 180), (428, 282), (393, 79), (345, 169), (332, 231), (329, 359), (432, 359), (218, 121), (349, 255), (423, 294), (520, 150), (510, 378), (573, 201), (448, 123), (321, 235), (166, 285), (519, 211), (389, 361), (153, 279), (98, 298), (259, 355), (497, 204), (425, 271), (168, 362), (504, 376), (457, 193), (235, 362), (396, 167), (318, 356), (175, 178), (398, 129), (318, 364), (265, 132), (256, 121), (517, 167), (357, 313), (421, 301), (381, 104), (287, 114), (435, 338), (388, 359), (210, 359), (293, 202), (284, 159), (229, 296), (350, 227), (351, 225), (401, 357), (581, 105), (291, 170), (305, 198), (96, 299), (451, 260), (387, 138), (602, 203), (350, 227), (219, 121), (441, 126), (173, 179), (314, 313), (302, 130), (319, 277), (471, 205), (447, 203), (211, 365), (214, 358), (569, 200), (451, 210), (485, 207), (301, 119), (534, 121), (246, 359), (514, 139), (357, 286), (448, 121), (500, 122), (313, 231), (347, 217), (463, 379), (218, 294), (209, 156), (369, 202), (335, 210), (174, 104), (579, 103), (424, 296), (424, 300), (509, 123), (494, 211), (193, 215), (452, 362), (286, 276), (449, 227), (239, 352), (289, 175), (238, 124), (99, 298), (42, 304), (487, 344), (456, 389), (373, 93), (30, 329), (601, 129), (178, 346), (302, 122), (441, 368), (203, 123), (1, 331), (519, 107), (266, 117), (384, 161), (394, 163), (398, 359), (402, 354), (155, 317), (381, 116), (442, 150), (440, 289), (343, 90), (6, 270), (512, 174), (312, 355), (448, 230), (343, 180), (301, 93), (345, 265), (304, 201), (130, 293), (173, 181), (277, 273), (381, 284), (176, 342), (445, 155), (401, 135), (467, 106), (310, 96), (531, 125), (2, 330), (241, 304), (573, 105), (4, 318), (251, 364), (601, 181), (343, 154), (172, 342), (345, 256), (260, 294), (289, 173), (516, 144), (287, 94), (321, 359), (522, 198), (361, 101), (560, 102), (467, 336), (220, 299), (164, 216), (452, 247), (330, 235), (174, 169), (385, 278), (401, 149), (236, 297), (284, 263), (187, 223), (455, 242), (509, 398), (306, 235), (332, 231), (450, 402), (372, 364), (451, 245), (185, 114), (168, 346), (302, 100), (267, 118), (476, 209), (441, 106), (175, 279), (307, 229), (175, 204), (385, 313), (255, 302), (123, 290), (484, 210), (402, 123), (546, 97), (315, 276), (466, 223), (1, 306), (438, 205), (171, 178), (464, 191), (346, 267), (287, 102), (319, 196), (450, 233), (633, 128), (602, 175), (299, 97), (370, 200), (383, 112), (166, 283), (475, 341), (173, 102), (353, 233), (391, 85), (287, 310), (441, 159), (516, 137), (638, 93), (520, 127), (386, 138), (419, 169), (27, 305), (382, 194), (289, 223), (172, 173), (137, 301), (352, 218), (591, 183), (263, 299), (178, 188), (264, 296), (341, 231), (236, 297), (366, 314), (358, 142), (349, 94), (185, 154), (286, 182), (512, 382), (474, 209), (471, 363), (347, 244), (226, 121), (374, 78), (213, 366), (87, 301), (175, 186), (268, 301), (346, 140), (285, 221), (302, 125), (381, 294), (539, 195), (45, 271), (475, 396), (382, 278), (267, 304), (369, 362), (592, 158), (318, 362), (433, 197), (305, 201), (480, 108), (274, 361), (156, 218), (217, 361), (173, 216), (383, 113), (300, 228), (287, 255), (591, 164), (512, 178), (326, 94), (576, 98), (387, 184), (302, 95), (354, 307), (117, 296), (378, 360), (108, 300), (355, 95), (379, 306), (324, 95), (286, 142), (552, 203), (373, 363), (361, 138), (330, 352), (534, 124), (347, 147), (379, 199), (558, 201), (340, 153), (355, 358), (112, 297), (636, 97), (244, 121), (365, 143), (268, 298), (240, 119), (345, 353), (301, 197), (360, 359), (349, 253), (481, 206), (458, 216), (323, 198), (454, 247), (385, 97), (620, 93), (291, 180), (104, 294), (519, 109), (564, 202), (394, 363), (235, 361), (483, 102), (448, 126), (301, 123), (594, 179), (186, 360), (383, 182), (167, 365), (386, 186), (435, 219), (362, 356), (184, 316), (250, 123), (518, 178), (473, 208), (158, 279), (345, 151), (505, 215), (121, 295), (562, 195), (286, 195), (598, 201), (438, 363), (92, 294), (290, 260), (171, 120), (174, 189), (384, 150), (199, 359), (341, 357), (4, 272), (363, 196), (397, 169), (353, 301), (360, 98), (463, 191), (291, 256), (301, 132), (270, 129), (186, 361), (212, 299), (304, 117), (451, 254), (481, 213), (360, 365), (505, 396), (438, 336), (133, 303), (305, 129), (484, 106), (528, 206), (367, 358), (595, 204), (445, 351), (162, 279), (200, 124), (256, 300), (536, 99), (332, 363), (512, 181), (233, 359), (284, 249), (173, 158), (352, 359), (239, 294), (383, 277), (309, 357), (352, 94), (173, 179), (287, 298), (283, 217), (283, 187), (195, 291), (519, 171), (452, 126), (311, 232), (288, 204), (598, 139), (376, 300), (48, 281), (260, 366), (296, 93), (451, 259), (263, 295), (508, 332), (306, 198), (241, 303), (286, 105), (174, 162), (519, 162), (272, 361), (445, 131), (290, 139), (350, 251), (296, 354), (463, 293), (602, 156), (246, 366), (450, 396), (375, 362), (390, 359), (226, 303), (344, 152), (39, 294), (445, 335), (620, 126), (512, 179), (343, 99), (297, 236), (174, 355), (550, 197), (318, 297), (462, 214), (202, 357), (366, 363), (454, 139), (584, 98), (520, 133), (182, 354), (293, 230), (284, 165), (250, 123), (614, 97), (304, 98), (598, 192), (228, 297), (345, 151), (177, 159), (285, 253), (169, 330), (511, 145), (158, 223), (481, 334), (434, 195), (267, 299), (351, 219), (145, 245), (307, 236), (360, 138), (27, 294), (175, 216), (169, 299), (558, 202), (206, 121), (55, 303), (349, 246), (451, 269), (347, 294), (355, 135), (303, 115), (380, 198), (176, 237), (313, 201), (286, 320), (356, 205), (452, 353), (201, 215), (151, 226), (447, 158), (313, 310), (383, 118), (448, 143), (601, 201), (377, 314), (288, 149), (71, 299), (385, 108), (459, 107), (305, 133), (463, 107), (42, 327), (154, 280), (287, 248), (384, 109), (388, 361), (44, 281), (318, 286), (352, 210), (249, 124), (168, 353), (334, 94), (286, 239), (415, 357), (421, 361), (340, 174), (536, 198), (349, 275), (154, 292), (537, 98), (632, 147), (385, 360), (173, 204), (99, 296), (494, 126), (360, 364), (598, 113), (531, 119), (147, 214), (545, 97), (271, 120), (171, 335), (189, 220), (401, 123), (274, 124), (305, 97), (173, 210), (174, 173), (285, 177), (293, 197), (193, 306), (47, 270), (24, 324), (187, 311), (466, 222), (189, 231), (595, 175), (288, 222), (328, 95), (297, 229), (289, 183), (222, 361), (200, 238), (204, 298), (349, 242), (592, 103), (188, 321), (288, 279), (449, 115), (256, 119), (276, 122), (228, 296), (379, 201), (375, 197), (348, 252), (283, 192), (447, 343), (346, 232), (333, 231), (105, 301), (424, 300), (348, 249), (401, 126), (124, 297), (286, 230), (353, 239), (313, 232), (264, 117), (458, 213), (511, 153), (322, 199), (464, 286)]

path_dict = {model.starting_point : [1, 0], model.ending_point: [0, 1]}

meeting_point = (-1, -1)

for i in range(0, len(config_space)-1):
    for j in range(i+1, len(config_space)):
        if model.allowed(model.image, model.graph, config_space[i], config_space[j]):
            model.draw_line(config_space[i], config_space[j], model.image)

            if config_space[i] not in path_dict:
                path_dict[config_space[i]] = [0, 0, config_space[j]]
            if config_space[j] not in path_dict:
                path_dict[config_space[j]] = [0, 0, config_space[i]]

            path_dict[config_space[i]][0] = path_dict[config_space[i]][0] + path_dict[config_space[j]][0]
            path_dict[config_space[j]][0] = path_dict[config_space[i]][0] + path_dict[config_space[j]][0]

            path_dict[config_space[i]][1] = path_dict[config_space[i]][1] + path_dict[config_space[j]][1]
            path_dict[config_space[j]][1] = path_dict[config_space[i]][1] + path_dict[config_space[j]][1]

            path_dict[config_space[i]].append(config_space[j])
            path_dict[config_space[i]].append(config_space[i])

            if path_dict[config_space[i]][0] > 0 and path_dict[config_space[i]][1] > 0:
                meeting_point = config_space[i]
                break

print(meeting_point)


image = cv2.imread("processed_map.png")
model = RRT_star((452, 213), (473, 365), 1000, 10, 10)

current_point = meeting_point
temp_point = None

while True:
    for i in path_dict[current_point][2:]:
        if path_dict[i][0] > 0:
            image = model.draw_line(i, current_point, image)
            current_point = i
            break
    if current_point == model.starting_point:
        break

current_point = meeting_point

while True:
    for i in path_dict[current_point][2:]:
        if path_dict[i][1] > 0:
            image = model.draw_line(i, current_point, image)
            current_point = i
            break
    if current_point == model.ending_point:
        break

cv2.imshow("plot", image)
if cv2.waitKey(0) == 'q':
    cv2.destroyAllWindows()