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
    '1' : [-100.0,  100.0],
    '2' : [ 100.0,  100.0],
    '3' : [ 100.0, -100.0],
    '4' : [-100.0, -100.0],
}

def print_point(_point):
    pygame.draw.rect(screen, (0, 255, 0), (center[0] + points[_point][0], center[1] - points[_point][1], 5, 5))

def get_radius(_point):
    radius = math.hypot(points[_point][0], points[_point][1])
    return radius

def get_angle(_point):
    radius = get_radius(_point)
    side = points[_point][1]
    result = math.degrees(math.acos(side / radius))
    if points[_point][0] > 0:
        return result
    else:
        return 360 - result

def add_angle(_point, add_ang=0):
    angle = get_angle(_point) - add_ang
    radius = get_radius(_point)
    radius * math.cos(math.radians(angle))
    y_cord = round(radius * math.cos(math.radians(angle)), 2)
    x_cord = round(radius * math.sin(math.radians(angle)), 2)
    points[_point] = [x_cord, y_cord]


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
        add_angle(point, 1)

    pygame.display.flip()
    clock.tick(60)
print(points)
pygame.quit()