import pygame

# --- CLASE RENDERER (VISTA) ---
# Se encarga de toda la visualización usando Pygame.
# Recibe datos del modelo y los dibuja en pantalla.
class SimulacionRenderer:
    def __init__(self, width, height, title="Simulacion Grid File"):
        pygame.init()
        self.logical_width = width
        self.logical_height = height
        # Ventana redimensionable
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        # Canvas lógico donde dibujamos siempre a resolución fija
        self.canvas = pygame.Surface((width, height))
        
        pygame.display.set_caption(title)
        self.font = pygame.font.SysFont("Arial", 14)
        
    # Método principal de dibujo. Se llama en cada frame.
    def render(self, grid_file, agents, obstacles=[], history=[], query_rect=None, query_result=None):
        # 1. Limpiar canvas lógico (Fondo oscuro)
        self.canvas.fill((20, 20, 20))
        
        # 1.1 Dibujar Obstáculos
        self.draw_obstacles(obstacles)
        
        # 2. Dibujar líneas del Grid File (Escalas X)
        for x in grid_file.x_scales:
            # Usamos grid_file.height para no dibujar sobre el panel UI inferior
            pygame.draw.line(self.canvas, (50, 50, 50), (x, 0), (x, grid_file.height))
        # 3. Dibujar líneas del Grid File (Escalas Y)
        for y in grid_file.y_scales:
            pygame.draw.line(self.canvas, (50, 50, 50), (0, y), (self.logical_width, y))
            
        # Dibujar línea separadora del UI
        pygame.draw.line(self.canvas, (255, 255, 255), (0, grid_file.height), (self.logical_width, grid_file.height), 2)
            
        # 4. Dibujar Agentes
        for agent in agents:
            # Color Verde (Sano) o Rojo (Infectado)
            color = (0, 255, 0) if agent.state == 0 else (255, 0, 0)
            pygame.draw.circle(self.canvas, color, (int(agent.x), int(agent.y)), 3)
            
        # 5. Dibujar Rectángulo de Consulta (Si el usuario está arrastrando)
        if query_rect:
            x, y, w, h = query_rect
            s = pygame.Surface((w, h))
            s.set_alpha(50) # Transparencia para el efecto "Radar"
            s.fill((0, 255, 255))
            self.canvas.blit(s, (x, y))
            pygame.draw.rect(self.canvas, (0, 255, 255), query_rect, 1)
            
            # Mostrar conteo sobre el rectángulo
            if query_result is not None:
                text = self.font.render(f"Conteo: {query_result}", True, (255, 255, 255))
                self.canvas.blit(text, (x, y - 20))

        # 6. Dibujar Estadísticas y Métricas (MOVIDO AL PANEL INFERIOR)
        # El panel empieza en y = grid_file.height (600px).
        ui_start_y = grid_file.height + 10
        
        stats = grid_file.get_stats()
        info_lines = [
            f"Agentes: {stats['total_agents']}",
            f"Buckets: {stats['total_buckets']}",
            f"Grid: {stats['depth_x']}x{stats['depth_y']}",
            f"Utilizacion: {stats['utilization']:.2%}" # Porcentaje de llenado real
        ]
        
        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, (200, 200, 200))
            self.canvas.blit(text, (10, ui_start_y + i * 20))

        # 7. Dibujar Gráfico
        self.draw_chart(history)

        # 8. ESCALADO FINAL: Canvas Lógico -> Ventana Real
        win_w, win_h = self.screen.get_size()
        scaled_surface = pygame.transform.smoothscale(self.canvas, (win_w, win_h))
        self.screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()

    def draw_obstacles(self, obstacles):
        for obs in obstacles:
            pygame.draw.rect(self.canvas, (100, 100, 100), obs.rect)
            pygame.draw.rect(self.canvas, (150, 150, 150), obs.rect, 2)

    def draw_chart(self, history):
        # Dibujar gráfico en la esquina inferior derecha
        if not history: return
        
        chart_w, chart_h = 200, 100
        # Posición relativa al canvas lógico
        chart_x, chart_y = self.logical_width - chart_w - 10, self.logical_height - chart_h - 10
        
        # Fondo y Borde
        pygame.draw.rect(self.canvas, (30, 30, 30), (chart_x, chart_y, chart_w, chart_h))
        pygame.draw.rect(self.canvas, (100, 100, 100), (chart_x, chart_y, chart_w, chart_h), 1)
        
        if len(history) < 2: return

        # Escalar datos
        max_agents = max(h[0] + h[1] for h in history)
        if max_agents == 0: max_agents = 1
        
        # Dibujar líneas (Verde: Sanos, Rojo: Infectados)
        points_sanos = []
        points_infectados = []
        
        step_x = chart_w / len(history)
        
        for i, (sanos, infectados) in enumerate(history):
            x = chart_x + i * step_x
            y_sano = chart_y + chart_h - (sanos / max_agents * chart_h)
            y_inf = chart_y + chart_h - (infectados / max_agents * chart_h)
            points_sanos.append((x, y_sano))
            points_infectados.append((x, y_inf))

        if len(points_sanos) > 1:
            pygame.draw.lines(self.canvas, (0, 255, 0), False, points_sanos, 2)
            pygame.draw.lines(self.canvas, (255, 0, 0), False, points_infectados, 2)
        
    def quit(self):
        pygame.quit()