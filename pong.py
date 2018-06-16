#!/usr/bin/env python3
# coding=utf-8


import pygame
import pygame.locals
import time

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
BACKGROUND_COLOR = (0, 0, 0)
FPS = 120
BALL_SIZE = 15
BALL_COLOR = (255, 255, 255)
INITIAL_X_POSITION = WINDOW_WIDTH/2
INITIAL_Y_POSITION = WINDOW_HEIGHT/2
INITIAL_X_SPEED = 3
INITIAL_Y_SPEED = 3

class Board(object):
    """
    Plansza do gry. Odpowiada za rysowanie okna gry.
    """

    def __init__(self, width, height):
        """
        Konstruktor planszy do gry. Przygotowuje okienko gry.

        :param width:
        :param height:
        """
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Simple Pong')

    def draw(self, *args):
        """
        Rysuje okno gry

        :param args: lista obiektów do narysowania
        """
        self.surface.fill(BACKGROUND_COLOR)
        for drawable in args:
            drawable.draw_on(self.surface)

        # dopiero w tym miejscu następuje fatyczne rysowanie
        # w oknie gry, wcześniej tylko ustalaliśmy co i jak ma zostać narysowane
        pygame.display.update()


class PongGame(object):
    """Łączy wszystkie elementy gry w całość."""

    def __init__(self, width, height):
        pygame.init()
        self.board = Board(width, height)
        self.fps_clock = pygame.time.Clock()
        self.ball = Ball(BALL_SIZE,
                         BALL_SIZE,
                         INITIAL_X_POSITION,
                         INITIAL_Y_POSITION,
                         BALL_COLOR,
                         INITIAL_X_SPEED,
                         INITIAL_Y_SPEED)
        self.player1 = Racket(width=10, height=80, x=0, y=height/2)

    def run(self):
        """Główna pętla programu"""
        while not self.handle_events():
            # działaj w pętli do momentu otrzymania sygnału do wyjścia
            self.ball.move(self.board)
            self.board.draw(self.ball,
                            self.player1)
            self.fps_clock.tick(FPS)

    def handle_events(self):
        """Handle system events. Return True if pygame returns quit event"""
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                return True

                if event.type == pygame.locals.MOUSEMOTION:
                    x, y = event.pos
                    self.player1.move(y)


class Drawable(object):
    """Base class for drawable objects"""

    def __init__(self, width, height, x, y, color):
        self.width = width
        self.height = height
        self.color = color
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA, 32).convert_alpha()
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
        """
        Odwraca wektor prędkości w osi Y
        """
        self.y_speed *= -1

    def bounce_x(self):
        """
        Odwraca wektor prędkości w osi X
        """
        self.x_speed *= -1

    def reset(self):
        """
        Ustawia piłeczkę w położeniu początkowym i odwraca wektor prędkości w osi Y
        """
        self.rect.move(self.start_x, self.start_y)
        self.bounce_y()

    def move(self, board, *args):
        """
        Przesuwa piłeczkę o wektor prędkości
        """
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

        if self.rect.x < 0 or self.rect.x > board.surface.get_width()-BALL_SIZE:
            self.bounce_x()

        if self.rect.y < 0 or self.rect.y > board.surface.get_height()-BALL_SIZE:
            self.bounce_y()

        for racket in args:
            if self.rect.colliderect(racket.rect):
                self.bounce_x()

class Racket(Drawable):
    """
    Rakietka, porusza się w osi X z ograniczeniem prędkości.
    """

    def __init__(self, width, height, x, y, color=(255, 255, 255), max_speed=10):
        super(Racket, self).__init__(width, height, x, y, color)
        self.max_speed = max_speed
        self.surface.fill(color)

    def move(self, y):
        """
        Przesuwa rakietkę w wyznaczone miejsce.
        """
        delta = y - self.rect.y
        if abs(delta) > self.max_speed:
            delta = self.max_speed if delta > 0 else -self.max_speed
        self.rect.y += delta


if __name__ == "__main__":
    game = PongGame(WINDOW_WIDTH, WINDOW_HEIGHT)
    game.run()
