import pygame
import math
gog = 0
center = (1190, 540)
mouse_cords = center
var = {'active' : True, 'analytic' : True, 'animation' : [0,0],'dir_check' : ['',False]}
all_objects = []
all_cameras = []
object_order = []
points = {}
colors = {
    'red'   : (255,   0,   0),
    'green' : (  0, 255,   0),
    'blue'  : (  0,   0, 255),
    'yellow': (255, 255,   0),
    'orange': (255, 165,   0),
    'white' : (255, 255, 255),
    'gray'  : ( 50,  50,  50),
}


def make_mask(_points):
    surf = pygame.Surface((1920, 1080), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (255, 255, 255), _points)
    return pygame.mask.from_surface(surf)

def angle_calc(_radius, _cord_0, _cord_1):
    _angle = math.degrees(math.acos(_cord_1 / _radius)) if _radius != 0 else 0
    return 360 - _angle if _cord_0 < 0 else _angle

def create_cube(_obj_name,points_offset, color_input):
    cube_color = ('red','yellow','green','blue','white','orange')
    color_output = ['gray','gray','gray','gray','gray','gray']
    for _num in color_input:
        color_output[_num -1] = cube_color[_num-1]
    colored = ((('1', '2', '3', '4'), colors[color_output[0]]), (('5', '6', '7', '8'), colors[color_output[1]]),
               (('3', '4', '8', '7'), colors[color_output[2]]), (('1', '2', '6', '5'), colors[color_output[3]]),
               (('1', '4', '8', '5'), colors[color_output[4]]), (('2', '3', '7', '6'), colors[color_output[5]]))
    cube_points = {
        '1': [ 33.0, 33.0, 33.0], '2': [ 33.0,-33.0, 33.0],
        '3': [-33.0,-33.0, 33.0], '4': [-33.0, 33.0, 33.0],
        '5': [ 33.0, 33.0,-33.0], '6': [ 33.0,-33.0,-33.0],
        '7': [-33.0,-33.0,-33.0], '8': [-33.0, 33.0,-33.0]}
    for _point in cube_points:
        cube_points[_point][0] += points_offset[0]
        cube_points[_point][1] += points_offset[1]
        cube_points[_point][2] += points_offset[2]
    return [_obj_name,colored,cube_points]

def create_button(_obj_name,points_offset, direction):
    colored = ((('1', '2', '3', '4'), (255,255,255)),)
    cof = -1 if direction in ['b','r','d'] else 1
    if   direction in ['f','b']:
        _points = {'1': [ 33.0, 33.0,  0], '2': [ 33.0,-33.0,   0],
                   '3': [-33.0,-33.0,  0], '4': [-33.0, 33.0,   0],}
        index = (0, 1, 2)
    elif direction in ['l','r']:
        _points = {'1': [ 0, 33.0,  33.0], '2': [ 0,-33.0,  33.0],
                   '3': [ 0,-33.0, -33.0], '4': [ 0, 33.0, -33.0],}
        index = (1, 2, 0)
    elif direction in ['u','d']:
        _points = {'1': [ 33.0, 0,  33.0], '2': [ 33.0, 0, -33.0],
                   '3': [-33.0, 0, -33.0], '4': [-33.0, 0,  33.0],}
        index = (2, 0, 1)
    for _point in _points:
        _points[_point][index[0]] += points_offset[0] * cof
        _points[_point][index[1]] += points_offset[1] * cof
        _points[_point][index[2]] += 100 * cof
    return [_obj_name,colored,_points]

def render_object(_object, choose_color):
    for _point in points[_object.name]:
        # z cord (depth calculation)
        mult = (((camera.output[_object.name][_point][2] + 125) / 375) + 2)
        # x and y cord output
        pygame.draw.rect(screen, (0, 0, choose_color),
                        (center[0] + (camera.output[_object.name][_point][0]) * mult,
                        center[1] - (camera.output[_object.name][_point][1]) * mult, 10, 10))

def calculate_polygon(_object):

    def calculate_color(_depth, _colors):
        f_colors = []
        limit = 80 * camera.size
        if _depth > limit:
            return _colors
        elif _depth < -limit:
            return (_colors[0] / 1.5, _colors[1] / 1.5, _colors[2] / 1.5),
        for _color in _colors:
            f_colors.append(int(_color / (1 + ((_depth - limit) / -40))))
        return f_colors

    def sort(_order, condition, content):
        if _order:
            for _num in range(len(_order)):
                if condition > _order[_num][1]:
                    _order.insert(_num, content)
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
        self.output = {}
        self.size = 1
        for _obj in points:
            self.output[_obj] = {}
            for dott in points[_obj]:
                self.output[_obj][dott] = [0, 0, 0]

    def rotate(self,index, _add_ang):
        self.rotation[index] += _add_ang
        var['active'] = True

    def resize(self,add_size):
        self.size *= 1 + add_size / 100
        var['active'] = True

    def render(self):
        for _obj in all_objects:
            for _point in points[_obj.name]:
                # camera y rotation offset
                index = (0,2,1)
                radius = math.hypot(points[_obj.name][_point][index[0]] + _obj.pos[index[0]],
                                    points[_obj.name][_point][index[1]] + _obj.pos[index[1]])
                angle = angle_calc(radius, points[_obj.name][_point][index[0]] + _obj.pos[index[0]],
                                   points[_obj.name][_point][index[1]] + _obj.pos[index[1]]) - self.rotation[index[2]]
                cord_x = points[_obj.name][_point][index[2]] + _obj.pos[index[2]]
                cord_y = round(radius * math.sin(math.radians(angle)), 2)
                cord_z = round(radius * math.cos(math.radians(angle)), 2)
                # camera x rotation offset
                index = (1, 2, 0)
                radius = math.hypot(cord_x, cord_z)
                angle = angle_calc(radius, cord_x, cord_z) - self.rotation[index[2]]
                # final camera cord output
                self.output[_obj.name][_point][index[0]] = round(radius * math.sin(math.radians(angle)) * self.size, 2)
                self.output[_obj.name][_point][index[2]] = round(cord_y * self.size,2)
                self.output[_obj.name][_point][index[1]] = round(radius * math.cos(math.radians(angle)) * self.size, 2)

class ObjectChanger:
    def __init__(self, obj_name,polygons,_points):
        all_objects.append(self)
        points[obj_name] = _points
        self.point_dict = points[obj_name]
        self.name = obj_name
        self.pos = [0,0,0]
        self.rotation = [0, 0, 0]
        self.size = 1
        self.polygons = polygons

    def rotate(self,index, _add_ang):
        for _point in points[active_object.name]:
            radius = math.hypot(self.point_dict[_point][index[0]], self.point_dict[_point][index[1]])
            angle = angle_calc(radius, self.point_dict[_point][index[0]], self.point_dict[_point][index[1]]) - _add_ang
            self.point_dict[_point][index[0]] = round(radius * math.sin(math.radians(angle)), 2)
            self.point_dict[_point][index[1]] = round(radius * math.cos(math.radians(angle)), 2)
        self.rotation[1] += _add_ang
        var['active'] = True

    def move(self, index, add_move):
        self.pos[index] += add_move
        var['active'] = True

    def resize(self,add_size):
        for _point in self.point_dict:
            for index in [0,1,2]:
                self.point_dict[_point][index] *= round(1 + add_size / 100,2)
        self.size *= 1 + add_size / 100
        var['active'] = True

"""Objects"""
cube_active = True
if cube_active:
    # corners
    corner_lfu = ObjectChanger(*create_cube('corner_lfu',(-66, 66, 66), (1,3,5)))
    corner_lfd = ObjectChanger(*create_cube('corner_lfd',(-66,-66, 66), (1,3,6)))
    corner_rfu = ObjectChanger(*create_cube('corner_rfu',( 66, 66, 66), (1,4,5)))
    corner_rfd = ObjectChanger(*create_cube('corner_rfd',( 66,-66, 66), (1,4,6)))

    corner_lbu = ObjectChanger(*create_cube('corner_lbu',(-66, 66,-66), (2,3,5)))
    corner_lbd = ObjectChanger(*create_cube('corner_lbd',(-66,-66,-66), (2,3,6)))
    corner_rbu = ObjectChanger(*create_cube('corner_rbu',( 66, 66,-66), (2,4,5)))
    corner_rbd = ObjectChanger(*create_cube('corner_rbd',( 66,-66,-66), (2,4,6)))
    # cuts
    cut_lu = ObjectChanger(*create_cube('cut_lu',(-66, 66,  0), (3,5)))
    cut_ru = ObjectChanger(*create_cube('cut_ru',( 66, 66,  0), (4,5)))
    cut_fu = ObjectChanger(*create_cube('cut_fu',(  0, 66, 66), (1,5)))
    cut_bu = ObjectChanger(*create_cube('cut_bu',(  0, 66,-66), (2,5)))

    cut_lf = ObjectChanger(*create_cube('cut_lf',(-66,  0, 66), (3,1)))
    cut_rf = ObjectChanger(*create_cube('cut_rf',( 66,  0, 66), (4,1)))
    cut_lb = ObjectChanger(*create_cube('cut_lb',(-66,  0,-66), (3,2)))
    cut_rb = ObjectChanger(*create_cube('cut_rb',( 66,  0,-66), (4,2)))

    cut_ld = ObjectChanger(*create_cube('cut_ld',(-66,-66,  0), (3,6)))
    cut_rd = ObjectChanger(*create_cube('cut_rd',( 66,-66,  0), (4,6)))
    cut_fd = ObjectChanger(*create_cube('cut_fd',(  0,-66, 66), (1,6)))
    cut_bd = ObjectChanger(*create_cube('cut_bd',(  0,-66,-66), (2,6)))
    # sides
    side_f = ObjectChanger(*create_cube('side_f',(  0,  0, 66), (1,)))
    side_b = ObjectChanger(*create_cube('side_b',(  0,  0,-66), (2,)))
    side_l = ObjectChanger(*create_cube('side_l',(-66,  0,  0), (3,)))
    side_r = ObjectChanger(*create_cube('side_r',( 66,  0,  0), (4,)))
    side_u = ObjectChanger(*create_cube('side_u',(  0, 66,  0), (5,)))
    side_d = ObjectChanger(*create_cube('side_d',(  0,-66,  0), (6,)))
    # center
    cent_p = ObjectChanger(*create_cube('cent_p',(  0,  0,  0), ()))

# buttons
buttons = {}
for side in ['f','b','l','r']:
    break
    buttons[f'{side}m'] = ObjectChanger(*create_button(f'button_{side}m',(  0,  0),side))
    buttons[f'{side}u'] = ObjectChanger(*create_button(f'button_{side}u',(  0, 66),side))
    buttons[f'{side}d'] = ObjectChanger(*create_button(f'button_{side}d',(  0,-66),side))
    buttons[f'{side}l'] = ObjectChanger(*create_button(f'button_{side}l',( 66,  0),side))
    buttons[f'{side}r'] = ObjectChanger(*create_button(f'button_{side}r',(-66,  0),side))


# cameras
camera1 = CameraChanger('Camera 1')
camera2 = CameraChanger('Camera 2')

# default settings
if cube_active:
    rubik = {# first layer (front)
             '111' : corner_lfu, '112' : cut_fu, '113' : corner_rfu,
             '121' : cut_lf    , '122' : side_f, '123' : cut_rf    ,
             '131' : corner_lfd, '132' : cut_fd, '133' : corner_rfd,
             # second layer (mid)
             '211' : cut_lu    , '212' : side_u, '213' : cut_ru    ,
             '221' : side_l    , '222' : cent_p, '223' : side_r    ,
             '231' : cut_ld    , '232' : side_d, '233' : cut_rd    ,
             # third layer (back)
             '311' : corner_lbu, '312' : cut_bu, '313' : corner_rbu,
             '321' : cut_lb    , '322' : side_b, '323' : cut_rb    ,
             '331' : corner_lbd, '332' : cut_bd, '333' : corner_rbd,}

active_object = all_objects[0]
camera = all_cameras[0]
#camera.rotate(1,45) ; camera.rotate(0,20)

# pygame initialization
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
clock = pygame.time.Clock()
background_color = (0, 5, 0)
screen.fill(background_color)

# main cycle
running = True
while running:
    """ BRAIN """
    # objects output calculation
    if var['active']:
        var['active'] = False
        camera.render()
        object_order = []
        for _object in all_objects:
            if _object.polygons:
                calculate_polygon(_object)

    if var['animation'][0] == 1:
        var['dir_check'] = ['', False]
        if var['animation'][1] < 90:
            add_ang = 10 if 10 <= var['animation'][1] <= 70 else 2
            for obj_location in ['111', '112', '113', '121', '122', '123', '131', '132', '133']:
                rubik[obj_location].rotate((0, 1), add_ang)
            var['animation'][1] += add_ang
        else:
            place_list = []
            for place in ['111', '112', '113', '121', '122', '123', '131', '132', '133']:
                place_list.append(rubik[place])
            for place in ['131', '121', '111', '132', '122', '112', '133', '123', '113']:
                rubik[place] = place_list.pop(0)
            var['animation'] = [0,0]

    if var['animation'][0] == 2:
        var['dir_check'] = ['', False]
        if var['animation'][1] < 90:
            add_ang = 10 if 10 <= var['animation'][1] <= 70 else 2
            for obj_location in ['113', '123', '133', '213', '223', '233', '313', '323', '333']:
                rubik[obj_location].rotate((1, 2), add_ang)
            var['animation'][1] += add_ang
        else:
            place_list = []
            for place in ['113', '123', '133', '213', '223', '233', '313', '323', '333']:
                place_list.append(rubik[place])
            for place in ['133', '233', '333', '123', '223', '323', '113', '213', '313']:
                rubik[place] = place_list.pop(0)
            var['animation'] = [0,0]

    if var['animation'][0] == 3:
        var['dir_check'] = ['', False]
        if var['animation'][1] < 90:
            add_ang = 10 if 10 <= var['animation'][1] <= 70 else 2
            for obj_location in ['112', '122', '132', '212', '222', '232', '312', '322', '332']:
                rubik[obj_location].rotate((1, 2), add_ang)
            var['animation'][1] += add_ang
        else:
            place_list = []
            for place in ['112', '122', '132', '212', '222', '232', '312', '322', '332']:
                place_list.append(rubik[place])
            for place in ['132', '232', '332', '122', '222', '322', '112', '212', '312']:
                rubik[place] = place_list.pop(0)
            var['animation'] = [0,0]


    """ INPUT """
    # rotation,movement and sizing
    keys = pygame.key.get_pressed()
    mouse_keys = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        # ways to exit
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # camera sizing with mouse
        elif event.type == pygame.MOUSEWHEEL:
            if (camera.size < 2 or event.y < 0) and (camera.size > 0.3 or event.y > 0):
                camera.resize(event.y * 5)
        # camera rotation with mouse and cursor control
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pygame.mouse.set_visible(False) ; pygame.event.set_grab(True)
            mouse_cords = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            pygame.mouse.set_visible(True) ; pygame.event.set_grab(False)
            pygame.mouse.set_pos(mouse_cords)
        elif event.type == pygame.MOUSEMOTION and mouse_keys[2]:
            dx, dy = event.rel
            if (camera.rotation[0] < 85 or dy < 0) and (camera.rotation[0] > -85 or dy > 0):
                camera.rotate(0, dy / 20)
            camera.rotate(1, -dx / 20)

        # analytic mode
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            var['analytic'] = True if var['analytic'] == False else False
            center = (1190, 540) if center == (990, 540) else (990, 540)
            var['active'] = True

        #object change
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_o:
            _index = all_objects.index(active_object)
            active_object = all_objects[_index + 1] if _index < len(all_objects) - 1 else all_objects[0]
            var['active'] = True
        # camera change
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_k:
            _index = all_cameras.index(camera)
            camera = all_cameras[_index + 1] if _index < len(all_cameras) - 1 else all_cameras[0]
            var['active'] = True


        #testing
        if not var['animation'][0]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                var['animation'] = [1,0]
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                var['animation'] = [2,0]


            if var['dir_check'][1] and var['dir_check'][0] == 'button_f':
                if event.type == pygame.MOUSEMOTION and mouse_keys[0]:
                    _dx += event.rel[0] ; _dy += event.rel[1]
                    if _dy > 20:
                        var['animation'] = [3, 0]
                    if _dx > 20:
                        var['animation'] = [2, 0]
                else:
                    var['dir_check'] = [0,0]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                new_list = []
                for obj in object_order:
                    if obj[0] == buttons['fm']:
                        for point in list(obj[3][('1', '2', '3', '4')]['render_points']):
                            new_list.append((point[0], point[1]))
                        break
                mask = make_mask(new_list)
                mx, my = pygame.mouse.get_pos()
                if mask.get_at((mx, my)):
                    var['dir_check'] = ['button_f',True]
                    _dx, _dy = 0,0


    # object movement
    if keys[pygame.K_g]:
        if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            active_object.move(0,2)
        elif keys[pygame.K_LEFT]  and not keys[pygame.K_RIGHT]:
            active_object.move(0, -2)
        if keys[pygame.K_RALT]    and not keys[pygame.K_DOWN]:
            active_object.move(1,2)
        elif keys[pygame.K_RCTRL]  and not keys[pygame.K_UP]:
            active_object.move(1,-2)
        if keys[pygame.K_DOWN]  and not keys[pygame.K_RCTRL]:
            active_object.move(2, 2)
        elif keys[pygame.K_UP] and not keys[pygame.K_RALT]:
            active_object.move(2, -2)
    # object resizing
    elif keys[pygame.K_x]:
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN] and active_object.size < 3:
            active_object.resize(1)
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP] and active_object.size > 0.20:
            active_object.resize(-1)
    # object rotation
    elif keys[pygame.K_r]:
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            active_object.rotate((0, 2), 1)
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            active_object.rotate((0, 2),-1)
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            active_object.rotate((1, 2), 1)
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            active_object.rotate((1, 2),-1)
        if keys[pygame.K_RALT] and not keys[pygame.K_RCTRL]:
            active_object.rotate((0, 1), 1)
        elif keys[pygame.K_RCTRL] and not keys[pygame.K_RALT]:
            active_object.rotate((0, 1),-1)

    """ OUTPUT """
    # background
    screen.fill(background_color)
    pygame.draw.rect(screen, (255, 255, 0),(center[0], center[1], 5, 5))

    # objects output render
    for _object in object_order[::-1]:
        render_polygon(_object)

    # in-game info output
    if var['analytic']:
        fps = int(clock.get_fps())
        font = pygame.font.Font(None, 40)
        messages = [

        f'Fps : {fps}',
        f'' ,
        f'Objects : {[i.name for i in all_objects]}',
        f'Object : {active_object.name}',
        f'Rotation : x {active_object.rotation[0]:.0f}° y {active_object.rotation[1]:.0f}° z {active_object.rotation[2]:.0f}°',
        f'Coordinates : x {active_object.pos[0]:.2f} y {active_object.pos[1]:.2f} z {-active_object.pos[2]:.2f}',
        f'Size : {active_object.size:.2f}',
        f'',
        f'Cameras : {[i.name for i in all_cameras]}',
        f'Camera : {camera.name}',
        f'Rotation : x {camera.rotation[0]:.0f}° y {camera.rotation[1]:.0f}°',
        f'Size : {camera.size:.2f}',
        f'',
        f'State : {'active' if var['active'] else 'passive'}',
        f'{gog}']
        for num, message in enumerate(messages):
            text = font.render(message, True, (255, 255, 255))
            screen.blit(text, (15, 5 + num * 35))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()