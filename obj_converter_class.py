class ObjConverter:
    """
    Attributes:
        self.points (list[ x,y,z ]):
            points of the object

        self.colored_polygons (list[ tuple[ points` indexes for polygon ] , list[ color ] ):
            object`s polygons points` indexes and colors

    Args:
        filename (str): name of the .obj file

        colors (dict[ tuple[ r,g,b ], tuple[ r,g,b ] ]): polygons colors and lines colors

    """
    def __init__(self, filename: str, colors: dict) -> None:
        # main attributes
        self.points: list = []
        self.colored_polygons: list = []
        # local attributes
        self.__colors: dict = colors
        self.__filename: str = filename
        # make convertion, fill up self.points and self.colored_polygons
        self.__convert_obj()

    def __convert_obj(self) -> None:
        """ converts file.obj to lists of points and colored polygons """
        color: str = ''
        # open .obj file
        with open(self.__filename, 'r') as file:
            for index, line in enumerate(file):

                # if no line is empty
                if not line or line.startswith('#'):
                    continue
                words: list = line.split()
                if not words:
                    continue

                # match first word
                match words[0]:
                    # point line
                    case 'v':
                        points = [round(float(words[1]), 2), round(float(words[2]), 2), round(float(words[3]), 2)]
                        self.points.append(points)
                    # color line
                    case 'usemtl':
                        color = words[1]
                    # polygon line
                    case 'f':
                        polygon_list = []
                        points_amount = len(words) - 1
                        for _index in range(points_amount):
                            polygon_list.append(int(words[_index + 1].split('/')[0]))
                        polygon = tuple(polygon_list)
                        self.colored_polygons.append([polygon, color])


