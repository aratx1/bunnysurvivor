from settings import *


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((ANCHO_VENTADA, ALTO_VENTA))
        pygame.display.set_caption("Bunny Survivor!")
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            #dt
            dt = self.clock.tick() / 1000

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            #update

            #draw
            pygame.display.update()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()



