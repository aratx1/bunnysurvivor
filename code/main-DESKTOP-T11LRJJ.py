from settings import *
from player import Player


class Game:
    def __init__(self):

        #setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((ANCHO_VENTADA, ALTO_VENTA))
        pygame.display.set_caption("Bunny Survivor!")
        self.clock = pygame.time.Clock()
        self.running = True

        #groups
        self.all_sprites = pygame.sprite.Group()

        #sprites
        self.player = Player((400, 300), self.all_sprites)

    def run(self):
        while self.running:
            #dt
            dt = self.clock.tick() / 1000

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            #update
            self.all_sprites.update(dt)

            #draw
            pygame.display.update()
            self.all_sprites.draw(self.display_surface)

        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()



