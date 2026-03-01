import pygame
import math
import sys, os

# local classes import
from json_class import Json
from timer_class import Timer
from rubik_class import Rubik

# globals
var = {'analytic' : False, 'solid' : True, 'mouse_lock' : '', 'flag' : '',
       'motion_start' : '', 'mode' : '', 'mode_anim' : ['',0]}

anim = {'menu' : 0, 'win_fade' : 0, 'restart' : 0,}


""" Working Path """

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

def get_texture(texture):
    return pygame.image.load(resource_path( f"assets/textures/{texture}") ).convert_alpha()



""" Basic Functions """

def basic_animation(lock_word, if_const, if_plus, else_minus):
    if var['mouse_lock'] == lock_word:
        if anim[lock_word] < if_const:
            anim[lock_word] += if_plus
    elif anim[lock_word] > 0:
        anim[lock_word] -= else_minus

def sound(track):
    if main_json.data['sound']:
        sounds[track].play()

""" Output Functions """

def ingame_info(message):
    _font = pygame.font.Font(None, 40)
    for _num, line in enumerate(message):
        _text = _font.render(line, True, (255, 255, 255))
        screen.blit(_text, (15, 5 + _num * 35))


""" Class Json """

# object
main_json = Json("MiRubik","MiRubik_data.json",
                 {'sound' : True, 'best_time' : [None,None,None] })

""" World Class """

class World:
    def __init__(self):
        self.solved = False
        # rerendering screen
        self.rerender_bool = False

    def rerender(self):
        self.rerender_bool = True

    def reset(self):
        camera.reset()
        rubik.reset()
        for animation in anim:
            anim[animation] = 0
        self.rerender()

# world
world = World()

""" Camera Class """

class CameraChanger:
    """ Calculating all points` position on the screen and rendering objects in order """

    def __init__(self, name: str, center: tuple, rotation: tuple = (0,0)):
        # main properties
        self.name: str = name
        self.rotation: list = list(rotation)
        self.size: float = 1
        self.center: list = list(center)
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

    def resize(self,add_size) -> None:
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

        def angle_calc(_radius, _cord_0, _cord_1):
            """ get angle of the point to the center """
            _angle = math.degrees(math.acos(_cord_1 / _radius)) if _radius != 0 else 0
            return 360 - _angle if _cord_0 < 0 else _angle

        self.order = []
        for obj in rubik.elements.values():
            # creating colored polygons from points and sorting them
            polygons = {} ; pol_order = [] ; obj_depth = 0
            for polygon, color in obj.polygons:
                polygons[polygon] = {'render_points': [], 'depth': 0}
                for wrong_index in polygon:
                    # real index
                    index = wrong_index - 1
                    # camera y rotation offset
                    radius = math.hypot(obj.points[index][0], obj.points[index][2])
                    angle = angle_calc(radius,
                                obj.points[index][0], obj.points[index][2]) - self.rotation[1]
                    cord_x = round(radius * math.sin(math.radians(angle)), 2)
                    cord_y = obj.points[index][1]
                    cord_z = round(radius * math.cos(math.radians(angle)), 2)
                    # camera x rotation offset and final camera cord output
                    radius = math.hypot(cord_y, cord_z)
                    angle = angle_calc(radius, cord_y, cord_z) - self.rotation[0]
                    cord_x = round(cord_x * self.size, 2)
                    cord_y = round(radius * math.sin(math.radians(angle)) * self.size, 2)
                    cord_z = round(radius * math.cos(math.radians(angle)) * self.size, 2)

                    # saving point output cords
                    mult = round(((( cord_z + 125) / 375) + 2), 2)
                    polygons[polygon]['render_points'].append((int(camera.center[0] + cord_x * mult),
                                                               int(camera.center[1] - cord_y * mult)))
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
            if obj_info[0].visibility:
                for _polygon, _depth, _color in obj_info[2]:
                    if var['solid']:
                        pygame.draw.polygon(screen, _color[0], obj_info[3][_polygon]['render_points'])
                    pygame.draw.polygon(screen, _color[1], obj_info[3][_polygon]['render_points'], 3)


# cameras
camera = CameraChanger('Camera',(550,540), (20,45))


""" Class Rubik """

# rubik
rubik = Rubik()

""" PyGame """

pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
clock = pygame.time.Clock()
background_color = (55, 55, 55)
screen.fill(background_color)

# Textures

textures = {
    'fade'         : get_texture("fade.png"),
    'win_fade'     : get_texture("win_fade.png"),
    'background'   : get_texture("lake.jpg"),
    'black'        : get_texture("black.png"),
    # top menu
    'menu'         : get_texture("menu.png"),
    'left_button'  : get_texture("left_button.png"),
    'right_button' : get_texture("right_button.png"),
    'corner_button': get_texture("corner_button.png"),
    # sound textures
    'sound_on'     : get_texture("sound_on.png"),
    'sound'        : get_texture("sound.png"),
}
textures['background'] = pygame.transform.scale(textures['background'], (1920, 1080))
textures['fade'] = pygame.transform.scale(textures['fade'], (1920, 1080))
textures['win_fade'] = pygame.transform.scale(textures['win_fade'], (1920, 1080))
textures['black'].set_alpha(60)
textures['win_fade'].set_alpha(60)

# Sounds

sounds = {
    'click': pygame.mixer.Sound("assets/sounds/click.wav"),
    'select': pygame.mixer.Sound("assets/sounds/select.wav"),
}
pygame.mixer.music.load("assets/sounds/cosmo.mp3")
pygame.mixer.music.play(-1)
# if silent mode is on
if not main_json.data['sound']:
    pygame.mixer.music.pause()

# Fonts

fonts = {
    'sans': "assets/textures/sans.ttf",
    'cosmo': "assets/textures/cosmo.otf",

}

# Clickable Buttons

clicks = {
    # top menu
    'menu'        : pygame.Rect(0, 0, 1920, 130),
    'menu_exit'   : pygame.Rect(990, 0, 110, 100),
    'menu_sound'  : pygame.Rect(15, 0, 110, 100),
    'menu_restart': pygame.Rect(830, 0, 110, 100),
    # main menu
    'play'        : pygame.Rect(1300, 350, 300, 130),
    'inspect'     : pygame.Rect(1315, 600, 300, 130),
}

""" Starting Variables """

var['mode'] = 'menu'
camera.size = 0.8
camera.center = [550,540]

""" Main Cycle """

def main() -> None:

    # Class Timer
    timer = Timer()

    running = True
    while running:

        """ BRAIN """

        # objects re-render if change in camera
        if world.rerender_bool:
            world.rerender_bool = False
            camera.calculate()
        # objects re-render if change in rubik
        if rubik.rerender_bool:
            rubik.rerender_bool = False
            camera.calculate()

        # timer update
        rubik.solved = rubik.check_solved()
        timer.update(pygame.time.get_ticks())
        # switches
        if rubik.solved != var['flag']:
            var['flag'] = rubik.check_solved()
            if rubik.solved and var['mode'] == 'game' and var['game_type'] == 'play':
                timer.stop()
                for ind, best_time in enumerate(main_json.data['best_time']):
                    if timer.real_time < best_time and timer.real_time not in main_json.data['best_time']:
                        main_json.data['best_time'].insert(ind, timer.time)
                        main_json.data['best_time'].pop(-1)
                        break


        # if shuffle mode
        if rubik.shuffle_val and not rubik.animation['button_name']:
            rubik.shuffle()


        # twist rubik one time, if instructions given
        if rubik.animation['button_name']:
            rubik.twist()


        # rubik reshuffling
        if anim['restart']:
            if anim['restart'] == 200:
                final_camera_rot_x = (camera.init_rotation[0] - camera.rotation[0] + 360) / 200
                final_camera_rot_y = (camera.init_rotation[1] - camera.rotation[1] + 360) / 200
            anim['restart'] -= 1
            rubik.shuffle_val = 'fast'
            camera.rotate(0, final_camera_rot_x)
            camera.rotate(1, final_camera_rot_y)
            timer.reset()
            if anim['restart'] == 0:
                rubik.shuffle_val = ''
                timer.start(pygame.time.get_ticks())


        # start animation
        if var['mode_anim'][0] == 'start':
            if var['mode_anim'][1] < 1:
                var['mode_anim'][1] += 1
                camera.center = [550, 540]
                camera.size = 0.8

                final_camera_rot_x = (camera.init_rotation[0] - camera.rotation[0] + 360) / 143
                final_camera_rot_y = (camera.init_rotation[1] - camera.rotation[1] + 360) / 143
                final_center_x = (960 - camera.center[0])  / 149
                final_camera_size = (1 - camera.size)  / 150

            elif var['mode_anim'][1] > 0:
                var['mode_anim'][1] += 1
                camera.size += final_camera_size
                camera.center[0] += final_center_x
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
                        rubik.shuffle_val = 'slow'

                if var['mode_anim'][1] > 150:
                    var['mode'] = 'game'
                    var['mode_anim'] = ['', 0]
                    rubik.shuffle_val = ''
                    camera.center = [960, 540]
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
                        rubik.shuffle_val = 'fast'
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
                        camera.center = [550, 540]
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
                        rubik.shuffle_val = 'fast' if rubik.shuffle_val != 'fast' else ''


                    # informating if any button was activated
                    elif not rubik.animation['button_name']:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not mouse_keys[2]:
                            new_list = []
                            for _object in camera.order:
                                # if button`s depth < 0 mask won`t work
                                if _object[0].name[:6] == 'button' and _object[1] > 0:
                                    for point in list(_object[3][( 1, 2, 3, 4 )]['render_points']):
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
                                    if var['mode'] == 'game' and rubik.shuffle_val != 'fast' and main_json.data['sound']:
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
                font = pygame.font.Font( fonts["cosmo"] , 170)
                text = font.render("play", True, (255, 255, 255))
                screen.blit(text, (1300, 350))

                font = pygame.font.Font( fonts["cosmo"] , 80)
                text = font.render("INSPECT", True, (255, 255, 255))
                screen.blit(text, (1315, 600))

                screen.blit(textures['black'], (0, 0))

                # top 3 best runs
                font = pygame.font.Font( fonts["sans"] , 40)
                if main_json.data['best_time'][0] or True:
                    text = font.render(f"1. {main_json.data['best_time'][0]}", True, (255, 255, 255))
                    screen.blit(text, (1650, 15))
                if main_json.data['best_time'][1] or True:
                    text = font.render(f"2. {main_json.data['best_time'][1]}", True, (255, 255, 255))
                    screen.blit(text, (1650, 55))
                if main_json.data['best_time'][2] or True:
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
                f'last rubik rotation : {rubik.animation}',
                f'Camera : {camera.name}',
                f'Rotation : x {camera.rotation[0]:.0f}° y {camera.rotation[1]:.0f}°',
                f'Size : {camera.size:.2f}',
                f'Mode : {var["mode"]}',
                f'Top menu anim. :{anim['menu']} {var['mouse_lock']}',
                f'Timer : {timer.time}',
                f'Front side rotation : {rubik.elements['side_f'].rotation}',
                f'Center rotation : {rubik.elements['cent_p'].rotation}',
            ])


        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


""" Main Cycle Init """

if __name__ == '__main__':
    main()