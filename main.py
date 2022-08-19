import os
import random
import time
import datetime
from PIL import Image

print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
mazeList = []
DIRECTION_DICT = {
    "up": None,
    "down": None,
    "left": None,
    "right": None
}
DICTION_OPPOSITE = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left"
}


class Imager:
    def __init__(self, maze):
        self.parent = maze
        self.height = maze.hallWallSum * maze.height + maze.wallWidth
        self.width = maze.hallWallSum * maze.width + maze.wallWidth
        self.image = Image.new("L", (self.width, self.height))
        self.pixels = self.image.load()
        self.data = [[-1] * self.width for _ in range(self.height)]
        if self.pixels is not None:
            for i in range(self.height):
                for j in range(self.width):
                    self.pixels[j, i] = 255 - 64

    def make_image(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.data[i][j] != -1:
                    self.pixels[j, i] = self.data[i][j]
                else:
                    raise Exception("data was not set at: " + str(j) + ", " + str(i))

    def get_corresponding_cell_from_pixel(self, x, y):
        maze = self.parent
        corresponding_cell_x = int(x / maze.hallWallSum)
        if corresponding_cell_x >= maze.width:
            corresponding_cell_x = -1
        corresponding_cell_y = int(y / maze.hallWallSum)
        if corresponding_cell_y >= maze.height:
            corresponding_cell_y = -1
        return maze.cellList[corresponding_cell_y][corresponding_cell_x]

    def get_pixel_wall_info(self, x, y):  # Tells what walls a pixel is part of
        maze = self.parent
        corresponding_cell = self.get_corresponding_cell_from_pixel(x, y)
        pixel_wall_info = {}
        x -= corresponding_cell.x * maze.hallWallSum
        y -= corresponding_cell.y * maze.hallWallSum
        if x < maze.wallWidth:
            pixel_wall_info["left"] = 1
        if x >= maze.hallWallSum:
            pixel_wall_info["right"] = 1
        if y < maze.wallWidth:
            pixel_wall_info["up"] = 1
        if y >= maze.hallWallSum:
            pixel_wall_info["down"] = 1
        if len(pixel_wall_info) > 2:
            raise Exception("Pixel part of more than two walls",
                            x, y, maze.wallWidth, maze.hallWidth)
        return pixel_wall_info

    def build_data(self):
        for row_y in range(self.height):
            for column_x in range(self.width):
                corresponding_cell = self.get_corresponding_cell_from_pixel(column_x, row_y)
                pixel_wall_info = self.get_pixel_wall_info(column_x, row_y)
                if len(pixel_wall_info) == 2:
                    self.data[row_y][column_x] = 0
                else:
                    for wall_info_key in pixel_wall_info:
                        if corresponding_cell.wallList[wall_info_key] == 1:
                            self.data[row_y][column_x] = 0
                            break
                    if not self.data[row_y][column_x] == 0:
                        self.data[row_y][column_x] = 1

    def build_data_from_cell(self, cell, key):
        hall_width = self.parent.hallWidth
        wall_width = self.parent.wallWidth
        hall_wall_sum = self.parent.hallWallSum
        cell_start_x = cell.x * hall_wall_sum
        cell_start_y = cell.y * hall_wall_sum
        x_cell_offset = 0
        y_cell_offset = 0
        if key == "up" or key == "down":
            range_x = 2 * wall_width + hall_width
            range_y = wall_width
            if key == "down":
                y_cell_offset = hall_wall_sum
        elif key == "left" or key == "right":
            range_x = wall_width
            range_y = 2 * wall_width + hall_width
            if key == "right":
                x_cell_offset = hall_wall_sum
        elif key == "middle":
            range_x = hall_width
            range_y = hall_width
            x_cell_offset = wall_width
            y_cell_offset = wall_width
        else:
            raise Exception("Invalid key")
        if cell.wallList.get(key, 0) == 1:
            pixel_setting = 0
        else:
            pixel_setting = 1
        for row_y in range(range_y):
            for column_x in range(range_x):
                relation_to_cell_x = column_x + x_cell_offset
                relation_to_cell_y = row_y + y_cell_offset
                top_or_bottom_check = (relation_to_cell_y < wall_width) or (relation_to_cell_y >= hall_wall_sum)
                left_or_right_check = (relation_to_cell_x < wall_width) or (relation_to_cell_x >= hall_wall_sum)
                corner_check = top_or_bottom_check and left_or_right_check
                pixel_x = cell_start_x + relation_to_cell_x
                pixel_y = cell_start_y + relation_to_cell_y
                if (not corner_check) and pixel_setting == 1:
                    self.pixels[pixel_x, pixel_y] = 255
                elif (not corner_check) and pixel_setting == 0:
                    self.pixels[pixel_x, pixel_y] = 0
                elif corner_check and pixel_setting == 0:
                    self.pixels[pixel_x, pixel_y] = 0
        return


class Cell:
    def __init__(self, x, y, maze):
        self.parent = maze
        self.x = x
        self.y = y
        self.wallList = DIRECTION_DICT.copy()
        self.explored = False

    def get_cells_around(self):
        cells_around = {}
        for key in DIRECTION_DICT:
            if key == "up":
                if self.y < 1:
                    continue
                cells_around[key] = self.parent.cellList[self.y - 1][self.x]
            elif key == "down":
                if self.y > self.parent.height - 2:
                    continue
                cells_around[key] = self.parent.cellList[self.y + 1][self.x]
            elif key == "left":
                if self.x < 1:
                    continue
                cells_around[key] = self.parent.cellList[self.y][self.x - 1]
            elif key == "right":
                if self.x > self.parent.width - 2:
                    continue
                cells_around[key] = self.parent.cellList[self.y][self.x + 1]
            else:
                raise Exception("Invalid key")
        return cells_around

    def count_cells_explored_around(self):
        cells_around = self.get_cells_around()
        cells_explored_around = 0
        for key in cells_around:
            if cells_around[key].explored:
                cells_explored_around += 1
        return cells_explored_around


class Maze:
    def __init__(self):
        mazeList.append(self)
        self.name = str(random.random())[2:]
        print(self.name)
        self.wallWidth = 1
        self.hallWidth = 1
        self.hallWallSum = self.wallWidth + self.hallWidth
        self.width = 10  # in cells
        self.height = 10  # in cells
        self.chanceToMakeShortcut = 0.001
        self.percentRangeOfExits = 0.5
        self.buildMode = 0
        # 0: Latest cell | 1: First cell (Not a good maze)
        # 2: Random cell in cell queue | 3: Completely random (Not a good maze)
        self.recordVideo = False
        self.imageCounter = 0
        self.cellList = []
        self.cellQueue = []
        self.imageHolder = Imager(self)

    def save(self):
        try:
            os.makedirs("Maze Images/")
        except FileExistsError:
            pass
        self.imageHolder.image.save("Maze Images/" + self.name + ".png", "png")

    def save_video(self):
        try:
            os.makedirs("Maze Images/" + self.name + "/")
        except FileExistsError:
            pass
        self.imageHolder.image.save("Maze Images/" + self.name + "/" + str(self.imageCounter) + ".png", "png")
        self.imageCounter += 1

    def reload_maze(self):
        self.hallWallSum = self.wallWidth + self.hallWidth
        self.imageHolder = Imager(self)

    def create_cell_list(self):
        for i in range(self.height):
            self.cellList.append([])
            for j in range(self.width):
                current_cell = Cell(j, i, self)
                self.cellList[i].append(current_cell)
                if self.buildMode == 3:
                    self.cellQueue.append(current_cell)
            self.cellList[i][0].wallList["left"] = 1
            self.imageHolder.build_data_from_cell(self.cellList[i][0], "left")
            if self.recordVideo:
                self.save_video()
            self.cellList[i][-1].wallList["right"] = 1
            self.imageHolder.build_data_from_cell(self.cellList[i][self.width - 1], "right")
            if self.recordVideo:
                self.save_video()

        for j in range(self.width):
            self.cellList[0][j].wallList["up"] = 1
            self.imageHolder.build_data_from_cell(self.cellList[0][j], "up")
            if self.recordVideo:
                self.save_video()
            self.cellList[-1][j].wallList["down"] = 1
            self.imageHolder.build_data_from_cell(self.cellList[-1][j], "down")
            if self.recordVideo:
                self.save_video()

    def make_goals(self):
        width_range = self.width * self.percentRangeOfExits
        height_range = self.height * self.percentRangeOfExits
        if self.height >= self.width:
            random_x0 = random.randrange(0, int(width_range))
            random_x1 = random.randrange(int(self.width - width_range), self.width)
            self.cellList[0][random_x0].wallList["up"] = 0
            self.imageHolder.build_data_from_cell(self.cellList[0][random_x0], "up")
            if self.recordVideo:
                self.save_video()
            self.cellList[-1][random_x1].wallList["down"] = 0
            self.imageHolder.build_data_from_cell(self.cellList[-1][random_x1], "down")
            if self.recordVideo:
                self.save_video()
        else:
            random_y0 = random.randrange(0, int(height_range))
            random_y1 = random.randrange(int(self.height - height_range), self.height)
            self.cellList[random_y0][0].wallList["left"] = 0
            self.imageHolder.build_data_from_cell(self.cellList[random_y0][0], "left")
            if self.recordVideo:
                self.save_video()
            self.cellList[random_y1][-1].wallList["right"] = 0
            self.imageHolder.build_data_from_cell(self.cellList[random_y1][-1], "right")
            if self.recordVideo:
                self.save_video()

    def build_walls(self):
        if self.buildMode == 0:
            next_cell = self.cellQueue[-1]
        elif self.buildMode == 1:
            next_cell = self.cellQueue[0]
        elif self.buildMode == 2 or self.buildMode == 3:
            next_cell = self.cellQueue[random.randrange(0, len(self.cellQueue))]
        else:
            raise Exception("Invalid build mode")

        cells_around = next_cell.get_cells_around()
        considerations = cells_around.copy()
        for key in cells_around:
            if cells_around[key].explored:
                current_wall = next_cell.wallList[key]
                connected_wall = cells_around[key].wallList[DICTION_OPPOSITE[key]]
                if (current_wall is not None) and (connected_wall is not None):
                    if current_wall != connected_wall:
                        raise Exception("Mismatch between connecting walls and neither were None")
                    considerations.pop(key)
                    continue
                elif random.random() >= self.chanceToMakeShortcut:
                    next_cell.wallList[key] = 1
                    considerations[key].wallList[DICTION_OPPOSITE[key]] = 1
                    self.imageHolder.build_data_from_cell(next_cell, key)
                    considerations.pop(key)
                    if self.recordVideo:
                        self.save_video()
                    continue
                else:
                    next_cell.wallList[key] = 0
                    considerations[key].wallList[DICTION_OPPOSITE[key]] = 0
                    self.imageHolder.build_data_from_cell(next_cell, key)
                    considerations.pop(key)
                    if self.recordVideo:
                        self.save_video()
                    continue
        if not (len(considerations) == 0):
            chosen_key = random.choice(list(considerations.keys()))
            next_cell.wallList[chosen_key] = 0
            considerations[chosen_key].wallList[DICTION_OPPOSITE[chosen_key]] = 0
            considerations[chosen_key].explored = True
            self.imageHolder.build_data_from_cell(next_cell, chosen_key)
            if self.recordVideo:
                self.save_video()
            if self.buildMode != 3:
                self.cellQueue.append(considerations[chosen_key])
            self.imageHolder.build_data_from_cell(considerations[chosen_key], "middle")
            if self.recordVideo:
                self.save_video()
        else:
            self.cellQueue.remove(next_cell)
        return

    def build_maze(self, first_cell):
        start = time.time()
        first_cell.explored = True
        self.cellQueue.append(first_cell)
        self.imageHolder.build_data_from_cell(first_cell, "middle")
        if self.recordVideo:
            self.save_video()
        while not (len(self.cellQueue) == 0):
            self.build_walls()
        self.make_goals()
        print("Done making maze! It took " + str(time.time() - start) + " seconds")

    def get_random_cell(self):
        rand_x = random.randint(0, firstMaze.width - 1)
        rand_y = random.randint(0, firstMaze.height - 1)
        return self.cellList[rand_y][rand_x]

    def check_cell_walls(self):
        for cellRow in self.cellList:
            for cell in cellRow:
                cells_around_cell = cell.get_cells_around()
                for direction in cells_around_cell:
                    if cell.wallList[direction] != cells_around_cell[direction].wallList[DICTION_OPPOSITE[direction]]:
                        raise Exception("Something's screwed up when checking walls at",
                                        cell.x, cell.y, "to the", direction)


firstMaze = Maze()
firstMaze.width = 100
firstMaze.height = 100
firstMaze.wallWidth = 1
firstMaze.hallWidth = 1
firstMaze.buildMode = 0
firstMaze.chanceToMakeShortcut = 0.001
# firstMaze.recordVideo = True
firstMaze.reload_maze()
firstMaze.create_cell_list()
firstMaze.build_maze(firstMaze.get_random_cell())
firstMaze.save()
