import pygame
from settings import *
from collections import deque #Для эффективной реализации анимации выбрал структуру данных, как очередь deque
from ray_casting import mapping
from numba.core import types
from numba.typed import Dict
from numba import int32

#Класс, где хранятся типы и карта спрайтов
class Sprites:
    def __init__(self):
        self.sprite_parameters = { #типы спрайтов в словаре, где ключи соответствуют названиям картинок
            'sprite_barrel': {
                'sprite': pygame.image.load('sprites/barrel/base/0.png').convert_alpha(), #спрайты из баз папки
                'viewing_angles': None, #переименнованый параметр статик, имеют ли все углы обзора у спрайта
                'shift': 1.8, #сдвиг и масштаб
                'scale': (0.4, 0.4),
                'side': 30,
                #анимация
                'animation': deque( #создадим очередь из всех спрайтов, но если аним нет то ложь
                    [pygame.image.load(f'sprites/barrel/anim/{i}.png').convert_alpha() for i in range(12)]),
                'death_animation': deque([pygame.image.load(f'sprites/barrel/death/{i}.png')
                                          .convert_alpha() for i in range(4)]),
                'is_dead': None,
                'dead_shift': 2.6, #Сдвиг спрайта после его гибели
                'animation_dist': 800, #расстояние дл спрайта
                'animation_speed': 10, #скорость анимации
                'blocked': True, #столкновения со спрайтами(пламя проходимое)
                'flag': 'decor', #Тип спрайта
                'obj_action': [] #Действие объекта при виде игрока
            },
            'sprite_pin': {
                'sprite': pygame.image.load('sprites/pin/base/0.png').convert_alpha(),
                'viewing_angles': None,
                'shift': 0.6,
                'scale': (0.6, 0.6),
                'side': 30,
                'animation': deque([pygame.image.load(f'sprites/pin/anim/{i}.png').convert_alpha() for i in range(8)]),
                'death_animation': [],
                'is_dead': 'immortal', #бессмертный
                'dead_shift': None,
                'animation_dist': 800,
                'animation_speed': 10,
                'blocked': True,
                'flag': 'decor',
                'obj_action': []
            },
            'sprite_flame': {
                'sprite': pygame.image.load('sprites/flame/base/0.png').convert_alpha(),
                'viewing_angles': None,
                'shift': 0.7,
                'scale': (0.6, 0.6),
                'side': 30, #Собственный размер
                'animation': deque(
                    [pygame.image.load(f'sprites/flame/anim/{i}.png').convert_alpha() for i in range(16)]),
                'death_animation': [],
                'is_dead': 'immortal',
                'dead_shift': 1.8,
                'animation_dist': 1800,
                'animation_speed': 5,
                'blocked': None,
                'flag': 'decor',
                'obj_action': []
            },
            'npc_devil': {
                'sprite': [pygame.image.load(f'sprites/devil/base/{i}.png').convert_alpha() for i in range(8)],
                'viewing_angles': True,
                'shift': 0.0,
                'scale': (1.1, 1.1),
                'side': 50,
                'animation': [],
                'death_animation': deque([pygame.image.load(f'sprites/devil/death/{i}.png')
                                           .convert_alpha() for i in range(6)]),
                'is_dead': None,
                'dead_shift': 0.6,
                'animation_dist': None,
                'animation_speed': 10,
                'blocked': True,
                'flag': 'npc',
                'obj_action': deque(
                    [pygame.image.load(f'sprites/devil/anim/{i}.png').convert_alpha() for i in range(9)]),
            },
            'sprite_door_v': {
                'sprite': [pygame.image.load(f'sprites/doors/door_v/{i}.png').convert_alpha() for i in range(16)],
                'viewing_angles': True,
                'shift': 0.1,
                'scale': (2.6, 1.2),
                'side': 100,
                'animation': [],
                'death_animation': [],
                'is_dead': 'immortal',
                'dead_shift': 0,
                'animation_dist': 0,
                'animation_speed': 0,
                'blocked': True,
                'flag': 'door_h',
                'obj_action': []
            },
            'sprite_door_h': {
                'sprite': [pygame.image.load(f'sprites/doors/door_h/{i}.png').convert_alpha() for i in range(16)],
                'viewing_angles': True,
                'shift': 0.1,
                'scale': (2.6, 1.2),
                'side': 100,
                'animation': [],
                'death_animation': [],
                'is_dead': 'immortal',
                'dead_shift': 0,
                'animation_dist': 0,
                'animation_speed': 0,
                'blocked': True,
                'flag': 'door_v',
                'obj_action': []
            },
            'npc_soldier0': {
                'sprite': [pygame.image.load(f'sprites/npc/soldier0/base/{i}.png').convert_alpha() for i in range(8)],
                'viewing_angles': True,
                'shift': 0.8,
                'scale': (0.4, 0.6),
                'side': 30,
                'animation': [],
                'death_animation': deque([pygame.image.load(f'sprites/npc/soldier0/death/{i}.png')
                                         .convert_alpha() for i in range(10)]),
                'is_dead': None,
                'dead_shift': 1.7,
                'animation_dist': None,
                'animation_speed': 6,
                'blocked': True,
                'flag': 'npc',
                'obj_action': deque([pygame.image.load(f'sprites/npc/soldier0/action/{i}.png')
                                    .convert_alpha() for i in range(4)])
            },
        }
#Карта спрайтов, настраиваем положение спрайта по сдвигу
        self.list_of_objects = [
            SpriteObject(self.sprite_parameters['sprite_barrel'], (7.1, 2.1)),
            SpriteObject(self.sprite_parameters['sprite_barrel'], (5.9, 2.1)),
            SpriteObject(self.sprite_parameters['sprite_pin'], (8.7, 2.5)),
            SpriteObject(self.sprite_parameters['npc_devil'], (7, 4)),
            SpriteObject(self.sprite_parameters['sprite_flame'], (8.6, 5.6)),
            SpriteObject(self.sprite_parameters['sprite_door_v'], (3.5, 3.5)),
            SpriteObject(self.sprite_parameters['sprite_door_h'], (1.5, 4.5)),
            SpriteObject(self.sprite_parameters['npc_soldier0'], (2.5, 1.5)),
            SpriteObject(self.sprite_parameters['npc_soldier0'], (5.51, 1.5)),
            SpriteObject(self.sprite_parameters['npc_soldier0'], (6.61, 2.92)),
            SpriteObject(self.sprite_parameters['npc_soldier0'], (7.68, 1.47)),
            SpriteObject(self.sprite_parameters['npc_soldier0'], (8.75, 3.65)),
            SpriteObject(self.sprite_parameters['npc_soldier0'], (1.27, 11.5)),
            SpriteObject(self.sprite_parameters['npc_soldier0'], (1.26, 8.29)),
        ]
#возвращает ближайший спрайт, если таких спрайтов много под выстрелом
    @property
    def sprite_shot(self):
        return min([obj.is_on_fire for obj in self.list_of_objects], default=(float('inf'), 0))
#возвращает словарь всех закрытых дверей на карте (нумба!!!)
    @property
    def blocked_doors(self):
        blocked_doors = Dict.empty(key_type=types.UniTuple(int32, 2), value_type=int32)
        for obj in self.list_of_objects:
            if obj.flag in {'door_h', 'door_v'} and obj.blocked:
                i, j = mapping(obj.x, obj.y)
                blocked_doors[(i, j)] = 0
        return blocked_doors

#Класс, где вычисляем местоположение спрайта и его проекционные характеристики
class SpriteObject:
    #Начальные параметры каждого спрайта - его тип(статичная картинка или нет), положение, сдвиг и масштабирование
    def __init__(self, parameters, pos):
        self.object = parameters['sprite'].copy() #Инициализируем атрибуты второго класса
        self.viewing_angles = parameters['viewing_angles']
        self.shift = parameters['shift'] # Устанавливаем сдвиг по высоте атрибутов шифт
        self.scale = parameters['scale'] #Если есть необходимость смасштабировать картинку
        self.animation = parameters['animation'].copy()
        # ---------------------
        self.death_animation = parameters['death_animation'].copy()
        self.is_dead = parameters['is_dead']
        self.dead_shift = parameters['dead_shift']
        # ---------------------
        self.animation_dist = parameters['animation_dist']
        self.animation_speed = parameters['animation_speed']
        self.blocked = parameters['blocked']
        self.flag = parameters['flag']
        self.obj_action = parameters['obj_action'].copy()
        self.x, self.y = pos[0] * TILE, pos[1] * TILE
        self.side = parameters['side']
        self.dead_animation_count = 0
        self.animation_count = 0 #счетчик для реализаии анимации
        self.npc_action_trigger = False #Триггер для выполнения действия объекта
        self.door_open_trigger = False #триггер открытия дверей
        self.door_prev_pos = self.y if self.flag == 'door_h' else self.x
        self.delete = False
        if self.viewing_angles:
            if len(self.object) == 8:
                #Формируем диапозоны углов для каждого спрайта, на каждый спрайт 45 градусов, т.к. 8
                self.sprite_angles = [frozenset(range(338, 361)) | frozenset(range(0, 23))] + \
                                     [frozenset(range(i, i + 45)) for i in range(23, 338, 45)]
            else:
                self.sprite_angles = [frozenset(range(348, 361)) | frozenset(range(0, 11))] + \
                                     [frozenset(range(i, i + 23)) for i in range(11, 348, 23)]
                #Для быстрого поиска используем замороженные множества
            self.sprite_positions = {angle: pos for angle, pos in zip(self.sprite_angles, self.object)}
#Свойство, возвращающе расстояние и проекцию спрайта, который под огнем
    @property
    def is_on_fire(self): #если спрайт на центральном луче, в небольшом диапазоне, то спрайт под огнем
        if CENTER_RAY - self.side // 2 < self.current_ray < CENTER_RAY + self.side // 2 and self.blocked:
            return self.distance_to_sprite, self.proj_height
        return float('inf'), None

    @property
    def pos(self):
        return self.x - self.side // 2, self.y - self.side // 2
#Метод, на вход которого идут экземпляр класса игрок, а также словарь с номерами лучей и расстояния до стен
    def object_locate(self, player):
#Найдем разности координат между игроком и спрайтом
        dx, dy = self.x - player.x, self.y - player.y
        self.distance_to_sprite = math.sqrt(dx ** 2 + dy ** 2) #Вычислим расстояние до него
#Рассчитаем углы тета и гамма
        self.theta = math.atan2(dy, dx)
        gamma = self.theta - player.angle
        if dx > 0 and 180 <= math.degrees(player.angle) <= 360 or dx < 0 and dy < 0: #Условие, гамма в нужном пределе
            gamma += DOUBLE_PI #При выполнении условия прибавляем 2п, в зависимости от направления игрока
        self.theta -= 1.4 * gamma

        delta_rays = int(gamma / DELTA_ANGLE) #Смещение спрайта относительно центрального луча
        self.current_ray = CENTER_RAY + delta_rays
        if self.flag not in {'door_h', 'door_v'}:
            self.distance_to_sprite *= math.cos(HALF_FOV - self.current_ray * DELTA_ANGLE) #Расстояние(убираем рыб глаз)
#Проверим, попадает ли луч, на котором спрайт, в наш диапазон лучей, будет ли спрайт ближе к нам, чем стена
        fake_ray = self.current_ray + FAKE_RAYS
        if 0 <= fake_ray <= FAKE_RAYS_RANGE and self.distance_to_sprite > 30:
            self.proj_height = min(int(PROJ_COEFF / self.distance_to_sprite), #Расчет проекционной высоты спрайта
                                   DOUBLE_HEIGHT if self.flag not in {'door_h', 'door_v'} else HEIGHT)
            sprite_width = int(self.proj_height * self.scale[0])
            sprite_height = int(self.proj_height * self.scale[1])
            half_sprite_width = sprite_width // 2 #Коэффициент массштабирования спрайта
            half_sprite_height = sprite_height // 2
            shift = half_sprite_height * self.shift #Механизм регулирования спрайта по высоте

            # logic for doors, npc, decor (в случае срабатывания триггера для двери, запускаем функцию открытия ее)
            if self.flag in {'door_h', 'door_v'}:
                if self.door_open_trigger:
                    self.open_door()
                self.object = self.visible_sprite()
                sprite_object = self.sprite_animation()
            else:
                if self.is_dead and self.is_dead != 'immortal': #анимация смерти и взаимодействия нпс с игроком
                    sprite_object = self.dead_animation()
                    shift = half_sprite_height * self.dead_shift
                    sprite_height = int(sprite_height / 1.3)
                elif self.npc_action_trigger:
                    sprite_object = self.npc_in_action()
                else:
                    self.object = self.visible_sprite() #первоначальная анимация для спрайтов
                    sprite_object = self.sprite_animation()


            # sprite scale and pos (Вычисляем позицию спрайта относительно его луча)
            sprite_pos = (self.current_ray * SCALE - half_sprite_width, HALF_HEIGHT - half_sprite_height + shift)
            #Масштабируем спрайт по размеру проекции(коэффициент для соотношения сторон спрайта)
            sprite = pygame.transform.scale(sprite_object, (sprite_width, sprite_height))
            return (self.distance_to_sprite, sprite, sprite_pos) #Если условие не выполнилось, возвращ ложное знач
        else:
            return (False,)

    def sprite_animation(self):
        if self.animation and self.distance_to_sprite < self.animation_dist:
            sprite_object = self.animation[0]
            if self.animation_count < self.animation_speed:
                self.animation_count += 1
            else:
                self.animation.rotate()
                self.animation_count = 0
            return sprite_object
        return self.object
#Функция анимация спрайта
    def visible_sprite(self):
        if self.viewing_angles:
            if self.theta < 0:
                self.theta += DOUBLE_PI
            self.theta = 360 - int(math.degrees(self.theta))

            for angles in self.sprite_angles:
                if self.theta in angles:
                    return self.sprite_positions[angles]
        return self.object
#Анимация смерти
    def dead_animation(self):
        if len(self.death_animation):
            if self.dead_animation_count < self.animation_speed:
                self.dead_sprite = self.death_animation[0]
                self.dead_animation_count += 1
            else:
                self.dead_sprite = self.death_animation.popleft()
                self.dead_animation_count = 0
        return self.dead_sprite
#Анимация взаимодействия нпс с игроком
    def npc_in_action(self):
        sprite_object = self.obj_action[0]
        if self.animation_count < self.animation_speed:
            self.animation_count += 1
        else:
            self.obj_action.rotate()
            self.animation_count = 0
        return sprite_object
#Функия открытия дверей (в зависимости от типа, она будет уходит в стену, а после прохождения расстояния удалим с карты)
    def open_door(self):
        if self.flag == 'door_h':
            self.y -= 3
            if abs(self.y - self.door_prev_pos) > TILE:
                self.delete = True
        elif self.flag == 'door_v':
            self.x -= 3
            if abs(self.x - self.door_prev_pos) > TILE:
                self.delete = True
