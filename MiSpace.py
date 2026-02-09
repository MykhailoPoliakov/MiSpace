import pygame
import math

center = (1190, 540)
all_objects = []
all_cameras = []
object_order = []
colors = {
    'red'   : (255,   0,   0),
    'green' : (  0, 255,   0),
    'blue'  : (  0,   0, 255),
    'yellow': (255, 255,   0),
    'orange': (255, 165,   0),
    'white' : (255, 255, 255),
    'gray'  : (127, 127, 127),
}

pygame.init()
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
    },
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

def render_object(_object, choose_color):
    for _point in points[_object.name]:
        # z cord (depth calculation)
        mult = (((camera.output[_object.name][_point][2] + 125) / 375) + 2)
        # changing color and size depending on depth
        if 55 <= (camera.output[_object.name][_point][2]  + 100) + 55 <= 255:
            _color = (camera.output[_object.name][_point][2]  + 100) + 55
            _size = (camera.output[_object.name][_point][2]  + 100) / 20 + 5
        elif 55 > (camera.output[_object.name][_point][2]  + 100) + 55:
            _color = 55  ; _size = 5
        else:
            _color = 255 ; _size = 15
        # x and y cord output
        pygame.draw.rect(screen, (0, _color, choose_color),
                        (center[0] + (camera.output[_object.name][_point][0]) * mult,
                        center[1] - (camera.output[_object.name][_point][1]) * mult, _size, _size))

def calculate_polygon(_object):
    def calculate_color(_depth, _colors):
        f_colors = []
        if _depth > 100:
            return _colors
        elif _depth < -100:
            return (_colors[1] / 1.5, _colors[1] / 1.5, _colors[2] / 1.5),
        for _color in _colors:
            f_colors.append(int(_color / (1 + ((_depth - 100) / -40))))
        return f_colors
    def sort(_order, condition, content):
        if _order:
            for num in range(len(_order)):
                if condition > _order[num][1]:
                    _order.insert(num, content)
                    return
        _order.append(content)
        return
    polygons = {}
    order = []
    polygon_depth = 0
    for polygon, color in _object.polygons:
        polygons[polygon] = {'render_points' : [], 'depth_ev' : 0}
        for _point in polygon:
            # z cord (depth calculation)
            mult = round((((camera.output[_object.name][_point][2] + 125) / 375) + 2),2)
            polygons[polygon]['render_points'].append((round(center[0] + (camera.output[_object.name][_point][0]) * mult,2),
                                    round(center[1] - (camera.output[_object.name][_point][1]) * mult,2)))
            depth = int(camera.output[_object.name][_point][2])
            polygons[polygon]['depth_ev'] += depth
            polygon_depth += depth
        # color of the polygon calculation
        final_color = calculate_color(polygons[polygon]['depth_ev'] / 4, color)
        # in "order" sorting all polygons of an object
        sort(order, polygons[polygon]['depth_ev'], (polygon, polygons[polygon]['depth_ev'],tuple(final_color)))
    # in "object_order" sorting object itself
    sort(object_order, polygon_depth , (_object, polygon_depth, order[::-1],polygons))

def render_polygon(object_info):
    for _polygon, _depth, _color in object_info[2]:
        pygame.draw.polygon(screen, _color, object_info[3][_polygon]['render_points'])
        pygame.draw.polygon(screen, (0, 0, 0) , object_info[3][_polygon]['render_points'],4)

class CameraChanger:
    def __init__(self,name):
        all_cameras.append(self)
        self.name = name
        self.rotation = [0,0]
        self.pos = [0,0,0]
        self.output = {}
        for obj in points:
            self.output[obj] = {}
            for dott in points[obj]:
                self.output[obj][dott] = [0, 0, 0]

    def rotate(self,index, add_ang):
        self.rotation[index] += add_ang

    def move(self,index,add_mov):
        pass

    def render(self):
        for _obj in all_objects:
            for _point in points[_obj.name]:
                # camera y rotation offset
                index = (0,2,1)
                radius = math.hypot(points[_obj.name][_point][index[0]] + _obj.pos[index[0]],
                                    points[_obj.name][_point][index[1]] + _obj.pos[index[1]])
                if radius != 0:
                    side = points[_obj.name][_point][index[1]] + _obj.pos[index[1]]
                    start_angle = math.degrees(math.acos(side / radius))
                    if points[_obj.name][_point][index[0]] + _obj.pos[index[0]] < 0:
                        start_angle = 360 - start_angle
                    angle = start_angle - self.rotation[index[2]]
                else:
                    angle = 0
                cord_x = points[_obj.name][_point][index[2]] + _obj.pos[index[2]]
                cord_y = round(radius * math.sin(math.radians(angle)), 2)
                cord_z = round(radius * math.cos(math.radians(angle)), 2)
                # camera x rotation offset
                index = (1, 2, 0)
                radius = math.hypot(cord_x, cord_z)
                if radius != 0:
                    side = cord_z
                    start_angle = math.degrees(math.acos(side / radius))
                    if cord_x < 0:
                        start_angle = 360 - start_angle
                    angle = start_angle - self.rotation[index[2]]
                else:
                    angle = 0
                # final camera cord output
                self.output[_obj.name][_point][index[0]] = round(radius * math.sin(math.radians(angle)), 2)
                self.output[_obj.name][_point][index[2]] = cord_y
                self.output[_obj.name][_point][index[1]] = round(radius * math.cos(math.radians(angle)), 2)

class ObjectChanger:
    def __init__(self, obj_name,polygons=None,_points=None):
        all_objects.append(self)
        if _points:
            points[obj_name] = _points
        self.point_dict = points[obj_name]
        self.name = obj_name
        self.pos = [0,0,0]
        self.rotation = [0, 0, 0]
        self.size = 1
        self.polygons = polygons

    def rotate(self,_point, index, add_ang):
        def __get_angle(_point, _index, _radius):
            if radius == 0:
                return 0
            side = self.point_dict[_point][_index[1]]
            result = math.degrees(math.acos(side / _radius))
            if self.point_dict[_point][_index[0]] < 0:
                result = 360 - result
            return result
        radius = math.hypot(self.point_dict[_point][index[0]], self.point_dict[_point][index[1]])
        angle = __get_angle(_point, index,radius) - add_ang
        self.point_dict[_point][index[0]] = round(radius * math.sin(math.radians(angle)), 2)
        self.point_dict[_point][index[1]] = round(radius * math.cos(math.radians(angle)), 2)

    def move(self, index, add_move):
        self.pos[index] += add_move

    def resize(self,add_size):
        for _point in self.point_dict:
            for index in [0,1,2]:
                self.point_dict[_point][index] *= round(1 + add_size / 100,2)
        active_object.size *= 1 + add_size / 100

# objects
square = ObjectChanger('square')
plane = ObjectChanger('plane')
block1 = ObjectChanger('block1', (
     (('1','2','3','4'),colors['red'])  ,(('5','6','7','8'),colors['gray']) ,
     (('3','4','8','7'),colors['gray']) ,(('1','2','6','5'),colors['blue']) ,
     (('1','4','8','5'),colors['white']),(('2','3','7','6'),colors['gray'])),
    {'1' : [ 100.0, 100.0, 100,0],
            '2' : [ 100.0,  33.0, 100.0],
            '3' : [  33.0,  33.0, 100.0],
            '4' : [  33.0, 100.0, 100.0],
            '5' : [ 100.0, 100.0,  33,0],
            '6' : [ 100.0,  33.0,  33.0],
            '7' : [  33.0,  33.0,  33.0],
            '8' : [  33.0, 100.0,  33.0]})
block2 = ObjectChanger('block2', (
    (('1', '2', '3', '4'), colors['orange']), (('5', '6', '7', '8'), colors['gray']) ,
    (('3', '4', '8', '7'), colors['gray'])  , (('1', '2', '6', '5'), colors['green']),
    (('1', '4', '8', '5'), colors['yellow']), (('2', '3', '7', '6'), colors['gray'])),
    {'1' : [-100.0,-100.0,-100,0],
            '2' : [-100.0, -33.0,-100.0],
            '3' : [ -33.0, -33.0,-100.0],
            '4' : [ -33.0,-100.0,-100.0],
            '5' : [-100.0,-100.0, -33,0],
            '6' : [-100.0, -33.0, -33.0],
            '7' : [ -33.0, -33.0, -33.0],
            '8' : [ -33.0,-100.0, -33.0]})
camera1 = CameraChanger('Camera 1')
camera2 = CameraChanger('Camera 2')


active_object = all_objects[0]
camera = all_cameras[0]

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
        # testing
        if event.type == pygame.KEYDOWN and event.key == pygame.K_9:
            camera = camera2
        if event.type == pygame.KEYDOWN and event.key == pygame.K_8:
            camera = camera1

    # rotation,movement and sizing
    keys = pygame.key.get_pressed()
    camera.render()

    # object movement
    if keys[pygame.K_g]:
        if   keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            active_object.move(0,2)
        elif keys[pygame.K_LEFT]  and not keys[pygame.K_RIGHT]:
            active_object.move(0, -2)
        if   keys[pygame.K_UP]    and not keys[pygame.K_DOWN]:
            active_object.move(1,2)
        elif keys[pygame.K_DOWN]  and not keys[pygame.K_UP]:
            active_object.move(1,-2)
        if   keys[pygame.K_RALT]  and not keys[pygame.K_RCTRL]:
            active_object.move(2, 2)
        elif keys[pygame.K_RCTRL] and not keys[pygame.K_RALT]:
            active_object.move(2, -2)

    # object size
    elif keys[pygame.K_s]:
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN] and active_object.size < 3:
            active_object.resize(1)
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP] and active_object.size > 0.20:
            active_object.resize(-1)

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
        if keys[pygame.K_RIGHT]:
            camera.rotate( 1, 1)
        elif keys[pygame.K_LEFT]:
            camera.rotate( 1, -1)

    """ OUTPUT """
    screen.fill(background_color)
    pygame.draw.rect(screen, (255, 255, 0),(center[0], center[1], 5, 5))
    render_object(plane, 255)
    render_object(square, 0)
    for _object in all_objects:
        if _object.polygons:
            calculate_polygon(_object)
    for _object in object_order[::-1]:
        render_polygon(_object)
    object_order = []

    # in-game info output
    font = pygame.font.Font(None, 40)
    messages = [
    f'Objects : {[i.name + f" ({num})" for num, i in enumerate(all_objects, 1)]}',
    f'Object : {active_object.name}',
    f'Rotation : x {active_object.rotation[0]:.0f}° y {active_object.rotation[1]:.0f}° z {active_object.rotation[2]:.0f}°',
    f'# Coordinates : x {active_object.pos[0]:.2f} y {active_object.pos[1]:.2f} z {-active_object.pos[2]:.2f}',
    f'Size : {active_object.size:.2f}',
    f' ',
    f'Cameras : {[i.name + f" ({num})" for num, i in enumerate(all_cameras,8)]}',
    f'Camera : {camera.name}',
    f'Rotation : x {camera.rotation[0]:.0f}° y {camera.rotation[1]:.0f}°',
    f'# Coordinates : x {active_object.pos[0]:.2f} y {active_object.pos[1]:.2f} z {-active_object.pos[2]:.2f}',
    f'# Size : {active_object.size:.2f}']
    for num, message in enumerate(messages):
        text = font.render(message, True, (255, 255, 255))
        screen.blit(text, (5, 5 + num * 35))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()