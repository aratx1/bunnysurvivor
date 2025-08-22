#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import pygame, sys
# ...existing code...
import os


# Setup pygame/window
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('game base')
screen = pygame.display.set_mode((1244, 700), 0, 32)


# Cargar la fuente m6x11plus (asegúrate de tener el archivo en "fonts/m6x11plus.ttf")
font = pygame.font.Font("fonts/m6x11plus.ttf", 150)

background = pygame.image.load(os.path.join("images", "menu", "fondo.png")).convert()


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def main_menu():
    while True:
        screen.blit(background, (0, 0))  # Dibuja la imagen de fondo
        draw_text('BUNNY SURVIVOR!!', font, (0, 0, 0), screen, 200, 40)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        mainClock.tick(60)

main_menu()

