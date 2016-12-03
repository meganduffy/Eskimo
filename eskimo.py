#!/usr/bin/env python
#------------------------------------------------------
# Eskimo tutorial Version 0.1
#
# Created by RoeBros
# License: GPL
#
#------------------------------------------------------

""" This is an easy but complex game tutorial for pygame.
    It will explain in detail all the parts needed to program a game using python/pygame."""
    
#import required libraries/Modules
import os, pygame, sys, random
import random
from pygame.locals import *


#functions used to load sounds and images
def load_image(name, colorkey=None):
    """loads an image into memory"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    """loads a sound file (.wav) in memory"""
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

#classes(sprites) for our game objects
class Eskimo(pygame.sprite.Sprite):
    """this is the class for our hero unit"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #this is the base image
        self.image, self.rect = load_image('eskimo1.png', -1)

        #this is the sprites starting point on the screen
        self.rect.centerx = 100
        self.rect.centery = 350

        #this group of data is used to animate the sprite
        self.moving1 = pygame.image.load(os.path.join('data','eskimo1.png'))
        self.movingnorm = pygame.image.load(os.path.join('data','eskimo2.png'))
        self.moving3 = pygame.image.load(os.path.join('data','eskimo3.png'))
        self.movingfast1 = pygame.image.load(os.path.join('data','eskimofast1.png'))
        self.movingfast2 = pygame.image.load(os.path.join('data','eskimofast2.png'))
        self.movingslow = pygame.image.load(os.path.join('data','eskimoslow.png'))

        #sounds for the players movements
        #can only be a .wav file
        self.speed = load_sound('whoosh.wav')
        self.slow = load_sound('slow.wav')
        self.normal = load_sound('norm-walk.wav')

        #these are the timers that control the animation
        self.counter = 0
        self.fast_counter = 0

        #this tells the animator how fast the sprite is moving
        self.fast = 0

    def update(self):
        """animate the sprite based on its speed"""
        if self.fast == 0:
            self.counter += 1
            if self.counter == 20:
                self.image = self.moving3
                self.normal.play()
            if self.counter == 30:
                self.image = self.movingnorm
            if self.counter == 40:
                self.image = self.moving1
                self.normal.play()
            if self.counter == 50:
                self.image = self.movingnorm
                self.counter = 0
        if self.fast == 1:
            self.fast_counter += 1
            if self.fast_counter == 10:
                self.image = self.movingfast1
                self.speed.play()
            if self.fast_counter == 20:
                self.image = self.movingnorm
            if self.fast_counter == 30:
                self.image = self.movingfast2
            if self.fast_counter == 40:
                self.image = self.movingnorm
                self.fast_counter = 0
        if self.fast == -1:
            self.fast_counter += 1
            if self.fast_counter == 10:
                self.image = self.movingslow
                self.slow.play()
            if self.fast_counter == 30:
                self.image = self.movingnorm
                self.fast_counter = 0


class Trail(pygame.sprite.Sprite):
    """this is the class for the trail that follows the unit"""
    def __init__(self, startpos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('path.png', None)
        self.rect.centerx = startpos[0]
        self.rect.centery = startpos[1] + 25

    def update(self):
        """this forces the trail to move down at the same speed as the background
           giving the illusion that the eskimo is moving"""
        self.rect.move_ip((0,2))
        #this kills the sprite if it goes too low
        if self.rect.centery > 650:
            self.kill()   

class PolarBear(pygame.sprite.Sprite):
    """class for the enemy Polar Bear"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('polar_bear.gif', -1)
        self.rect.centerx = 100
        self.rect.centery = 560
        self.counter = 0
    
    def update(self, speed, gox, goy):
        """this moves the polar bear based on the position of the eskimo and trees
           causing it to follow you but go around trees.
           The extra information must be supplied when you tell this sprite to update."""
        self.counter += 1

        #'global' means this information is available to any class or function that might need it
        #and not limited to one class or function
        
        #this calls the class hero which is later defined, used to check eskimos position
        global hero
        
        if self.counter == 2:
            if gox == 0 and goy == 0:
                if hero.rect.centerx > self.rect.centerx:
                    if not self.rect.centerx > 174:
                        self.rect.move_ip((speed * 1,0))
                if hero.rect.centerx < self.rect.centerx:
                    if not self.rect.centerx < 20:
                        self.rect.move_ip((speed * -1,0))
                if hero.rect.centery > self.rect.centery:
                    self.rect.move_ip((0,speed * 1))
                if hero.rect.centery < self.rect.centery:
                    self.rect.move_ip((0,speed * -1))
            self.counter = 0
            
        if gox == 1 or gox == -1 and goy == 0:
            if not self.rect.centery > 530:
                self.rect.move_ip((gox * 2,6))
        if gox == 1 or gox == -1 and goy == 1:
            if not self.rect.centery > 560:
                self.rect.move_ip((gox * 2,speed * 1))
                
class Tree(pygame.sprite.Sprite):
    """class for the trees that you must dodge"""
    def __init__(self, startpos):
        #this sprite doesnt have a fixed start position so you must give it one when you create it
        #used when you're placing multiple sprites or placing sprites at random positions
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('tree.png', -1)

        #this is another way of placing the starting point
        self.rect.midtop = startpos
    
    def update(self, speed):
        #this sprite needs to know what speed it must move at
        self.rect.move_ip((0,speed))
        
        if self.rect.centery > 600:
            self.kill()

class Stump(pygame.sprite.Sprite):
    """this is the class for the stump that is left behind when the eskimo or the polar bear destroy a tree"""
    def __init__(self, startpos):
        #this sprite also requires a start position so that it is placed at the spot where the tree was
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('stump.png', -1)
        self.rect.midtop = startpos
    
    def update(self, speed):
        self.rect.move_ip((0,speed))
        if self.rect.centery > 600:
            self.kill()
            
class EndFlag(pygame.sprite.Sprite):
    """this is the class for the finish line"""
    def __init__(self, startpos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('finishline.png', -1)
        self.image.convert()
        self.rect.midtop = startpos
        self.counter = 0

    def update(self, speed):
        self.counter += 1
        if self.counter == 3:
            self.rect.move_ip((0,speed - 1))
            self.counter = 0
        if self.rect.centery > 600:
            self.kill()

#Functions for creating the eskimo and polarbear     
def createEskimo(screen):
    #here is where 'hero' is defined
    global hero
    hero = Eskimo()

    #this tells the game that this object is a sprite and draws it on the screen
    hero_sprites = pygame.sprite.RenderClear()
    hero_sprites.add(hero)
    hero_sprites.draw(screen)
    return hero_sprites

def createPBear(screen):
    global enemy
    enemy = PolarBear()
    
    enemy_sprites = pygame.sprite.RenderClear()
    enemy_sprites.add(enemy)
    enemy_sprites.draw(screen)
    return enemy_sprites

#class for the game phases or windows
#always place the first phase at the bottom, 2nd phase next, last phase top, etc.
def youLose():
    """this is the screen for when you lose"""
    #this initiates pygame and causes it to run
    pygame.init()

    #this the font information, used to write words/information onto the screen
    font = pygame.font.Font(None, 35)
    green = 38, 246, 11
    hum = 2, 81, 76

    #this creates the screen and then fills it with a color
    screen = pygame.display.set_mode((500, 600))
    screen.fill([100,100,200])

    #this tells the game what 'caption' to set at the top of the screen
    pygame.display.set_caption("Eskimo Tutorial -- You lost")
    
    #this writes the words onto the screen
    #the first message is "You have lost the game." you must have the message in "" or it wont work
    #ignore the number in 'ren' the last pice of data is the color
    ren = font.render("You have lost the game.", 1, green)
    #this tells the game to draw the message to a cetain start location, x = 115,y = 150
    screen.blit(ren, (115, 150))

    
    ren = font.render("Press Escape to quit.", 1, hum)
    screen.blit(ren, (115, 300))

    #this tells the program to quit when you press the escape key
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
                raise SystemExit()

    #this tells the game to make the screen to update and draw everything correctly
    pygame.display.flip()

def youWin():
    """this is the screen for when you win"""
    pygame.init()
    
    font = pygame.font.Font(None, 40)
    fontt = pygame.font.Font(None, 30)
    green = 38, 246, 11
    hum = 2, 81, 76

    global hitpoints
    global difficulty
    
    screen = pygame.display.set_mode((500, 600))
    screen.fill([100,100,200])
    pygame.display.set_caption("Eskimo Tutorial -- You Won!")

    ren = font.render("Congradulations!You Won!", 1, green)
    screen.blit(ren, (75, 100))

    #this is how you put data into your message,
    #%=difficulty  %s tells the game to print the data in difficulty in the message
    ren = font.render("You were playing on %s mode!" % difficulty, 1, green)
    screen.blit(ren, (20, 200))   
    ren = fontt.render("You had %s hitpoints!." % hitpoints, 1, hum)
    screen.blit(ren, (150, 350))
    
    ren = fontt.render("Press Escape to quit.", 1, hum)
    screen.blit(ren, (155, 500))

    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
                raise SystemExit()

    pygame.display.flip()

def main():
    """the main scren for the game"""
    
    pygame.init()
    random.seed()

    #this is how you load music and is what you should use for background music
    #this way also supports more than one sound file type including, .mp3, .mid, .ogg, and .wav
    background_music = pygame.mixer
    background_music.init()
    background_music.music.load(os.path.join('data', 'theme.mid'))
    #this sets the volume of the track and plays it
    background_music.music.set_volume(0.5)
    background_music.music.play()

    #data is modified based on the difficulty you choose
    global difficulty
    global hitpoints
    
    if difficulty == 'easy':
        pb_speed = 1
        tree_speed = 2
        #this is where 'hitpoints' is defined
        hitpoints = 10
        #this is the maximum number of trees the game can create at one time
        max_trees = 15
        #this makes sure the game knows how many hitpoints you start with
        max_hp = 10
        energy = 20
        #this makes sure the game knows how much energy you start with
        max_energy = 20
    if difficulty == 'medium':
        pb_speed = 1
        tree_speed = 3
        hitpoints = 8
        max_trees = 17
        max_hp = 8
        energy = 17
        max_energy = 17
    if difficulty == 'hard':
        pb_speed = 2
        tree_speed = 3
        hitpoints = 6
        max_trees = 25
        max_hp = 6
        energy = 15
        max_energy = 15
    if difficulty == 'expert':
        pb_speed = 2
        tree_speed = 4
        hitpoints = 5
        max_trees = 30
        max_hp = 5
        energy = 13
        max_energy = 13


    #this is all the data required for the playing part of the game
    #this is how long you must wait to before you see the finish line
    timer_num = 0                     #
    
    timer = 585                     #
    t_n_c = 0                     #
    paused = 0                     #
    
    #this is used to make the backgrouns 'snow' move
    up = 0                     #
    upS = -1200                     #
    
    moving_up = 1                     #
    move_dir = 0                     #
    polar_bear_dirx = 0                     #
    polar_bear_diry = 0                     #
    pb_counter = 0                     #
    pb_start = 0                     #
    hero_dirx = 0                     #
    hero_diry = 0                     #
    energyloss_counter = 0
    energygain_counter = 0
    
    #used when creating extra trees or trail
    trail_counter = 0                     #
    tree_counter = 0                     #
    
    clk = 0                     #
    
    font = pygame.font.Font(None, 25)     #
    teal = 64,255,248                     #
    yellow = 240,255,0                  #

    pbe_counter = 0                     #
    endflags = 0                        #
    finish = False                     #
    #end data###########################
    
    #This sets up the game clock
    clock = pygame.time.Clock()
   
    global screen
    screen = pygame.display.set_mode((500, 600))
    pygame.display.set_caption("Eskimo Tutorial")

    #instead of filling the the screen, during the game we load a background image
    background_image, background_rect = load_image('background.gif')

    #This is the data used to make the timer and hhitpoint 'bars'
    timebar_image, timebar_rect = load_image('bargreen.gif')
    healthbar_image, healthbar_rect = load_image('barblue.gif')
    clearbar_image, clearbar_rect = load_image('barred.gif')

    #Here is where we create the sprite 'groups'
    eskimo_sprites = pygame.sprite.RenderClear()
    trail_sprites = pygame.sprite.RenderClear()
    stump_sprites = pygame.sprite.RenderClear()
    tree_sprites = pygame.sprite.RenderClear()
    finish_sprites = pygame.sprite.RenderClear()

    #here is where you load and set the volume of the non-player sounds
    roar = load_sound("roar.wav")
    roar.set_volume(0.4)
    tree_break = load_sound("tree_fall.wav")
    tree_break.set_volume(0.7)

    #Here is where we create the eskimo and polar bear
    global hero
    eskimo_sprites = createEskimo(screen)
    global enemy
    enemy_sprites = createPBear(screen)

    #this is where we create the 'first' trees at the start of the game
    tree_sprites.add(Tree((random.randint(10,190),random.randint(10,20))))
    tree_sprites.add(Tree((random.randint(10,190),random.randint(130,140))))
    tree_sprites.add(Tree((random.randint(10,190),random.randint(250,260))))
    
    ren = font.render("hitpoints", 1, teal)
    screen.blit(ren, (225, 20))

    ren = font.render("Timer", 1, yellow)
    screen.blit(ren, (385, 20))

    ren = font.render("Energy", 1, yellow)
    screen.blit(ren, (225, 175))

    #this is where we start the loop that will cause the game to continue playing unless you lose,
    #you quit, or there is an error in the game.
    while 1:
        #here we tell the game to limit the speed of the game to 60 frames a second
        clock.tick(60)

        #here is where the game collects and processes the keyboard inputs during the game
        for event in pygame.event.get():

            #this checks if any keys are pressed(down)
            if event.type == KEYDOWN:
                #this tells the game which keys are down,
                #and causes the game to act accordingly
                if event.key == K_ESCAPE:
                    #tells the game to quit
                    background_music.music.stop()
                    raise SystemExit()

                #sees if the 'up' arrow key is pressed
                if event.key == K_UP:
                    #makes sure eskimo has enough energy to go faster
                    if not energy < 0:
                        #instead of moving the eskimo with 'update', we want to have the controls for him
                        #so we tell the computer which direction he needs to move and the computer moves him
                        hero_diry = -1
                        move_dir = 1

                        #this adjusts the trees to move faster if you go faster
                        if difficulty == 'easy':
                            tree_speed = 4
                        if difficulty == 'medium' or difficulty == 'hard':
                            tree_speed = 5
                        if difficulty == 'expert':
                            tree_speed = 6

                        #this tells the eskimo that it is moving fast and to change the animation
                        hero.fast = 1
                if event.key == K_RIGHT:
                    hero_dirx = 1
                if event.key == K_LEFT:
                    hero_dirx = -1
                if event.key == K_DOWN:
                    hero_diry = 1
                    move_dir = -1
                    if difficulty == 'easy':
                        tree_speed = 2
                    if difficulty == 'medium' or difficulty == 'hard':
                        tree_speed = 3
                    if difficulty == 'expert':
                        tree_speed = 4

                    #this tell the eskimo that its moving slowly
                    hero.fast = -1
                    
                if event.key == K_p:
                    #this causes the game to pause/unpause if you press 'p'
                    if not paused:
                        paused = 1
                    else:
                        paused = 0

                        
            #this checks if any keys are not pressed
            #then adjusts the data accordingly
            elif event.type == KEYUP:
                if event.key == K_UP:
                    if not hero_diry == 1:
                        hero_diry = 0
                        move_dir = 0

                    if difficulty == 'easy':
                        tree_speed = 3
                    if difficulty == 'medium' or difficulty == 'hard':
                        tree_speed = 4
                    if difficulty == 'expert':
                        tree_speed = 5
                    if hero.fast == 1:
                        hero.fast = 0

                        #this tells the eskimo to reset its animation counter so it doesnt stop working
                        hero.fast_counter = 0
                if event.key == K_RIGHT:
                    if not hero_dirx == -1:
                        hero_dirx = 0
                if event.key == K_LEFT:
                    if not hero_dirx == 1:
                        hero_dirx = 0
                if event.key == K_DOWN:
                    if not hero_diry == -1:
                        hero_diry = 0
                        move_dir = 0
                    if difficulty == 'easy':
                        tree_speed = 3
                    if difficulty == 'medium' or difficulty == 'hard':
                        tree_speed = 4
                    if difficulty == 'expert':
                        tree_speed = 5
                    if hero.fast == -1:
                        hero.fast = 0
                        hero.fast_counter = 0

            elif event.type == QUIT:
                background_music.music.stop()
                raise SystemExit()
            
                                            
        if not paused:

            #tells the eskimo that hes moving normally if energy is out
            if energy < 0:
                energy = 0
            if energy == 0:
                hero.fast = 0

                
            #this makes the polar bear move faster if it hits a tree
            if pb_start == 1:
                pb_counter += 1
                if difficulty == 'easy' or difficulty == 'medium':
                    pb_speed = 2
                    if pb_counter == 50:
                        pb_start = 0
                        pb_counter = 0
                        pb_speed = 1
                if difficulty == 'hard' or difficulty == 'expert':
                    pb_speed = 3
                    if pb_counter == 50:
                        pb_start = 0
                        pb_counter = 0
                        pb_speed = 2

#####################################Status Bars############################################
            #this tells the timer bar to update and add images based on how far you've gone
            if not timer_num == 575:
                t_n_c += 1
                if t_n_c == 5:
                    timer_num += 1
                    timer -= 1
                    t_n_c = 0
                screen.blit(timebar_image,(465, timer - 5))
                """here we use the pygame.draw.rect function to draw a rectangle around the duration of the timer"""
                #pygame.draw.rect(Surface, color, length/width of rect, thickness of borders)
                pygame.draw.rect(screen, teal, (465, 5, 15, 580), 1)

            #this makes the game show the hitpoints you have and the hitpoints you've lost
            for rows in xrange(max_hp):
                screen.blit(clearbar_image, (325, rows * -5 + 50))
            for rows in xrange(hitpoints):
                screen.blit(healthbar_image,(325, rows * -5 + 50))
            if difficulty == 'easy' or difficulty == 'medium':
                pygame.draw.rect(screen, teal, (325, (max_hp + 45), 15, (max_hp * 5 * -1)), 1)
            else:
                pygame.draw.rect(screen, teal, (325, (max_hp + 50), 15, (max_hp * 5 * -1)), 1)

            #this is where we make the bar for energy using the rect function
            for rows in xrange(max_energy):
                #a rect with '0' border size forces the rect to be filled with color
                pygame.draw.rect(screen, [0, 0, 0], (325, (rows * -5 + 250), 15, 5), 0)
            for rows in xrange(energy):
                pygame.draw.rect(screen, [255, 0 , 204], (325, (rows * -5 + 250), 15, 5), 0)
            if difficulty == 'easy':
                pygame.draw.rect(screen, teal, (325, (max_energy + 235), 15, (max_energy * 5 * -1)), 1)
            if difficulty == 'medium':
                pygame.draw.rect(screen, teal, (325, (max_energy + 238), 15, (max_energy * 5 * -1)), 1)
            if difficulty == 'hard':
                pygame.draw.rect(screen, teal, (325, (max_energy + 240), 15, (max_energy * 5 * -1)), 1)
            if difficulty == 'expert':
                pygame.draw.rect(screen, teal, (325, (max_energy + 242), 15, (max_energy * 5 * -1)), 1)
#####################################Status Bars######################################################################
                
            #this causes the finish flag to appear after you've gone far enough
            if timer_num == 575:
                if endflags == 0:
                    finish_sprites.add(EndFlag((100, -50)))
                    endflags = 1
                finish = True

            #makes sure re-gain energy the longer you wait
            if not energy == max_energy or energy > max_energy:
                energygain_counter += 1
                if energygain_counter == 120:
                    energy += 1
                    energygain_counter = 0


            #this causes new trees to appear if there are fewer than the max amount,
            #and it limits it to creating a certain number a second
            tree_counter += 1
            if difficulty == 'easy':
                if tree_counter == 20:
                    tree_counter = 0
            if difficulty == 'medium':
                if tree_counter == 18:
                    tree_counter = 0
            if difficulty == 'hard':
                if tree_counter == 15:
                    tree_counter = 0
            if difficulty == 'expert':
                if tree_counter == 10:
                    tree_counter = 0
            if not len(tree_sprites.sprites()) == max_trees:
                """len counts how many tree_sprites there are in that group of sprites"""
                if difficulty == 'easy':
                    if tree_counter == 19:
                        #this places a tree at a random location on the map in a range of acceptable positions
                        tree_sprites.add(Tree((random.randint(10,190),random.randint(-100,10))))
                if difficulty == 'medium':
                    if tree_counter == 17:
                        tree_sprites.add(Tree((random.randint(10,190),random.randint(-100,10))))
                if difficulty == 'hard':
                    if tree_counter == 14:
                        tree_sprites.add(Tree((random.randint(10,190),random.randint(-100,10))))
                if difficulty == 'expert':
                    if tree_counter == 9:
                        tree_sprites.add(Tree((random.randint(10,190),random.randint(-100,10))))

                        
            #this adds the trail behind you as you move    
            trail_counter += 1
            if hero_diry == 0:
                if trail_counter > 6:
                    trail_counter = 0
                if trail_counter == 6:
                    trail_counter = 0
                    trail_sprites.add(Trail((hero.rect.midtop[0], hero.rect.midtop[1] + 15)))
                    trail_sprites.draw(screen)
            if hero.fast == 1:
                if trail_counter > 3:
                    trail_counter = 0
                if trail_counter == 3:
                    trail_counter = 0
                    trail_sprites.add(Trail((hero.rect.midtop[0], hero.rect.midtop[1] + 12)))
                    trail_sprites.draw(screen)
            if hero.fast == -1:
                if trail_counter > 4:
                    trail_counter = 0
                if trail_counter == 4:
                    trail_counter = 0
                    trail_sprites.add(Trail((hero.rect.midtop[0], hero.rect.midtop[1] + 35)))
                    trail_sprites.draw(screen)

                    
            #this is where the computer moves the eskimo based on what direction he should go                   
            if hero_dirx == 1:
                if not hero.rect.centerx > 185:
                    hero.rect.move_ip((2,0))
            if hero_dirx == -1:
                if not hero.rect.centerx < 10:
                    hero.rect.move_ip((-2,0))

            if hero_diry == 1:
                if not hero.rect.centery > 560:
                    #move eskimo and take away energy as long as your fighting to slow down
                    if not energy == 0 or energy < 0:
                        hero.rect.move_ip((0,2))
                        energygain_counter = 0
                        energyloss_counter += 1
                        if energyloss_counter == 10:
                            energy -= 1
                            energyloss_counter = 0
            if hero_diry == -1:
                if not hero.rect.centery < 75:
                    #lose energy as long as your pushing harder
                    if not energy == 0 or energy < 0:
                        hero.rect.move_ip((0,-2))
                        energygain_counter = 0
                        energyloss_counter += 1
                        if energyloss_counter == 10:
                            energy -= 2
                            energyloss_counter = 0


            #this is where we move the background to give the illusion that the eskimo is moving      
            screen.blit(background_image, (0,up))
            screen.blit(background_image, (0,upS))
            if moving_up == 1:
                if hero_diry == -1:
                    up += 4
                    upS += 4
                if hero_diry == 1:
                    up += 2
                    upS += 2
                if hero_diry == 0:
                    up += 3
                    upS += 3                  
                if up > 1200:
                    #this tells the backgrounds to 'scroll'so that they restart at the top of the screen
                    #and dont continue moving down forever
                    up = 0
                if upS > 0:
                    upS = -1200

            #this is where all the sprites are erased from there old positions
            finish_sprites.clear(screen,background_image)
            eskimo_sprites.clear(screen,background_image)
            trail_sprites.clear(screen,background_image)
            tree_sprites.clear(screen,background_image)
            stump_sprites.clear(screen,background_image)
            enemy_sprites.clear(screen,background_image)

            #this is where the sprites are drawn onto there new positions
            finish_sprites.draw(screen)
            eskimo_sprites.draw(screen)
            trail_sprites.draw(screen)
            tree_sprites.draw(screen)
            stump_sprites.draw(screen)
            enemy_sprites.draw(screen)

            #this is where the sprites are told to update
            #this is where we specify the extra data that each function may need
            finish_sprites.update(tree_speed)
            eskimo_sprites.update()
            trail_sprites.update()
            tree_sprites.update(tree_speed)
            stump_sprites.update(tree_speed)
            enemy_sprites.update(pb_speed, polar_bear_dirx, polar_bear_diry)

            #'len' counts the number of objects in a given group (finish_sprites.sprites())
            #this area sees if you missed the finish line and tells you you-ve lost if you did
            if finish == True:
                if len(finish_sprites.sprites()) == 0:
                    paused = 1
                    youLose()


            #this is where the game checks if the ekimo collides with any trees
            #if the game detects a collision we tell it to find which sprites collided and destroy the tree,
            #take away one of the players hitpoints, and add a stump where the tree was
                    
            #these two lines see which sprites collide#<--
            for s in tree_sprites:                    #<--
                for a in eskimo_sprites:              #<--
                    #this tells the game what two specific sprites collided
                    if a.rect.colliderect(s.rect):
                        #this adds the stump where the tree was(this must be done before you destroy the sprite)
                        #and it plays the tree_break sound
                        stump_sprites.add(Stump((s.rect.centerx,s.rect.centery)))
                        tree_break.play()
                        
                        #here is where it kills the sprite
                        s.kill()
                        
                        #here we take away 1 hitpoint and force the player back if he isnt at the bottom of the screen
                        hitpoints -= 1
                        if not hero.rect.centery > 553:
                            hero.rect.move_ip((0,7))
                        else:
                            hero.rect.centery = 560

            #this is where the game sees if any sprites from the given group(eskimo_sprites, finish_sprites) collide
            #if you did it brings up the 'you won' screen, and stops the game from running and playing music              
            #the numbers in (eskimo_sprites, tree_sprites, 0, 0) tell the game which sprites to kill 1 = kill,
            #0 = dont kill.
            for hit in pygame.sprite.groupcollide(eskimo_sprites, finish_sprites, 0, 0):
                youWin()
                paused = 1
                background_music.music.stop()



            #this is the most complex piece of code in the tutorial
            #first it sees if the polar bear collided with any trees
            #then it starts/re-starts the polar bear 'fast counter'  making it move faster
            #after that it figures out the 'path' the polar bear will take around the tree
            #and if the polar bear gets too low it roars and breaks down the tree
            for s in tree_sprites:
                for a in enemy_sprites:
                    pb_start = 1
                    pb_counter = 0
                    #these lines of code make sure first that th polar bear doenst go too far right or left,
                    #then it finds the fastest way around the tree
                    if s.rect.centerx > a.rect.centerx:
                        """if the tree is farther right than the bear, the bears goes left,
                           because it is the shorter route,
                           if the tree is farther left the bear goes right."""
                        if not a.rect.centerx < 50:
                            polar_bear_dirx = -1
                        else:
                            polar_bear_dirx = 1                                
                    if s.rect.centerx < a.rect.centerx:
                        """if the tree is farther right than the bear, the bears goes left,
                           because it is the shorter route,
                           if the tree is farther left the bear goes right."""
                        if not a.rect.centerx > 130:
                            polar_bear_dirx = 1
                        else:
                            polar_bear_dirx = -1                                
                    if s.rect.centerx == a.rect.centerx:
                        """this tells the bear that there is no 'shortest' way,
                           and tells it to choose randomly a direction around the tree"""
                        dice = random.randint(-1,1)
                            
                        #this makes sure that the dice arent anything but -1 or 1,
                        #because the dice will roll 0 and 2 as well
                        if dice == 0:
                            dice = -1
                        if dice == 2:
                            dice = 1
                            
                        if not a.rect.centerx > 160 or a.rect.centerx < 20:
                            polar_bear_dirx = dice
                        if a.rect.centerx > 160:
                            polar_bear_dirx = -1
                        if a.rect.centerx < 20:
                            polar_bear_dirx = 1

                    #this forces the bear to stop and move with the trees if it isnt too low      
                    if not a.rect.centery > 530:
                        polar_bear_diry = 1
                    #if it is too low it will break the tree downand roar
                    else:
                        roar.play()
                        if a.rect.colliderect(s.rect):
                            stump_sprites.add(Stump((s.rect.centerx,s.rect.centery)))
                        for hit in pygame.sprite.groupcollide(enemy_sprites, tree_sprites, 0, 1):
                            pass

            #this makes sure that the bear doesnt try to go around trees if it isnt hitting any trees          
            if not pygame.sprite.groupcollide(enemy_sprites, tree_sprites, 0, 0):
                polar_bear_dirx = 0
                polar_bear_diry = 0

            #this tells the game that every 3/4 of a second the bear is hitting you ,you lose health
            #and it plays the roar sound
            for hit in pygame.sprite.groupcollide(eskimo_sprites, enemy_sprites, 0, 0):
                roar.play()
                pbe_counter += 1
                if pbe_counter == 45:
                    hitpoints -= 1
                    pbe_counter = 0

            #this checks if you are out of hitpoints and makes you lose if you are
            if hitpoints == 0:
                youLose()
                paused = 1
                background_music.music.stop()

            #these make the display update and make the units and events happen
            pygame.event.pump()
            pygame.display.flip()

def menu():
    """the start-up screen that asks you which difficulty to play"""
    
    pygame.init()
    running = 1
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 40)
    yellow = 240,255,0
    hum = 2, 81, 76

    global difficulty

    screen = pygame.display.set_mode((500, 600))
    screen.fill([52,232,243])

    ren = font.render("Choose a difficulty level", 1, yellow)
    screen.blit(ren, (75, 10))

    ren = font.render("for Easy type 'e'", 1, hum)
    screen.blit(ren, (125, 100))
    ren = font.render("for Medium type 'm'", 1, hum)
    screen.blit(ren, (125, 200))
    ren = font.render("for Hard type 'h'", 1, hum)
    screen.blit(ren, (125, 300))
    ren = font.render("for Expert type 'x'", 1, hum)
    screen.blit(ren, (125, 400))

    while running:
        clock.tick(55)
        pygame.display.flip()
        pygame.event.pump()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    raise SystemExit()
                if event.key == K_e:
                    running = 0
                    difficulty = 'easy'
                    main()
                if event.key == K_m:
                    running = 0
                    difficulty = 'medium'
                    main()
                if event.key == K_h:
                    running = 0
                    difficulty = 'hard'
                    main()
                if event.key == K_x:
                    running = 0
                    difficulty = 'expert'
                    main()
r = 1
if r:
    menu()      
