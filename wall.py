import pygame   # biblioteca de criação de jogos 
import os       # integrar com arquivos do computador
import random

# Load de imagens 
IMAGEM_WALL = pygame.image.load(os.path.join('imgs', 'wall.png'))

class Wall:
    # Constantes do wall
    DISTANCIA = 200 # distancia de um para o outro
    VELOCIDADE = 5  # velocidade de movimentação do wall

    def __init__(self, x):
        self.x = x
        self.altura = 0
        # posição no eixo y
        self.pos_topo = 0
        self.pos_base = 0
        # imagens do wall
        self.WALL_TOPO = IMAGEM_WALL
        self.WALL_BASE = IMAGEM_WALL
        # Diz se o wall ja passou do drone
        self.passou = False
        # gera altura do wall
        self.definir_altura()

    # Gera o ponto de referência para altura dos walls de cima e de baixo
    def definir_altura(self):
        self.altura = random.randrange(0, 410) # restringe o range do numero intervalo
        # restringir torna menos provável que uma dupla de walls vá surgir muito distante da proxima
        # posição do wall do topo
        self.pos_topo = self.altura - self.WALL_TOPO.get_height() 
        # posição do wall da base
        self.pos_base = self.altura + self.DISTANCIA

    # Função que move o wall
    def mover(self):
        self.x -= self.VELOCIDADE

    # Desenha o wall na tela
    def desenhar(self, tela):
        tela.blit(self.WALL_TOPO, (self.x, self.pos_topo))
        tela.blit(self.WALL_BASE, (self.x, self.pos_base))

    # Verifica se a mascara de pixels do drone colide com a mascara do wall
    def colidir(self, drone):
        drone_mask = drone.get_mask()
        topo_mask = pygame.mask.from_surface(self.WALL_TOPO) # imagem do topo
        base_mask = pygame.mask.from_surface(self.WALL_BASE) # imagem da base

        # # dist. da mascara do topo para a mascara do drone
        distancia_topo = (self.x - drone.x, self.pos_topo - round(drone.y)) 
        # # dist. da mascara da base para a mascara do drone
        distancia_base = (self.x - drone.x, self.pos_base - round(drone.y))

        # verifica se há overlap das mascaras (retorna verdadeiro se há colisão)
        topo_ponto = drone_mask.overlap(topo_mask, distancia_topo)
        base_ponto = drone_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False

