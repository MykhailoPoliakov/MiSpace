import numpy as np

class Camera:
    """ Calculating all points` position on the screen and rendering objects in order """

    def __init__(self, center: tuple, rotation: tuple = (0,0)):
        # main properties
        self.rotation: list = list(rotation)
        self.size: float = 1
        self.center: list = list(center)
        # all objects and their`s info order (for rendering)
        self.order: list = []
        # save start rotation
        self.init_rotation: tuple = rotation
        # rerender bool
        self.rerender_bool = False

    def reset(self) -> None:
        """ full camera reset """
        self.rotation = list(self.init_rotation)
        self.size = 1

    def rotate(self,index: int, add_angle: int | float) -> None:
        """ rotate the camera """
        self.rotation[index] = (self.rotation[index] + add_angle) % 360
        self.rerender_bool = True

    def resize(self, add_size: int | float) -> None:
        """ resize the camera """
        if (self.size < 2 or add_size < 0) and (self.size > 0.3 or add_size > 0):
            self.size *= 1 + add_size / 20
            self.rerender_bool = True


    def calculate(self, obj_dict: dict) -> None:
        """
            1) calculating points position on the screen
            2) creating polygon presets, including polygon depth,color and points
            3) saving all object`s polygons in order
            4) saving object in self.order for rendering later
        """
        def calculate_color(_depth, _colors) -> tuple:
            """calculate color based on z position of an object"""
            f_colors = []
            limit = 80 * self.size
            if _depth > limit:
                return _colors
            elif _depth < -limit:
                return int(_colors[0] / 1.5), int(_colors[1] / 1.5), int(_colors[2] / 1.5)
            for _color in _colors:
                f_colors.append(int(_color / (1 + ((_depth - limit) / -40))))
            return tuple(f_colors)

        # ROTATION MATRICES

        # y
        rad_angle = np.radians( self.rotation[1] )
        cos_a, sin_a = np.cos(rad_angle), np.sin(rad_angle)

        rotation_matrix_y = np.array([
            [cos_a, 0, sin_a],
            [0, 1, 0],
            [-sin_a, 0, cos_a],
        ], dtype=np.float32)

        # x
        rad_angle = np.radians( -self.rotation[0] )
        cos_a, sin_a = np.cos(rad_angle), np.sin(rad_angle)

        rotation_matrix_x = np.array([
            [1, 0, 0],
            [0, cos_a, -sin_a],
            [0, sin_a, cos_a],
        ], dtype=np.float32)

        # FOR EVERY POINT

        self.order = []
        for element in obj_dict.values():

            points = element.points.copy()
            # camera y and x rotation offset

            points @= rotation_matrix_y
            points @= rotation_matrix_x

            # resizing
            if self.size != 1:
                points *= self.size

            # creating colored polygons from points and sorting them
            for polygon, color in element.polygons:
                polygons = {'render_points': [], 'depth': 0}
                for index in polygon:
                    # real index
                    index -= 1

                    # save data
                    cord_x, cord_y, cord_z = points[index]

                    # saving point output cords
                    mult = 300 / (cord_z + 600)
                    polygons['render_points'].append((int(self.center[0] + cord_x / mult),
                                                      int(self.center[1] - cord_y / mult)))
                    # saving depth of the polygon
                    polygons['depth'] += cord_z

                # color of the polygon calculation
                new_color = (calculate_color(polygons['depth'] / 4, color[0]),
                             calculate_color(polygons['depth'] / 4, color[1]))

                # adding to order
                self.order.append(( element, polygons['render_points'], new_color, polygons['depth']))

        # SORT BY DEPTH

        self.order = sorted(self.order, key=lambda item: item[ -1 ])