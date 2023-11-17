import pygame   # biblioteca de criação de jogos 
import os       # integrar com arquivos do computador
import random

# Constantes (padrão letra maiúscula)
# Tamanho da tela
TELA_LARGURA = 800 
TELA_ALTURA = 650    

# join = junta pasta com nome do arquivo
# image.load = carrega imagem 
IMAGEM_WALL = pygame.image.load(os.path.join('imgs', 'wall.png'))
IMAGEM_BACKGROUND = pygame.image.load(os.path.join('imgs', 'map.png'))
IMAGEM_DRONE = pygame.image.load(os.path.join('imgs', 'drone.png'))

# Texto usado (familia, tamanho)
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 40)


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



# Função auxiliar que desenha a tela do jogo
def desenhar_tela(tela, drones, walls, pontos):
    # Desenha o fundo
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    # Desenha passaros (mais de um por causa da IA)
    for drone in drones:
        drone.desenhar(tela)

    # Desenha walls
    for wall in walls:
        wall.desenhar(tela)

    # Renderiza texto (texto, arredondado, rgb)
    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), TELA_ALTURA - 10 - texto.get_height())) # (texto, posicao)

    # Atualiza tela
    pygame.display.update()

# Lógica de funcionamento do jogo
def main():
    # Cria instancias das classes
    drones = [Drone(230, 350)]
    
    walls = [Wall(700), Wall(1050)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(30)    # roda o relógio de acordo com o framerate indicado (30fps)

        # interação com o usuário
        for evento in pygame.event.get():
            # Fechar a tela
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()   # fecha pygame
                quit()          # sai do código

            # eventos do teclado
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    for drone in drones:
                        drone.mover_cima()
                elif evento.key == pygame.K_DOWN:
                    for drone in drones:
                        drone.mover_baixo()

        adicionar_wall = False
        remover_wall = []
        for wall in walls:
            for i, drone in enumerate(drones): # i, com enumerate, retorna posição na lista
                if wall.colidir(drone):
                    drones.pop(i) # remove passaros que colidiram com o wall 
                if not wall.passou and drone.x > wall.x:  # se o drone passou o wall
                    wall.passou = True      # atualiza variável
                    adicionar_wall = True   # adiciona novo wall
            wall.mover()                    # move wall
            if wall.x + wall.WALL_TOPO.get_width() < 0:     # remove walls que ja sairam da tela
                remover_wall.append(wall)  # adiciona em uma lista de walls para remover 

        if adicionar_wall:
            pontos += 1                 # ganha ponto quando passou do wall
            walls.append(Wall(900))     # adiciona wall na posição 600
        for wall in remover_wall:      # remove walls
            walls.remove(wall)

        # verifica colisão do drone com chão ou com o teto de tela e remove passaros
        for i, drone in enumerate(drones):
            if (drone.y + drone.imagem.get_height()) > 600 or drone.y < 0:
                drones.pop(i)

        # Desenhar a tela acontece somente depois da lógica do jogo
        desenhar_tela(tela, drones, walls, pontos)


# Se for executado diretamente pelo prompt, manualmente, vai rodar o main
# Se for importado por outro arquivo, não executa o que está dentro do if
if __name__ == '__main__':
    main()
