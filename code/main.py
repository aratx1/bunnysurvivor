from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from os.path import join
from groups import AllSprites


from random import randint, choice

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption('Bunny Survivor!')
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_images()

        # groups 
        self.all_sprites = AllSprites()
        self.ground_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # sistema de vidas
        self.player_lives = INITIAL_LIVES
        self.invulnerable = False
        self.invulnerability_time = 0
        self.invulnerability_duration = INVULNERABILITY_TIME

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0 
        self.gun_cooldown = 1000

        # enemy timer 
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 1000)
        self.spawn_positions = []
        
        # setup
        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'gun', 'bala.png')).convert_alpha()
        
        # Cargar imágenes de corazones para el sistema de vidas
        self.empty_heart = pygame.image.load(join('images', 'items', 'Empty-heart.png')).convert_alpha()
        self.full_heart = pygame.image.load(join('images', 'items', 'Heart.png')).convert_alpha()
        
        folders = list(walk(join('images', 'enemies', "vivo")))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', "vivo", folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

        self.enemy_dead_frames = {}
        dead_folders = list(walk(join('images', 'enemies', "muerto")))[0][1]
        for folder in dead_folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', "muerto", folder)):
                self.enemy_dead_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_dead_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def invulnerability_timer(self):
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerability_time >= self.invulnerability_duration:
                self.invulnerable = False

    def check_player_enemy_collision(self):
        if not self.invulnerable:
            for enemy in self.enemy_sprites:
                if enemy.alive and enemy.hitbox_rect.colliderect(self.player.hitbox_rect):
                    self.player_lives -= 1
                    self.invulnerable = True
                    self.invulnerability_time = pygame.time.get_ticks()
                    
                    if self.player_lives <= 0:
                        print("¡Game Over!")
                        self.running = False
                    break

    def draw_lives(self):
        # Posición inicial para los corazones
        heart_x = 20
        heart_y = 20
        heart_spacing = 40  # Espacio entre corazones
        
        # Dibujar los corazones según las vidas actuales
        for i in range(INITIAL_LIVES):
            if i < self.player_lives:
                # Dibujar corazón lleno si aún tiene esta vida
                self.display_surface.blit(self.full_heart, (heart_x + i * heart_spacing, heart_y))
            else:
                # Dibujar corazón vacío si ha perdido esta vida
                self.display_surface.blit(self.empty_heart, (heart_x + i * heart_spacing, heart_y))

    def setup(self):
        map = load_pygame(join("data", "maps", "world.tmx"))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.ground_sprites)

        for obj in map.get_layer_by_name('Objetos'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Colisiones'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Enemigos'):
            if obj.name == 'Player':
                self.player = Player((obj.x,obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def run(self):
        while self.running:
            # dt 
            dt = self.clock.tick() / 1000

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    if len(self.enemy_sprites) < 10:  # Limita la cantidad máxima de enemigos
                        Enemy(
                            choice(self.spawn_positions),
                            self.enemy_frames, self.enemy_dead_frames,
                            (self.all_sprites, self.enemy_sprites),
                            self.player,
                            self.collision_sprites)

            # update 
            self.gun_timer()
            self.invulnerability_timer()
            self.input()
            
            # aplicar efecto de invulnerabilidad al jugador
            self.player.check_invulnerability_effect(self.invulnerable)
            
            self.all_sprites.update(dt)

            # colisiones
            self.check_player_enemy_collision()

            # Detectar colisión bala-enemigo
            for enemy in self.enemy_sprites:
                if enemy.alive:
                    for bullet in pygame.sprite.spritecollide(enemy, self.bullet_sprites, dokill=True):
                        enemy.hit()

            # draw
            self.display_surface.fill('black')
            self.ground_sprites.draw(self.display_surface)   # primero el suelo
            self.all_sprites.draw(self.player.rect.center)   # luego el resto
            self.draw_lives()  # mostrar vidas
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()