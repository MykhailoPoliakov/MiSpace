import pygame
import time
import random
import math

pygame.init()       # pygame
screen = pygame.display.set_mode((1500, 800))
clock = pygame.time.Clock()
center = (750,400)
rubik = {
    '11' : 'r', '12' : 'r', '13' : 'r',
    '14' : 'r', '15' : 'r', '16' : 'r',
    '17' : 'r', '18' : 'r', '19' : 'r',
}
example = {
    '1' : [-100,100,100,'r'],
    '2' : [100,-100,100,'g'],
    '3' : [-100,-100,100,'r'],
    '4' : [100,100,100,'g'],
    '5' : [-100,100,-100,'b'],
    '6' : [100,-100,-100,'y'],
    '7' : [-100,-100,-100,'b'],
    '8' : [100,100,-100,'y'],
}
running = True

color = (255,255,255)
player_x = 0
player_y = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_y += math.pi / 16
            if event.key == pygame.K_DOWN:
                player_y -= math.pi / 16
            if event.key == pygame.K_LEFT:
                player_x -= math.pi / 16
            if event.key == pygame.K_RIGHT:
                player_x += math.pi / 16
        if player_x > math.pi * 2:
            player_x -= math.pi * 2
        elif player_x < 0:
            player_x += math.pi * 2


    screen.fill((0, 0, 0))

    for key in example.keys():
        # modifing cordinates
        test_x_cord = example[key][0] * math.cos(player_x + (example[key][0] / example[key][2]))
        test_z_cord = (example[key][2] / 100 )



        #final formula for output
        x_cord = test_x_cord / test_z_cord + center[0]
        y_cord = example[key][1] / test_z_cord + center[1]

        point = pygame.Rect(x_cord, y_cord, 5, 5)
        pygame.draw.rect(screen, color, point)

    pygame.display.flip()
    clock.tick(10)