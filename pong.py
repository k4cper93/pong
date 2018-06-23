#!/usr/bin/env python3
# coding=utf-8

import pygame
import pygame.locals
import time
import configparser
import sys


def load_config(filename):
    """Loads config file"""
    config = configparser.ConfigParser()

    # don't convert option names to lowercase,
    # see configparser.RawConfigParser()
    config.optionxform = str
    config.read(filename)

    for section in config:
        variables = dict(config[section])
        for key in variables:
            try:
                variables[key] = int(variables[key])
            except ValueError:
                variables[key] = \
                list(map(int,variables[key].replace(' ', '').split(',')))
        globals().update(variables)


class Board(object):
    """Game's board. Draws everything"""

    def __init__(self, width, height):
        """Game window constructor. Size in pixels"""
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Simple Pong')

    def draw(self, *args):
        """Draw game window.

        :param args: list of objects to draw
        """
        self.surface.fill(BACKGROUND_COLOR)
        for drawable in args:
            drawable.draw_on(self.surface)

        pygame.display.update()


class PongGame(object):
    """Main game object"""
    def __init__(self, width, height):
        pygame.init()
        self.board = Board(width, height)
        self.fps_clock = pygame.time.Clock()
        self.ball = Ball(BALL_SIZE,
                         BALL_SIZE,
                         WINDOW_WIDTH/2,
                         WINDOW_HEIGHT/2,
                         BALL_COLOR,
                         INITIAL_X_SPEED,
                         INITIAL_Y_SPEED)

        self.player1 = Racket(10,
                              P1_RACKET_SIZE,
                              0,
                              height/2 - P1_RACKET_SIZE/2,
                              P1_RACKET_COLOR,
                              P1_MAX_SPEED)

        self.player2 = Racket(10,
                              P2_RACKET_SIZE,
                              width - 10,
                              height/2 - P2_RACKET_SIZE/2,
                              P2_RACKET_COLOR,
                              #P2_MAX_SPEED)
                              1)

        if OPPONENT == 1: self.ai = Ai(self.player2, self.ball)
        self.judge = Judge(self.board, self.ball, self.player2, self.ball)
        self.fps = FPS[7]

    def run(self):
        """Main loop"""
        self.board.draw(self.ball,
                        self.player1,
                        self.player2,
                        self.judge)
        time.sleep(1)
        while not self.handle_events():
            self.ball.move(self.board, self.player1, self.player2)
            self.board.draw(self.ball,
                            self.player1,
                            self.player2,
                            self.judge)
            if OPPONENT == 1: self.ai.move()
            pressed_keys = pygame.key.get_pressed()
            self.player1.move_with_keys()
            if pressed_keys[pygame.K_1]: self.fps = FPS[0]
            if pressed_keys[pygame.K_2]: self.fps = FPS[1]
            if pressed_keys[pygame.K_3]: self.fps = FPS[2]
            if pressed_keys[pygame.K_4]: self.fps = FPS[3]
            if pressed_keys[pygame.K_5]: self.fps = FPS[4]
            if pressed_keys[pygame.K_6]: self.fps = FPS[5]
            if pressed_keys[pygame.K_7]: self.fps = FPS[6]
            if pressed_keys[pygame.K_8]: self.fps = FPS[7]
            if pressed_keys[pygame.K_9]: self.fps = FPS[8]
            if pressed_keys[pygame.K_r]:
                self.judge.reset()
            self.fps_clock.tick(self.fps)

    def handle_events(self):
        """Handle system events like quit or pause"""
        for event in pygame.event.get():
            if (event.type == pygame.locals.QUIT or
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return True

            if OPPONENT == 0:
                if event.type == pygame.locals.MOUSEMOTION:
                    x, y = event.pos
                    self.player2.move_with_mouse(y)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.pause()

    def pause(self):
        """Pause game, use SPACE button by default"""
        pause_text = "PAUSE"
        self.judge.draw_text(self.board.surface,
                             pause_text,
                             WINDOW_WIDTH/2,
                             WINDOW_HEIGHT/2)
        pygame.display.update()

        while True:
            event = pygame.event.wait()
            if (event.type == pygame.locals.QUIT or
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return


class Drawable(object):
    """Base class for drawable objects"""

    def __init__(self, width, height, x, y, color):
        self.width = width
        self.height = height
        self.color = color
        self.surface = pygame.Surface((width, height),
                                      pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.surface.get_rect(x=x, y=y)

    def draw_on(self, surface):
        """Draws a surface onto Rect"""
        surface.blit(self.surface, self.rect)


class Ball(Drawable):
    """The ball has its speed and movement direction."""
    def __init__(self, width, height, x, y, color, x_speed, y_speed):
        super(Ball, self).__init__(width, height, x, y, color)
        pygame.draw.ellipse(self.surface, self.color, [0, 0, self.width, self.height])
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.start_x = x
        self.start_y = y

    def bounce_y(self):
        """Reverse y_speed"""
        self.y_speed *= -1

    def bounce_x(self):
        """Reverse x_speed"""
        self.x_speed *= -1

    def reset(self):
        """Reset ball's position and reverse x_speed"""
        self.rect.x, self.rect.y = self.start_x, self.start_y
        self.bounce_x()

    def move(self, board, *args):
        """Moves ball in direction given by x_speed and y_speed"""
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

        if self.rect.y < 0 or self.rect.y > board.surface.get_height()-BALL_SIZE:
            self.bounce_y()

        for racket in args:
            if self.rect.colliderect(racket.rect):
                self.bounce_x()

class Racket(Drawable):
    """Racket, moves up/down with board's size and speed constraints.
    P1 - UP/DOWN ARROWS
    P2 - MOUSE STEERING/AI as in config file
    """

    def __init__(self, width, height, x, y, color, max_speed):
        super(Racket, self).__init__(width, height, x, y, color)
        self.max_speed = max_speed
        self.surface.fill(color)

    def move_with_mouse(self, y):
        """Moves racket's middle point to mouse pointer location"""
        delta = y - self.rect.y
        if abs(delta) > self.max_speed:
            delta = self.max_speed if delta > 0 else -self.max_speed
        if (self.rect.y + delta <= WINDOW_HEIGHT - self.height and
            self.rect.y + delta >= 0):
            self.rect.y += delta

    def move_with_keys(self):
        keystate = pygame.key.get_pressed()
        delta = keystate[pygame.K_DOWN] - keystate[pygame.K_UP]
        if (self.rect.y + delta <= WINDOW_HEIGHT - self.height and
            self.rect.y + delta >= 0):
            self.rect.y += delta



class Ai(object):
    """AI always chasing the ball with its center point"""
    def __init__(self, racket, ball):
        self.ball = ball
        self.racket = racket

    def move(self):
        y = self.ball.rect.centery - self.racket.height/2
        self.racket.move_with_mouse(y)


class Judge(object):
    """Judges when and who wins the point and updates score table"""

    def __init__(self, board, ball, *args):
        self.ball = ball
        self.board = board
        self.rackets = args
        self.score = [0, 0]

        pygame.font.init()
        font_path = pygame.font.match_font('arial')
        self.font = pygame.font.Font(font_path, 64)

    def update_score(self, board_width):
        """Gives point when conditions met and resets ball"""
        if self.ball.rect.x < 0:
            self.score[1] += 1
            self.ball.reset()
            time.sleep(1)
        elif self.ball.rect.x > board_width - BALL_SIZE:
            self.score[0] += 1
            self.ball.reset()
            time.sleep(1)

    def reset(self):
        self.score[0] = 0
        self.score[1] = 0
        self.ball.reset()
        time.sleep(1)

    def draw_text(self, surface,  text, x, y):
        """Draws given text in given location"""
                                # text, antialias, color
        text = self.font.render(text, True, (150, 150, 150))
        rect = text.get_rect()
        rect.center = x, y
        surface.blit(text, rect)

    def draw_on(self, surface):
        """Refreshes and draws score table"""
        height = self.board.surface.get_height()
        width = self.board.surface.get_width()
        self.update_score(width)
        self.draw_text(surface, "{} : {}".format(self.score[0],
                                                 self.score[1]), width/2, 30)


if __name__ == "__main__":
    load_config('config.ini')
    game = PongGame(WINDOW_WIDTH, WINDOW_HEIGHT)
    game.run()
