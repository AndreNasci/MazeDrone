import pygame   # biblioteca de criação de jogos 
import os       # integrar com arquivos do computador
import neat

# Classes
from drone import Drone
from wall import Wall

# Variáveis globais
ai_jogando = True
geracao = 0

# Constantes
# Tamanho da tela
TELA_LARGURA = 800 
TELA_ALTURA = 650    

# Load de imagens 
IMAGEM_WALL = pygame.image.load(os.path.join('imgs', 'wall.png'))
IMAGEM_BACKGROUND = pygame.image.load(os.path.join('imgs', 'map.png'))
IMAGEM_DRONE = pygame.image.load(os.path.join('imgs', 'drone.png'))

# Texto usado (familia, tamanho)
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 40)


# Função auxiliar que desenha a tela do jogo
def desenhar_tela(tela, drones, walls, pontos):
    # Desenha o fundo
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    
    # Desenha drones
    for i in range(10):
        if i >= len(drones):
            break
        drones[i].desenhar(tela)

    # Desenha walls
    for wall in walls:
        wall.desenhar(tela)

    # Renderiza texto (texto, arredondado, rgb)
    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), TELA_ALTURA - 10 - texto.get_height())) # (texto, posicao)

    if ai_jogando:
        # Texto Geração
        texto = FONTE_PONTOS.render(f"Geração: {geracao}", 1, (255, 255, 255))
        tela.blit(texto, (10, TELA_ALTURA - 10 - texto.get_height())) # (texto, posicao)

    # Atualiza tela
    pygame.display.update()

# Fitness function
# Lógica de funcionamento do jogo 
# genomas - cria um drone para cada instancia dessa lista
def main(genomas, config):
    global geracao
    geracao += 1

    # Cria instancias das classes
    if ai_jogando:
        # link pelo indice entre as 3 listas
        redes = []
        lista_genomas = []
        drones = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config) # cria rede neural
            redes.append(rede)
            genoma.fitness = 0  # pontuação do genoma
            lista_genomas.append(genoma)
            drones.append(Drone(230, 350))
    else:
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

            if not ai_jogando:
                # eventos do teclado
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP:
                        for drone in drones:
                            drone.mover_cima()
                    elif evento.key == pygame.K_DOWN:
                        for drone in drones:
                            drone.mover_baixo()

        indice_wall = 0
        if len(drones) > 0:
            if len(walls) > 1 and drones[0].x > (walls[0].x + walls[0].WALL_TOPO.get_width()):
                indice_wall = 1 # pode estar errado
        else:
            rodando = False
            break


        # aumenta fitness dos drones | controle do drone pela NN
        for i, drone in enumerate(drones):
            lista_genomas[i].fitness += 0.1

            # entre -1 e 1
            output = redes[i].activate((drone.y, 
                                        abs(drone.y - walls[indice_wall].altura), 
                                        abs(drone.y - walls[indice_wall].pos_base))) 

            if output[0] > 0.5:
                drone.mover_cima()
            if output[1] > 0.5:
                drone.mover_baixo()
            



        adicionar_wall = False
        remover_wall = []
        for wall in walls:
            for i, drone in enumerate(drones): # i, com enumerate, retorna posição na lista
                if wall.colidir(drone):
                    drones.pop(i) # remove drones que colidiram com o wall 
                    if ai_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)
                if not wall.passou and drone.x > wall.x:  # se o drone passou o wall
                    wall.passou = True      # atualiza variável
                    adicionar_wall = True   # adiciona novo wall
            wall.mover()                    # move wall
            if wall.x + wall.WALL_TOPO.get_width() < 0:     # remove walls que ja sairam da tela
                remover_wall.append(wall)  # adiciona em uma lista de walls para remover 

        if adicionar_wall:
            pontos += 1                 # ganha ponto quando passou do wall
            walls.append(Wall(900))     # adiciona wall na posição 600
            for fenoma in lista_genomas:
                genoma.fitness += 5     # reward para os drones que passaram as paredes
        for wall in remover_wall:       # remove walls
            walls.remove(wall)

        # verifica colisão do drone com chão ou com o teto de tela e remove drones
        for i, drone in enumerate(drones):
            if (drone.y + drone.imagem.get_height()) > 600 or drone.y < 0:
                drones.pop(i)
                if ai_jogando:
                    lista_genomas.pop(i)
                    redes.pop(i)

        # Desenhar a tela acontece somente depois da lógica do jogo
        desenhar_tela(tela, drones, walls, pontos)

def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,         # configuracoes da NN
                                neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, 
                                neat.DefaultStagnation, 
                                caminho_config)

    populacao = neat.Population(config) # criar população de drones

    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())
    
    if ai_jogando:
        populacao.run(main, 50)
    else:
        main(None, None)

# Se for executado diretamente pelo prompt, manualmente, vai rodar o main
# Se for importado por outro arquivo, não executa o que está dentro do if
if __name__ == '__main__':
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    rodar(caminho_config)
