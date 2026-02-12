import pygame
import math

center = (1190, 540)
var = {'active' : True, 'analytic' : True, 'animation' : [[],0],'dir_check' : ['',False], 'out_text' : ''}
all_objects = []
all_cameras = []
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

def rubik_rotation(rotation_cord):
    # rotation properties
    if   rotation_cord[0] == 'x':
        _blocks = blocks_x ; index = (1,2)
    elif rotation_cord[0] == 'y':
        _blocks = blocks_y ; index = (0,2)
    elif rotation_cord[0] == 'z':
        _blocks = blocks_z ; index = (0,1)
    # rotation animation
    _cof = -1 if rotation_cord[1] in ['u','r'] else 1
    if var['animation'][0][1] == rotation_cord[1]:
        if var['animation'][1] < 90:
            _add_ang = 10 if 10 <= var['animation'][1] <= 70 else 2
            for _obj_location in _blocks:
                rubik[_obj_location].rotate(index, _add_ang * _cof)
            var['animation'][1] += _add_ang
        else:
            # blocks change after rotation animation
            _blocks.pop(4) # delete center point
            index_add = []
            if rotation_cord[0] == 'x':
                index_add = _blocks[2:] + _blocks[:2] if rotation_cord[1] == 'd' else _blocks[-2:] + _blocks[:-2]
            elif rotation_cord[0] == 'z':
                index_add = _blocks[2:] + _blocks[:2] if rotation_cord[1] == 'd' else _blocks[-2:] + _blocks[:-2]
            elif rotation_cord[0] == 'y':
                index_add = _blocks[2:] + _blocks[:2] if rotation_cord[1] == 'r' else _blocks[-2:] + _blocks[:-2]
            # rewriting position
            _place_list = []
            for _place in _blocks:
                _place_list.append(rubik[_place])
            for _place in index_add:
                rubik[_place] = _place_list.pop(0)
            var['animation'] = [[], 0]

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
    cof = -1 if direction in ['b','l','d'] else 1
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
    for _point in colored[0][0]:
        _points[_point][index[0]] += points_offset[0] * cof
        _points[_point][index[1]] += points_offset[1] * cof
        _points[_point][index[2]] += 100 * cof
    return [_obj_name,colored,_points]

def calculate_polygon(_object):
    """calculate point output from camera angle and sort objects from nearest to farthest"""
    def calculate_color(_depth, _colors):
        """calculate color based on z position of an object"""
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
        """sort object or polygon based on z position"""
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
    sort(camera.object_order, polygon_depth , (_object, polygon_depth, order[::-1],polygons))

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
        self.object_order = []
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
        """calculating points position on the screen"""
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
        # creating colored polygons from points and sorting them
        self.object_order = []
        for _obj in all_objects:
            calculate_polygon(_obj)

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
i_let = (['u','l','d','r'],['l','d','r','u'],['d','r','u','l'],['r','u','l','d'])
for num, side in enumerate(['f','r','b','l']):
    let = i_let[num]
    buttons[f'{side}m'] = ObjectChanger(*create_button(f'button_{side}m',(  0,  0),side))
    buttons[f'{side}{let[0]}'] = ObjectChanger(*create_button(f'button_{side}{let[0]}',(  0, 66),side))
    buttons[f'{side}{let[1]}'] = ObjectChanger(*create_button(f'button_{side}{let[1]}',(-66,  0),side))
    buttons[f'{side}{let[2]}'] = ObjectChanger(*create_button(f'button_{side}{let[2]}',(  0,-66),side))
    buttons[f'{side}{let[3]}'] = ObjectChanger(*create_button(f'button_{side}{let[3]}',( 66,  0),side))

# cameras
camera1 = CameraChanger('Camera 1')
camera2 = CameraChanger('Camera 2')

# default settings
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
camera.rotate(1,45) ; camera.rotate(0,20)

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
    # objects re-render if action made
    if var['active']:
        var['active'] = False
        camera.render()

    # button animation and blocks rotation
    if var['animation'][0]:
        var['dir_check'] = ['', False]
        blocks_x = ['112', '122', '132', '232', '222', '332', '322', '312', '212']
        blocks_y = ['121', '122', '123', '223', '222', '323', '322', '321', '221']
        blocks_z = ['211', '221', '231', '232', '222', '233', '223', '213', '212']

        if var['animation'][0][0][-1] == 'm':


            if var['animation'][0][0][-2] in ['f','b']:
                for letter in ['xd','xu','yl','yr']:
                    if var['animation'][0][1] == letter[1]:
                        rubik_rotation(letter)
                        break

            elif var['animation'][0][0][-2] in ['r','l']:
                for letter in ['zd', 'zu', 'yl', 'yr']:
                    if var['animation'][0][1] == letter[1]:
                        rubik_rotation(letter)
                        break

        elif var['animation'][0][0][-1] in ['l','r'] and var['animation'][0][-1] in ['u','d']:
            # all left and right buttons for x rotation
            if var['animation'][0][0][-2] in ['f', 'b']:

                if var['animation'][0][0][-1] == 'l':
                    for num in range(9):
                        blocks_x[num] = str(int(blocks_x[num]) - 1)
                if var['animation'][0][0][-1] == 'r':
                    for num in range(9):
                        blocks_x[num] = str(int(blocks_x[num]) + 1)

                for letter in ['xd', 'xu']:
                    if var['animation'][0][1] == letter[1]:
                        rubik_rotation(letter)
                        break

            elif var['animation'][0][0][-2] in ['l', 'r']:

                if var['animation'][0][0][-1] == 'l':
                    for num in range(9):
                        blocks_z[num] = str(int(blocks_z[num]) - 100)
                if var['animation'][0][0][-1] == 'r':
                    for num in range(9):
                        blocks_z[num] = str(int(blocks_z[num]) + 100)

                for letter in ['zd', 'zu']:
                    if var['animation'][0][1] == letter[1]:
                        rubik_rotation(letter)
                        break

        # all up and down buttons for y rotation
        elif var['animation'][0][0][-1] in ['u','d'] and var['animation'][0][-1] in ['l','r']:

            if var['animation'][0][0][-1] == 'u':
                for num in range(9):
                    blocks_y[num] = str(int(blocks_y[num]) - 10)
            if var['animation'][0][0][-1] == 'd':
                for num in range(9):
                    blocks_y[num] = str(int(blocks_y[num]) + 10)

            for letter in ['yl', 'yr']:
                if var['animation'][0][1] == letter[1]:
                    rubik_rotation(letter)
                    break

        else:
            var['animation'] = [[],0]

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

        # informating if any button was activated
        if not var['animation'][0]:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                new_list = []
                for _object in camera.object_order:
                    if _object[0].name[:6] == 'button' and _object[1] > 0:
                        for point in list(_object[3][('1', '2', '3', '4')]['render_points']):
                            new_list.append((point[0], point[1]))
                        button_name = _object[0].name
                        # mask creation
                        surf = pygame.Surface((1920, 1080), pygame.SRCALPHA)
                        pygame.draw.polygon(surf, (255, 255, 255), new_list)
                        mask = pygame.mask.from_surface(surf)
                        mx, my = pygame.mouse.get_pos()
                        # check if click was in the polygon
                        if mask.get_at((mx, my)):
                            var['dir_check'] = [button_name,True]
                            dx, dy = 0,0
                            break
            if var['dir_check'][1] and var['dir_check'][0] == button_name:
                if event.type == pygame.MOUSEMOTION and mouse_keys[0]:
                    dx += event.rel[0] ; dy += event.rel[1]
                    # inversion of mirrored side
                    if   dx >  30:
                        var['animation'] = [[button_name,'r'], 0]
                    elif dy < -30:
                        inv_let = 'd' if button_name[-2] in ['b', 'r'] and button_name[-1] not in ['d', 'u'] else 'u'
                        var['animation'] = [[button_name, inv_let], 0]
                    elif dx < -30:
                        var['animation'] = [[button_name,'l'], 0]
                    elif dy >  30:
                        inv_let = 'u' if button_name[-2] in ['b', 'r'] and button_name[-1] not in ['d', 'u'] else 'd'
                        var['animation'] = [[button_name, inv_let], 0]
                var['out_text'] = var['animation'] # for visualization


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
    for _object in camera.object_order[::-1]:
        if _object[0].name[:6] != 'button':
            render_polygon(_object)

    # in-game info output
    if var['analytic']:
        fps = int(clock.get_fps())
        font = pygame.font.Font(None, 40)
        messages = [

        f'Fps : {fps}',
        f'' ,
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
        f'last rubik rotation : {var['out_text']}']

        for num, message in enumerate(messages):
            text = font.render(message, True, (255, 255, 255))
            screen.blit(text, (15, 5 + num * 35))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()