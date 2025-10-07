from settings import * 

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'frente', 0
        self.image = pygame.image.load(join('images', 'player', 'FRENTE', '0.png')).convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)
    
        # movement 
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites

        # velocidad de animación (frames por segundo aprox)
        self.animation_speed = 12  

        # efecto de parpadeo para invulnerabilidad
        self.blink_timer = 0
        self.blink_duration = 150  # parpadea cada 150ms
        self.is_invulnerable = False  # guardar estado de invulnerabilidad

    def load_images(self):
        self.frames = {'izquierda': [], 'derecha': [], 'frente': [], 'atras': []}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
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

    def animate(self, dt):
        # get state 
        if self.direction.x != 0:
            self.state = 'derecha' if self.direction.x > 0 else 'izquierda'
        if self.direction.y != 0:
            self.state = 'frente' if self.direction.y > 0 else 'atras'

        # animate con velocidad ajustable
        if self.direction:  
            self.frame_index += self.animation_speed * dt
        else:
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
        
        # Aplicar efecto de invulnerabilidad DESPUÉS de cargar la imagen normal
        if self.is_invulnerable:
            # Parpadeo blanco cada cierto tiempo
            if (pygame.time.get_ticks() // self.blink_duration) % 2:
                # Crear una copia de la imagen y hacerla blanca manteniendo la transparencia
                temp_image = self.image.copy()
                
                # Crear máscara para mantener solo los píxeles no transparentes
                mask = pygame.mask.from_surface(temp_image)
                white_surface = mask.to_surface(setcolor=(255, 255, 255, 200))
                white_surface.set_colorkey((0, 0, 0))  # Hacer el fondo negro transparente
                
                self.image = white_surface

    def check_invulnerability_effect(self, invulnerable):
        ##Estado de invulnerabilidad
        self.is_invulnerable = invulnerable

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)