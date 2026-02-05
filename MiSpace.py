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

output = {}
for obj in points:
    output[obj] = {}
    for dott in points[obj]:
        output[obj][dott] = [0,0,0]

def print_point(_object,_point, choose_color):
    mult = ((output[_object.name][_point][2] -  _object.offset[2] + 100) / 300) + 2
    if 55 <= (output[_object.name][_point][2]  + 100) + 55 <= 255:
        _color = (output[_object.name][_point][2]  + 100) + 55
        _size = (output[_object.name][_point][2]  + 100) / 20 + 5
    elif 55 > (output[_object.name][_point][2]  + 100) + 55:
        _color = 55
        _size = 5
    else:
        _color = 255
        _size = 15
    pygame.draw.rect(screen, (0, _color, choose_color),
                     (center[0] + (_object.offset[0] + output[_object.name][_point][0]) * mult,
                      center[1] - (_object.offset[1] + output[_object.name][_point][1]) * mult, _size, _size))

class CameraChanger:
    def __init__(self):
        self.rotation = [0,0,0]
        self.offset = [0,0,0]

    def rotate(self,index, add_ang):
        self.rotation[index] += add_ang

    def angle_calc(self,_obj,_point,index,last_index):
        radius = math.hypot(points[_obj][_point][index[0]], points[_obj][_point][index[1]])
        if radius != 0:
            side = points[_obj][_point][index[1]]
            start_angle = math.degrees(math.acos(side / radius))
            if points[_obj][_point][index[0]] < 0:
                start_angle = 360 - start_angle
        else:
            start_angle = 0
        return start_angle - self.rotation[last_index]

    def render(self, index):
        for num in [0,1,2]:
            if num not in index:
                last_index = num
                break
        for _obj in points:
            for _point in points[_obj]:
                angle1 = self.angle_calc(_obj,_point,(1,2),last_index)
                radius = math.hypot(points[_obj][_point][index[0]], points[_obj][_point][index[1]])
                output[_obj][_point][index[0]] = round(radius * math.sin(math.radians(angle1)), 2)
                output[_obj][_point][index[1]] = round(radius * math.cos(math.radians(angle1)), 2)
                output[_obj][_point][last_index] = points[_obj][_point][last_index]

class CordChanger:
    def __init__(self, obj_name):
        self.point_dict = points[obj_name]
        self.name = obj_name
        self.offset = [0,0,0]
        self.rotation = [0, 0, 0]
        self.size = 1

    def __get_angle(self,_point, index):
        radius = math.hypot(self.point_dict[_point][index[0]], self.point_dict[_point][index[1]])
        if radius == 0:
            return 0
        side = self.point_dict[_point][index[1]]
        result = math.degrees(math.acos(side / radius))
        if self.point_dict[_point][index[0]] < 0:
            result = 360 - result
        return result

    def rotate(self,_point, index, add_ang):
        angle = self.__get_angle(_point, index) - add_ang
        radius = math.hypot(self.point_dict[_point][index[0]], self.point_dict[_point][index[1]])
        self.point_dict[_point][index[0]] = round(radius * math.sin(math.radians(angle)), 2)
        self.point_dict[_point][index[1]] = round(radius * math.cos(math.radians(angle)), 2)

    def move(self,_point, index, add_move):
        pass

    def resize(self,_point,add_size, index=0):
        if not index:
            for index in [0,1,2]:
                changed_cord = self.point_dict[_point][index] * (1 + add_size / 100)
                self.point_dict[_point][index] = round(changed_cord,2)
        else:
            changed_cord = self.point_dict[_point][index] * (1 + add_size / 100)
            self.point_dict[_point][index] = round(changed_cord, 2)

# objects
square = CordChanger('square')
plane = CordChanger('plane')
all_objects = [square,plane]
active_object = all_objects[0]
camera = CameraChanger()

running = True
while running:
    """ BRAIN """
    pass
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
    camera.render((1, 2))

    if keys[pygame.K_g]:
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            active_object.offset[0] += 2
        elif keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            active_object.offset[0] += -2
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            active_object.offset[1] += 2
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            active_object.offset[1] += -2
        if keys[pygame.K_RALT] and not keys[pygame.K_RCTRL]:
            active_object.offset[2] += 2
        elif keys[pygame.K_RCTRL] and not keys[pygame.K_RALT]:
            active_object.offset[2] += -2

    # object size
    elif keys[pygame.K_s]:
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN] and active_object.size < 3:
            for point in points[active_object.name]:
                active_object.resize(point, 1)
            active_object.size *= 1 + 1 / 100
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP] and active_object.size > 0.20:
            for point in points[active_object.name]:
                active_object.resize(point,-1)
            active_object.size *= 1 - 1 / 100

    # object rotation
    elif keys[pygame.K_r]:
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            for point in points[active_object.name]:
                active_object.rotate(point, (0,2),1)
            active_object.rotation[1] += 1
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            for point in points[active_object.name]:
                active_object.rotate(point,(0,2), -1)
            active_object.rotation[1] -= 1
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            for point in points[active_object.name]:
                active_object.rotate(point, (1,2),-1)
            active_object.rotation[0] -= 1
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            for point in points[active_object.name]:
                active_object.rotate(point,(1,2), 1)
            active_object.rotation[0] += 1
        if keys[pygame.K_RALT] and not keys[pygame.K_RCTRL]:
            for point in points[active_object.name]:
                active_object.rotate(point, (0,1),1)
            active_object.rotation[2] += 1
        elif keys[pygame.K_RCTRL] and not keys[pygame.K_RALT]:
            for point in points[active_object.name]:
                active_object.rotate(point,(0,1),-1)
            active_object.rotation[2] -= 1

    # camera rotation
    else:
        if keys[pygame.K_UP]:
            if camera.rotation[0] < 85:
                camera.rotate( 0, 1)
        elif keys[pygame.K_DOWN]:
            if camera.rotation[0] > -85:
                camera.rotate( 0, -1)
        if keys[pygame.K_LEFT]:
            if camera.rotation[0] < 85:
                camera.rotate( 1, 1)
        elif keys[pygame.K_RIGHT]:
            if camera.rotation[0] > -85:
                camera.rotate( 1, -1)

    # camera movement
    #self.offset[index] += add_move

    """ OUTPUT """
    screen.fill(background_color)
    pygame.draw.rect(screen, (255, 255, 0),(center[0], center[1], 5, 5))
    for point in points['plane']:
        print_point(plane, point, 255)
    for point in points['square']:
        print_point(square, point, 0)
    font = pygame.font.Font(None, 40)
    output_text = \
    f"""
        Object : {active_object.name}
        Rotation : x {active_object.rotation[0]:.0f}° y {active_object.rotation[1]:.0f}° z {active_object.rotation[2]:.0f}°
        Coordinates : x {active_object.offset[0]:.2f} y {active_object.offset[1]:.2f} z {-active_object.offset[2]:.2f}
        
        
        Camera
        Rotation : x {camera.rotation[0]:.0f}° y {camera.rotation[1]:.0f}° z {camera.rotation[2]:.0f}
        #Coordinates : x {active_object.offset[0]:.2f} y {active_object.offset[1]:.2f} z {-active_object.offset[2]:.2f}
        
    """
    text = font.render(output_text, True, (255, 255, 255))
    screen.blit(text, (0, 0))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()