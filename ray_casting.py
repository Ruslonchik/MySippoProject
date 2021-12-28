#Импортируем пайгейм, настройки и карту
import pygame
from settings import *
from map import world_map, WORLD_WIDTH, WORLD_HEIGHT
from numba import njit

@njit(fastmath=True, cache=True)
def mapping(a, b): #Функция для координат левого верхнего угла(квадрата, в котором мы находимся в данный момент)
    return int(a // TILE) * TILE, int(b // TILE) * TILE

#Функция, которая принимает поверхность отрисовки, позицию и угол игрока
@njit(fastmath=True, cache=True)
def ray_casting(player_pos, player_angle, world_map):
    casted_walls = []
    ox, oy = player_pos #Обозначим начальные координаты всех лучей
    texture_v, texture_h = 1, 1 #Дефолтные номера текстур для гориз и вертик стен, ошибка выхода за предел
    xm, ym = mapping(ox, oy) #Координаты левого верхнего угла(квадрата, в котором мы находимся в данный момент)
    cur_angle = player_angle - HALF_FOV #Введем угол для первого луча
    for ray in range(NUM_RAYS): #Пройдемся в цикле по всем лучам, вычисляя для каждого синус и косинус его направления
        sin_a = math.sin(cur_angle)
        sin_a = sin_a if sin_a else 0.000001
        cos_a = math.cos(cur_angle)
        cos_a = cos_a if cos_a else 0.000001

        # verticals (Пересечение с вертикалями)
        x, dx = (xm + TILE, 1) if cos_a >= 0 else (xm, -1) #Косинус определяет, в какую сторону идти по вертикалям
        for i in range(0, WORLD_WIDTH, TILE): #Пройдемся по ширине экрана, с шагом равным стороне квадрата карты
            depth_v = (x - ox) / cos_a #Найдем расстояние до вертикали
            yv = oy + depth_v * sin_a #И ее координату y по выведенным ранее формулам
          #Проверка на предмет столкновения со стеной, если столкновения не было, то переходим к следующей вер-ли
            tile_v = mapping(x + dx, yv)
            if tile_v in world_map:
                texture_v = world_map[tile_v] #Дополнительно определяем номер текстуры
                break
            x += dx * TILE #х - текущая вертикаль, dx - вспомогательная переменная, при помощи которой получаем вер-ль

        # horizontals (Пересечение с горизноталями, аналогично вертикалям)
        y, dy = (ym + TILE, 1) if sin_a >= 0 else (ym, -1) #Синус угла определяет верхнее и нижнее направление гор-лей
        for i in range(0, WORLD_HEIGHT, TILE):
            depth_h = (y - oy) / sin_a
            xh = ox + depth_h * cos_a
            tile_h = mapping(xh, y + dy)
            if tile_h in world_map:
                texture_h = world_map[tile_h] #Дополнительно определяем номер текстуры
                break
            y += dy * TILE

        # projection (Выбираем, какая из точек пересечения с верт или гор-лью ближе к нам)
        depth, offset, texture = (depth_v, yv, texture_v) if depth_v < depth_h else (depth_h, xh, texture_h)
        offset = int(offset) % TILE #Вычисляем смещение на текстуре, путем нахождения остатка отделения квадрата
        depth *= math.cos(player_angle - cur_angle)
        depth = max(depth, 0.00001) #избегаем падения игры из-за ошибки деления на 0
        proj_height = int(PROJ_COEFF / depth) #Ограничиваем процесс отрисовки проекции большой величины

        casted_walls.append((depth, offset, proj_height, texture))
        cur_angle += DELTA_ANGLE
    return casted_walls

def ray_casting_walls(player, textures):
    casted_walls = ray_casting(player.pos, player.angle, world_map)
    wall_shot = casted_walls[CENTER_RAY][0], casted_walls[CENTER_RAY][2]
    walls = []
    for ray, casted_values in enumerate(casted_walls):
        depth, offset, proj_height, texture = casted_values
        if proj_height > HEIGHT:
            coeff = proj_height / HEIGHT
            texture_height = TEXTURE_HEIGHT / coeff
            #Выделим подповерхность из текстуры в виде квадрата, в котором начальные коорд равны вычисленному смещению
            wall_column = textures[texture].subsurface(offset * TEXTURE_SCALE,
                                                       HALF_TEXTURE_HEIGHT - texture_height // 2,
                                                       TEXTURE_SCALE, texture_height)
            #Масштабируем только что выделенную часть текстуры в прямоугольник, учитывая величину проекции стены
            wall_column = pygame.transform.scale(wall_column, (SCALE, HEIGHT))
            wall_pos = (ray * SCALE, 0)
        else:
            wall_column = textures[texture].subsurface(offset * TEXTURE_SCALE, 0, TEXTURE_SCALE, TEXTURE_HEIGHT)
            wall_column = pygame.transform.scale(wall_column, (SCALE, proj_height))
            wall_pos = (ray * SCALE, HALF_HEIGHT - proj_height // 2)

        walls.append((depth, wall_column, wall_pos))
    return walls, wall_shot
