import pygame
from settings import *
from pygame import Vector2
from random import uniform

class Mob(pygame.sprite.Sprite):
    def __init__(self, game, x, y, image, max_health, other_groups):
        self.groups = game.mobs, other_groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.desired_velocity = Vector2(0, 0)
        self.max_health = max_health
        self.health = max_health

    @property
    def position(self):
        return Vector2(self.rect.centerx, self.rect.centery)

    def move(self):
        self.rect.center += self.velocity * self.game.dt

    def hit(self, damage):
        self.health -= damage
        if self.health < 0:
            self.kill()

    def move_with_wall_collisions(self):
        next_position = self.position + self.velocity * self.game.dt
        self.rect.centerx = next_position.x
        self.collide_with_walls('horizontal')
        self.rect.centery = next_position.y
        self.collide_with_walls('vertical')

    def collide_with_walls(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        if len(hits) == 0:
            self.grounded = False
            return
        wall = hits[0]
        if direction == 'horizontal':
            if self.rect.centerx < wall.rect.centerx:
                self.rect.right = wall.rect.left
            else:
                self.rect.left = wall.rect.right
            self.velocity.x = 0
        if direction == 'vertical':
            if self.rect.centery < wall.rect.centery:
                self.rect.bottom = wall.rect.top
                self.grounded = True
                self.double_jump_state = DOUBLEJUMP_AVAILABLE
            else:
                self.rect.top = wall.rect.bottom
            self.velocity.y = 0


class Player(Mob):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, game.image_player, PLAYER_HEALTH, game.players)
        self.trigger_jump = False
        self.grounded = False
        self.double_jump_state = DOUBLEJUMP_UNAVAILABLE
        self.last_key_state = pygame.key.get_pressed()
        self.last_shot_time = 0
        self.current_wapon = 'SHOTGUN'

    def update(self):
        self.keyboard_input()
        self.move()      

    def move(self):
        self.velocity.x = self.desired_velocity.x if self.grounded else self.desired_velocity.x*0.75
        self.velocity.y += (self.desired_velocity.y + GRAVITY) * self.game.dt
        if self.velocity.y > TERMINAL_VELOCITY:
            self.velocity.y = TERMINAL_VELOCITY
        if self.trigger_jump:
            self.trigger_jump = False
            if self.grounded or self.double_jump_state == DOUBLEJUMP_READY:
                self.velocity.y = -PLAYER_JUMP 
                if self.grounded == False and self.double_jump_state == DOUBLEJUMP_READY:
                    self.double_jump_state = DOUBLEJUMP_UNAVAILABLE
        self.move_with_wall_collisions()

    def collide_with_walls(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        if len(hits) == 0:
            self.grounded = False
            return
        wall = hits[0]
        if direction == 'horizontal':
            if self.rect.centerx < wall.rect.centerx:
                self.rect.right = wall.rect.left
            else:
                self.rect.left = wall.rect.right
            self.velocity.x = 0
        if direction == 'vertical':
            if self.rect.centery < wall.rect.centery:
                self.rect.bottom = wall.rect.top
                self.grounded = True
                self.double_jump_state = DOUBLEJUMP_AVAILABLE
            else:
                self.rect.top = wall.rect.bottom
            self.velocity.y = 0

    def shoot(self, orientation):
        weapon = WEAPONS[self.current_wapon]
        if pygame.time.get_ticks() - self.last_shot_time > weapon['FIRING_RATE']:
            self.last_shot_time = pygame.time.get_ticks()
            for _ in range(0, weapon['AMMO_PER_SHOT']):
                Bullet(self.game, weapon, self.position.x, 
                    self.position.y, orientation, self.game.enemies)

    def keyboard_input(self):
        keystate = pygame.key.get_pressed()
        self.desired_velocity = Vector2(0, 0)
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.desired_velocity.x = -PLAYER_SPEED
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.desired_velocity.x = PLAYER_SPEED
        if keystate[pygame.K_UP] or keystate[pygame.K_SPACE]:
            self.trigger_jump = True
        else:
            did_pressed_up = self.last_key_state[pygame.K_UP] or self.last_key_state[pygame.K_SPACE]
            if did_pressed_up and self.double_jump_state == DOUBLEJUMP_AVAILABLE:
                self.double_jump_state = DOUBLEJUMP_READY
        self.last_key_state = keystate
        mouse = pygame.mouse.get_pressed()
        if mouse[0]:
            mx, my = pygame.mouse.get_pos()
            towards_mouse = Vector2(mx, my) - self.position
            if towards_mouse.magnitude() > 0:
                towards_mouse = towards_mouse.normalize()
            self.shoot(towards_mouse)


class Wasp(Mob):
    def __init__(self, game, x ,y):
        super().__init__(game, x, y, game.image_wasp, WASP_HEALTH, game.enemies)

    def update(self):
        towards_player = self.game.player.position - self.position
        if towards_player.magnitude() > 0:
            self.velocity = towards_player.normalize() * WASP_SPEED
        self.avoid_mates()
        self.move()
        self.try_attack()

    def try_attack(self):
        hits = pygame.sprite.spritecollide(self, self.game.players, False)
        if len(hits):
            target = hits[0]
            target.hit(WASP_DAMAGE)
            print(target.health)

    def avoid_mates(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if len(hits) == 0:
            return
        avoid_vector = Vector2(0, 0)
        for mate in hits:
            if mate == self:
                continue
            towards_mate = mate.position - self.position
            if towards_mate.magnitude() > 0:
                avoid_vector += towards_mate.normalize()
        avoid_vector /= len(hits)
        self.velocity -= avoid_vector * WASP_SPEED*(
            WASP_SPEED + uniform(-WASP_SPEED, WASP_SPEED))


class WaspNest(Mob):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, game.image_wasp_nest, WASP_NEST_HEALTH, game.enemies)
        self.wasp_spawn_frecuency = WASP_NEST_SPAWN_FREQ
        self.last_spawn_time = 0

    def update(self):
        can_spawn = (pygame.time.get_ticks() - 
                    self.last_spawn_time) > self.wasp_spawn_frecuency
        if can_spawn:
            Wasp(self.game, self.rect.centerx, self.rect.top)
            ticks = pygame.time.get_ticks()
            self.last_spawn_time = uniform(ticks*0.75, ticks*1.25)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, weapon, x, y, orientation, target_group):
        self.groups = game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.image_bullet
        self.image.fill(weapon['COLOR'])
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)
        self.damage = weapon['DMG']
        self.speed = weapon['SPEED'] * uniform(0.8, 1.2)
        self.ttl = weapon['TTL']
        self.spawn_bullet_time = pygame.time.get_ticks()
        orientation += Vector2(uniform(-weapon['SPREAD'], weapon['SPREAD']),
                                uniform(-weapon['SPREAD'], weapon['SPREAD']))
        self.velocity = orientation.normalize() * weapon['SPEED']
        self.target_group = target_group

    def update(self):
        self.rect.center += self.velocity * self.game.dt
        if pygame.time.get_ticks() - self.spawn_bullet_time > self.ttl:
            self.kill()
        self.check_hits()

    def check_hits(self):
        hits = pygame.sprite.spritecollide(self, self.target_group, False)
        if len(hits):
            target = hits[0]
            target.hit(self.damage)
            self.kill()
        if pygame.sprite.spritecollideany(self, self.game.walls):
            self.kill()



class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.image_wall
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

