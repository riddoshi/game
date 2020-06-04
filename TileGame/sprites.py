import pygame as pg
from settings import *
import random
from pygame import Vector2


GREEN_SHIP  = pg.Rect(0, 292, 32, 32)
RED_SHIP    = pg.Rect(0, 324, 32, 32)
BLUE_SHIP   = pg.Rect(0, 356, 32, 32)
YELLOW_SHIP = pg.Rect(0, 388, 32, 32)


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = pg.image.load(SpaceShip, get_keys(self), (YELLOW_SHIP))
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0, 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE

    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vx = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vx = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vy = PLAYER_SPEED
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0:
                    self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y

    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')

class Animation:
        def __init__(self, frames, speed, sprite):
            self.sprite = sprite
            self.speed = speed
            self.ticks = 0
            self.frames = frames
            self.running = 0
            self.start()

        def cycle_func(self, iterable):
            saved = []
            for element in iterable:
                yield element
                saved.append(element)
            if hasattr(self.sprite, 'on_animation_end'):
                self.sprite.on_animation_end()
            while saved:
                for element in saved:
                    yield element
                if hasattr(self.sprite, 'on_animation_end'):
                    self.sprite.on_animation_end()
        def stop(self):
            self.running = 0
            if self.idle_image:
                self.sprite.image = self.idle_image

        def start(self):
            if not self.running:
                self.running = 1
                self.cycle = self.cycle_func(self.frames)
                self.sprite.image = next(self.cycle)

        def update(self, dt):
            self.ticks += dt
            if self.ticks >= self.speed:
                self.ticks = self.ticks % self.speed
                if self.running:
                    self.sprite.image = next(self.cycle)

class AnimatedSprite(pg.sprite.Sprite):

    def __init__(self, pos, frames, speed):
        super().__init__()
        self.animation = Animation(frames, speed, self)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.animation.start()

    def update(self, events, dt):
        self.animation.update(dt)


class DirectionalImageSprite(pg.sprite.Sprite):

    directions = [(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(0,0)]
    def __init__(self, pos, directional_images_rect):
        super().__init__()
        images = parse_sprite_sheet(SPRITE_SHEET, directional_images_rect, 9, 1)
        self.images = { x: img for (x, img) in zip(DirectionalImageSprite.directions, images) }
        self.direction = Vector2(0, 0)
        self.image = self.images[(self.direction.x, self.direction.y)]
        self.rect = self.image.get_rect(center=pos)
        self.pos = pos


class SpaceShip(DirectionalImageSprite):

        def __init__(self, pos, controller, directional_images_rect):
            self.groups = game.all_sprites
            super().__init__(pos, directional_images_rect)
            self.controller = controller
            self.speed = 3

        def update(self, events, dt):
            super().update(events, dt)

            if self.controller:
                self.controller.update(self, events, dt)

            self.image = self.images[(self.direction.x, self.direction.y)]
            if self.direction.length():
                self.pos = self.pos + self.direction.normalize() * self.speed

            self.rect.center = int(self.pos[0]), int(self.pos[1])

def parse_sprite_sheet(sheet, start_rect, frames_in_row, lines):
     frames = []
     rect = start_rect.copy()
     for _ in range(lines):
        for _ in range(frames_in_row):
            frame = sheet.subsurface(rect)
            frames.append(frame)
            rect.move_ip(rect.width, 0)
        rect.move_ip(0, rect.height)
        rect.x = start_rect.x
        return frames


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE