import copy
import random

# local imports
from obj_converter_class import ObjConverter
from element_class import Element


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
        # converter
        self.converter = ObjConverter("assets/models/low_rubik.obj", self.__colors)
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
            'orange': [(204, 102, 0)],
            'yellow': [(204, 204, 0)],
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
        """
        Creates cube parts of class Element
        Changes: updates self.elements (adds cube parts)
        """
        cube_color = ( 'red', 'orange' , 'blue', 'green', 'white', 'yellow')
        def create_cube(_obj_name, points_offset, color_input):
            """ Helps to create cube """
            # color
            colored_polygons: list = copy.deepcopy(self.converter.colored_polygons)

            # list of colors cube would have
            exact_colors = []
            for num in color_input:
                exact_colors.append(cube_color[num - 1])

            # make inside polygons black
            for index, colored_polygon in enumerate(colored_polygons,1):
                if colored_polygon[1] not in exact_colors:
                    colored_polygon[1] = self.__colors['gray']
                else:
                    colored_polygon[1] = self.__colors[colored_polygon[1]]

            # adding offset
            cube_points = copy.deepcopy(self.converter.points)
            for index, point in enumerate(self.converter.points):
                cube_points[index][0] += points_offset[0]
                cube_points[index][1] += points_offset[1]
                cube_points[index][2] += points_offset[2]
            # visibility
            visibility = True

            return [_obj_name, colored_polygons, cube_points, visibility]

        # creating Element objects (Rubik parts)
        self.elements.update({
            # FRONT
            # upper line
            'corner_lfu': Element(*create_cube('corner_lfu', (-66, 66, 66), (1, 3, 5))),
            'cut_fu'    : Element(*create_cube('cut_fu', (0, 66, 66), (1, 5))),
            'corner_rfu': Element(*create_cube('corner_rfu', (66, 66, 66), (1, 4, 5))),
            # middle line

            'cut_lf'    : Element(*create_cube('cut_lf', (-66, 0, 66), (3, 1))),
            'side_f'    : Element(*create_cube('side_f', (0, 0, 66), (1,))),
            'cut_rf'    : Element(*create_cube('cut_rf', (66, 0, 66), (4, 1))),
            # down line
            'corner_lfd': Element(*create_cube('corner_lfd', (-66, -66, 66), (1, 3, 6))),
            'cut_fd'    : Element(*create_cube('cut_fd', (0, -66, 66), (1, 6))),
            'corner_rfd': Element(*create_cube('corner_rfd', (66, -66, 66), (1, 4, 6))),

            # MIDDLE
            # upper line
            'cut_lu'    : Element(*create_cube('cut_lu', (-66, 66, 0), (3, 5))),
            'side_u'    : Element(*create_cube('side_u', (0, 66, 0), (5,))),
            'cut_ru'    : Element(*create_cube('cut_ru', (66, 66, 0), (4, 5))),
            # middle line
            'side_l'    : Element(*create_cube('side_l', (-66, 0, 0), (3,))),
            'cent_p'    : Element(*create_cube('cent_p', (0, 0, 0), ())),
            'side_r'    : Element(*create_cube('side_r', (66, 0, 0), (4,))),
            # down line
            'cut_ld'    : Element(*create_cube('cut_ld', (-66, -66, 0), (3, 6))),
            'side_d'    : Element(*create_cube('side_d', (0, -66, 0), (6,))),
            'cut_rd'    : Element(*create_cube('cut_rd', (66, -66, 0), (4, 6))),

            # BACK
            # upper line
            'corner_lbu': Element(*create_cube('corner_lbu', (-66, 66, -66), (2, 3, 5))),
            'cut_bu'    : Element(*create_cube('cut_bu', (0, 66, -66), (2, 5))),
            'corner_rbu': Element(*create_cube('corner_rbu', (66, 66, -66), (2, 4, 5))),
            # middle line
            'cut_lb'    : Element(*create_cube('cut_lb', (-66, 0, -66), (3, 2))),
            'side_b'    : Element(*create_cube('side_b', (0, 0, -66), (2,))),
            'cut_rb'    : Element(*create_cube('cut_rb', (66, 0, -66), (4, 2))),
            # down line
            'corner_lbd': Element(*create_cube('corner_lbd', (-66, -66, -66), (2, 3, 6))),
            'cut_bd'    : Element(*create_cube('cut_bd', (0, -66, -66), (2, 6))),
            'corner_rbd': Element(*create_cube('corner_rbd', (66, -66, -66), (2, 4, 6))),
        })

    def __create_elements_buttons(self) -> None:
        """
        Creates cube buttons of class Element
        Changes: updates self.elements (adds buttons)
        """
        def create_button(_obj_name, points_offset, direction):
            """ helps to create button """
            colored = (((1, 2, 3, 4), ((255, 255, 255), (255, 255, 255))),)
            cof = -1 if direction in ['b', 'l', 'd'] else 1
            if direction in ['f', 'b']:
                _points = [[33.0, 33.0, 0]  , [33.0, -33.0, 0],
                           [-33.0, -33.0, 0], [-33.0, 33.0, 0]]
                color_index = (0, 1, 2)
            elif direction in ['l', 'r']:
                _points = [[0, 33.0, 33.0]  , [0, -33.0, 33.0],
                           [0, -33.0, -33.0], [0, 33.0, -33.0]]
                color_index = (1, 2, 0)
            elif direction in ['u', 'd']:
                _points = [[33.0, 0, 33.0]  , [33.0, 0, -33.0],
                           [-33.0, 0, -33.0], [-33.0, 0, 33.0]]
                color_index = (2, 0, 1)
            for index, point in enumerate(colored[0][0]):
                _points[index][color_index[0]] += points_offset[0] * cof
                _points[index][color_index[1]] += points_offset[1] * cof
                _points[index][color_index[2]] += 100 * cof
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

