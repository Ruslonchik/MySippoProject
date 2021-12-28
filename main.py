from player import Player
from sprite_objects import *
from ray_casting import ray_casting_walls #Функция, которая принимает поверхность отрисовки, позицию и угол игрока
from drawing import Drawing
from interaction import Interaction

#Основное рабочее окно
pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIGHT)) #Создание поверхности карты
sc_map = pygame.Surface(MINIMAP_RES) #Создание поверхности миникарты

sprites = Sprites() #экземпляры спрайтов
#Объект класса клок для установки количества желаемого кадров в секунду
clock = pygame.time.Clock()
player = Player(sprites)
drawing = Drawing(sc, sc_map, player, clock)
interaction = Interaction(player, sprites, drawing)
#вызываем меню до начала запуска меню
drawing.menu()
pygame.mouse.set_visible(False) #Убираем указатель мыши, чтобы не мешал

while True:

    player.movement() #Вызываем метод мувмент на каждой итерации основного цикла
    drawing.background(player.angle) #В метод построения фона передадим значение угла игрока
    walls, wall_shot = ray_casting_walls(player, drawing.textures) #список стен
    drawing.world(walls + [obj.object_locate(player) for obj in sprites.list_of_objects])#список параметров стен и спр
    drawing.fps(clock)
    drawing.mini_map(player)
    drawing.player_weapon([wall_shot, sprites.sprite_shot])

    interaction.interaction_objects()
    interaction.npc_action()
    interaction.clear_world()
    interaction.check_win()

#Обновляем содержимое приложения на каждой итерации
    pygame.display.flip()
    clock.tick()