from settings import * 

from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # player connection 
        self.player = player 
        self.distance = 80
        self.player_direction = pygame.Vector2(0,1)

        # sprite setup 
        super().__init__(groups)
        self.gun_surf = pygame.image.load(join('images', 'gun', 'escopeta.png')).convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)
    
    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(ANCHO_VENTANA / 2, ALTO_VENTANA / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)

        # calcular ángulo a partir de la dirección
        angle = degrees(atan2(-direction.y, direction.x))

        # rotar la bala según el ángulo
        self.image = pygame.transform.rotozoom(surf, angle, 1)
        self.rect = self.image.get_frect(center = pos)

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

        self.direction = direction 
        self.speed = 1200 
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

# ...existing code...
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames_dict, dead_frames_dict, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player

        self.frames = frames_dict
        self.dead_frames = dead_frames_dict
        self.state = 'izquierda'
        self.frame_index = 0
        self.image = self.frames[self.state][self.frame_index]
        self.animation_speed = 6

        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 350

        self.alive = True
        self.death_anim_done = False

    def animate(self, dt):
        if self.alive:
            # elegir animación según dirección
            if abs(self.direction.x) > abs(self.direction.y):
                self.state = 'derecha' if self.direction.x > 0 else 'izquierda'
            else:
                self.state = 'frente' if self.direction.y > 0 else 'atras'
            if len(self.frames[self.state]) > 0:
                self.frame_index += self.animation_speed * dt
                self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
        else:
            # Animación de muerte
            if len(self.dead_frames[self.state]) > 0:
                self.frame_index += self.animation_speed * dt
                idx = int(self.frame_index)
                if idx < len(self.dead_frames[self.state]):
                    self.image = self.dead_frames[self.state][idx]
                else:
                    self.death_anim_done = True
                    self.kill()

    def move(self, dt):
        if not self.alive:
            return
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()

        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top

    def hit(self):
        # Llamar a esto cuando la bala toque al enemigo
        self.alive = False
        self.frame_index = 0

    def update(self, dt):
        self.move(dt)
        self.animate(dt)
# ...existing code...
