import pygame
import math

center = (990, 540)

pygame.init()
screen = pygame.display.set_mode((1980, 1080))
screen = pygame.display.set_mode((1980, 1080), pygame.FULLSCREEN | pygame.SCALED)
clock = pygame.time.Clock()
background_color = (0, 5, 0)
screen.fill(background_color)

points = { #(x,y,z)
    '1' : [-100.0,  100.0,  100.0],
    '2' : [ 100.0,  100.0,  100,0],
    '3' : [-100.0, -100.0, -100.0],
    '4' : [ 100.0, -100.0, -100.0],
    '5' : [-100.0,  100.0, -100.0],
    '6' : [ 100.0,  100.0, -100,0],
    '7' : [-100.0, -100.0,  100.0],
    '8' : [ 100.0, -100.0,  100.0],
}

def print_point(_dict,_point,local_center,):
    mult = ((_dict[_point][2] + 100) / 200) + 2
    if 55 <= (_dict[_point][2] + 100) + 55 <= 255:
        _color = (_dict[_point][2] + 100) + 55
    elif 55 > (_dict[_point][2] + 100) + 55:
        _color = 55
    else:
        _color = 255
    pygame.draw.rect(screen, (0, _color, 0),
                    (local_center[0] + _dict[_point][0] * mult, local_center[1] - _dict[_point][1] * mult, 10, 10))

def print_polygon(_dict,_point,local_center, polygon):
    mult = ((_dict[_point][2] + 100) / 200) + 2
    if _dict[_point][0] > 0:
        polygon.pol_dict['x+'][_point] = (local_center[0] + _dict[_point][0] * mult, local_center[1] - _dict[_point][1] * mult)
    if _dict[_point][0] < 0:
        polygon.pol_dict['x-'][_point] = (local_center[0] + _dict[_point][0] * mult, local_center[1] - _dict[_point][1] * mult)
    if _dict[_point][0] > 0:
        polygon.pol_dict['y+'][_point] = (local_center[0] + _dict[_point][0] * mult, local_center[1] - _dict[_point][1] * mult)
    if _dict[_point][0] < 0:
        polygon.pol_dict['y-'][_point] = (local_center[0] + _dict[_point][0] * mult, local_center[1] - _dict[_point][1] * mult)
    if _dict[_point][0] > 0:
        polygon.pol_dict['z+'][_point] = (local_center[0] + _dict[_point][0] * mult, local_center[1] - _dict[_point][1] * mult)
    if _dict[_point][0] < 0:
        polygon.pol_dict['z-'][_point] = (local_center[0] + _dict[_point][0] * mult, local_center[1] - _dict[_point][1] * mult)



class CordChanger:
    def __init__(self, input_points):
        self.point_dict = input_points
        self.pol_dict = {
            'x+' : {},
            'x-' : {},
            'y+' : {},
            'y-' : {},
            'z+' : {},
            'z-' : {},
        }
        self.dots = []

    def __get_angle(self,_point, index):
        radius = math.hypot(self.point_dict[_point][index[0]], self.point_dict[_point][index[1]])
        side = self.point_dict[_point][index[1]]
        if radius != 0:
            result = math.degrees(math.acos(side / radius))
        else:
            return 0
        if self.point_dict[_point][index[0]] > 0:
            return result
        else:
            return 360 - result

    def add_angle(self,_point, index, add_ang=0):
        angle = self.__get_angle(_point, index) - add_ang
        radius = math.hypot(self.point_dict[_point][index[0]], self.point_dict[_point][index[1]])
        radius * math.cos(math.radians(angle))
        if index == (0, 1):
            x_cord = round(radius * math.sin(math.radians(angle)), 2)
            y_cord = round(radius * math.cos(math.radians(angle)), 2)
            z_cord = self.point_dict[_point][2]
        if index == (0, 2):
            x_cord = round(radius * math.sin(math.radians(angle)), 2)
            y_cord = self.point_dict[_point][1]
            z_cord = round(radius * math.cos(math.radians(angle)), 2)
        if index == (1, 2):
            x_cord = self.point_dict[_point][0]
            y_cord = round(radius * math.sin(math.radians(angle)), 2)
            z_cord = round(radius * math.cos(math.radians(angle)), 2)
        self.point_dict[_point] = [x_cord, y_cord, z_cord]

square = CordChanger(points)
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
    if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
        for point in points:
            square.add_angle(point, (0,2),1)
    elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
        for point in points:
            square.add_angle(point,(0,2), -1)
    if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
        for point in points:
            square.add_angle(point, (1,2),-1)
    elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
        for point in points:
            square.add_angle(point,(1,2), 1)

    """ OUTPUT """
    screen.fill(background_color)
    pygame.draw.rect(screen, (255, 255, 0),(center[0], center[1], 5, 5))
    for point in points:
        print_point(points, point, center)
        #print_polygon(points,point,center,square)

    '''
    for keys in square.pol_dict:
        square.dots = []
        for keys2 in square.pol_dict[keys]:
           square.dots.append(square.pol_dict[keys][keys2])
        pygame.draw.polygon(screen, (0, 255, 0), square.dots)
    '''

    pygame.display.flip()
    clock.tick(60)
pygame.quit()