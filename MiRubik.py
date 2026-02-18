import pygame
import math
import random
import sys, os
import copy

# globals
var = {'active' : True, 'analytic' : False, 'animation' : [[],0,''], 'solid' : True,
       'mouse_lock' : '', 'silent_mode' : False,
       'dir_check' : '', 'out_text' : '','shuffle' : '', 'mode' : 'menu', 'mode_anim' : ['',0]}

anim = {'menu' : 0}
cord_to_index = {'x' : (1,2), 'y' : (0,2), 'z' : (0,1)}
blocks_x = ['112', '122', '132', '232', '332', '322', '312', '212', '222']
blocks_y = ['121', '122', '123', '223', '323', '322', '321', '221', '222']
blocks_z = ['211', '221', '231', '232', '233', '223', '213', '212', '222']

all_colors = ({
        'red': [(153, 0, 0)],
        'green': [(0, 102, 0)],
        'blue': [(0, 76, 153)],
        'yellow': [(204, 204, 0)],
        'orange': [(204, 102, 0)],
        'white': [(255, 229, 204)],
        'gray': [(50, 50, 50)], },
    {
        'red': [(255, 0, 0)],
        'green': [(0, 255, 0)],
        'blue': [(0, 0, 255)],
        'yellow': [(210, 210, 0)],
        'orange': [(255, 165, 0)],
        'white': [(255, 255, 255)],
        'gray': [(50, 50, 50)], })

for group_colors in all_colors:
    for pol_color in group_colors:
        group_colors[pol_color].append(
            (int(group_colors[pol_color][0][0] / 1.2), int(group_colors[pol_color][0][1] / 1.2),
             int(group_colors[pol_color][0][2] / 1.2)))



""" Textures """
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

""" Basic Functions """
def angle_calc(_radius, _cord_0, _cord_1):
    _angle = math.degrees(math.acos(_cord_1 / _radius)) if _radius != 0 else 0
    return 360 - _angle if _cord_0 < 0 else _angle

def basic_animation(lock_word, if_const, if_plus, else_minus):
    if var['mouse_lock'] == lock_word:
        if anim[lock_word] < if_const:
            anim[lock_word] += if_plus
    elif anim[lock_word] > 0:
        anim[lock_word] -= else_minus

def sound(track):
    if not var['silent_mode']:
        sounds[track].play()

""" Rubik Rotation Functions """
def rubik_rotation(rotation_cord,_blocks,_index,_cof):
    # rotation animation
    if var['animation'][1] < 90:
        if var['shuffle'] == 'fast':
            _add_ang = 30
        else:
            _add_ang = 10 if 10 <= var['animation'][1] <= 70 else 2
        for _obj_location in _blocks:
            world.rubik[_obj_location].rotate(_index, _add_ang * _cof)
        var['animation'][1] += _add_ang
    else:
        # rewriting position
        _blocks.pop(-1)
        off_blocks = _blocks[2:] + _blocks[:2] if rotation_cord[1] in ['d', 'r'] else _blocks[-2:] + _blocks[:-2]
        place_save = []
        for pl in _blocks:  place_save.append(world.rubik[pl])
        for pl in off_blocks:  world.rubik[pl] = place_save.pop(0)
        var['animation'] = [[], 0, '']

def rubik_calculation():
    coef = ()
    # side rotation
    if var['animation'][0][0][-1] in ['u', 'd'] and var['animation'][0][-1] in ['l', 'r']:
        direction = f'y{var['animation'][0][-1]}'
        coef = (10, ('u', 'd'))
        blocks_ = blocks_y
    # front and back side vertical rotation and center
    elif var['animation'][0][0][-2] in ['f', 'b']:
        if var['animation'][0][0][-1] == 'm':
            direction = f'{'x' if var['animation'][0][-1] in ['u', 'd'] else 'y'}{var['animation'][0][-1]}'
            blocks_ = blocks_x if var['animation'][0][-1] in ['u', 'd'] else blocks_y
        elif var['animation'][0][0][-1] in ['l', 'r'] and var['animation'][0][-1] in ['u', 'd']:
            direction = f'x{var['animation'][0][-1]}'
            coef = (1, ('l', 'r'))
            blocks_ = blocks_x
        else:
            var['animation'] = [[], 0, '']
            return
    # left and right side vertical rotation and center
    elif var['animation'][0][0][-2] in ['l', 'r']:
        if var['animation'][0][0][-1] == 'm':
            direction = f'{'z' if var['animation'][0][-1] in ['u', 'd'] else 'y'}{var['animation'][0][-1]}'
            blocks_ = blocks_z if var['animation'][0][-1] in ['u', 'd'] else blocks_y
        elif var['animation'][0][0][-1] in ['l', 'r'] and var['animation'][0][-1] in ['u', 'd']:
            direction = f'z{var['animation'][0][-1]}'
            coef = (100, ('l', 'r'))
            blocks_ = blocks_z
        else:
            var['animation'] = [[], 0, '']
            return
    else:
        var['animation'] = [[], 0, '']
        return
    # rotation sound
    if var['mode'] == 'game':
        sound('click')
    # if action was recognized
    new_blocks = blocks_.copy()
    if coef:
        mult = -1 if var['animation'][0][0][-1] in ['l', 'u'] else 1
        for i in range(9):
            new_blocks[i] = str(int(blocks_[i]) + coef[0] * mult)
    var['animation'][2] = direction
    i_index = cord_to_index[var['animation'][2][0]]
    _cof = -1 if var['animation'][2][1] in ['u', 'r'] else 1
    var['animation'].append([new_blocks, i_index, _cof])

""" Objects Creation Functions """
def create_cube(_obj_name,points_offset, color_input):
    cube_color = ('red','yellow','green','blue','white','orange')
    color_output = ['gray','gray','gray','gray','gray','gray']
    for _num in color_input:
        color_output[_num -1] = cube_color[_num-1]
    colored = ((('1', '2', '3', '4'), world.colors[color_output[0]]), (('5', '6', '7', '8'), world.colors[color_output[1]]),
               (('3', '4', '8', '7'), world.colors[color_output[2]]), (('1', '2', '6', '5'), world.colors[color_output[3]]),
               (('1', '4', '8', '5'), world.colors[color_output[4]]), (('2', '3', '7', '6'), world.colors[color_output[5]]))
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
    colored = ((('1', '2', '3', '4'), ((255,255,255),(255,255,255))),)
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

""" World Class """
class World:
    def __init__(self):
        all_worlds.append(self)
        self.colors = all_colors[0]
        self.all_objects = []
        self.all_cameras = []
        self.points = {}
        self.rubik = {}
        self.points_copy = None
        self.rubik_copy = None

    def save_data(self):
        self.rubik_copy = copy.deepcopy(self.rubik)
        self.points_copy = copy.deepcopy(self.points)

    def reset(self):
        for camera_ in self.all_cameras:
            camera_.reset()
        for object_ in self.all_cameras:
            object_.reset()
        self.rubik = copy.deepcopy(self.rubik_copy)
        self.points = copy.deepcopy(self.points_copy)
        var['active'] = True
        for animation in anim:
            anim[animation] = 0


""" Camera Class """
class CameraChanger:
    def __init__(self,name,rotation=(0,0)):
        world.all_cameras.append(self)
        self.name = name
        self.init_rotation = rotation
        self.rotation = [rotation[0],rotation[1]]
        self.size = 1
        self.order = []

    def reset(self):
        self.rotation = list(self.init_rotation)
        self.size = 1

    def rotate(self,index, _add_ang):
        self.rotation[index] += _add_ang
        if self.rotation[index] > 360:
            self.rotation[index] -= 360
        elif self.rotation[index] < -360:
            self.rotation[index] += 360
        var['active'] = True

    def resize(self,add_size):
        self.size *= 1 + add_size / 100
        var['active'] = True

    def render(self):
        """calculating points position on the screen"""

        def calculate_color(_depth, _colors):
            """calculate color based on z position of an object"""
            f_colors = []
            limit = 80 * camera.size
            if _depth > limit:
                return _colors
            elif _depth < -limit:
                return int(_colors[0] / 1.5), int(_colors[1] / 1.5), int(_colors[2] / 1.5)
            for _color in _colors:
                f_colors.append(int(_color / (1 + ((_depth - limit) / -40))))
            return f_colors

        def sort(_order, condition, content):
            """sort object or polygon based on z position"""
            if _order:
                for _num in range(len(_order)):
                    if condition > _order[_num][1]:
                        return _order.insert(_num, content)
            return _order.append(content)


        self.order = []
        for _obj in world.all_objects:
            # creating colored polygons from points and sorting them
            polygons = {} ; pol_order = [] ; obj_depth = 0
            for polygon, color in _obj.polygons:
                polygons[polygon] = {'render_points': [], 'depth': 0}
                for _point in polygon:
                    # camera y rotation offset
                    radius = math.hypot(world.points[_obj.name][_point][0], world.points[_obj.name][_point][2])
                    angle = angle_calc(radius,
                                world.points[_obj.name][_point][0], world.points[_obj.name][_point][2]) - self.rotation[1]
                    cord_x = round(radius * math.sin(math.radians(angle)), 2)
                    cord_y = world.points[_obj.name][_point][1]
                    cord_z = round(radius * math.cos(math.radians(angle)), 2)
                    # camera x rotation offset and final camera cord output
                    radius = math.hypot(cord_y, cord_z)
                    angle = angle_calc(radius, cord_y, cord_z) - self.rotation[0]
                    cord_x = round(cord_x * self.size, 2)
                    cord_y = round(radius * math.sin(math.radians(angle)) * self.size, 2)
                    cord_z = round(radius * math.cos(math.radians(angle)) * self.size, 2)

                    # saving point output cords
                    mult = round(((( cord_z + 125) / 375) + 2), 2)
                    polygons[polygon]['render_points'].append((int(center[0] + cord_x * mult),
                                                               int(center[1] - cord_y * mult)))
                    # saving point depth
                    polygons[polygon]['depth'] += cord_z
                    if -50 < cord_y < 50 and -50 < cord_x < 50:
                        polygons[polygon]['depth'] += 6

                # saving object depth
                obj_depth += polygons[polygon]['depth']
                # color of the polygon calculation
                final_color = (calculate_color(polygons[polygon]['depth'] / 4, color[0]),
                               calculate_color(polygons[polygon]['depth'] / 4, color[1]))
                # in "pol_order" sorting all polygons of an object
                sort(pol_order, polygons[polygon]['depth'], (polygon, polygons[polygon]['depth'], final_color))
            # in "order" sorting object itself
            sort(self.order, obj_depth, (_obj, obj_depth, pol_order[::-1], polygons))

    def render_polygon(self):
        for obj_info in self.order[::-1]:
            if obj_info[0].name[:6] != 'button':
                for _polygon, _depth, _color in obj_info[2]:
                    if var['solid']:
                        pygame.draw.polygon(screen, _color[0], obj_info[3][_polygon]['render_points'])
                    pygame.draw.polygon(screen, _color[1], obj_info[3][_polygon]['render_points'], 3)


""" Object Class """
class ObjectChanger:
    def __init__(self, obj_name,polygons,_points):
        world.all_objects.append(self)
        self.name = obj_name
        world.points[self.name] = _points
        self.rotation = [0, 0, 0]
        self.size = 1
        self.polygons = polygons


    def reset(self):
        self.rotation = [0, 0, 0]

    def rotate(self,index, _add_ang):
        for _point in world.points[self.name]:
            radius = math.hypot(world.points[self.name][_point][index[0]],
                                world.points[self.name][_point][index[1]])
            angle = angle_calc(radius, world.points[self.name][_point][index[0]],
                               world.points[self.name][_point][index[1]]) - _add_ang
            world.points[self.name][_point][index[0]] = round(radius * math.sin(math.radians(angle)), 2)
            world.points[self.name][_point][index[1]] = round(radius * math.cos(math.radians(angle)), 2)
        self.rotation[1] += _add_ang
        var['active'] = True

    def resize(self,add_size):
        for _point in world.points[self.name]:
            for index in [0,1,2]:
                world.points[self.name][_point][index] *= round(1 + add_size / 100,2)
        self.size *= 1 + add_size / 100
        var['active'] = True


"""Objects"""
# world
all_worlds = []
world_1 = World()
world = all_worlds[0]

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

world.rubik = {# first layer (front)
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

# cameras
camera1 = CameraChanger('Camera 1',(20,45))
camera2 = CameraChanger('Camera 2',(20,45))
camera = world.all_cameras[0]

""" PyGame """

pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
clock = pygame.time.Clock()
background_color = (55, 55, 55)
screen.fill(background_color)

textures = {
    'fade'         : pygame.image.load(resource_path("textures/fade.png")).convert_alpha(),
    'cosmos'       : pygame.image.load(resource_path("textures/cosmos.jpg")).convert_alpha(),
    'black'        : pygame.image.load(resource_path("textures/black.png")).convert_alpha(),
    'menu'         : pygame.image.load(resource_path("textures/menu.png")).convert_alpha(),
    'left_button'  : pygame.image.load(resource_path("textures/left_button.png")).convert_alpha(),
    'right_button' : pygame.image.load(resource_path("textures/right_button.png")).convert_alpha(),
    'sound_on'     : pygame.image.load(resource_path("textures/sound_on.png")).convert_alpha(),
}
textures['fade'] = pygame.transform.scale(textures['fade'], (1920, 1080))
textures['black'].set_alpha(60)
sounds = {
    'click'  : pygame.mixer.Sound("textures/click.wav"),
    'select' : pygame.mixer.Sound("textures/select.wav"),
}
pygame.mixer.music.load("textures/cosmo.mp3")
pygame.mixer.music.play(-1)

clicks = {
    'menu' : pygame.Rect(0, 0, 1920, 130),
    'menu_exit' : pygame.Rect(990, 0, 110, 100),
    'menu_sound' : pygame.Rect(830, 0, 110, 100),
}

var['mode'] = 'menu'
center = [550,540]
camera.size = 0.8
mouse_cords = center
world.save_data()

""" Main Cycle """
running = True
while running:
    """ BRAIN """
    # if shuffle mode
    if var['shuffle']:
        if not var['animation'][0]:
            while True:
                button1 = random.choice(world.all_objects)
                if button1.name[:6] == 'button':
                    break
            letter1 = random.choice(['l', 'r', 'u', 'd'])
            var['animation'] = [[button1.name, letter1], 0,'']

    # objects re-render if action made
    if var['active']:
        var['active'] = False
        camera.render()

    # calculating blocks to move and the direction
    if var['animation'][0] and not var['animation'][2]:
        var['dir_check'] = ''
        rubik_calculation()

    # rotation
    if var['animation'][2]:
        rubik_rotation(var['animation'][2],*var['animation'][3])

    # start animation
    if var['mode_anim'][0] == 'start':
        if var['mode_anim'][1] < 1:
            var['mode_anim'][1] += 1
            center = [550, 540]
            camera.size = 0.8

            final_camera_rot_x = (camera.init_rotation[0] - camera.rotation[0] + 360) / 143
            final_camera_rot_y = (camera.init_rotation[1] - camera.rotation[1] + 360) / 143
            final_center_x = (960 - center[0])  / 149
            final_camera_size = (1 - camera.size)  / 150

        elif var['mode_anim'][1] > 0:
            var['mode_anim'][1] += 1
            camera.size += final_camera_size
            center[0] += final_center_x
            if var['mode_anim'][1] <= 141:
                camera.rotate(0,final_camera_rot_x)
                camera.rotate(1, final_camera_rot_y)
            else:
                camera.rotate(0, final_camera_rot_x / 3)
                camera.rotate(1, final_camera_rot_y / 3)

            if var['mode_anim'][1] > 90:
                textures['black'].set_alpha(textures['black'].get_alpha() - 1)

            if var['mode_anim'][1] > 100:
                var['shuffle'] = 'slow'

            if var['mode_anim'][1] > 150:
                var['mode'] = 'game'
                var['mode_anim'] = ['', 0]
                var['shuffle'] = ''
                center = [960, 540]
                camera.size = 1
                camera.rotation = list(camera.init_rotation)
                var['active'] = True
                textures['black'].set_alpha(60)

    """ INPUT """
    keys = pygame.key.get_pressed()
    mouse_keys = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        var['mouse_lock'] = ''

        # ways to exit
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # analytic mode
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            var['analytic'] = True if var['analytic'] == False else False
            sound('select')

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            world.reset()

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
            var['solid'] = True if var['solid'] == False else False
            sound('select')

        # game mode
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if var['mode'] == 'menu':
                var['mode'] = 'start'
                var['mode_anim'] = ['start', 0]
                var['shuffle'] = 'fast'
                var['active'] = True
            else:
                world.reset()
                var['mode'] = 'menu'
                center = [550, 540]
                camera.size = 0.8
            sound('select')


        if var['mode'] == 'game':
            if clicks['menu'].collidepoint(mouse_pos) and not (event.type == pygame.MOUSEMOTION and mouse_keys[2]):
                var['mouse_lock'] = 'menu'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and clicks['menu_exit'].collidepoint(mouse_pos):
                world.reset()
                var['mode'] = 'menu'
                center = [550, 540]
                camera.size = 0.8
                sound('select')
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and clicks['menu_sound'].collidepoint(mouse_pos):
                if var['silent_mode'] == False:
                    print('1')
                    var['silent_mode'] = True
                    pygame.mixer.pause()
                    pygame.mixer.music.pause()
                else:
                    var['silent_mode'] = False
                    pygame.mixer.unpause()
                    pygame.mixer.music.unpause()
                sound('select')


            # camera sizing with mouse
            if event.type == pygame.MOUSEWHEEL:
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

            # shuffle mode activation
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                var['shuffle'] = 'fast' if var['shuffle'] != 'fast' else ''

            # camera change
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_k:
                _index = world.all_cameras.index(camera)
                camera = world.all_cameras[_index + 1] if _index < len(world.all_cameras) - 1 else world.all_cameras[0]
                var['active'] = True

            # informating if any button was activated
            elif not var['animation'][0]:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not mouse_keys[2]:
                    new_list = []
                    for _object in camera.order:
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
                                var['dir_check'] = button_name
                                dx, dy = 0,0
                                break
                if var['dir_check']:
                    if event.type == pygame.MOUSEMOTION and mouse_keys[0]:
                        dx += event.rel[0] ; dy += event.rel[1]
                        # inversion of mirrored side
                        if   dx >  30:
                            var['animation'] = [[button_name,'r'], 0,'']
                        elif dy < -30:
                            inv_let = 'd' if button_name[-2] in ['b', 'r'] and button_name[-1] not in ['d','u'] else 'u'
                            var['animation'] = [[button_name, inv_let], 0,'']
                        elif dx < -30:
                            var['animation'] = [[button_name,'l'], 0,'']
                        elif dy >  30:
                            inv_let = 'u' if button_name[-2] in ['b', 'r'] and button_name[-1] not in ['d','u'] else 'd'
                            var['animation'] = [[button_name, inv_let], 0,'']
                    var['out_text'] = var['animation'] # for visualization

    """ OUTPUT """
    # background
    screen.blit(textures['cosmos'], (0, 0))
    screen.blit(textures['fade'], (0, 0))

    # objects output render
    camera.render_polygon()

    # start menu
    if var['mode'] == 'menu':
        font = pygame.font.Font(None, 90)
        text = font.render(f"Play", True, (255, 255, 255))
        screen.blit(text, (1500, 450))
        camera.rotate(1,1)
        camera.rotate(0, 1)
        screen.blit(textures['black'], (0, 0))

    # start animation
    if var['mode'] == 'start':
        screen.blit(textures['black'], (0, 0))

    # in-game animation
    if var['mode'] == 'game':
        basic_animation('menu', 90, 9, 3)
        # upper menu output
        if anim['menu'] > 0:
            cords = (0, -90 + anim['menu'])
            screen.blit(textures['menu'], cords)
            if not var['silent_mode']:
                screen.blit(textures['sound_on'], cords)
            if clicks['menu_sound'].collidepoint(mouse_pos):
                screen.blit(textures['left_button'], cords)
            if clicks['menu_exit'].collidepoint(mouse_pos):
                screen.blit(textures['right_button'], cords)

    # in-game info output
    if var['analytic']:
        fps = int(clock.get_fps())
        font = pygame.font.Font(None, 40)
        messages = [

        f'Fps : {fps}',
        f'State : {'active' if var['active'] else 'passive'}',
        f'last rubik rotation : {var['out_text']}'
        f'' ,
        f'Cameras : {[i.name for i in world.all_cameras]}',
        f'Camera : {camera.name}',
        f'Rotation : x {camera.rotation[0]:.0f}° y {camera.rotation[1]:.0f}°',
        f'Size : {camera.size:.2f}',
        f'Mode : {var["mode"]}',
        f'{anim['menu']} {var['mouse_lock']}']


        for num, message in enumerate(messages):
            text = font.render(message, True, (255, 255, 255))
            screen.blit(text, (15, 5 + num * 35))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()