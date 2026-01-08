import random
import math
import pygame # Ncesario para Rects y Colisiones

# --- CLASE OBSTACULO ---
class Obstaculo:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

# --- CLASE AGENTE ---
# Representa a una persona en la simulación.
class Agente:
    def __init__(self, x, y, canvas_width, canvas_height):
        self.x = x
        self.y = y
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.state = 0 # 0: Sano (Verde), 1: Infectado (Rojo)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.current_bucket = None 

    def move(self, obstacles=[]):
        # Movimiento tentativo
        next_x = self.x + self.dx
        next_y = self.y + self.dy
        
        # Colisión con Obstáculos (Rebote simple)
        hit = False
        for obs in obstacles:
            # Creamos un rect temporal para el agente
            agent_rect = pygame.Rect(int(next_x)-3, int(next_y)-3, 6, 6)
            if agent_rect.colliderect(obs.rect):
                hit = True
                # Invertir dirección simple (mejorable)
                self.dx *= -1
                self.dy *= -1
                break
        
        if not hit:
            self.x = next_x
            self.y = next_y

        # Rebote en bordes del canvas
        if self.x <= 0 or self.x >= self.canvas_width:
            self.dx *= -1
            self.x = max(0, min(self.x, self.canvas_width))
        
        if self.y <= 0 or self.y >= self.canvas_height:
            self.dy *= -1
            self.y = max(0, min(self.y, self.canvas_height))

# --- CLASE GRID BUCKET ---
class GridBucket:
    def __init__(self, capacity):
        self.points = []
        self.capacity = capacity

    def is_full(self):
        return len(self.points) >= self.capacity

    def add(self, agent):
        if agent not in self.points:
            self.points.append(agent)
            agent.current_bucket = self

    def remove(self, agent):
        if agent in self.points:
            self.points.remove(agent)
            agent.current_bucket = None

# --- CLASE GRID FILE ---
class GridFile:
    def __init__(self, width, height, bucket_capacity):
        self.width = width
        self.height = height
        self.bucket_capacity = bucket_capacity
        
        self.x_scales = [0.0, float(width)]
        self.y_scales = [0.0, float(height)]
        
        self.grid = [[GridBucket(bucket_capacity)]]

    def _get_indices(self, x, y):
        ix = 0
        for k in range(len(self.x_scales) - 1):
            if self.x_scales[k] <= x < self.x_scales[k+1]:
                ix = k
                break
        else:
            ix = len(self.x_scales) - 2
        
        iy = 0
        for k in range(len(self.y_scales) - 1):
            if self.y_scales[k] <= y < self.y_scales[k+1]:
                iy = k
                break
        else:
            iy = len(self.y_scales) - 2
            
        return ix, iy

    def insert(self, agent):
        ix, iy = self._get_indices(agent.x, agent.y)
        bucket = self.grid[iy][ix]
        
        if bucket.is_full():
            self._split_bucket(ix, iy, bucket)
            self.insert(agent) 
        else:
            bucket.add(agent)

    def update(self, agent, old_x, old_y):
        if agent.current_bucket:
            agent.current_bucket.remove(agent)
        self.insert(agent)

    def _split_bucket(self, ix, iy, bucket):
        x_range = self.x_scales[ix+1] - self.x_scales[ix]
        y_range = self.y_scales[iy+1] - self.y_scales[iy]
        
        points = bucket.points[:] 
        bucket.points = [] 

        if x_range > y_range:
            split_val = sum(p.x for p in points) / len(points)
            self._split_x(ix, split_val, points) 
        else:
            split_val = sum(p.y for p in points) / len(points)
            self._split_y(iy, split_val, points)

    def _split_x(self, ix, split_val, points):
        self.x_scales.insert(ix + 1, split_val)
        
        for r in range(len(self.grid)):
            self.grid[r].insert(ix + 1, self.grid[r][ix])

        points_left = [p for p in points if p.x < split_val]
        points_right = [p for p in points if p.x >= split_val]
        
        L = GridBucket(self.bucket_capacity)
        R = GridBucket(self.bucket_capacity)
        
        for p in points_left: L.add(p)
        for p in points_right: R.add(p)

        for rr in range(len(self.grid)):
            self.grid[rr][ix] = L
            self.grid[rr][ix+1] = R

    def _split_y(self, iy, split_val, points):
        self.y_scales.insert(iy + 1, split_val)
        
        new_row = []
        for c in range(len(self.grid[0])):
            new_row.append(self.grid[iy][c])
        self.grid.insert(iy + 1, new_row)
        
        points_top = [p for p in points if p.y < split_val]
        points_bottom = [p for p in points if p.y >= split_val]
        
        T = GridBucket(self.bucket_capacity)
        B = GridBucket(self.bucket_capacity)
        
        for p in points_top: T.add(p)
        for p in points_bottom: B.add(p)
        
        for cc in range(len(self.grid[0])):
            self.grid[iy][cc] = T
            self.grid[iy+1][cc] = B

    # Devuelve LISTA DE AGENTES (para infección)
    def query_agents(self, x, y, w, h):
        found = []
        x2, y2 = x + w, y + h
        checked_buckets = set()
        
        ix_start, iy_start = self._get_indices(x, y)
        ix_end, iy_end = self._get_indices(x2, y2)
        
        ix_end = min(ix_end, len(self.x_scales) - 2)
        iy_end = min(iy_end, len(self.y_scales) - 2)
        
        for r in range(iy_start, iy_end + 1):
            for c in range(ix_start, ix_end + 1):
                if 0 <= r < len(self.grid) and 0 <= c < len(self.grid[0]):
                    b = self.grid[r][c]
                    if b not in checked_buckets:
                        checked_buckets.add(b)
                        for p in b.points:
                            if x <= p.x <= x2 and y <= p.y <= y2:
                                found.append(p)
        return found

    def query_range(self, x, y, w, h):
        return len(self.query_agents(x, y, w, h))

    def get_stats(self):
        unique_buckets = set()
        for r in self.grid:
            for b in r:
                unique_buckets.add(b)
        
        total_agents = 0
        for b in unique_buckets:
            total_agents += len(b.points)
            
        utilization = 0
        if len(unique_buckets) > 0:
            utilization = total_agents / (len(unique_buckets) * self.bucket_capacity)
            
        return {
            "total_agents": total_agents,
            "total_buckets": len(unique_buckets),
            "utilization": utilization,
            "depth_x": len(self.x_scales) - 1,
            "depth_y": len(self.y_scales) - 1
        }