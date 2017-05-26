#!/usr/bin/env python2

import sys
import pygame

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BUTTON_GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
BUTTON_BRIGHT_GREEN = (0, 255, 0)


class Model(object):

    def __init__(self, rows, cols):
        self.rows = rows
        self.columns = cols

    def num_neighbours(self, state, x, y):
        """
        Return number of neighbours for a cell given by its coordinates.
        :param state: Two-dimensional list filled with 0 and 1. 1 means that
                      cell is occupied. 0 means that cell is empty.
        :param x: x-coord of cell
        :param y: y-coord of cell
        :return: number of neighbours of the cell
        """
        result = - state[x][y]

        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                neighbour_x, neighbour_y = [(x + i) % self.rows,
                                            (y + j) % self.columns]
                result = result + state[neighbour_x][neighbour_y]

        return result

    def update_state(self, old_state):
        new_state = [[0] * self.columns for col in xrange(self.rows)]
        for x in xrange(self.rows):
            for y in xrange(self.columns):
                num_neighbours = self.num_neighbours(old_state, x, y)
                new_state[x][y] = Model.get_state_cell(num_neighbours,
                                                       old_state[x][y])

        return new_state

    @staticmethod
    def get_state_cell(num_neighbours, cell_state):
        # underpopulation
        if num_neighbours < 2:
            return 0

        # survive to next generation
        if 2 <= num_neighbours <= 3 and cell_state == 1:
            return 1

        # overpopulation
        if num_neighbours >= 4:
            return 0

        # reproduction
        if num_neighbours == 3 and cell_state == 0:
            return 1

        return 0


class View(object):

    BACK_COLOR = WHITE
    CELL_COLOR = BLUE
    BOUND_COLOR = BLACK

    BOX_SIZE = 20
    MENU_BAR_SIZE = 50
    LINE_WIDTH = 1
    CAPTION = "Game Of Life"

    def __init__(self, configuration_file=None, rows=30, columns=40):
        if configuration_file is None:
            self.__initialize(rows, columns)
            self.state = [[0] * columns for col in xrange(rows)]
        else:
            with open(configuration_file) as f:
                content = f.readlines()
            self.state = [map(int, x.strip().split(' ')) for x in content]
            self.__initialize(len(self.state), len(self.state[0]))
        self.frame_speed = 64

    def __initialize(self, rows, columns):
        self.height = rows * self.BOX_SIZE
        self.width = columns * self.BOX_SIZE
        self.screen = pygame.display.set_mode((self.width,
                                               self.height +
                                               self.MENU_BAR_SIZE))
        pygame.display.set_caption(self.CAPTION)

        self.colorFlag = True
        self.gameStartFlag = False
        self.done = False

        self.cannot_slower = False
        self.cannot_faster = False

        self.clock = pygame.time.Clock()
        self.screen.fill(self.BACK_COLOR)

        for x in xrange(-self.BOX_SIZE, self.height, self.BOX_SIZE):
            pygame.draw.line(self.screen, self.BOUND_COLOR, [0, 20 + x],
                             [self.width, 20 + x], self.LINE_WIDTH)

        for x in xrange(-self.BOX_SIZE, self.width, self.BOX_SIZE):
            pygame.draw.line(self.screen, self.BOUND_COLOR, [20 + x, 0],
                             [20 + x, self.height], self.LINE_WIDTH)

        self.game = Model(rows, columns)

    def start(self):
        while not self.done:
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.done = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.check_start_button(mouse):
                        self.gameStartFlag = True

                    if self.check_reset_button(mouse):
                        for x in xrange(self.game.rows):
                            for y in xrange(self.game.columns):
                                self.state[x][y] = 0

                    if self.check_slower_button(mouse):
                        if self.frame_speed > 8:
                            self.frame_speed /= 2
                            self.cannot_faster = False
                        else:
                            self.cannot_slower = True

                    if self.check_faster_button(mouse):
                        if self.frame_speed < 600:
                            self.frame_speed *= 2
                            self.cannot_slower = False
                        else:
                            self.cannot_faster = True

                    if 0 < mouse[1] < self.height:
                        print >> sys.stderr, mouse[0], mouse[1]

                        x_ = int(mouse[1] / self.BOX_SIZE)
                        y_ = int(mouse[0] / self.BOX_SIZE)

                        print >> sys.stderr, "Clicked On", x_, y_
                        if self.state[x_][y_] == 0:
                            self.state[x_][y_] = 1
                        else:
                            self.state[x_][y_] = 0

            pygame.draw.rect(self.screen,
                             BUTTON_GREEN,
                             [10, self.height + 2, 50, 20], 0)
            pygame.draw.rect(self.screen,
                             RED if self.cannot_slower else BUTTON_GREEN,
                             [10, self.height + 25, 60, 20], 0)
            pygame.draw.rect(self.screen,
                             BUTTON_GREEN,
                             [100, self.height + 2, 50, 20], 0)
            pygame.draw.rect(self.screen,
                             RED if self.cannot_faster else BUTTON_GREEN,
                             [100, self.height + 25, 60, 20], 0)

            if self.check_start_button(mouse):
                pygame.draw.rect(self.screen, YELLOW,
                                 [12, self.height + 4, 46, 16], 0)
            else:
                pygame.draw.rect(self.screen, BUTTON_BRIGHT_GREEN,
                                 [12, self.height + 4, 46, 16], 0)

            self.screen.blit(startLabel, (16, self.height + 6))
            self.screen.blit(resetLabel, (106, self.height + 6))
            self.screen.blit(slowerLabel, (16, self.height + 6 + 25))
            self.screen.blit(fasterLabel, (106, self.height + 6 + 25))

            cell_color = BLUE
            self.colorFlag = True
            for x in range(0, self.game.rows):
                for y in range(0, self.game.columns):
                    if self.state[x][y] == 1:
                        pygame.draw.rect(self.screen, cell_color,
                                         [y * self.BOX_SIZE + self.LINE_WIDTH,
                                          x * self.BOX_SIZE + self.LINE_WIDTH,
                                          self.BOX_SIZE - self.LINE_WIDTH,
                                          self.BOX_SIZE - self.LINE_WIDTH], 0)
                    else:
                        pygame.draw.rect(self.screen, self.BACK_COLOR,
                                         [y * self.BOX_SIZE + self.LINE_WIDTH,
                                          x * self.BOX_SIZE + self.LINE_WIDTH,
                                          self.BOX_SIZE - self.LINE_WIDTH,
                                          self.BOX_SIZE - self.LINE_WIDTH], 0)

            pygame.display.flip()
            self.clock.tick(self.frame_speed)

            while self.gameStartFlag:
                mouse = pygame.mouse.get_pos()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.gameStartFlag = False
                        self.done = True

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.check_start_button(mouse):
                            self.gameStartFlag = False

                pygame.draw.rect(self.screen, BUTTON_GREEN,
                                 [10, self.height + 2, 50, 20], 0)

                if self.check_start_button(mouse):
                    pygame.draw.rect(self.screen, YELLOW,
                                     [12, self.height + 4, 46, 16], 0)
                else:
                    pygame.draw.rect(self.screen, BUTTON_BRIGHT_GREEN,
                                     [12, self.height + 4, 46, 16], 0)
                self.screen.blit(stopLabel, (16, self.height + 6))

                if self.colorFlag:
                    cell_color = RED
                    self.colorFlag = False
                else:
                    cell_color = BLUE
                    self.colorFlag = True

                self.state = self.game.update_state(self.state)

                for x in range(0, self.game.rows):
                    for y in range(0, self.game.columns):
                        if self.state[x][y] == 1:
                            pygame.draw.rect(self.screen, cell_color,
                                             [y * self.BOX_SIZE +
                                              self.LINE_WIDTH,
                                              x * self.BOX_SIZE +
                                              self.LINE_WIDTH,
                                              self.BOX_SIZE -
                                              self.LINE_WIDTH,
                                              self.BOX_SIZE -
                                              self.LINE_WIDTH], 0)
                        else:
                            pygame.draw.rect(self.screen, self.BACK_COLOR,
                                             [y * self.BOX_SIZE +
                                              self.LINE_WIDTH,
                                              x * self.BOX_SIZE +
                                              self.LINE_WIDTH,
                                              self.BOX_SIZE -
                                              self.LINE_WIDTH,
                                              self.BOX_SIZE -
                                              self.LINE_WIDTH], 0)

                pygame.display.flip()
                self.clock.tick(self.frame_speed)

        pygame.quit()

    def check_start_button(self, mouse):
        return self.height + 2 < mouse[1] < self.height + 22 and \
               10 < mouse[0] < 60

    def check_reset_button(self, mouse):
        return self.height + 2 < mouse[1] < self.height + 22 and \
               100 < mouse[0] < 150

    def check_slower_button(self, mouse):
        return self.height + 25 < mouse[1] < self.height + 45 and \
               10 < mouse[0] < 60

    def check_faster_button(self, mouse):
        return self.height + 25 < mouse[1] < self.height + 45 and \
               100 < mouse[0] < 150


if __name__ == '__main__':
    pygame.init()

    font = pygame.font.SysFont('Arial Black', 15)

    startLabel = font.render("START", 1, BLACK)
    stopLabel = font.render("PAUSE", 1, BLACK)
    resetLabel = font.render("RESET", 1, BLACK)
    slowerLabel = font.render("SLOWER", 1, BLACK)
    fasterLabel = font.render("FASTER", 1, BLACK)

    game = View()
    game.start()
