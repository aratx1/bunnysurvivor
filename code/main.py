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
        self.game_over = False   # <- nuevo estado
        self.game_started = False  # <- añadir solo esta línea
        self.load_images()

        # groups 
        self.all_sprites = AllSprites()
        self.ground_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # sistema de vidas, contador de enemigos
        self.player_lives = INITIAL_LIVES
        self.invulnerable = False
        self.invulnerability_time = 0
        self.invulnerability_duration = INVULNERABILITY_TIME
        self.enemy_counter = INITIAL_ENEMIES

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0 
        self.gun_cooldown = 1000

        # enemy timer 
        self.enemy_event = pygame.event.custom_type()
        # pygame.time.set_timer(self.enemy_event, 1000)  # <- comentar esta línea
        self.spawn_positions = []
        
        #audio
        self.background_sound = pygame.mixer.Sound(join("audio", "katamari.mp3"))
        self.background_sound.set_volume(0.6)

        self.shoot_sound = pygame.mixer.Sound(join("audio", "escopeta.mp3"))
        self.shoot_sound.set_volume(0.6)

        self.player_impact_sound = pygame.mixer.Sound(join("audio", "golpeplayer.mp3"))
        self.player_impact_sound.set_volume(0.3)
        self.enemy_impact_sound = pygame.mixer.Sound(join("audio", "golpeenemigo.mp3"))
        self.enemy_impact_sound.set_volume(0.3)


        # setup
        self.load_images()
        self.setup()

        # --- cargar fuente y fondo para la pantalla de Game Over ---
        self.game_start_bg = pygame.image.load(join("images", "menu", "fondoinicio.png")).convert()
        self.game_start_font = pygame.font.Font(join("fonts", "m6x11plus.ttf"), 80)  

        # --- cargar fuente y fondo para la pantalla de Start ---
        self.game_over_bg = pygame.image.load(join("images", "menu", "fondofinal.png")).convert()
        self.game_over_font = pygame.font.Font(join("fonts", "m6x11plus.ttf"), 80)  

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'gun', 'bala.png')).convert_alpha()

        #Cargar imagen de contador de enemigos
        self.skull = pygame.image.load(join('images', 'items', 'Skull.png')).convert_alpha()
        
        # Cargar imagenes de corazones para el sistema de vidas
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
            self.shoot_sound.play()
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
                    self.player_impact_sound.play() 
                    self.invulnerable = True
                    self.invulnerability_time = pygame.time.get_ticks()
                    
                    if self.player_lives <= 0:
                        self.game_over_screen()  # muestra pantalla 
                    break

    def draw_lives(self):
        # PosiciÃ³n inicial para los corazones
        heart_x = 20
        heart_y = 20
        heart_spacing = 40  # Espacio entre corazones
        
        # Dibujar los corazones segÃºn las vidas actuales
        for i in range(INITIAL_LIVES):
            if i < self.player_lives:
                self.display_surface.blit(self.full_heart, (heart_x + i * heart_spacing, heart_y))
            else:
                self.display_surface.blit(self.empty_heart, (heart_x + i * heart_spacing, heart_y))

    def draw_enemy_counter(self):
        # Posición del icono de calavera (debajo de las vidas)
        skull_x = 20
        skull_y = 90  # un poco más abajo que los corazones
    
        # Dibujar la calavera
        self.display_surface.blit(self.skull, (skull_x, skull_y))

        # Fuente para el número
        font = pygame.font.Font(join("fonts", "m6x11plus.ttf"), 40)
        text_surface = font.render(str(self.enemy_counter), True, (255, 255, 255))

        # Mostrar número al costado derecho del icono
        text_rect = text_surface.get_rect(midleft=(skull_x + self.skull.get_width() + 10, skull_y + self.skull.get_height()//2))
        self.display_surface.blit(text_surface, text_rect)


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

    def game_over_screen(self):
        self.background_sound.stop()
        self.game_over = True
        while self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = False
                    self.running = False
                # <- añadir solo estas líneas
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                        self.game_over = False

            # dibujar fondo
            self.display_surface.blit(self.game_over_bg, (0, 0))

            # renderizar texto
            text_surface = self.game_over_font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(ANCHO_VENTANA//2, ALTO_VENTANA//2))
            self.display_surface.blit(text_surface, text_rect)

            # <- añadir solo estas líneas
            restart_font = pygame.font.Font(join("fonts", "m6x11plus.ttf"), 40)
            restart_surface = restart_font.render("Presiona R para reiniciar", True, (255, 255, 255))
            restart_rect = restart_surface.get_rect(center=(ANCHO_VENTANA//2, ALTO_VENTANA//2 + 100))
            self.display_surface.blit(restart_surface, restart_rect)

            pygame.display.update()
            self.clock.tick(60)
        
    def game_start_screen(self):
        while not self.game_started and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.game_started = True
                        pygame.time.set_timer(self.enemy_event, 1000)
                        self.background_sound.play(-1)

            # dibujar fondo
            self.display_surface.blit(self.game_start_bg, (0, 0))

            # renderizar texto
            text_surface = self.game_start_font.render("¡¡BUNNY SURVIVOR!!", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(ANCHO_VENTANA//2, ALTO_VENTANA//2))
            self.display_surface.blit(text_surface, text_rect)

            # texto de pantalla 
            instruction_font = pygame.font.Font(join("fonts", "m6x11plus.ttf"), 40)
            instruction_surface = instruction_font.render("Presiona ENTER para comenzar", True, (255, 255, 255))
            instruction_rect = instruction_surface.get_rect(center=(ANCHO_VENTANA//2, ALTO_VENTANA//2 + 100))
            self.display_surface.blit(instruction_surface, instruction_rect)

            pygame.display.update()
            self.clock.tick(60)

    # reiniciar juego
    def restart_game(self):
        self.all_sprites.empty()
        self.ground_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        
        self.player_lives = INITIAL_LIVES
        self.invulnerable = False
        self.can_shoot = True
        self.spawn_positions = []
        
        self.setup()
        pygame.time.set_timer(self.enemy_event, 1000)

    def run(self):
        # <- añadir solo esta línea al inicio
        self.game_start_screen()
        
        while self.running:
            # dt 
            dt = self.clock.tick() / 1000

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    if len(self.enemy_sprites) < 10:
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

            # Detectar colisiÃ³n bala-enemigo
            for enemy in self.enemy_sprites:
                if enemy.alive:
                    for bullet in pygame.sprite.spritecollide(enemy, self.bullet_sprites, dokill=True):
                        enemy.hit()
                        self.enemy_impact_sound.play()
                        self.enemy_counter += 1

            # draw
            self.display_surface.fill('black')
            self.ground_sprites.draw(self.display_surface)   # primero el suelo
            self.all_sprites.draw(self.player.rect.center)   # luego el resto
            self.draw_lives()  # mostrar vidas
            self.draw_enemy_counter()  #mostrar contador de enemigos
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()