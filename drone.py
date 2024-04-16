import pygame   # biblioteca de criação de jogos 
import os       # integrar com arquivos do computador

# Load de imagens 
IMAGEM_DRONE = pygame.image.load(os.path.join('imgs', 'drone.png'))

class Drone:

    VELOCIDADE = 20

    def __init__(self, x, y):
        # Atributos do drone
        # x, y: posição do drone
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y    # posição no eixo y
        self.tempo = 0          # tempo de animação
        self.imagem = IMAGEM_DRONE  # a imagem em si, usada no momento

    # Essa função é executada a cada frame
    def mover_cima(self):
        self.y -= self.VELOCIDADE

    def mover_baixo(self):
        self.y += self.VELOCIDADE

    def desenhar(self, tela):
         # definir qual imagem do drone vai usar
         tela.blit(self.imagem, (self.x, self.y))

    # Importante para identificar a colisão dos objetos
    def get_mask(self):
        # mask é utilizada para identificar sobreposição de pixels 
        return pygame.mask.from_surface(self.imagem)

