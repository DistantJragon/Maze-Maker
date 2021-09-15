import sys
import os
import random
from PIL import Image

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
        self.image = Image.new("1", (self.width, self.height))
        self.pixels = self.image.load()
        self.data = [[None] * self.width for _ in range(self.height)]

    def make_image(self):
        for i in range(self.image.size[1]):
            for j in range(self.image.size[0]):
                self.pixels[j, i] = self.data[i][j]

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
        # 0: Latest cell | 1: First cell | 2: Random cell in cell queue | 3: Completely random
        # 1 and 3 do not give good mazes
        self.recordVideo = 0
        self.imageCounter = 0
        self.cellList = []
        self.cellQueue = []
        self.imageHolder = Imager(self)
        self.startCoordinates = []
        self.endCoordinates = []

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
            self.cellList[i][self.width - 1].wallList["right"] = 1
        for cell in self.cellList[0]:
            cell.wallList["up"] = 1
        for cell in self.cellList[-1]:
            cell.wallList["down"] = 1

    def make_goals(self):
        width_range = self.width * self.percentRangeOfExits
        height_range = self.height * self.percentRangeOfExits
        if self.height >= self.width:
            self.cellList[0][random.randrange(0, int(width_range))].wallList["up"] = 0
            self.cellList[-1][random.randrange(int(self.width - width_range), self.width)].wallList["down"] = 0
        else:
            self.cellList[random.randrange(0, int(height_range))][0].wallList["left"] = 0
            self.cellList[random.randrange(int(self.height - height_range), self.height)][-1].wallList["right"] = 0

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
                if (current_wall != connected_wall) and (connected_wall is not None) and (current_wall is not None):
                    raise Exception("Mismatch between connecting walls and neither were None")
                elif (current_wall is None) and (connected_wall is not None):
                    next_cell.wallList[key] = connected_wall
                    considerations.pop(key)
                    continue
                elif (current_wall is not None) and (connected_wall is None):
                    cells_around[key].wallList[DICTION_OPPOSITE[key]] = current_wall
                    considerations.pop(key)
                    continue
                elif (current_wall is not None) and (connected_wall is not None):
                    considerations.pop(key)
                    continue
                if random.random() >= self.chanceToMakeShortcut:
                    next_cell.wallList[key] = 1
                    considerations[key].wallList[DICTION_OPPOSITE[key]] = 1
                    considerations.pop(key)
                    continue
                else:
                    next_cell.wallList[key] = 0
                    considerations[key].wallList[DICTION_OPPOSITE[key]] = 0
                    considerations.pop(key)
                    continue
        if not (len(considerations) == 0):
            chosen_key = list(considerations.keys())[random.randrange(0, len(considerations))]
            next_cell.wallList[chosen_key] = 0
            considerations[chosen_key].wallList[DICTION_OPPOSITE[chosen_key]] = 0
            considerations[chosen_key].explored = True
            if self.buildMode != 3:
                self.cellQueue.append(considerations[chosen_key])
        else:
            self.cellQueue.remove(next_cell)
        return

    def build_maze(self, first_cell):
        first_cell.explored = True
        self.cellQueue.append(first_cell)
        while not (len(self.cellQueue) == 0):
            self.build_walls()
        self.make_goals()

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
firstMaze.width = 10
firstMaze.height = 10
firstMaze.wallWidth = 1
firstMaze.hallWidth = 1
firstMaze.buildMode = 0
firstMaze.chanceToMakeShortcut = 0.001
firstMaze.reload_maze()
firstMaze.create_cell_list()
firstMaze.build_maze(firstMaze.get_random_cell())
firstMaze.check_cell_walls()
firstMaze.imageHolder.build_data()
firstMaze.imageHolder.make_image()
firstMaze.save()