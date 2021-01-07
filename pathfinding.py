import pygame as pg
from pygame.color import THECOLORS as colors
from pygame.display import toggle_fullscreen
from pygame.draw import *

from enum import IntEnum
from random import random, randrange, choice
import time

pg.init()
pg.mixer.init()

############################################ PROGRAM VARIABLES ################################################

running = True
wall_place = False
to_restart = False

dim = 600
n_tiles = 30
tile_size = dim // n_tiles
bg_color = colors['lightblue']

up = 'music/up.mp3'
down = 'music/down.mp3'
left = 'music/left.mp3'
right = 'music/right.mp3'

screen = pg.display.set_mode((dim, dim))
pg.display.set_caption('Pathfinding')

font = pg.font.Font('freesansbold.ttf', 32)

##################################################################################################


class NodeState(IntEnum):
    start = 0
    finish = 1
    wall = 2
    moveable = 3


class Node:
    def __init__(self, i, j, state=NodeState.moveable):
        # for a*
        self.f = 0
        self.g = 0
        self.h = 0

        self.pos = i, j
        self.state = state
        self.visited = False
        self.parent = None

        if random() < 0.2:
            self.state = NodeState.wall

        self.parent = None
        self.in_path = False

        self.music = None

    def show(self, screen):
        rect_color = colors['white']

        if self.in_path:
            rect_color = colors['yellow']
        elif self.state == NodeState.start:
            rect_color = colors['lightgreen']
        elif self.state == NodeState.finish:
            rect_color = colors['coral']
        elif self.visited:
            rect_color = colors['purple']
        elif self.state == NodeState.wall:
            rect_color = colors['black']

        rect(screen, rect_color, (self.pos[0] * tile_size,
                                  self.pos[1] * tile_size, tile_size, tile_size))

        rect(screen, bg_color, (self.pos[0] * tile_size,
                                self.pos[1] * tile_size, tile_size, tile_size), 2)

    def get_neighbours(self, grid):
        nb = []
        if self.state == NodeState.wall:
            return nb

        arr = [
            [-1, 0, up],
            [1, 0, down],
            [0, 1, right],
            [0, -1, left],

            # [-1, 1, up],
            # [1, 1, down],
            # [1, -1, right],
            # [-1, -1, left]
        ]

        for n, pos in enumerate(arr):
            i = self.pos[0] + pos[0]
            j = self.pos[1] + pos[1]

            if 0 <= i < len(grid) and 0 <= j < len(grid[0]):
                t = grid[i][j]
                if t.state != NodeState.wall and not t.visited:
                    t.parent = self
                    t.music = pos[2]

                    nb.append(t)

        return nb

#################################################### ALGORITHM FUNCTIONS #################################################################


def make_path(node):
    for i in grid:
        for j in i:
            j.in_path = False

    n = node
    while True:
        if n is None: break

        n.in_path = True
        n = n.parent


def play_music(music):
    if music is None:
        return

    pg.mixer.music.load(music)
    pg.mixer.music.play()
    pg.mixer.music.set_volume(0.1)

#################################################### ALGORITHMS #################################################################


def bfs():
    node = queue.pop(0)

    if not node.visited:
        queue.extend(node.get_neighbours(grid))

    return node


def dfs():
    node = queue.pop()

    if not node.visited:
        queue.extend(node.get_neighbours(grid))

    return node


def best_search_heuristic(n, end):
    return pow(pow(n.pos[0] - end.pos[0], 2) + pow(n.pos[1] - end.pos[1], 2), .5)
    # return abs(n.pos[0] - end.pos[0]) + abs(n.pos[1] - end.pos[1])
    # return max(abs(n.pos[0] - end.pos[0]), abs(n.pos[1] - end.pos[1]))


def greedy_bfs():
    winner = 0
    for i in range(len(queue)):
        if (queue[i].h < queue[winner].h):
            winner = i

    node = queue.pop(winner)

    if not node.visited:
        for n in node.get_neighbours(grid):
            if n.visited:
                continue

            n.h = best_search_heuristic(n, finish_node)
            queue.append(n)

    return node


def a_star():
    winner = 0
    for i in range(len(queue)):
        if (queue[i].f < queue[winner].f):
            winner = i

    node = queue.pop(winner)

    if not node.visited:
        for n in node.get_neighbours(grid):
            if n.visited:
                continue

            temp_g = node.g + 1
            new_path = False

            if n in queue:
                if temp_g < n.g:
                    n.g = temp_g
                    new_path = True
            else:
                n.g = temp_g
                new_path = True
                queue.append(n)

            if new_path:
                n.h = best_search_heuristic(n, finish_node)
                n.f = n.g + n.h

    return node


def dijkstra():
    winner = 0
    for i in range(len(queue)):
        if (queue[i].g < queue[winner].g):
            winner = i

    node = queue.pop(winner)
    play_music(node.music)

    if not node.visited:
        for n in node.get_neighbours(grid):
            if n.visited:
                continue

            temp_g = node.g + 1

            if n in queue:
                if temp_g < n.g:
                    n.g = temp_g
            else:
                n.g = temp_g
                queue.append(n)

    return node


################################################### ALGORITHM VARIABLES #########################################################

order = 0

(grid,
start_node,
finish_node,
queue,
algorithm,
text,
text_rect,
simul_running) = [None for _ in range(8)]

def restart():

    global grid, start_node, finish_node, queue, algorithm, simul_running, text, text_rect, order, to_restart

    if order == 0:
        simul_running = False
    else:
        simul_running = True
        time.sleep(.3)

    grid = [[Node(i, j) for j in range(n_tiles)] for i in range(n_tiles)]

    start_node = grid[randrange(n_tiles)][randrange(n_tiles)]
    finish_node = grid[randrange(n_tiles)][randrange(n_tiles)]

    start_node.state = NodeState.start
    finish_node.state = NodeState.finish
    start_node.visited = True

    queue = start_node.get_neighbours(grid)
    algorithm, text_content = [
        (a_star, 'A Star'),
        (dijkstra, 'Dijkstra'),
        (greedy_bfs, 'Greedy Best First Search'),
        (dfs, 'Depth First Search'),
        (bfs, 'Breadth First Search')
    ][order % 5]

    text = font.render(text_content, True, colors['red'])
    text_rect = text.get_rect()
    text_rect.center = dim*2//3, 50

    order += 1
    to_restart = False

def check_finish(node):
    global simul_running
    global to_restart

    node.visited = True
    play_music(node.music)
    make_path(node)

    if node.state == NodeState.finish:
        print('Found the finish node!!!')
        simul_running = False
        to_restart = True

##################################################### MAIN LOOP #########################################################
    
restart()

while running:
    screen.fill(bg_color)

    if simul_running:
        if len(queue) > 0:
            check_finish(algorithm())
        else:
            print("Couldn't find the finish node :(")
            simul_running = False
            to_restart = True

    for row in grid:
        for tile in row:
            tile.show(screen)
   

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                simul_running = True

        elif event.type == pg.MOUSEBUTTONDOWN and not simul_running:
            wall_place = True

        elif event.type == pg.MOUSEBUTTONUP and not simul_running:
            wall_place = False
            
    if wall_place:
        pos = pg.mouse.get_pos()

        i = int(pos[0] / dim * n_tiles)
        j = int(pos[1] / dim * n_tiles)

        t = grid[i][j]
        if t.state == NodeState.moveable:
            t.state = NodeState.wall

    screen.blit(text, text_rect)
    pg.display.update()

    if to_restart:
        restart()

pg.quit()
