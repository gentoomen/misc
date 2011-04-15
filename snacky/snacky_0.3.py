#!/usr/bin/python
import sys
import random
import pygame
from pygame.locals import *

#constants
screen_size = (640, 480)

class rect_array:
    def __init__(self, color = (0,0,0), size = (10,10)):
        self.color = color
        self.size = size
        self.surface = pygame.Surface(self.size).convert()
        self.surface.fill(self.color)
        self.rect = self.surface.get_rect()
        self.array = [self.rect]
    def mv(self, index, x, y):
        self.array[index] = self.array[index].move(x, y)
    def add(self, x, y, fresh = False, index = -1):
        if fresh:
            self.tmp_rect = self.surface.get_rect()
        else:
            self.tmp_rect = self.array[index]
        self.array.append(self.tmp_rect.move(x, y))
    def rem(self, index):
        self.array.pop(index)

def Quittan(score):
    print "YOUR SCORE: " +str(score)
    sys.exit()

def main():
    #LET'S INIT IN THIS MOFO
    DIRECTION = "RIGHT" #initial direction
    LENGHT = 10 #initial length
    score = 0 #initial score
    price = 100 #points per apple
    wrapping = True
    pygame.init() #init pygame
    screen = pygame.display.set_mode(screen_size) #get screen object
    background = pygame.Surface(screen_size).convert() #bg surface for blitting/clearing screen
    background.fill((0, 0 ,100)) #color it blue
    bg_rect = background.get_rect() #get bg sized rectangle for collision testing
    snake = rect_array((255 ,0 ,0)) #init snake using our own class
    snake.mv(0, 100, 50) #initial pos for snake
    apple = rect_array((0, 255, 0)) #init apples
    apple.rem(0) #current rect_array class adds an initial value, so let's pop it
    font = pygame.font.Font(None, 36) #init font
    clock = pygame.time.Clock()#get clock for FPS limit
    screen.blit(background, (0, 0)) #draw bg to screen object to clear shit
    pygame.display.update() #flip it
    pygame.mixer.quit #sound shit
    pygame.mixer.init(44100, 16, 2)
    main_music = pygame.mixer.Sound('./ter_vel_2.ogg')
    eat_snd = pygame.mixer.Sound('./eat_snd.wav')
    new_apple_snd = pygame.mixer.Sound('./new_apple.wav')
    #HERE WE GO
    main_music.play(-1) #music kicks in
    muted = False
    while 1:
    
        #GET EVENTS
        for event in pygame.event.get():
            if event.type == QUIT: Quittan(score)
            if (event.type == KEYDOWN):
                if event.key == K_p or event.key == K_SPACE:
                    paused = True
                    paused_text = font.render("PAUSED", 1, (255, 0, 0))
                    screen.blit(paused_text, (280, 220))
                    pygame.display.update()
                    while paused:
                        for event in pygame.event.get():
                            if event.type == KEYDOWN:
                                if event.key == K_SPACE or event.key == K_p:
                                    paused = False
                                    break
                            elif event.type == QUIT:
                                Quittan(score)
                if event.key == K_m:
                    if not muted:
                        main_music.stop()
                        muted = True
                    else:
                        main_music.play()
                        muted = False
                if (event.key == K_UP) and ( DIRECTION == "LEFT" or DIRECTION == "RIGHT" ): DIRECTION = "UP"
                if (event.key == K_LEFT) and ( DIRECTION == "UP" or DIRECTION == "DOWN" ): DIRECTION = "LEFT"
                if (event.key == K_RIGHT) and ( DIRECTION == "UP" or DIRECTION == "DOWN" ): DIRECTION = "RIGHT"
                if (event.key == K_DOWN) and ( DIRECTION == "LEFT" or DIRECTION == "RIGHT" ): DIRECTION = "DOWN"

        #CLEAR
        screen.blit(background, (0, 0))

        #UPDATE SHIT
        if DIRECTION == "DOWN": snake.add(0, 10) #where we going..
        elif DIRECTION == "UP": snake.add(0, -10)
        elif DIRECTION == "LEFT": snake.add(-10, 0)
        elif DIRECTION == "RIGHT": snake.add(10, 0)
        if LENGHT <= len(snake.array): snake.rem(0) #snake length logic
        if random.randrange(1, 101) == 1: #randun apples
            #here needs to be an check if apple collides with snake
            if not muted:
                new_apple_snd.play()
            apple.add(random.randrange(0, 641, 10), random.randrange(0, 481, 10), True)

        #COLLISION TESTS
        if wrapping:
            if snake.array[-1].right > screen_size[0]:snake.mv(-1, -640,0)
            elif snake.array[-1].left < 0:snake.mv(-1, 640,0)
            elif snake.array[-1].top < 0:snake.mv(-1, 0, +480)
            elif snake.array[-1].bottom > screen_size[1]:snake.mv(-1, 0, -480)
        #COLLISION TESTS
        else:
            if not bg_rect.contains(snake.array[-1]): Quittan(score) #out of bounds
        if snake.array[-1].collidelist(snake.array[0:-1]) != -1: Quittan(score) #poking self
        if snake.array[-1].collidelist(apple.array) != -1: #omnomnom
            if not muted:
                eat_snd.play()
            apple.array.pop(snake.array[-1].collidelist(apple.array))
            score = score + price * int((len(snake.array) + 1) / 10)
            LENGHT = LENGHT + 5

        score_text = font.render("SCORE: "+ str(score), 1, (220, 220, 220))

        #REDRAW SHIT
        screen.blit(score_text, (25, 25))
        for i in snake.array:
            screen.blit(snake.surface, i)
        for i in apple.array:
            screen.blit(apple.surface, i)
        pygame.display.update()

        #30 FPS
        clock.tick(30)
main()
