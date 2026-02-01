import pygame
import math

center = (990, 540)

pygame.init()
screen = pygame.display.set_mode((1980, 1080))
screen = pygame.display.set_mode((1980, 1080), pygame.FULLSCREEN | pygame.SCALED)
clock = pygame.time.Clock()
background_color = (0, 0, 0)
screen.fill(background_color)

points = { #(x,y,z)
    #'1' : [-100.0,  100.0,  100.0],
    #'2' : [ 100.0,  100.0,  100,0],
    #'3' : [-100.0, -100.0, -100.0],
    #'4' : [ 100.0, -100.0, -100.0],
    #'5' : [-100.0,  100.0, -100.0],
    #'6' : [ 100.0,  100.0, -100,0],
    #'7' : [-100.0, -100.0,  100.0],
    #'8' : [ 100.0, -100.0,  100.0],
}

for i in range(-20, 20):
    points['x1' + str(i)] = [ i * 5, 100, 100]
    points['x2' + str(i)] = [ i * 5,-100, 100]
    points['x3' + str(i)] = [ i * 5,-100,-100]
    points['x4' + str(i)] = [ i * 5, 100,-100]
    points['y1' + str(i)] = [ 100, i * 5, 100]
    points['y2' + str(i)] = [-100, i * 5, 100]
    points['y3' + str(i)] = [-100, i * 5,-100]
    points['y4' + str(i)] = [ 100, i * 5,-100]
    points['z1' + str(i)] = [ 100, 100, i * 5]
    points['z2' + str(i)] = [-100, 100, i * 5]
    points['z3' + str(i)] = [-100,-100, i * 5]
    points['z4' + str(i)] = [ 100,-100, i * 5]

def print_point(_dict,_point):
    mult = ((_dict[_point][2] + 100) / 200) + 2
    pygame.draw.rect(screen, (0, 255, 0),
                    (center[0] + _dict[_point][0] * mult, center[1] - _dict[_point][1] * mult, 5, 5))

def get_radius(_point,index):
    radius = math.hypot(points[_point][index[0]], points[_point][index[1]])
    return radius

def get_angle(_point,index):
    radius = get_radius(_point,index)
    side = points[_point][index[1]]
    if radius != 0:
        result = math.degrees(math.acos(side / radius))
    else:
        return 0
    if points[_point][index[0]] > 0:
        return result
    else:
        return 360 - result

def add_angle(_point, index, add_ang=0):
    angle = get_angle(_point, index) - add_ang
    radius = get_radius(_point, index)
    radius * math.cos(math.radians(angle))
    if index == (0,1):
        x_cord = round(radius * math.sin(math.radians(angle)), 2)
        y_cord = round(radius * math.cos(math.radians(angle)), 2)
        z_cord = points[_point][2]
    if index == (0, 2):
        x_cord = round(radius * math.sin(math.radians(angle)), 2)
        y_cord = points[_point][1]
        z_cord = round(radius * math.cos(math.radians(angle)), 2)
    if index == (1, 2):
        x_cord = points[_point][0]
        y_cord = round(radius * math.sin(math.radians(angle)), 2)
        z_cord = round(radius * math.cos(math.radians(angle)), 2)
    points[_point] = [x_cord, y_cord, z_cord]

running = True
while running:
    """ BRAIN """

    """ INPUT """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        for point in points:
            add_angle(point, (0,2),1)
    elif keys[pygame.K_RIGHT]:
        for point in points:
            add_angle(point,(0,2), -1)
    elif keys[pygame.K_UP]:
        for point in points:
            add_angle(point, (1,2),-1)
    elif keys[pygame.K_DOWN]:
        for point in points:
            add_angle(point,(1,2), 1)

    """ OUTPUT """
    screen.fill(background_color)
    #pygame.draw.rect(screen, (255, 255, 0),(center[0], center[1], 5, 5))
    for point in points:
        print_point(points,point)


    pygame.display.flip()
    clock.tick(60)
print(points)
pygame.quit()