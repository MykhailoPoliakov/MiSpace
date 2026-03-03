import math
import copy
import numpy as np

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

    def __init__(self, name: str, polygons: tuple[tuple,tuple], points: np.ndarray, visibility: bool):
        # main properties
        self.name: str = name
        self.points: np.ndarray = points
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

        match index:
            case 2:
                # z
                rad_angle = np.radians( -add_angle )
                cos_a, sin_a = np.cos( rad_angle), np.sin( rad_angle)

                rotation_matrix =  np.array([
                    [cos_a , -sin_a,    0],
                    [sin_a , cos_a ,    0],
                    [0     ,      0,    1],
                ], dtype=np.float32)
            case 1:
                # y
                rad_angle = np.radians( add_angle )
                cos_a, sin_a = np.cos( rad_angle), np.sin( rad_angle)

                rotation_matrix = np.array([
                    [cos_a ,    0, sin_a],
                    [0     ,    1,     0],
                    [-sin_a,    0, cos_a],
                ], dtype=np.float32)
            case 0:
                # x
                rad_angle = np.radians(-add_angle)
                cos_a, sin_a = np.cos( rad_angle), np.sin( rad_angle)

                rotation_matrix = np.array([
                    [   1,     0,      0],
                    [   0, cos_a, -sin_a],
                    [   0, sin_a,  cos_a],
                ], dtype=np.float32)

        self.points = self.points @ rotation_matrix

        # update object`s rotation angle
        self.rotation[index] -= add_angle
        if self.rotation[index] >= 360:
            self.rotation[index] -= 360
        if self.rotation[index] < 0:
            self.rotation[index] += 360
