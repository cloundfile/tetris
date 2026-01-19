import pygame
import random
import os

pygame.init()

# --- CONFIGURAÇÕES ---
TAM_BLOCO = 40
COLS, LINHAS = 10, 20

# Configuração inicial do display
pygame.display.set_caption("Tetris Cube")
TELA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA, ALTURA = TELA.get_size()
MODO_FULLSCREEN = True

# Dimensões para modo janela (calculadas para caber tabuleiro + painel)
LARGURA_JANELA = (COLS * TAM_BLOCO) + 300
ALTURA_JANELA = (LINHAS * TAM_BLOCO) + 100

# Cores (Mais vibrantes e saturadas baseadas na imagem)
PRETO = (10, 10, 15)  # Fundo quase preto
BRANCO = (255, 255, 255)
CINZA_FUNDO = (20, 20, 20) # Cor base dos quadrados de fundo
CINZA_BORDA = (35, 35, 35) # Borda dos quadrados de fundo

CORES = [
    (0, 160, 255),    # Azul Ciano
    (255, 210, 10),   # Amarelo Ouro
    (50, 230, 50),    # Verde Vibrante
    (255, 30, 60),    # Vermelho Vivo
    (220, 0, 255),    # Roxo/Magenta
    (255, 120, 0),    # Laranja
    (0, 80, 255)      # Azul Profundo
]

# Formas
FORMAS = [
    [[1,1,1,1]],             # I
    [[1,1,1],[0,1,0]],       # T
    [[1,1,0],[0,1,1]],       # S
    [[0,1,1],[1,1,0]],       # Z
    [[1,1],[1,1]],           # O
    [[1,1,1],[1,0,0]],       # L
    [[1,1,1],[0,0,1]]        # J
]

# --- CLASSES E FUNÇÕES ---
def criar_grid():
    return [[0 for _ in range(COLS)] for _ in range(LINHAS)]

class Peca:
    def __init__(self, x, y, forma):
        self.x = x
        self.y = y
        self.forma = forma
        self.cor = random.choice(CORES)

def colisao(peca, grid, dx=0, dy=0):
    for i, linha in enumerate(peca.forma):
        for j, bloco in enumerate(linha):
            if bloco:
                x = peca.x + j + dx
                y = peca.y + i + dy
                if x < 0 or x >= COLS or y >= LINHAS or grid[y][x]:
                    return True
    return False

def fixar_peca(peca, grid):
    for i, linha in enumerate(peca.forma):
        for j, bloco in enumerate(linha):
            if bloco:
                grid[peca.y + i][peca.x + j] = CORES.index(peca.cor) + 1

def remover_linhas(grid):
    linhas_removidas = 0
    for i in range(LINHAS-1,-1,-1):
        if 0 not in grid[i]:
            grid.pop(i)
            grid.insert(0,[0 for _ in range(COLS)])
            linhas_removidas +=1
    return linhas_removidas

def rotacionar(peca):
    peca.forma = [list(x)[::-1] for x in zip(*peca.forma)]

def desenhar_bloco_cube(tela, x, y, cor, fundo=False):
    # Dimensões e padding para o chanfro (bevel)
    # Na imagem, o chanfro parece ocupar cerca de 20% do bloco
    offset = TAM_BLOCO // 5
    
    # Cores de sombreamento
    if fundo:
        # Fundo: Cores muito escuras e sutis
        face_cor = (min(cor[0] + 5, 255), min(cor[1] + 5, 255), min(cor[2] + 5, 255))
        brilho = (cor[0] + 15, cor[1] + 15, cor[2] + 15)
        sombra = (max(cor[0] - 10, 0), max(cor[1] - 10, 0), max(cor[2] - 10, 0))
    else:
        # Peças: Cores vibrantes e contraste alto
        face_cor = cor
        brilho = (min(cor[0] + 80, 255), min(cor[1] + 80, 255), min(cor[2] + 80, 255))
        sombra = (max(cor[0] - 60, 0), max(cor[1] - 60, 0), max(cor[2] - 60, 0))

    # Desenhar os 4 trapézios que formam o bevel (chanfro)
    # Topo (mais claro)
    pygame.draw.polygon(tela, brilho, [
        (x, y), (x + TAM_BLOCO, y), 
        (x + TAM_BLOCO - offset, y + offset), (x + offset, y + offset)
    ])
    # Esquerda (mais claro)
    pygame.draw.polygon(tela, brilho, [
        (x, y), (x + offset, y + offset), 
        (x + offset, y + TAM_BLOCO - offset), (x, y + TAM_BLOCO)
    ])
    # Baixo (mais escuro)
    pygame.draw.polygon(tela, sombra, [
        (x, y + TAM_BLOCO), (x + offset, y + TAM_BLOCO - offset), 
        (x + TAM_BLOCO - offset, y + TAM_BLOCO - offset), (x + TAM_BLOCO, y + TAM_BLOCO)
    ])
    # Direita (mais escuro)
    pygame.draw.polygon(tela, sombra, [
        (x + TAM_BLOCO, y), (x + TAM_BLOCO - offset, y + offset), 
        (x + TAM_BLOCO - offset, y + TAM_BLOCO - offset), (x + TAM_BLOCO, y + TAM_BLOCO)
    ])

    # Desenhar a face central quadrada
    pygame.draw.rect(tela, face_cor, (x + offset, y + offset, TAM_BLOCO - 2*offset, TAM_BLOCO - 2*offset))
    
    # Linha preta fina divisória (opcional, na imagem parece ter uma separação mínima)
    pygame.draw.rect(tela, (5, 5, 5), (x, y, TAM_BLOCO, TAM_BLOCO), 1)

def desenhar_vidro(tela, rect, cor=(0, 0, 0), alpha=160):
    # Cria uma superfície temporária para o efeito de transparência
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((*cor, alpha))
    tela.blit(s, (rect.x, rect.y))
    # Borda fina
    pygame.draw.rect(tela, (60, 60, 60), rect, 2)

def desenhar_tabuleiro(tela, grid, tabuleiro_x, tabuleiro_y):
    # Fundo do tabuleiro com os blocos 3D (para visibilidade da grade)
    cor_grid = (20, 20, 22) 
    for i in range(LINHAS):
        for j in range(COLS):
            x = tabuleiro_x + j*TAM_BLOCO
            y = tabuleiro_y + i*TAM_BLOCO
            desenhar_bloco_cube(tela, x, y, cor_grid, fundo=True)
    
    # Peças fixas
    for i in range(LINHAS):
        for j in range(COLS):
            if grid[i][j]:
                cor = CORES[grid[i][j]-1]
                desenhar_bloco_cube(tela, tabuleiro_x + j*TAM_BLOCO, tabuleiro_y + i*TAM_BLOCO, cor)

def desenhar_peca(tela, peca, tabuleiro_x, tabuleiro_y):
    for i, linha in enumerate(peca.forma):
        for j, bloco in enumerate(linha):
            if bloco:
                x = tabuleiro_x + (peca.x + j)*TAM_BLOCO
                y = tabuleiro_y + (peca.y + i)*TAM_BLOCO
                desenhar_bloco_cube(tela, x, y, peca.cor)

def desenhar_proxima_peca(tela, proxima, centro_x, y):
    largura_peca = len(proxima.forma[0]) * TAM_BLOCO
    start_x = centro_x - (largura_peca // 2)
    for i, linha in enumerate(proxima.forma):
        for j, bloco in enumerate(linha):
            if bloco:
                desenhar_bloco_cube(tela, start_x + j*TAM_BLOCO, y + i*TAM_BLOCO, proxima.cor)

def desenhar_texto(tela, texto, tamanho, x, y, cor=BRANCO, centralizado=True):
    fonte = pygame.font.SysFont("Arial", tamanho, bold=True)
    superficie = fonte.render(texto, True, cor)
    rect = superficie.get_rect()
    if centralizado:
        rect.center = (x,y)
    else:
        rect.topleft = (x,y)
    tela.blit(superficie, rect)

def desenhar_moldura_3d(tela, x, y, largura, altura, cor_base):
    # Efeito 3D
    sombra_clara = (min(cor_base[0]+50,255), min(cor_base[1]+50,255), min(cor_base[2]+50,255))
    sombra_escura = (max(cor_base[0]-80,0), max(cor_base[1]-80,0), max(cor_base[2]-80,0))

    pygame.draw.rect(tela, cor_base, (x, y, largura, altura))

    # Bordas 3D
    pygame.draw.line(tela, sombra_clara, (x, y), (x+largura, y), 4)   # topo
    pygame.draw.line(tela, sombra_clara, (x, y), (x, y+altura), 4)    # esquerda
    pygame.draw.line(tela, sombra_escura, (x+largura, y), (x+largura, y+altura), 4)  # direita
    pygame.draw.line(tela, sombra_escura, (x, y+altura), (x+largura, y+altura), 4)  # baixo

class Botao:
    def __init__(self, x, y, largura, altura, texto, cor, cor_hover):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.cor = cor
        self.cor_hover = cor_hover
        self.clicado = False

    def desenhar(self, tela):
        pos_mouse = pygame.mouse.get_pos()
        cor_atual = self.cor_hover if self.rect.collidepoint(pos_mouse) else self.cor
        
        # Efeito de bloco 3D em toda a extensão do botão
        # Se for maior que um bloco, desenhamos com a lógica de chanfro expandida
        offset = TAM_BLOCO // 5
        brilho = (min(cor_atual[0] + 80, 255), min(cor_atual[1] + 80, 255), min(cor_atual[2] + 80, 255))
        sombra = (max(cor_atual[0] - 60, 0), max(cor_atual[1] - 60, 0), max(cor_atual[2] - 60, 0))

        # Chanfros do botão retangular
        pygame.draw.polygon(tela, brilho, [(self.rect.x, self.rect.y), (self.rect.right, self.rect.y), (self.rect.right - offset, self.rect.y + offset), (self.rect.x + offset, self.rect.y + offset)])
        pygame.draw.polygon(tela, brilho, [(self.rect.x, self.rect.y), (self.rect.x + offset, self.rect.y + offset), (self.rect.x + offset, self.rect.bottom - offset), (self.rect.x, self.rect.bottom)])
        pygame.draw.polygon(tela, sombra, [(self.rect.x, self.rect.bottom), (self.rect.x + offset, self.rect.bottom - offset), (self.rect.right - offset, self.rect.bottom - offset), (self.rect.right, self.rect.bottom)])
        pygame.draw.polygon(tela, sombra, [(self.rect.right, self.rect.y), (self.rect.right - offset, self.rect.y + offset), (self.rect.right - offset, self.rect.bottom - offset), (self.rect.right, self.rect.bottom)])
        
        # Centro
        pygame.draw.rect(tela, cor_atual, (self.rect.x + offset, self.rect.y + offset, self.rect.width - 2*offset, self.rect.height - 2*offset))
        pygame.draw.rect(tela, (5, 5, 5), self.rect, 1) # Borda
        
        desenhar_texto(tela, self.texto, 24, self.rect.centerx, self.rect.centery, BRANCO)

    def checar_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def criar_superficie_fundo(largura_tela, altura_tela):
    # Cria uma superfície persistente para o fundo para otimizar performance
    superficie = pygame.Surface((largura_tela, altura_tela))
    cor_fundo_base = (10, 10, 15)
    superficie.fill(cor_fundo_base)
    
    cor_bloco = (20, 20, 22)
    # Tiling por toda a tela
    for y in range(0, altura_tela, TAM_BLOCO):
        for x in range(0, largura_tela, TAM_BLOCO):
            desenhar_bloco_cube(superficie, x, y, cor_bloco, fundo=True)
            
    return superficie

# --- MAIN ---
def main():
    global TELA, LARGURA, ALTURA, MODO_FULLSCREEN
    import json
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_save = os.path.join(diretorio_atual, "savegame.json")

    def salvar_jogo(grid, score, level, lines, next_peca):
        estado = {
            "grid": grid,
            "score": score,
            "level": level,
            "lines": lines,
            "next_peca": FORMAS.index(next_peca.forma)
        }
        with open(caminho_save, "w") as f:
            json.dump(estado, f)

    def carregar_jogo():
        if os.path.exists(caminho_save):
            try:
                with open(caminho_save, "r") as f:
                    return json.load(f)
            except:
                return None
        return None

    clock = pygame.time.Clock()
    grid = criar_grid()
    peca = Peca(COLS//2-1, 0, random.choice(FORMAS))
    proxima = Peca(0,0, random.choice(FORMAS))
    pontuacao = 0
    nivel = 1
    linhas_totais = 0
    menu_inicial = carregar_jogo() is not None
    
    game_over = False
    pausado = False

    # Carrega imagem de fundo
    def carregar_e_ajustar_fundo():
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_img = os.path.join(diretorio_atual, "img", "bg.jpg")
        try:
            if os.path.exists(caminho_img):
                img = pygame.image.load(caminho_img).convert()
                return pygame.transform.scale(img, (LARGURA, ALTURA))
        except:
            pass
        fallback = pygame.Surface((LARGURA, ALTURA))
        fallback.fill((10, 10, 15))
        return fallback

    imagem_fundo = carregar_e_ajustar_fundo()

    # Botões de controle
    btn_fechar = Botao(LARGURA - 50, 10, 40, 40, "X", (200, 50, 50), (255, 80, 80))
    btn_redimensionar = Botao(LARGURA - 100, 10, 40, 40, "_", (80, 80, 80), (120, 120, 120))
    
    # Novo botão de Pause
    btn_pause = Botao(0, 0, 120, 40, "PAUSE", (50, 150, 50), (70, 200, 70))

    # Botão de Restart
    btn_restart = Botao(0, 0, 140, 40, "RESTART", (50, 200, 50), (70, 255, 70))

    # Botões do Menu Inicial
    btn_continuar = Botao(0, 0, 200, 50, "CONTINUE", (50, 150, 50), (70, 200, 70))
    btn_novo_jogo = Botao(0, 0, 200, 50, "NEW GAME", (150, 100, 50), (200, 130, 70))

    def reset_jogo():
        nonlocal grid, peca, proxima, pontuacao, nivel, linhas_totais, queda_velocidade, game_over, pausado, menu_inicial
        grid = criar_grid()
        peca = Peca(COLS//2-1, 0, random.choice(FORMAS))
        proxima = Peca(0,0, random.choice(FORMAS))
        pontuacao = 0
        nivel = 1
        linhas_totais = 0
        queda_velocidade = 500
        game_over = False
        pausado = False
        menu_inicial = False
        if os.path.exists(caminho_save):
            os.remove(caminho_save)
        pygame.time.set_timer(pygame.USEREVENT, queda_velocidade)

    def continuar_jogo():
        nonlocal grid, peca, proxima, pontuacao, nivel, linhas_totais, queda_velocidade, menu_inicial
        dados = carregar_jogo()
        if dados:
            grid = dados["grid"]
            pontuacao = dados["score"]
            nivel = dados["level"]
            linhas_totais = dados["lines"]
            proxima = Peca(0, 0, FORMAS[dados["next_peca"]])
            peca = Peca(COLS//2-1, 0, random.choice(FORMAS))
            queda_velocidade = max(100, 500 - (nivel - 1) * 50)
            pygame.time.set_timer(pygame.USEREVENT, queda_velocidade)
            menu_inicial = False

    queda_velocidade = 500
    pygame.time.set_timer(pygame.USEREVENT, queda_velocidade)

    rodando = True
    while rodando:
        TELA.blit(imagem_fundo, (0, 0))

        # Ajuste de layout baseado no modo
        if MODO_FULLSCREEN:
            tabuleiro_x = (LARGURA - COLS*TAM_BLOCO)//2
            tabuleiro_y = (ALTURA - LINHAS*TAM_BLOCO)//2
            btn_fechar.rect.x = LARGURA - 50
            btn_redimensionar.rect.x = LARGURA - 100
        else:
            tabuleiro_x = 50
            tabuleiro_y = 50
            btn_fechar.rect.x = LARGURA - 50
            btn_redimensionar.rect.x = LARGURA - 100

        # Moldura 3D ao redor do tabuleiro
        desenhar_moldura_3d(TELA, tabuleiro_x-4, tabuleiro_y-4, COLS*TAM_BLOCO+8, LINHAS*TAM_BLOCO+8, (30,30,30))

        # Desenhar grid e peça atual
        desenhar_tabuleiro(TELA, grid, tabuleiro_x, tabuleiro_y)
        desenhar_peca(TELA, peca, tabuleiro_x, tabuleiro_y)

        # Painel lateral
        painel_offset_x = 50 if not MODO_FULLSCREEN else 150
        padding = 20
        largura_painel = 240
        altura_painel = 420
        
        painel_rect = pygame.Rect(
            tabuleiro_x + COLS*TAM_BLOCO + painel_offset_x,
            tabuleiro_y,
            largura_painel,
            altura_painel
        )
        
        # Desenhar fundo do painel lateral (preto transparente)
        desenhar_vidro(TELA, painel_rect)

        # Elementos dentro do painel (centralizados)
        centro_painel_x = painel_rect.centerx
        elem_y = painel_rect.y + padding

        # Próxima peça
        desenhar_texto(TELA, "NEXT", 28, centro_painel_x, elem_y, centralizado=True)
        desenhar_proxima_peca(TELA, proxima, centro_painel_x, elem_y + 40)

        # Pontuação e Nível
        desenhar_texto(TELA, "LEVEL", 24, centro_painel_x, elem_y + 140, centralizado=True)
        desenhar_texto(TELA, str(nivel), 32, centro_painel_x, elem_y + 175, centralizado=True, cor=(0, 255, 255))
        
        desenhar_texto(TELA, "SCORE", 24, centro_painel_x, elem_y + 220, centralizado=True)
        desenhar_texto(TELA, str(pontuacao), 32, centro_painel_x, elem_y + 255, centralizado=True, cor=(255,215,0))

        # Posicionar e desenhar botão de Pause (centralizado)
        btn_pause.rect.centerx = centro_painel_x
        btn_pause.rect.y = elem_y + 340
        btn_pause.texto = "PLAY" if pausado else "PAUSE"
        
        # Cores solicitadas: Verde para Play (quando pausado) e Vermelho para Pause (quando jogando)
        cor_base = (50, 200, 50) if pausado else (200, 50, 50)
        btn_pause.cor = cor_base
        btn_pause.cor_hover = (min(cor_base[0]+30, 255), min(cor_base[1]+30, 255), min(cor_base[2]+30, 255))
        btn_pause.desenhar(TELA)

        # Desenhar botões de controle
        btn_fechar.desenhar(TELA)
        btn_redimensionar.desenhar(TELA)

        # Overlay de Game Over
        if game_over:
            overlay_rect = pygame.Rect(LARGURA//2 - 150, ALTURA//2 - 100, 300, 200)
            desenhar_vidro(TELA, overlay_rect, cor=(30, 0, 0), alpha=220)
            desenhar_texto(TELA, "GAME OVER", 48, overlay_rect.centerx, overlay_rect.y + 40, cor=(255, 50, 50))
            desenhar_texto(TELA, f"Score: {pontuacao}", 24, overlay_rect.centerx, overlay_rect.y + 90)
            
            btn_restart.rect.centerx = overlay_rect.centerx
            btn_restart.rect.y = overlay_rect.y + 130
            btn_restart.desenhar(TELA)

        # Menu Inicial (Overlay)
        if menu_inicial:
            menu_rect = pygame.Rect(LARGURA//2 - 200, ALTURA//2 - 120, 400, 240)
            desenhar_vidro(TELA, menu_rect, alpha=240)
            desenhar_texto(TELA, "TETRIS CUBE", 48, menu_rect.centerx, menu_rect.y + 40, cor=(255, 255, 255))
            
            btn_continuar.rect.centerx = menu_rect.centerx
            btn_continuar.rect.y = menu_rect.y + 100
            btn_continuar.desenhar(TELA)
            
            btn_novo_jogo.rect.centerx = menu_rect.centerx
            btn_novo_jogo.rect.y = menu_rect.y + 165
            btn_novo_jogo.desenhar(TELA)

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            
            # Checar cliques nos botões
            if btn_fechar.checar_click(event):
                rodando = False
            
            if btn_redimensionar.checar_click(event):
                MODO_FULLSCREEN = not MODO_FULLSCREEN
                if MODO_FULLSCREEN:
                    TELA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    TELA = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
                
                LARGURA, ALTURA = TELA.get_size()
                imagem_fundo = carregar_e_ajustar_fundo()
                # Atualiza posição dos botões para o novo tamanho
                btn_fechar.rect.x = LARGURA - 50
                btn_redimensionar.rect.x = LARGURA - 100

            if menu_inicial:
                if btn_continuar.checar_click(event):
                    continuar_jogo()
                if btn_novo_jogo.checar_click(event):
                    reset_jogo()
                continue # Pula o resto dos eventos se estiver no menu

            if btn_pause.checar_click(event):
                pausado = not pausado

            if game_over and btn_restart.checar_click(event):
                reset_jogo()

            elif event.type == pygame.USEREVENT:
                if not pausado and not game_over and not menu_inicial:
                    if not colisao(peca, grid, dy=1):
                        peca.y += 1
                    else:
                        fixar_peca(peca, grid)
                        linhas_removidas = remover_linhas(grid)
                        if linhas_removidas > 0:
                            linhas_totais += linhas_removidas
                            pontuacao += linhas_removidas * 100 * nivel
                            # Lógica de Nível (fase)
                            novo_nivel = (linhas_totais // 10) + 1
                            if novo_nivel > nivel:
                                nivel = novo_nivel
                                queda_velocidade = max(100, 500 - (nivel - 1) * 50)
                                pygame.time.set_timer(pygame.USEREVENT, queda_velocidade)

                        peca = proxima
                        proxima = Peca(0,0,random.choice(FORMAS))
                        if colisao(peca, grid):
                            game_over = True
                            if os.path.exists(caminho_save):
                                os.remove(caminho_save)
            elif event.type == pygame.KEYDOWN:
                if not pausado and not game_over and not menu_inicial:
                    if event.key == pygame.K_LEFT and not colisao(peca, grid, dx=-1):
                        peca.x -= 1
                    elif event.key == pygame.K_RIGHT and not colisao(peca, grid, dx=1):
                        peca.x += 1
                    elif event.key == pygame.K_DOWN and not colisao(peca, grid, dy=1):
                        peca.y += 1
                    elif event.key == pygame.K_UP:
                        rotacionar(peca)
                        if colisao(peca, grid):
                            # desfaz rotação
                            rotacionar(peca)
                            rotacionar(peca)
                            rotacionar(peca)
    
    # Salva ao fechar
    if not game_over and not menu_inicial:
        salvar_jogo(grid, pontuacao, nivel, linhas_totais, proxima)
    
    pygame.quit()

if __name__ == "__main__":
    main()
