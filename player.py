from settings import *
import pygame
import math
from map import collision_walls

#Атрибуты класса - это координаты игрока, его направление взгляда
class Player:
    def __init__(self, sprites):
        self.x, self.y = player_pos
        self.sprites = sprites
        self.angle = player_angle
        self.sensitivity = 0.004
        # collision parameters (атрибуты необходимыедля расчета коллизий)
        self.side = 50 #размер стороны квадрата игрока вместо точки
        self.rect = pygame.Rect(*player_pos, self.side, self.side) #сторона и позиция игрока на карте
        # weapon
        self.shot = False

#Свойство, возвращающее позицию по х и у
    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def collision_list(self):
        return collision_walls + [pygame.Rect(*obj.pos, obj.side, obj.side) for obj in
                                  self.sprites.list_of_objects if obj.blocked]
#функция определения столкновений, которая перенимает передвижение наодин шаг по обоим осям
    def detect_collision(self, dx, dy):
        next_rect = self.rect.copy() #копия нашего текущего положения
        next_rect.move_ip(dx, dy) #перемещаем его на дх ду
        hit_indexes = next_rect.collidelistall(self.collision_list) #формируем индекс стен, с которыми столкнулся игрок
#находим сторону с которой столкнулись
        if len(hit_indexes):
            delta_x, delta_y = 0, 0
            for hit_index in hit_indexes:
                hit_rect = self.collision_list[hit_index] #коллизий мб несколько, например промежуток между 2 стен
                if dx > 0:
                    delta_x += next_rect.right - hit_rect.left #случаи если воткнулись в угол
                else:
                    delta_x += hit_rect.right - next_rect.left
                if dy > 0:
                    delta_y += next_rect.bottom - hit_rect.top
                else:
                    delta_y += hit_rect.bottom - next_rect.top

            if abs(delta_x - delta_y) < 10:
                dx, dy = 0, 0
            elif delta_x > delta_y:
                dy = 0
            elif delta_y > delta_x:
                dx = 0
        self.x += dx
        self.y += dy

    # Основной метод, отслеживает нажатые клавиши, и меняет соответствующие значения атрибутов
    def movement(self):
        self.keys_control() #подключение клавиш управления
        self.mouse_control()
        self.rect.center = self.x, self.y
        self.angle %= DOUBLE_PI

    # Меняем управление на 3д
    def keys_control(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            exit()

        if keys[pygame.K_w]:
            dx = player_speed * cos_a
            dy = player_speed * sin_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_s]:
            dx = -player_speed * cos_a
            dy = -player_speed * sin_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_a]:
            dx = player_speed * sin_a
            dy = -player_speed * cos_a
            self.detect_collision(dx, dy)
        if keys[pygame.K_d]:
            dx = -player_speed * sin_a
            dy = player_speed * cos_a
            self.detect_collision(dx, dy)

        if keys[pygame.K_LEFT]:
            self.angle -= 0.02
        if keys[pygame.K_RIGHT]:
            self.angle += 0.02

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN: #Лог параметр принимающий истинное значение при нажатии лкм
                if event.button == 1 and not self.shot:
                    self.shot = True

    def mouse_control(self): #управление мышью
        if pygame.mouse.get_focused(): #если курсор мыши в окне, то рассчитываем разницу между положением мыши и
            difference = pygame.mouse.get_pos()[0] - HALF_WIDTH #серединой экрана, затем с каждым циклом
            pygame.mouse.set_pos((HALF_WIDTH, HALF_HEIGHT))#переносим указатель в центр и прибавляем разницу
            self.angle += difference * self.sensitivity#к углу направления игрока с учетом чувствительности

