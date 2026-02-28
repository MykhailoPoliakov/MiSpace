import math
import copy
import random

""" Class Element """

class Element:
    """
    Creates element with it`s points and colored polygons , element can be rotated and reset

    Attributes:
        self.name: str - object`s name
        self.polygons: tuple[polygon: tuple, color: tuple] - object`s polygons and theirs colors
        self.points: dict[ point name: str, xyz cords: list] - object`s points
        self.rotation: list[x,y,z] - object`s rotation angle
        self.visibility: bool - if object will be visible on render
    Methods:
        self.reset()
            resets element to starting position
        self.rotate( index: int , add_angle: int|float )
            rotates element on cord (0 = x,1 = y, 2 = z) by add_angle degree
    Args:
        name (str) : object`s name
        polygons (tuple[polygon: tuple, color: tuple]) : object`s polygons and theirs colors
        points (dict[ point name: str, xyz cords: list]) : object`s points
        visibility (bool) : if object will be visible on render
    """
    invert_index: dict = { 0 : (1, 2), 1 : (0, 2), 2 : (0, 1)}

    def __init__(self, name: str, polygons: tuple[tuple,tuple], points: dict[str,list], visibility: bool):
        # main properties
        self.name: str = name
        self.points: dict[str,list] = points
        self.rotation: list = [0, 0, 0]
        self.polygons = polygons
        self.visibility: bool = visibility
        # saving start points position
        self.__points_copy = copy.deepcopy(self.points)

    def reset(self) -> None:
        """ reset the object """
        self.rotation = [0, 0, 0]
        self.points = copy.deepcopy(self.__points_copy)

    def rotate(self, index: int, add_angle: int | float) -> None:
        """ rotate object """
        def angle_calc(_radius, cord_0, cord_1):
            """ get angle of the point to the center """
            _angle = math.degrees(math.acos( cord_1 / _radius )) if _radius != 0 else 0
            return 360 - _angle if cord_0 < 0 else _angle

        # inverted index
        inv_index: tuple = self.invert_index[index]
        # for all object`s points
        for _point in self.points:
            # get radius
            radius = math.hypot(self.points[_point][inv_index[0]], self.points[_point][inv_index[1]])
            # get angle
            angle = angle_calc(radius, self.points[_point][inv_index[0]], self.points[_point][inv_index[1]]) - add_angle
            # update points dictionary
            self.points[_point][inv_index[0]] = round(radius * math.sin(math.radians(angle)), 2)
            self.points[_point][inv_index[1]] = round(radius * math.cos(math.radians(angle)), 2)

        # update object`s rotation angle
        self.rotation[index] -= add_angle
        if self.rotation[index] >= 360:
            self.rotation[index] -= 360
        if self.rotation[index] < 0:
            self.rotation[index] += 360


""" Class Rubik """

class Rubik:
    """
    something
    """
    blocks_x = ('112', '122', '132', '232', '332', '322', '312', '212', '222')
    blocks_y = ('121', '122', '123', '223', '323', '322', '321', '221', '222')
    blocks_z = ('211', '221', '231', '232', '233', '223', '213', '212', '222')

    def __init__(self):
        # rotation properties
        self.animation: dict = {
            'button_name': '',
            'button_direction': '',
            'rotation_angle': 0,
            'xyz_direction': '',
            'rotation_coef': (),
            'rotation_blocks': [],}
        self.__animation_copy: dict =  self.animation.copy()
        # colors
        self.__colors = self.__create_colors()
        # elements
        self.elements: dict = {}
        self.__create_elements_cubes()
        self.__create_elements_buttons()
        # rubik`s state
        self.state: dict = {
            # first layer (front)
            '111': 'corner_lfu', '112': 'cut_fu'  , '113': 'corner_rfu',
            '121': 'cut_lf'    , '122': 'side_f'  , '123': 'cut_rf'    ,
            '131': 'corner_lfd', '132': 'cut_fd'  , '133': 'corner_rfd',
            # second layer (mid)
            '211': 'cut_lu'    , '212': 'side_u'  , '213': 'cut_ru'    ,
            '221': 'side_l'    , '222': 'cent_p'  , '223': 'side_r'    ,
            '231': 'cut_ld'    , '232': 'side_d'  , '233': 'cut_rd'    ,
            # third layer (back)
            '311': 'corner_lbu', '312': 'cut_bu'  , '313': 'corner_rbu',
            '321': 'cut_lb'    , '322': 'side_b'  , '323': 'cut_rb'    ,
            '331': 'corner_lbd', '332': 'cut_bd'  , '333': 'corner_rbd',
        }
        self.__state_copy = copy.deepcopy(self.state)
        # solved or not
        self.solved: bool = False
        # shuffling the rubik
        self.shuffle_val: str = ''
        # re-rendering bool
        self.rerender_bool: bool = False

    def shuffle(self):
        """ shuffle the rubik """
        self.animation['button_name'] = random.choice(list(self.elements.values())[-20:]).name
        self.animation['button_direction'] = random.choice(['l', 'r', 'u', 'd'])

    def check_solved(self):
        for place in self.state:
            if self.elements[ self.state[ place ] ].rotation != self.elements[ 'cent_p' ].rotation:
                return False
        return True

    def reset(self):
        for element in self.elements:
            self.elements[element].reset()
        self.state = copy.deepcopy(self.__state_copy)

    def twist(self) -> None:
        """ makes one rotation of the rubik`s cube """
        # rotation animation
        if not self.animation['rotation_coef']:
            self.__calculate_rotation()
        # rotation
        if self.animation['rotation_coef']:
            self.__make_rotation()

    def __animation_reset(self) -> None:
        self.animation = self.__animation_copy.copy()

    def __calculate_rotation(self):
        """ calculates rotation, changes only self.animation"""
        def cord_to_index(cord: str) -> (int, int):
            transfer = {'x': 0, 'y': 1, 'z': 2}
            return transfer[cord]

        coef = ()
        # side rotation
        if self.animation['button_name'][-1] in ['u', 'd'] and self.animation['button_direction'] in ['l', 'r']:
            xyz_direction = 'y'
            coef = (10, ('u', 'd'))
            blocks = self.blocks_y
        # front and back side vertical rotation and center
        elif self.animation['button_name'][-2] in ['f', 'b']:
            if self.animation['button_name'][-1] == 'm':
                xyz_direction = f'{'x' if self.animation['button_direction'] in ['u', 'd'] else 'y'}'
                blocks = self.blocks_x if self.animation['button_direction'] in ['u', 'd'] else self.blocks_y
            elif self.animation['button_name'][-1] in ['l', 'r'] and self.animation['button_direction'] in ['u', 'd']:
                xyz_direction = 'x'
                coef = (1, ('l', 'r'))
                blocks = self.blocks_x
            else:
                self.__animation_reset()
                return
        # left and right side vertical rotation and center
        elif self.animation['button_name'][-2] in ['l', 'r']:
            if self.animation['button_name'][-1] == 'm':
                xyz_direction = f'{'z' if self.animation['button_direction'] in ['u', 'd'] else 'y'}'
                blocks = self.blocks_z if self.animation['button_direction'] in ['u', 'd'] else self.blocks_y
            elif self.animation['button_name'][-1] in ['l', 'r'] and self.animation['button_direction'] in ['u', 'd']:
                xyz_direction = 'z'
                coef = (100, ('l', 'r'))
                blocks = self.blocks_z
            else:
                self.__animation_reset()
                return
        else:
            self.__animation_reset()
            return
        # if action was recognized
        new_blocks = list(blocks)
        if coef:
            mult = -1 if self.animation['button_name'][-1] in ['l', 'u'] else 1
            for i in range(9):
                new_blocks[i] = str(int(blocks[i]) + coef[0] * mult)
        self.animation['rotation_blocks'] = new_blocks
        self.animation['rotation_index'] = cord_to_index(xyz_direction)
        self.animation['rotation_coef'] = -1 if self.animation['button_direction'] in ['u', 'r'] else 1

    def __make_rotation(self):
        _blocks, index, cof = self.animation['rotation_blocks'],self.animation['rotation_index'],self.animation['rotation_coef']
        # rotation animation
        if self.animation['rotation_angle'] < 90:
            if self.shuffle_val == 'fast':
                _add_ang = 30
            else:
                _add_ang = 10 if 10 <= self.animation['rotation_angle'] <= 70 else 2
            for obj_location in _blocks:
                self.elements[self.state[obj_location]].rotate( index, _add_ang * cof)
            self.animation['rotation_angle'] += _add_ang
            self.rerender_bool = True
        else:
            # rewriting position
            _blocks.pop(-1)
            off_blocks = _blocks[2:] + _blocks[:2] if self.animation['button_direction'] in ['d', 'r'] else _blocks[-2:] + _blocks[:-2]
            place_save = []
            for pl in _blocks:  place_save.append(self.state[pl])
            for pl in off_blocks:  self.state[pl] = place_save.pop(0)
            self.__animation_reset()


    @staticmethod
    def __create_colors() -> dict:
        """
            returns dict of lists of 2 tuples,
            with color of polygon as a first tuple and color of outlines as the second
        """
        colors: dict = {
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

    def __create_elements_cubes(self) -> None:
        """ Creates cube parts of class Element

            changes: updates self.elements (adds cube parts) """
        def create_cube(_obj_name, points_offset, color_input):
            """ helps to create cube """
            cube_color = ('red', 'yellow', 'green', 'blue', 'white', 'orange')
            color_output = ['gray', 'gray', 'gray', 'gray', 'gray', 'gray']
            for _num in color_input:
                color_output[_num - 1] = cube_color[_num - 1]
            colored = ((('1', '2', '3', '4'), self.__colors[color_output[0]]),
                       (('5', '6', '7', '8'), self.__colors[color_output[1]]),
                       (('3', '4', '8', '7'), self.__colors[color_output[2]]),
                       (('1', '2', '6', '5'), self.__colors[color_output[3]]),
                       (('1', '4', '8', '5'), self.__colors[color_output[4]]),
                       (('2', '3', '7', '6'), self.__colors[color_output[5]]))
            cube_points = {
                '1': [33.0, 33.0, 33.0], '2': [33.0, -33.0, 33.0],
                '3': [-33.0, -33.0, 33.0], '4': [-33.0, 33.0, 33.0],
                '5': [33.0, 33.0, -33.0], '6': [33.0, -33.0, -33.0],
                '7': [-33.0, -33.0, -33.0], '8': [-33.0, 33.0, -33.0],
            }
            for _point in cube_points:
                cube_points[_point][0] += points_offset[0]
                cube_points[_point][1] += points_offset[1]
                cube_points[_point][2] += points_offset[2]
            visibility = True
            return [_obj_name, colored, cube_points, visibility]

        # creating ObjectChanger objects
        self.elements.update({
            # FRONT
            # upper line
            'corner_lfu': Element(*create_cube('corner_lfu', (-66, 66, 66), (1, 3, 5))),
            'cut_fu': Element(*create_cube('cut_fu', (0, 66, 66), (1, 5))),
            'corner_rfu': Element(*create_cube('corner_rfu', (66, 66, 66), (1, 4, 5))),
            # middle line
            'cut_lf': Element(*create_cube('cut_lf', (-66, 0, 66), (3, 1))),
            'side_f': Element(*create_cube('side_f', (0, 0, 66), (1,))),
            'cut_rf': Element(*create_cube('cut_rf', (66, 0, 66), (4, 1))),
            # down line
            'corner_lfd': Element(*create_cube('corner_lfd', (-66, -66, 66), (1, 3, 6))),
            'cut_fd': Element(*create_cube('cut_fd', (0, -66, 66), (1, 6))),
            'corner_rfd': Element(*create_cube('corner_rfd', (66, -66, 66), (1, 4, 6))),

            # MIDDLE
            # upper line
            'cut_lu': Element(*create_cube('cut_lu', (-66, 66, 0), (3, 5))),
            'side_u': Element(*create_cube('side_u', (0, 66, 0), (5,))),
            'cut_ru': Element(*create_cube('cut_ru', (66, 66, 0), (4, 5))),
            # middle line
            'side_l': Element(*create_cube('side_l', (-66, 0, 0), (3,))),
            'cent_p': Element(*create_cube('cent_p', (0, 0, 0), ())),
            'side_r': Element(*create_cube('side_r', (66, 0, 0), (4,))),
            # down line
            'cut_ld': Element(*create_cube('cut_ld', (-66, -66, 0), (3, 6))),
            'side_d': Element(*create_cube('side_d', (0, -66, 0), (6,))),
            'cut_rd': Element(*create_cube('cut_rd', (66, -66, 0), (4, 6))),

            # BACK
            # upper line
            'corner_lbu': Element(*create_cube('corner_lbu', (-66, 66, -66), (2, 3, 5))),
            'cut_bu': Element(*create_cube('cut_bu', (0, 66, -66), (2, 5))),
            'corner_rbu': Element(*create_cube('corner_rbu', (66, 66, -66), (2, 4, 5))),
            # middle line
            'cut_lb': Element(*create_cube('cut_lb', (-66, 0, -66), (3, 2))),
            'side_b': Element(*create_cube('side_b', (0, 0, -66), (2,))),
            'cut_rb': Element(*create_cube('cut_rb', (66, 0, -66), (4, 2))),
            # down line
            'corner_lbd': Element(*create_cube('corner_lbd', (-66, -66, -66), (2, 3, 6))),
            'cut_bd': Element(*create_cube('cut_bd', (0, -66, -66), (2, 6))),
            'corner_rbd': Element(*create_cube('corner_rbd', (66, -66, -66), (2, 4, 6))),
        })

    def __create_elements_buttons(self) -> None:
        """ Creates cube buttons of class Element

            changes: updates self.elements (adds buttons) """
        def create_button(_obj_name, points_offset, direction):
            """ helps to create button """
            colored = ((('1', '2', '3', '4'), ((255, 255, 255), (255, 255, 255))),)
            cof = -1 if direction in ['b', 'l', 'd'] else 1
            if direction in ['f', 'b']:
                _points = {'1': [33.0, 33.0, 0], '2': [33.0, -33.0, 0],
                           '3': [-33.0, -33.0, 0], '4': [-33.0, 33.0, 0], }
                index = (0, 1, 2)
            elif direction in ['l', 'r']:
                _points = {'1': [0, 33.0, 33.0], '2': [0, -33.0, 33.0],
                           '3': [0, -33.0, -33.0], '4': [0, 33.0, -33.0], }
                index = (1, 2, 0)
            elif direction in ['u', 'd']:
                _points = {'1': [33.0, 0, 33.0], '2': [33.0, 0, -33.0],
                           '3': [-33.0, 0, -33.0], '4': [-33.0, 0, 33.0], }
                index = (2, 0, 1)
            for _point in colored[0][0]:
                _points[_point][index[0]] += points_offset[0] * cof
                _points[_point][index[1]] += points_offset[1] * cof
                _points[_point][index[2]] += 100 * cof
            visibility = False
            return [_obj_name, colored, _points, visibility]
        # buttons
        letter_list = (['u', 'l', 'd', 'r'], ['l', 'd', 'r', 'u'], ['d', 'r', 'u', 'l'], ['r', 'u', 'l', 'd'])
        for _index, side in enumerate(['f', 'r', 'b', 'l']):
            letter = letter_list[_index]
            self.elements.update({
                f'button_{side}m': Element(*create_button(f'button_{side}m', (0, 0), side)),
                f'button_{side}{letter[0]}': Element(*create_button(f'button_{side}{letter[0]}', (0, 66), side)),
                f'button_{side}{letter[1]}': Element(*create_button(f'button_{side}{letter[1]}', (-66, 0), side)),
                f'button_{side}{letter[2]}': Element(*create_button(f'button_{side}{letter[2]}', (0, -66), side)),
                f'button_{side}{letter[3]}': Element(*create_button(f'button_{side}{letter[3]}', (66, 0), side)),
            })

