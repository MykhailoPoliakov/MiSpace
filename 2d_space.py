import pygame
import math

center = (990, 540)

pygame.init()
screen = pygame.display.set_mode((1980, 1080))
screen = pygame.display.set_mode((1980, 1080), pygame.FULLSCREEN | pygame.SCALED)
clock = pygame.time.Clock()
background_color = (0, 0, 0)
screen.fill(background_color)

points = { #(x,y)
    '1' : [-100,100],
    '2' : [100, 100],
    '3' : [100,-100],
    '4' : [-100,-100],
    '5' : [0,-100],
    '6' : [55, - 75,2],
}

def print_point(_point):
    pygame.draw.rect(screen, (0, 255, 0), (center[0] - points[_point][0], center[1] - points[_point][1], 5, 5))

def get_radius(_point):
    radius = math.hypot(points[_point][0], points[_point][1])
    return radius

def get_angle(_point):
    radius = get_radius(_point)
    side = points[_point][1]
    result = side / radius
    if points[_point][0] > 0:
        return math.degrees(math.acos(result))
    else:
        return 360 - math.degrees(math.acos(result))

def add_angle(_point):
    angle = get_angle(_point)

running = True
while running:
    """ BRAIN """
    pass

    """ INPUT """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    """ OUTPUT """
    screen.fill(background_color)
    for point in points:
        print_point(point)

    print(get_angle('6'))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()