# PYGAME_2026.1
Pygame desenvolvido por Gabriel Rodrigues, Henrique Martins e Juliana Pires
Baseado em um jogos como 'Golf with your friends', 'Mini Golf Club' e '8 ball pool', é um jogo com os objetivos do golf, com alguns incrementos, e uma mecânica em relação as tacadas parecida com jogos de sinuca. A meta do jogo é simples, chegar ao buraco com o mínimo de tacadas possíveis, ou caso jogue em grupo, menos tacadas que o seu adversário.

VÍDEO COM GAMEPLAY (MOSTRA A FUNCIONALIDADE DO JOGO)

(adicionar link do vídeo aqui)

Durante o desenvolvimento, utilizamos principalmente a documentação oficial do Pygame, vídeos no YouTube sobre física, colisão e organização de projetos em Python, além de apoio pontual de IA para dúvidas relacionadas à modularização do código, organização dos arquivos, funcionamento de classes, colisões, estruturas de dados e correção de pequenos bugs encontrados ao longo do projeto.

O jogo necessita dos seguintes arquivos no mesmo diretório:
inicio.py
config.py
paredes.py
buracos_fase.py
agua.py
areia.py
esteiras.py
tuneis.py
paredes_moveis.py
ranking.py
ranking_golf.json (criado automaticamente)
buraco.wav
tacada.wav

MODO DE EXECUÇÃO
Clone ou baixe o repositório.

Instale o Pygame:
pip install pygame

Execute o jogo utilizando:
python inicio.py

CONTROLES
Mouse esquerdo → clicar, arrastar e soltar para realizar a tacada
ESC → sair do jogo ou voltar dependendo da tela atual
SPACE → avançar para a próxima fase após concluir o buraco
R → reiniciar o jogo na tela final/ranking

COMO JOGAR
O objetivo do jogo é completar todas as fases utilizando o menor número possível de tacadas. Cada mapa possui obstáculos e mecânicas diferentes, exigindo precisão, estratégia e controle de força nas jogadas.

As principais mecânicas do jogo incluem:
Areia: reduz significativamente a velocidade da bola.
Água: retorna a bola para a última posição válida e adiciona penalidade de tacada.
Túneis: funcionam como portais que transportam a bola entre dois pontos do mapa.
Esteiras: empurram continuamente a bola na direção indicada.
Paredes móveis: obstáculos dinâmicos que exigem timing correto para ultrapassar.

Ao concluir todas as fases, o jogo exibe um ranking final e salva automaticamente os melhores resultados em um arquivo JSON.

ESTRUTURA DO PROJETO
inicio.py → loop principal, menu, controle das fases e gerenciamento do jogo.
config.py → constantes globais, cores e configurações gerais.
paredes.py → classes Parede e Jogador.
buracos_fase.py → física, colisões e renderização das fases.
agua.py → classe Agua.
areia.py → classe Areia.
esteiras.py → classe Esteira.
tuneis.py → classe Tunel.
paredes_moveis.py → classe ParedeMovel.
ranking.py → sistema de ranking e salvamento de resultados.
ranking_golf.json → armazenamento automático do ranking.

PROBLEMAS E SOLUÇÕES
Tela preta ou erro de importação
Verifique se todos os arquivos .py estão no mesmo diretório.

Erro ao iniciar o jogo
Confirme se o Pygame foi instalado corretamente:
pip install pygame

Sons não funcionam
Verifique se os arquivos .wav utilizados estão nos caminhos corretos.

Ranking não salva
O arquivo ranking_golf.json é criado automaticamente após finalizar uma partida.

FUNCIONALIDADES IMPLEMENTADAS
múltiplas fases;
sistema de tacadas com física;
colisão com paredes;
areia e água;
túneis teleporte;
esteiras animadas;
paredes móveis;
ranking salvo automaticamente;
tela final com ranking;
multiplayer local por turnos;
menu inicial;
HUD durante a gameplay;
efeitos sonoros.

TECNOLOGIAS UTILIZADAS
Python
Pygame
JSON para armazenamento de ranking e dados persistentes

CRÉDITOS
Python e Pygame
Professor Márcio Fernando