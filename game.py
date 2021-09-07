import pygame
from settings import *
from map import Map
from sprites import Player


class Game():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption("PEWPEWPEW")
        self.clock = pygame.time.Clock()
        self.load_data()

    def load_data(self):
        self.image_wasp = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image_wasp.fill(YELLOW)
        self.image_wasp_nest = pygame.Surface((TILE_SIZE, TILE_SIZE*2))
        self.image_wasp_nest.fill(ORANGE)
        self.image_player = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image_player.fill(RED)
        self.image_wall = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image_wall.fill(DARK_GREEN)
        self.image_bullet = pygame.Surface((10, 10))

    def reset(self):
        pass

    def start(self):
        self.mobs = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.current_map = Map()
        self.current_map.load_map_from_file("map.txt")
        self.current_map.create_sprites_from_data(self)
        self.player = Player(self, 
                            self.current_map.player_entry.x, 
                            self.current_map.player_entry.y)
        game.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

    def update(self):
        self.bullets.update()
        self.mobs.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.walls.draw(self.screen)
        self.mobs.draw(self.screen)
        self.bullets.draw(self.screen)
        self.draw_ui(5, 5)
        pygame.display.flip()
    
    def draw_ui(self, x, y):
        #self.draw_player_health()
        self.draw_enemy_lifebar()    

#    def draw_player_health(self):
#        health = self.player.health
#        max_health = self.player.max_health
#        bar_height = 40
#        padding = 5
#        background = pygame.Rect(x, y, max_health, bar_height)
#        lifebar = pygame.Rect(x+padding, y+padding, max(0, health-padding*2),
#                                                 bar_height-padding*2)
#        pygame.draw.rect(self.screen, YELLOW, background)
#        normalized_health = health / max_health
#        bar_color = BLUE
#        if normalized_health < 0.4:
#            bar_color = RED
#        elif normalized_health < 0.75:
#            bar_color = ORANGE
#        pygame.draw.rect(self.screen, bar_color, lifebar)
    
    def draw_enemy_lifebar(self):
        bar_color = GREEN
        for enemy in self.mobs.sprites():
            if enemy.health == enemy.max_health:
                continue
            normalized_health = enemy.health / enemy.max_health
            bar_position = enemy.rect.topleft
            lifebar = pygame.Rect(bar_position[0], bar_position[1] - 10,
                                 enemy.rect.width * normalized_health, 5)
            if normalized_health < 0.4:
                bar_color = RED
            elif normalized_health < 0.75:
                bar_color = ORANGE
            pygame.draw.rect(self.screen, bar_color, lifebar)

game = Game()
game.start()