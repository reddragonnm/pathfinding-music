import pygame as pg
from pygame.color import THECOLORS as colors
from pygame.draw import *

from enum import IntEnum
from random import random, randrange, choice
import time

pg.init()

############################################ PROGRAM VARIABLES ################################################

running = True
wall_place = False
simul_running = False

dim = 600
n_tiles = 50
tile_size = dim // n_tiles
bg_color = colors['lightblue']

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
    def __init__(self, i, j):
        # for a*
        self.f = 0
        self.g = 0
        self.h = 0

        self.pos = i, j
        self.state = NodeState.moveable

        self.visited = False
        self.parent = None
        self.in_path = False

    def restart(self):
        self.state = NodeState.moveable
        self.visited = False
        self.parent = None
        self.in_path = False

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
            [-1, 0],
            [1, 0],
            [0, 1],
            [0, -1]
        ]

        for n, pos in enumerate(arr):
            i = self.pos[0] + pos[0]
            j = self.pos[1] + pos[1]

            if 0 <= i < len(grid) and 0 <= j < len(grid[0]):
                t = grid[i][j]
                if t.state != NodeState.wall and not t.visited:
                    t.parent = self
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

grid = [[Node(i, j) for j in range(n_tiles)] for i in range(n_tiles)]

algo_text = {
    'BFS': bfs,
    'DFS': dfs,
    'A Star': a_star,
    'Djikstra': dijkstra,
    'Greedy Search': greedy_bfs
}

queue = []
start_node = None
finish_node = None

text_content = 'A Star'
text = font.render(text_content, True, colors['red'])
text_rect = text.get_rect()
text_rect.center = dim*2//3, 50

def check_finish(node):
    global simul_running

    node.visited = True
    make_path(node)

    if node.state == NodeState.finish:
        print('Found the finish node!!!')
        simul_running = False

##################################################### MAIN LOOP #########################################################
    
n_clicks  = 0
prev_pos = []
algorithm = algo_text[text_content]

while running:
    screen.fill(bg_color)

    if simul_running:
        if len(queue) > 0:
            check_finish(algorithm())
        else:
            print("Couldn't find the finish node :(")
            simul_running = False

    for row in grid:
        for tile in row:
            tile.show(screen)
   
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                simul_running = True

            elif event.key == pg.K_r:
                simul_running = False
                n_clicks = 0
                queue = []            
                grid = [[Node(i, j) for j in range(n_tiles)] for i in range(n_tiles)]


        elif event.type == pg.MOUSEBUTTONDOWN and not simul_running:
            wall_place = True
            n_clicks += 1

        elif event.type == pg.MOUSEBUTTONUP and not simul_running:
            wall_place = False
            
    if wall_place:
        pos = pg.mouse.get_pos()

        i = int(pos[0] / dim * n_tiles)
        j = int(pos[1] / dim * n_tiles)

        t = grid[i][j]
        
        if n_clicks == 1:
            start_node = t
            t.state = NodeState.start
            t.visited = True
            wall_place = False
            queue.extend(t.get_neighbours(grid))
        elif n_clicks == 2:
            if t.state == NodeState.moveable:
                finish_node = t
                t.state = NodeState.finish
                wall_place = False
        elif t.pos != prev_pos:
            if t.state == NodeState.wall:
                t.state = NodeState.moveable
            elif t.state == NodeState.moveable:
                t.state = NodeState.wall
        
        prev_pos = t.pos

    screen.blit(text, text_rect)
    pg.display.update()

pg.quit()
