import pygame
import math
import random
import sys, os
import copy
# class import
from json_class import Json
from timer_class import Timer

# globals
var = {'analytic' : False, 'solid' : True,
       'mouse_lock' : '', 'flag' : '',
       'motion_start' : '','shuffle' : '', 'mode' : '', 'mode_anim' : ['',0]}

anim = {'menu' : 0, 'win_fade' : 0, 'restart' : 0,}
pairs_to_cords = {(1,2) :0 , (0,2) : 1, (0,1) : 2}


""" Working Path """

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path


""" Basic Functions """

def cord_to_index(cord: str) -> (int,int):
    transfer = {'x': (1, 2), 'y': (0, 2), 'z': (0, 1)}
    return transfer[cord]

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
    if main_json.data['sound']:
        sounds[track].play()

def rubik_solved():
    for key in world.rubik:
        if world.rubik[key].rotation != cent_p.rotation:
            return False
    return True

""" Output Functions """

def ingame_info(message):
    _font = pygame.font.Font(None, 40)
    for _num, line in enumerate(message):
        _text = _font.render(line, True, (255, 255, 255))
        screen.blit(_text, (15, 5 + _num * 35))


""" Class Rubik """

class Rubik:
    blocks_x = ['112', '122', '132', '232', '332', '322', '312', '212', '222']
    blocks_y = ['121', '122', '123', '223', '323', '322', '321', '221', '222']
    blocks_z = ['211', '221', '231', '232', '233', '223', '213', '212', '222']

    def __init__(self):
        # rotation properties
        self.animation = {
            'button_name': '',
            'button_direction': '',
            'rotation_angle': 0,
            'xyz_direction': '',
            'rotation_coef': (),
            'rotation_blocks': [],}
        self.animation_copy =  self.animation.copy()
        # colors
        self.colors = self.__colors


    def reset(self):
        pass

    def twist(self) -> None:
        # rotation animation
        if not rubik.animation['rotation_coef']:
            self.__calculate_rotation()
        # rotation
        if rubik.animation['rotation_coef']:
            self.__make_rotation()

    def __calculate_rotation(self):
        """ calculates rotation, changes only self.animation"""
        coef = ()
        # side rotation
        if self.animation['button_name'][-1] in ['u', 'd'] and self.animation['button_direction'] in ['l', 'r']:
            xyz_direction = 'y'
            coef = (10, ('u', 'd'))
            blocks_ = self.blocks_y
        # front and back side vertical rotation and center
        elif self.animation['button_name'][-2] in ['f', 'b']:
            if self.animation['button_name'][-1] == 'm':
                xyz_direction = f'{'x' if self.animation['button_direction'] in ['u', 'd'] else 'y'}'
                blocks_ = self.blocks_x if self.animation['button_direction'] in ['u', 'd'] else self.blocks_y
            elif self.animation['button_name'][-1] in ['l', 'r'] and self.animation['button_direction'] in ['u', 'd']:
                xyz_direction = 'x'
                coef = (1, ('l', 'r'))
                blocks_ = self.blocks_x
            else:
                self.__animation_reset()
                return
        # left and right side vertical rotation and center
        elif self.animation['button_name'][-2] in ['l', 'r']:
            if self.animation['button_name'][-1] == 'm':
                xyz_direction = f'{'z' if self.animation['button_direction'] in ['u', 'd'] else 'y'}'
                blocks_ = self.blocks_z if self.animation['button_direction'] in ['u', 'd'] else self.blocks_y
            elif self.animation['button_name'][-1] in ['l', 'r'] and self.animation['button_direction'] in ['u', 'd']:
                xyz_direction = 'z'
                coef = (100, ('l', 'r'))
                blocks_ = self.blocks_z
            else:
                self.__animation_reset()
                return
        else:
            self.__animation_reset()
            return
        # if action was recognized
        new_blocks = blocks_.copy()
        if coef:
            mult = -1 if self.animation['button_name'][-1] in ['l', 'u'] else 1
            for i in range(9):
                new_blocks[i] = str(int(blocks_[i]) + coef[0] * mult)
        self.animation['rotation_blocks'] = new_blocks
        self.animation['rotation_index'] = cord_to_index(xyz_direction)
        self.animation['rotation_coef'] = -1 if self.animation['button_direction'] in ['u', 'r'] else 1

    def __make_rotation(self):
        _blocks, index, cof = self.animation['rotation_blocks'],self.animation['rotation_index'],self.animation['rotation_coef']
        # rotation animation
        if self.animation['rotation_angle'] < 90:
            if var['shuffle'] == 'fast':
                _add_ang = 30
            else:
                _add_ang = 10 if 10 <= self.animation['rotation_angle'] <= 70 else 2
            for _obj_location in _blocks:
                world.rubik[_obj_location].rotate( index, _add_ang * cof)
            self.animation['rotation_angle'] += _add_ang
            world.rerender()
        else:
            # rewriting position
            _blocks.pop(-1)
            off_blocks = _blocks[2:] + _blocks[:2] if self.animation['button_direction'] in ['d', 'r'] else _blocks[-2:] + _blocks[:-2]
            place_save = []
            for pl in _blocks:  place_save.append(world.rubik[pl])
            for pl in off_blocks:  world.rubik[pl] = place_save.pop(0)
            self.__animation_reset()

    def __animation_reset(self) -> None:
        self.animation = self.animation_copy.copy()

    @property
    def __colors(self) -> dict:
        """
            returns dict of lists of 2 tuples,
            with color of polygon as a first tuple and color of outlines as the second
        """
        colors = {
            'red': [(153, 0, 0)],
            'green': [(0, 102, 0)],
            'blue': [(0, 76, 153)],
            'yellow': [(204, 102, 0)],
            'orange': [(204, 204, 0)],
            'white': [(255, 229, 204)],
            'gray': [(50, 50, 50)]
        }
        for color in colors:
            colors[color].append(
                (int(colors[color][0][0] * 0.8),
                 int(colors[color][0][1] * 0.8),
                 int(colors[color][0][2] * 0.8)))
        return colors



rubik = Rubik()

""" Objects Creation Functions """

def create_cube(_obj_name,points_offset, color_input):
    cube_color = ('red','yellow','green','blue','white','orange')
    color_output = ['gray','gray','gray','gray','gray','gray']
    for _num in color_input:
        color_output[_num -1] = cube_color[_num-1]
    colored = ((('1', '2', '3', '4'), rubik.colors[color_output[0]]), (('5', '6', '7', '8'), rubik.colors[color_output[1]]),
               (('3', '4', '8', '7'), rubik.colors[color_output[2]]), (('1', '2', '6', '5'), rubik.colors[color_output[3]]),
               (('1', '4', '8', '5'), rubik.colors[color_output[4]]), (('2', '3', '7', '6'), rubik.colors[color_output[5]]))
    cube_points = {
        '1': [ 33.0, 33.0, 33.0], '2': [ 33.0,-33.0, 33.0],
        '3': [-33.0,-33.0, 33.0], '4': [-33.0, 33.0, 33.0],
        '5': [ 33.0, 33.0,-33.0], '6': [ 33.0,-33.0,-33.0],
        '7': [-33.0,-33.0,-33.0], '8': [-33.0, 33.0,-33.0],
    }
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

""" Class Json """

# object
main_json = Json("MiRubik","MiRubik_data.json", {'sound' : True, 'best_time' : [None,None,None] })

""" Class Timer """

# timer
timer = Timer()

""" World Class """

class World:
    def __init__(self):
        self.all_objects = []
        self.rubik = {}
        self.rubik_copy = None
        self.solved = False
        # rerendering screen
        self.rerender_bool = False

    def rerender(self):
        self.rerender_bool = True

    def save_data(self):
        self.rubik_copy = copy.deepcopy(self.rubik)

    def reset(self):
        camera.reset()
        for object_ in self.all_objects:
            object_.reset()
        self.rubik = copy.deepcopy(self.rubik_copy)
        for animation in anim:
            anim[animation] = 0
        self.rerender()

# world
world = World()

""" Camera Class """

class CameraChanger:
    """ Calculating all points` position on the screen and rendering objects in order """

    def __init__(self, name: str, rotation: tuple = (0,0)):
        # main properties
        self.name: str = name
        self.rotation: list = list(rotation)
        self.size: float = 1
        # all objects and their`s info order (for rendering)
        self.order: list = []
        # save start rotation
        self.init_rotation: tuple = rotation

    def reset(self) -> None:
        """ full camera reset """
        self.rotation = list(self.init_rotation)
        self.size = 1
        world.rerender()

    def rotate(self,index: int, add_angle: int | float) -> None:
        """ rotate the camera """
        self.rotation[index] += add_angle
        if self.rotation[index] > 360:
            self.rotation[index] -= 360
        elif self.rotation[index] < -360:
            self.rotation[index] += 360
        world.rerender()

    def resize(self,add_size):
        """ resize the camera """
        if (self.size < 2 or add_size < 0) and (self.size > 0.3 or add_size > 0):
            self.size *= 1 + add_size / 20
            world.rerender()


    def calculate(self):
        """
            1) calculating points position on the screen
            2) creating polygon presets, including polygon depth,color and points
            3) saving all object`s polygons in order
            4) saving object in self.order for rendering later
        """
        def calculate_color(_depth, _colors):
            """calculate color based on z position of an object"""
            f_colors = []
            limit = 80 * self.size
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
        for obj in world.all_objects:
            # creating colored polygons from points and sorting them
            polygons = {} ; pol_order = [] ; obj_depth = 0
            for polygon, color in obj.polygons:
                polygons[polygon] = {'render_points': [], 'depth': 0}
                for _point in polygon:
                    # camera y rotation offset
                    radius = math.hypot(obj.points[_point][0], obj.points[_point][2])
                    angle = angle_calc(radius,
                                obj.points[_point][0], obj.points[_point][2]) - self.rotation[1]
                    cord_x = round(radius * math.sin(math.radians(angle)), 2)
                    cord_y = obj.points[_point][1]
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
            sort(self.order, obj_depth, (obj, obj_depth, pol_order[::-1], polygons))

    def render(self):
        """ rendering all objects` polygons relying on self.order """
        for obj_info in self.order[::-1]:
            if obj_info[0].name[:6] != 'button':
                for _polygon, _depth, _color in obj_info[2]:
                    if var['solid']:
                        pygame.draw.polygon(screen, _color[0], obj_info[3][_polygon]['render_points'])
                    pygame.draw.polygon(screen, _color[1], obj_info[3][_polygon]['render_points'], 3)


# cameras
camera = CameraChanger('Camera', (20,45))


""" Object Class """

class ObjectChanger:
    def __init__(self, name: str, polygons: tuple[tuple,tuple], points: dict[str,list]):
        # add object to all objects
        world.all_objects.append(self)
        # main properties
        self.name: str = name
        self.points: dict[str,list] = points
        self.rotation: list = [0, 0, 0]
        self.polygons = polygons
        # saving start points position
        self.__points_copy = copy.deepcopy(self.points)

    def reset(self) -> None:
        """ reset the object """
        self.rotation = [0, 0, 0]
        self.points = copy.deepcopy(self.__points_copy)
        world.rerender()

    def rotate(self,index, add_angle: int | float) -> None:
        """ rotate object """
        for _point in self.points:
            radius = math.hypot(self.points[_point][index[0]],
                                self.points[_point][index[1]])
            angle = angle_calc(radius, self.points[_point][index[0]],
                               self.points[_point][index[1]]) - add_angle
            self.points[_point][index[0]] = round(radius * math.sin(math.radians(angle)), 2)
            self.points[_point][index[1]] = round(radius * math.cos(math.radians(angle)), 2)
        self.rotation[pairs_to_cords[index]] -= add_angle
        if self.rotation[pairs_to_cords[index]] >= 360:
            self.rotation[pairs_to_cords[index]] -= 360
        if self.rotation[pairs_to_cords[index]] < 0:
            self.rotation[pairs_to_cords[index]] += 360
        world.rerender()

# creating ObjectChanger objects

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

""" Rubik starting state """

rubik_list = [# first layer (front)54
        corner_lfu,   cut_fu,   corner_rfu,
        cut_lf    ,   side_f,   cut_rf    ,
        corner_lfd,   cut_fd,   corner_rfd,
        # second layer (mid)
        cut_lu    ,   side_u,   cut_ru    ,
        side_l    ,   cent_p,   side_r    ,
        cut_ld    ,   side_d,   cut_rd    ,
        # third layer (back)
        corner_lbu,   cut_bu,   corner_rbu,
        cut_lb    ,   side_b,   cut_rb    ,
        corner_lbd,   cut_bd,   corner_rbd]

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

""" PyGame """

pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
clock = pygame.time.Clock()
background_color = (55, 55, 55)
screen.fill(background_color)

# Textures

textures = {
    'fade'         : pygame.image.load(resource_path("textures/fade.png")).convert_alpha(),
    'win_fade'     : pygame.image.load(resource_path("textures/win_fade.png")).convert_alpha(),
    'background'   : pygame.image.load(resource_path("textures/lake.jpg")).convert_alpha(),
    'black'        : pygame.image.load(resource_path("textures/black.png")).convert_alpha(),
    'menu'         : pygame.image.load(resource_path("textures/menu.png")).convert_alpha(),
    'left_button'  : pygame.image.load(resource_path("textures/left_button.png")).convert_alpha(),
    'right_button' : pygame.image.load(resource_path("textures/right_button.png")).convert_alpha(),
    'corner_button': pygame.image.load(resource_path("textures/corner_button.png")).convert_alpha(),
    'sound_on'     : pygame.image.load(resource_path("textures/sound_on.png")).convert_alpha(),
    'sound'        : pygame.image.load(resource_path("textures/sound.png")).convert_alpha(),
}
textures['background'] = pygame.transform.scale(textures['background'], (1920, 1080))
textures['fade'] = pygame.transform.scale(textures['fade'], (1920, 1080))
textures['win_fade'] = pygame.transform.scale(textures['win_fade'], (1920, 1080))
textures['black'].set_alpha(60)
textures['win_fade'].set_alpha(60)

# Sounds

sounds = {
    'click'  : pygame.mixer.Sound("sounds/click.wav"),
    'select' : pygame.mixer.Sound("sounds/select.wav"),
}
pygame.mixer.music.load("sounds/cosmo.mp3")
pygame.mixer.music.play(-1)
# if silent mode is on
if not main_json.data['sound']:
    pygame.mixer.music.pause()

# Clickable Buttons

clicks = {
    # top menu
    'menu' : pygame.Rect(0, 0, 1920, 130),
    'menu_exit' : pygame.Rect(990, 0, 110, 100),
    'menu_sound' : pygame.Rect(15, 0, 110, 100),
    'menu_restart' : pygame.Rect(830, 0, 110, 100),
    # main menu
    'play' : pygame.Rect(1300, 350, 300, 130),
    'inspect' : pygame.Rect(1315, 600, 300, 130),
}

""" Starting Variables """

var['mode'] = 'menu'
center = [550,540]
camera.size = 0.8
mouse_cords = center
world.save_data()

""" Main Cycle """

running = True
while running:

    """ BRAIN """

    # objects re-render if action made
    if world.rerender_bool:
        world.rerender_bool = False
        camera.calculate()

    # timer update
    world.solved = rubik_solved()
    timer.update(pygame.time.get_ticks())
    # switches
    if world.solved != var['flag']:
        var['flag'] = rubik_solved()
        if world.solved and var['mode'] == 'game' and var['game_type'] == 'play':
            timer.stop()
            for ind, best_time in enumerate(main_json.data['best_time']):
                if timer. real_time < best_time and timer. real_time not in main_json.data['best_time']:
                    main_json.data['best_time'].insert(ind, timer.time)
                    main_json.data['best_time'].pop(-1)
                    break


    # rubik reshuffling
    if anim['restart']:
        if anim['restart'] == 200:
            final_camera_rot_x = (camera.init_rotation[0] - camera.rotation[0] + 360) / 200
            final_camera_rot_y = (camera.init_rotation[1] - camera.rotation[1] + 360) / 200
        anim['restart'] -= 1
        var['shuffle'] = 'fast'
        camera.rotate(0, final_camera_rot_x)
        camera.rotate(1, final_camera_rot_y)
        timer.reset()
        if anim['restart'] == 1:
            anim['restart'] = 0
            var['shuffle'] = ''
            timer.start(pygame.time.get_ticks())

    # if shuffle mode
    if var['shuffle']:
        if not rubik.animation['button_name']:
            while True:
                random_button = random.choice(world.all_objects)
                if random_button.name[:6] == 'button':
                    break
            rubik.animation['button_name'] = random_button.name
            rubik.animation['button_direction'] = random.choice(['l', 'r', 'u', 'd'])


    # twist rubik one time, if instructions given
    if rubik.animation['button_name']:
        rubik.twist()


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
                if var['game_type'] == 'play':
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
                # start timer if game type play
                if var['game_type'] == 'play':
                    timer.start(pygame.time.get_ticks())

    if var['mode'] == 'menu':
        camera.rotate(1, 1)
        camera.rotate(0, 1)

    """ INPUT """

    mouse_keys = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        var['mouse_lock'] = ''

        # ways to exit
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # analytic mode (f3)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            var['analytic'] = True if var['analytic'] == False else False
            sound('select')

        # not solid mode (f4)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
            var['solid'] = True if var['solid'] == False else False
            sound('select')

        # silent mode
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and clicks['menu_sound'].collidepoint(mouse_pos):
            # updating the value
            main_json.data['sound'] = not main_json.data['sound']
            main_json.update_data()
            # turning on/off silent mode
            pygame.mixer.music.unpause() if main_json.data['sound'] else pygame.mixer.music.pause()


        match var['mode']:

            case 'menu':

                # game mode (space)
                if event.type == pygame.MOUSEBUTTONDOWN and clicks['play'].collidepoint(mouse_pos):
                    # start the game
                    var['mode'] = 'start'
                    var['game_type'] = 'play'
                    var['mode_anim'] = ['start', 0]
                    var['shuffle'] = 'fast'
                    var['active'] = True
                    timer.reset()
                    sound('select')

                # game mode no shuffle (c)
                elif event.type == pygame.MOUSEBUTTONDOWN and clicks['inspect'].collidepoint(mouse_pos):
                    # start the game
                    var['mode'] = 'start'
                    var['game_type'] = 'inspect'
                    var['mode_anim'] = ['start', 0]
                    var['active'] = True
                    timer.reset()
                    sound('select')


            case 'game':

                if clicks['menu'].collidepoint(mouse_pos) and not (event.type == pygame.MOUSEMOTION and mouse_keys[2]):
                    var['mouse_lock'] = 'menu'

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and clicks['menu_exit'].collidepoint(mouse_pos):
                    world.reset()
                    var['mode'] = 'menu'
                    center = [550, 540]
                    camera.size = 0.8
                    var['game_type'] = ''
                    timer.stop()
                    sound('select')

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and \
                clicks['menu_restart'].collidepoint(mouse_pos) and not anim['restart']:
                    anim['restart'] = 200
                    var['game_type'] = 'play'
                    sound('select')


                # camera sizing with mouse
                if event.type == pygame.MOUSEWHEEL:
                    camera.resize(event.y)
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


                # shuffle mode activation (for testing)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    var['shuffle'] = 'fast' if var['shuffle'] != 'fast' else ''


                # informating if any button was activated
                elif not rubik.animation['button_name']:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not mouse_keys[2]:
                        new_list = []
                        for _object in camera.order:
                            # if button`s depth < 0 mask won`t work
                            if _object[0].name[:6] == 'button' and _object[1] > 0:
                                for point in list(_object[3][('1', '2', '3', '4')]['render_points']):
                                    new_list.append((point[0], point[1]))
                                button_name = _object[0].name
                                # mask creation
                                surf = pygame.Surface((1920, 1080), pygame.SRCALPHA)
                                pygame.draw.polygon(surf, (255, 255, 255), new_list)
                                mask = pygame.mask.from_surface(surf)
                                # check if click was in the polygon
                                if mask.get_at((pygame.mouse.get_pos())):
                                    var['motion_start'] = button_name
                                    dx, dy = 0,0
                                    break
                    # if after button press action in any direction was made
                    if var['motion_start']:
                        if event.type == pygame.MOUSEMOTION and mouse_keys[0]:
                            dx += event.rel[0] ; dy += event.rel[1]
                            # inversion of mirrored side
                            if   dx >  30:
                                rubik.animation['button_name'] = var['motion_start']
                                rubik.animation['button_direction'] = 'r'

                            elif dy < -30:
                                inv_let = 'd' if var['motion_start'][-2] in ['b', 'r'] and \
                                                 var['motion_start'][-1] not in ['d','u'] else 'u'
                                rubik.animation['button_name'] = var['motion_start']
                                rubik.animation['button_direction'] = inv_let
                            elif dx < -30:
                                rubik.animation['button_name'] = var['motion_start']
                                rubik.animation['button_direction'] = 'l'
                            elif dy >  30:
                                inv_let = 'u' if var['motion_start'][-2] in ['b', 'r'] and \
                                                 var['motion_start'][-1] not in ['d','u'] else 'd'
                                rubik.animation['button_name'] = var['motion_start']
                                rubik.animation['button_direction'] = inv_let
                            # sounds
                            if rubik.animation['button_name']:
                                if var['mode'] == 'game' and var['shuffle'] != 'fast' and main_json.data['sound']:
                                    sound('click')
                                # turning off the switch
                                var['motion_start'] = ''

    """ OUTPUT """

    # background
    screen.blit(textures['background'], (0, 0))
    screen.blit(textures['fade'], (0, 0))

    # objects output render
    camera.render()

    # depending on current mode
    match var['mode']:

        # start menu
        case 'menu':
            # main menu buttons
            font = pygame.font.Font(resource_path("textures/cosmo.otf"), 170)
            text = font.render("play", True, (255, 255, 255))
            screen.blit(text, (1300, 350))
            font = pygame.font.Font(resource_path("textures/cosmo.otf"), 80)
            text = font.render("INSPECT", True, (255, 255, 255))
            screen.blit(text, (1315, 600))
            screen.blit(textures['black'], (0, 0))

            # top 3 best runs
            font = pygame.font.Font("textures/sans.ttf", 40)
            if main_json.data['best_time'][0]:
                text = font.render(f"1. {main_json.data['best_time'][0]}", True, (255, 255, 255))
                screen.blit(text, (1650, 15))
            if main_json.data['best_time'][1]:
                text = font.render(f"2. {main_json.data['best_time'][1]}", True, (255, 255, 255))
                screen.blit(text, (1650, 55))
            if main_json.data['best_time'][2]:
                text = font.render(f"3. {main_json.data['best_time'][2]}", True, (255, 255, 255))
                screen.blit(text, (1650, 95))

            # sound on/of
            screen.blit(textures['sound'], (15, 0))
            if main_json.data['sound']:
                screen.blit(textures['sound_on'], (15,0))
            if clicks['menu_sound'].collidepoint(mouse_pos):
                screen.blit(textures['corner_button'], (15,0))


        # start animation
        case 'start':
            screen.blit(textures['black'], (0, 0))


        # in-game animation
        case 'game':
            # upper menu output
            if not world.solved:
                basic_animation('menu', 90, 9, 3)
            if anim['menu'] > 0:
                cords = (0, -90 + anim['menu'])
                screen.blit(textures['menu'], cords)
                if main_json.data['sound']:
                    screen.blit(textures['sound_on'], cords)
                if clicks['menu_sound'].collidepoint(mouse_pos):
                    screen.blit(textures['corner_button'], cords)
                if clicks['menu_restart'].collidepoint(mouse_pos):
                    screen.blit(textures['left_button'], cords)
                if clicks['menu_exit'].collidepoint(mouse_pos):
                    screen.blit(textures['right_button'], cords)
                font = pygame.font.Font(None, 80)
                text = font.render(timer.time, True, (255, 255, 255))
                screen.blit(text, (cords[0] + 1650, cords[1] + 25))

            # if rubik is solved
            if world.solved:
                if anim['menu'] < 90:
                    anim['menu'] += 5
                if anim['win_fade'] < 90:
                    anim['win_fade'] += 5
                textures['win_fade'].set_alpha(anim['win_fade'])
                screen.blit(textures['win_fade'], (0, 0))
            elif anim['win_fade'] > 0:
                textures['win_fade'].set_alpha(anim['win_fade'])
                screen.blit(textures['win_fade'], (0, 0))
                anim['win_fade'] -= 5


    # in-game info output
    if var['analytic']:

        ingame_info([
            f'Fps : {int(clock.get_fps())}',
            f'State : {'active' if var['active'] else 'passive'}',
            f'last rubik rotation : {rubik.animation}',
            f'Camera : {camera.name}',
            f'Rotation : x {camera.rotation[0]:.0f}° y {camera.rotation[1]:.0f}°',
            f'Size : {camera.size:.2f}',
            f'Mode : {var["mode"]}',
            f'Top menu anim. :{anim['menu']} {var['mouse_lock']}',
            f'Timer : {timer.time}',
            f'Front side rotation : {side_f.rotation}',
            f'Center rotation : {cent_p.rotation}',
        ])


    pygame.display.flip()
    clock.tick(60)
pygame.quit()