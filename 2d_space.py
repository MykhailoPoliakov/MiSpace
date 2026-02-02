import pygame
import math

center = (990, 540)
all_objects = []

pygame.init()
screen = pygame.display.set_mode((1980, 1080))
screen = pygame.display.set_mode((1980, 1080), pygame.FULLSCREEN | pygame.SCALED)
clock = pygame.time.Clock()
background_color = (0, 5, 0)
screen.fill(background_color)

points = { #(x,y,z)
    'square' : {
        '1' : [-100.0,  100.0,  100.0],
        '2' : [ 100.0,  100.0,  100,0],
        '3' : [-100.0, -100.0, -100.0],
        '4' : [ 100.0, -100.0, -100.0],
        '5' : [-100.0,  100.0, -100.0],
        '6' : [ 100.0,  100.0, -100,0],
        '7' : [-100.0, -100.0,  100.0],
        '8' : [ 100.0, -100.0,  100.0],
        'center' : [0,      0,      0],
    },
    'plane' : {
        '1' : [ 200.0, -100.0,  200.0],
        '2' : [-200.0, -100.0,  200.0],
        '3' : [ 200.0, -100.0, -200.0],
        '4' : [-200.0, -100.0, -200.0],
        'center' : [0,      0,      0],
    }
}

for i in range(-20, 21):
    points['plane']['x1' + str(i)] = [ i * 15,-100, 300]
    points['plane']['x2' + str(i)] = [ i * 15,-100,-300]
    points['plane']['z1' + str(i)] = [ 300,-100, i * 15]
    points['plane']['z2' + str(i)] = [-300,-100, i * 15]
    points['plane']['x3' + str(i)] = [ i * 15,-100, 200]
    points['plane']['x4' + str(i)] = [ i * 15,-100,-200]
    points['plane']['z3' + str(i)] = [ 200,-100, i * 15]
    points['plane']['z4' + str(i)] = [-200,-100, i * 15]
    points['plane']['x5' + str(i)] = [ i * 15,-100, 100]
    points['plane']['x6' + str(i)] = [ i * 15,-100,-100]
    points['plane']['z5' + str(i)] = [ 100,-100, i * 15]
    points['plane']['z6' + str(i)] = [-100,-100, i * 15]
    points['plane']['x7' + str(i)] = [ i * 15,-100,   0]
    points['plane']['z7' + str(i)] = [   0,-100, i * 15]

for i in range(-20, 21):
    points['square']['x1' + str(i)] = [ i * 5, 100, 100]
    points['square']['x2' + str(i)] = [ i * 5,-100, 100]
    points['square']['x3' + str(i)] = [ i * 5,-100,-100]
    points['square']['x4' + str(i)] = [ i * 5, 100,-100]
    points['square']['y1' + str(i)] = [ 100, i * 5, 100]
    points['square']['y2' + str(i)] = [-100, i * 5, 100]
    points['square']['y3' + str(i)] = [-100, i * 5,-100]
    points['square']['y4' + str(i)] = [ 100, i * 5,-100]
    points['square']['z1' + str(i)] = [ 100, 100, i * 5]
    points['square']['z2' + str(i)] = [-100, 100, i * 5]
    points['square']['z3' + str(i)] = [-100,-100, i * 5]
    points['square']['z4' + str(i)] = [ 100,-100, i * 5]

def print_point(obj_name,_point, choose_color):
    mult = ((points[obj_name.name][_point][2] - obj_name.offset[2] + 100) / 200) + 2
    if 55 <= (points[obj_name.name][_point][2] + 100) + 55 <= 255:
        _color = (points[obj_name.name][_point][2] + 100) + 55
        _size = (points[obj_name.name][_point][2] + 100) / 20 + 5
    elif 55 > (points[obj_name.name][_point][2] + 100) + 55:
        _color = 55
        _size = 5
    else:
        _color = 255
        _size = 15
    pygame.draw.rect(screen, (0, _color, choose_color),
                    (center[0] + (obj_name.offset[0] + points[obj_name.name][_point][0]) * mult,
                          center[1] - (obj_name.offset[1] + points[obj_name.name][_point][1]) * mult, _size, _size))

class CameraChanger:
    def __init__(self):
        self.point_dict = {}
        for object_name in all_objects:
            for dot_name in object_name.point_dict:
                self.point_dict[f'{object_name}_{dot_name}'] = object_name.point_dict[dot_name]


class CordChanger:
    def __init__(self, input_points):
        self.point_dict = points[input_points]
        self.name = input_points
        self.offset = [0,0,0]

    def __get_angle(self,_point, index):
        radius = math.hypot(self.point_dict[_point][index[0]], self.point_dict[_point][index[1]])
        if radius == 0:
            return 0
        side = self.point_dict[_point][index[1]]
        result = math.degrees(math.acos(side / radius))
        if self.point_dict[_point][index[0]] < 0:
            result = 360 - result
        return result

    def rotate(self,_point, index, add_ang=0):
        angle = self.__get_angle(_point, index) - add_ang
        radius = math.hypot(self.point_dict[_point][index[0]], self.point_dict[_point][index[1]])
        radius * math.cos(math.radians(angle))
        self.point_dict[_point][index[0]] = round(radius * math.sin(math.radians(angle)), 2)
        self.point_dict[_point][index[1]] = round(radius * math.cos(math.radians(angle)), 2)

    def move(self,_point, index, add_move):
        self.offset[index] += round(add_move / 100,2)

    def size(self,_point, index, add_size):
        changed_cord = self.point_dict[_point][index] * (1 + add_size / 100)
        self.point_dict[_point][index] = round(changed_cord,2)


# objects
camera = CameraChanger()
square = CordChanger('square')
plane = CordChanger('plane')
all_objects = [square,plane]
active_object = all_objects[0]

running = True
while running:
    """ BRAIN """

    """ INPUT """
    for event in pygame.event.get():
        # ways to exit
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # choosing the object
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1 and len(all_objects) > 0:
            active_object = all_objects[0]
        if event.type == pygame.KEYDOWN and event.key == pygame.K_2 and len(all_objects) > 1:
            active_object = all_objects[1]
        if event.type == pygame.KEYDOWN and event.key == pygame.K_3 and len(all_objects) > 2:
            active_object = all_objects[2]
        if event.type == pygame.KEYDOWN and event.key == pygame.K_4 and len(all_objects) > 3:
            active_object = all_objects[3]

    # rotation,movement and sizing
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LSHIFT]:
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            for point in points[active_object.name]:
                square.move(point, 0,-1)
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            for point in points[active_object.name]:
                square.move(point,0,1)
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            for point in points[active_object.name]:
                square.move(point, 1,1)
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            for point in points[active_object.name]:
                square.move(point,1,-1)
        if keys[pygame.K_KP1] and not keys[pygame.K_KP0]:
            for point in points[active_object.name]:
                square.move(point, 2,1)
        elif keys[pygame.K_KP0] and not keys[pygame.K_KP1]:
            for point in points[active_object.name]:
                square.move(point,2,-1)
    elif keys[pygame.K_LCTRL]:
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            for point in points[active_object.name]:
                square.size(point, 0, -1)
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            for point in points[active_object.name]:
                square.size(point,0,1)
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            for point in points[active_object.name]:
                square.size(point, 1,1)
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            for point in points[active_object.name]:
                square.size(point,1, -1)
        if keys[pygame.K_KP1] and not keys[pygame.K_KP0]:
            for point in points[active_object.name]:
                square.size(point, 2,1)
        elif keys[pygame.K_KP0] and not keys[pygame.K_KP1]:
            for point in points[active_object.name]:
                square.size(point,2,-1)
    else:
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            for point in points[active_object.name]:
                square.rotate(point, (0,2),1)
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            for point in points[active_object.name]:
                square.rotate(point,(0,2), -1)
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            for point in points[active_object.name]:
                square.rotate(point, (1,2),-1)
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            for point in points[active_object.name]:
                square.rotate(point,(1,2), 1)
        if keys[pygame.K_KP1] and not keys[pygame.K_KP0]:
            for point in points[active_object.name]:
                square.rotate(point, (0,1),1)
        elif keys[pygame.K_KP0] and not keys[pygame.K_KP1]:
            for point in points[active_object.name]:
                square.rotate(point,(0,1),-1)

    """ OUTPUT """
    screen.fill(background_color)
    pygame.draw.rect(screen, (255, 255, 0),(center[0], center[1], 5, 5))
    for point in points['plane']:
        print_point(plane, point, 255)
    for point in points['square']:
        print_point(square, point, 0)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()