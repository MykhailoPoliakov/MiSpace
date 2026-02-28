colors: dict = {
            'red': [(153, 0, 0)],
            'green': [(0, 102, 0)],
            'blue': [(0, 76, 153)],
            'yellow': [(204, 102, 0)],
            'orange': [(204, 204, 0)],
            'white': [(255, 229, 204)],
            'gray': [(50, 50, 50)]
        }




def convert_obj(filename):

    points = []

    with open(filename, 'r') as file:
        for index, line in enumerate(file):
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if not parts:
                continue

            first_word = parts[0]

            match first_word:
                case 'v':
                    points.append([ round(float(parts[1]), 2) , round(float(parts[2]), 2) , round(float(parts[3]), 2) ])
                    print([ round(float(parts[1]), 2) , round(float(parts[2]), 2) , round(float(parts[3]), 2) ])




convert_obj("assets/models/cube_rubik.obj")



def create_cube(_obj_name, points_offset, color_input):
    """ helps to create cube """
    cube_color = ('red', 'yellow', 'green', 'blue', 'white', 'orange')
    color_output = ['gray', 'gray', 'gray', 'gray', 'gray', 'gray']
    for _num in color_input:
        color_output[_num - 1] = cube_color[_num - 1]
    colored = ((('1', '2', '3', '4'), colors[color_output[0]]),
               (('5', '6', '7', '8'), colors[color_output[1]]),
               (('3', '4', '8', '7'), colors[color_output[2]]),
               (('1', '2', '6', '5'), colors[color_output[3]]),
               (('1', '4', '8', '5'), colors[color_output[4]]),
               (('2', '3', '7', '6'), colors[color_output[5]]))
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

