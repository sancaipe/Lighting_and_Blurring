import pygame
import cv2
import random
import numpy as np
import math

pygame.init()

screen_width, screen_height = 2556,1290
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Light Particles")
clock = pygame.time.Clock()

# Colors
white = (255,255,255)
black = (0,0,0)
particle_color = [(255,255,255),    # list of RBG tuples to cycle through using mouse click left and right in the main loop
                  (255,100,100),
                  (0,255,255),
                  (0,255,0),
                  (100,100,100)
]


background_color = black
def draw_board(background_color,surface):
    """
    Draws the background color on the screen.
    This function is the first display definition in the main game loop.

    Args:
    background_color (tuple):   RGB color
    surface (pygame display):   The surface variable name (typically "screen")
    """
    surface.fill(background_color)

def light_circle_surf(radius,color):
    """
    Creates a surface of the shading circle and applies Gaussian Blurring to that circle to give the
    edges of the circle a haze.

    Args:
    radius (float): The size of the shading circle
    color (tuple):  RGB tuple

    Returns:
    surf (pygame Surface/image)
    """
    surf = pygame.Surface((radius*3,radius*3))  # Oversize the surf dimensions so that the Gaussian Blur does not generate flat edges at the borders.
    # If you remove the *3 scale factor above, you'll need to also modify the Kernel size of the GaussianBlur method to be smaller, otherwise the blurring will make the circle very blocky
    pygame.draw.circle(surf,color,(radius*1.5,radius*1.5),radius)   # Draw the circle at the center of the surf. The *1.5 depends on the *3 above
    rgb = pygame.surfarray.array3d(surf)    # Splits the surf up into a numpy 3D array of RGB values, which is the required input to the GaussianBlur method below
    cv2.GaussianBlur(rgb,[11,11],sigmaX=10,sigmaY=10,dst=rgb) # A larger kernel size allows for larger sigmaX & sigmaY values to make the haze effect more significant. But a larger kernel also results in more blockyness if not using appropriately large sigmas
    surf = pygame.image.frombuffer(rgb.flatten(),rgb.shape[1::-1],'RGB')
    surf.set_colorkey(black)    # Makes the black on the surf transparent, to the blit onto the screen
    return surf

# Individual particle class, and a class to collect the individual particles. This follows a particle effects method from one of DaFluffyPotato's videos
class particle():
    def __init__(self,pos,color):
        self.pos = np.array([pos[0],pos[1]]) # tuple as input, vector as usage
        self.color = color
        self.size = random.randint(10,20)
        vel_x = random.randint(-20,20) / 10
        vel_y = -9
        self.vel=np.array([vel_x,vel_y])
        self.lifetime = random.randint(180,240)
        self.decrease_size = self.size/self.lifetime

    def update(self,grav_on):
        self.pos = self.pos + self.vel
        if grav_on:
            self.vel = self.vel + np.array([0,0.07])
            self.size -= self.decrease_size
        self.lifetime -= 1

    def draw(self):
        # below will fail if radius < 1. The position argument multiplied by (currently) 1.5 is dependent on the size of the surf being created by light_circle_surf()
        screen.blit(light_circle_surf(max(1,self.size) * 4, tuple(int(x/3) for x in self.color)),tuple( self.pos - np.array([self.size*4*1.5,self.size*4*1.5]) ) ,special_flags=pygame.BLEND_RGB_ADD)
        pygame.draw.circle(screen,self.color,tuple(self.pos),self.size)

class particle_System():
    def __init__(self):
        self.particles = []

    def add_particle(self,pos,color):
        self.particles.append(particle(pos,color))

    def update(self,grav_on):
        for index, particle in enumerate(self.particles):
            particle.update(grav_on)
            if particle.lifetime <= 0:
                self.particles.pop(index)
    
    def draw(self):
        for particle in self.particles:
            particle.draw()

# Initialize the particle system 
Particles = particle_System()

timer = 0   # To count frames, used to determine when to generate a particle
color_index = 0 # To cycle through the colors list for the particles
running = True
while running:
    clock.tick(60)
    draw_board(black,screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:    # Cycle through the particle colors
            if event.button == 1:   # Left click, move forward in the list
                color_index +=1
                if color_index == len(particle_color):
                    color_index = 0
            elif event.button == 3: # Right click, move backwards in the list
                color_index -=1
                if color_index == -1:
                    color_index = len(particle_color)-1


    # Draw some rects on the screen to see the effects of the shading circles
    pygame.draw.rect(screen,(70,0,0),pygame.Rect(screen_width/8,screen_height/8,screen_width/4,screen_height/4))
    pygame.draw.rect(screen,(0,70,0),pygame.Rect(screen_width*3/8,screen_height*3/8,screen_width/4,screen_height/4))
    pygame.draw.rect(screen,(0,0,70),pygame.Rect(screen_width*5/8,screen_height*5/8,screen_width/4,screen_height/4))
    pygame.draw.rect(screen,(35,35,35),pygame.Rect(screen_width/8,screen_height*5/8,screen_width/4,screen_height/4))
    pygame.draw.rect(screen,(0,70,70),pygame.Rect(screen_width*5/8,screen_height/8,screen_width/4,screen_height/4))
    pygame.draw.rect(screen,(200,200,200),pygame.Rect(screen_width*5/8,screen_height*3/8,screen_width/4,screen_height/4))
    
    # Generate particles on the mouse position
    mouse_pos = pygame.mouse.get_pos()
    if timer % 5 == 0:
        Particles.add_particle(mouse_pos,particle_color[color_index])
    Particles.update(grav_on=1)
    Particles.draw()

    pygame.display.flip()
    timer += 1
    if timer >= 60:
        timer = 0

pygame.quit()