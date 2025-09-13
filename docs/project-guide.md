Agente Q-Learning para Jogo de Plataformas
🎮 Sobre o Projeto

Este projeto implementa um agente inteligente que joga automaticamente um jogo de plataformas com 24 casas numeradas de 0 a 23.

O agente aprende qual ação tomar (girar para esquerda, girar para direita ou pular) para maximizar suas recompensas usando Q-Learning, uma técnica de aprendizado por reforço.

🕹️ Como o Jogo Funciona

Plataformas: 24 casas (0 a 23).

Ações do agente:

0 → Girar para a esquerda

1 → Girar para a direita

2 → Pular

Recompensas:

Cada plataforma tem um valor de recompensa.

Algumas plataformas especiais dão +300 pontos.

Se o agente morrer, recebe -100 e volta automaticamente para a plataforma 0.

Movimento não determinístico:

Nem sempre a ação escolhida é executada corretamente.

O agente precisa aprender o melhor caminho considerando chances de sucesso e risco de morte.

Evitar loops:

Se o agente repetir sequências de ações sem progresso, é forçado a pular para sair do loop.

🧠 Como o Agente Aprende

Q-Learning: O agente constrói uma Q-table (96 estados x 3 ações) que armazena o valor esperado de cada ação em cada estado.

Estados:

Representados em binário, combinando plataforma (0–23) e direção (0–3).

24 plataformas × 4 direções = 96 estados.

Treinamento:

O agente joga episódios consecutivos, cada episódio termina com a morte do agente.

Auto-save da Q-table a cada 100 episódios.

Inicialmente 200 episódios para teste, depois pode ser aumentado para aprendizado completo.
