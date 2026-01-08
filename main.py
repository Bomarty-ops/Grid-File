import pygame
import random
from model import GridFile, Agente, Obstaculo
from view import SimulacionRenderer

# Configuración Global
# Dimensiones lógicas de la simulación
SIM_WIDTH = 800
SIM_HEIGHT = 600
# Altura extra para el panel UI (gráficos)
UI_HEIGHT = 150 
# Dimensiones totales de la ventana
WINDOW_WIDTH = SIM_WIDTH
WINDOW_HEIGHT = SIM_HEIGHT + UI_HEIGHT

BUCKET_CAPACITY = 10 

# --- CONTROLADOR PRINCIPAL ---
def main():
    # Inicializar Modelo con las dimensiones de la SIMULACIÓN (no de la ventana)
    grid = GridFile(SIM_WIDTH, SIM_HEIGHT, BUCKET_CAPACITY)
    agents = []
    
    # 2. Obstáculos (Paredes / Cuarentena)
    obstacles = [
        Obstaculo(300, 200, 20, 200), # Pared Vertical Central
        Obstaculo(100, 400, 200, 20), # Pared Horizontal I.I.
        Obstaculo(500, 100, 200, 20)  # Pared Horizontal S.D.
    ]
    
    # Inicializar con agentes sanos
    for _ in range(50):
        x = random.uniform(0, SIM_WIDTH)
        y = random.uniform(0, SIM_HEIGHT)
        # Evitar spawnear dentro de obstáculos
        valid_pos = True
        for o in obstacles:
            if o.rect.collidepoint(x, y):
                valid_pos = False
        if valid_pos:
            a = Agente(x, y, SIM_WIDTH, SIM_HEIGHT)
            a.state = 0
            agents.append(a)
            grid.insert(a)
    
    # Inicializar Vista con el tamaño TOTAL de la ventana
    renderer = SimulacionRenderer(WINDOW_WIDTH, WINDOW_HEIGHT)
    clock = pygame.time.Clock()
    running = True
    
    drag_start = None
    drag_current = None
    query_result = 0
    
    # Historial para gráficas [(sanos, infectados), ...]
    history = []
    history_timer = 0
    
    # --- BUCLE PRINCIPAL (GAME LOOP) ---
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    mx, my = event.pos
                    # IMPORTANTE: Ignorar clics en el área del UI
                    if my > SIM_HEIGHT:
                        continue

                    # Inyectar agentes infectados
                    for _ in range(30):
                        bx = mx + random.uniform(-20, 20)
                        by = my + random.uniform(-20, 20)
                        # Clampear a dimensiones de simulación
                        bx = max(0, min(bx, SIM_WIDTH))
                        by = max(0, min(by, SIM_HEIGHT))
                        
                        a = Agente(bx, by, SIM_WIDTH, SIM_HEIGHT)
                        a.state = 1 # Infectado
                        agents.append(a)
                        grid.insert(a)
                        
                elif event.button == 3:
                     # Ignorar clics UI
                    if event.pos[1] <= SIM_HEIGHT:
                        drag_start = event.pos
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    drag_start = None
                    drag_current = None
                    
            elif event.type == pygame.MOUSEMOTION:
                if drag_start:
                    cx, cy = event.pos
                    cy = min(cy, SIM_HEIGHT) # No arrastrar fuera de la simulación
                    drag_current = (cx, cy)
                    
        if drag_start and drag_current:
            x1, y1 = drag_start
            x2, y2 = drag_current
            qx = min(x1, x2)
            qy = min(y1, y2)
            qw = abs(x1 - x2)
            qh = abs(y1 - y2)
            query_rect = (qx, qy, qw, qh)
            query_result = grid.query_range(qx, qy, qw, qh)
        else:
            query_rect = None
            query_result = None

        # 1. Infección por Proximidad (Lógica del Grid File)
        # Solo los infectados pueden contagiar
        infectados = [a for a in agents if a.state == 1]
        for inf in infectados:
            # Consultar vecindario cercano (ej. 30px)
            radius = 30
            neighbors = grid.query_agents(inf.x - radius, inf.y - radius, radius*2, radius*2)
            
            for n in neighbors:
                if n.state == 0: # Si es sano
                    # Probabilidad de contagio
                    if random.random() < 0.05: # 5% por frame
                        n.state = 1

        # 2. Actualizar Agentes
        for a in agents:
            old_x, old_y = a.x, a.y
            a.move(obstacles) # Pasamos obstáculos para rebote
            grid.update(a, old_x, old_y)
            
        # 3. Actualizar Historial (cada 10 frames approx)
        if history_timer % 10 == 0:
            c_sanos = sum(1 for a in agents if a.state == 0)
            c_inf = sum(1 for a in agents if a.state == 1)
            history.append((c_sanos, c_inf))
            if len(history) > 200: history.pop(0) # Mantener ventana móvil
        history_timer += 1
            
        renderer.render(grid, agents, obstacles, history, query_rect, query_result)
        clock.tick(60)

    renderer.quit()

if __name__ == "__main__":
    main()