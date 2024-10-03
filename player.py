import pygame

class Player:
    def __init__(self, size):
        self.x = 0
        self.y = 0
        self.moving = False
        self.size = size
        