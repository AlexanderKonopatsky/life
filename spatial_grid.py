"""
Пространственная индексация для оптимизации поиска организмов
Использует сетку для ускорения поиска ближайших объектов
"""

import math

class SpatialGrid:
    """Пространственная сетка для быстрого поиска ближайших организмов"""
    
    def __init__(self, width, height, cell_size=50):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = math.ceil(width / cell_size)
        self.rows = math.ceil(height / cell_size)
        
        # Создаём сетку ячеек
        self.grid = {}
        self.clear()
        
    def clear(self):
        """Очищает сетку"""
        self.grid = {}
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[(row, col)] = []
                
    def _get_cell(self, x, y):
        """Получает координаты ячейки для позиции"""
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        col = max(0, min(self.cols - 1, col))
        row = max(0, min(self.rows - 1, row))
        return (row, col)
        
    def add_organism(self, organism):
        """Добавляет организм в сетку"""
        cell = self._get_cell(organism.x, organism.y)
        if cell in self.grid:
            self.grid[cell].append(organism)
            
    def add_food(self, food):
        """Добавляет пищу в сетку"""
        cell = self._get_cell(food['x'], food['y'])
        if cell in self.grid:
            self.grid[cell].append(food)
            
    def get_nearby_objects(self, x, y, radius):
        """Получает объекты в радиусе от позиции"""
        nearby = []
        
        # Определяем диапазон ячеек для поиска
        min_col = max(0, int((x - radius) // self.cell_size))
        max_col = min(self.cols - 1, int((x + radius) // self.cell_size))
        min_row = max(0, int((y - radius) // self.cell_size))
        max_row = min(self.rows - 1, int((y + radius) // self.cell_size))
        
        # Собираем объекты из соседних ячеек
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                cell = (row, col)
                if cell in self.grid:
                    for obj in self.grid[cell]:
                        # Проверяем расстояние
                        if hasattr(obj, 'x'):  # Организм
                            dx = obj.x - x
                            dy = obj.y - y
                        else:  # Пища
                            dx = obj['x'] - x
                            dy = obj['y'] - y
                            
                        dist_squared = dx * dx + dy * dy
                        if dist_squared <= radius * radius:
                            nearby.append(obj)
                            
        return nearby
        
    def get_nearby_organisms(self, organism, radius):
        """Получает организмы в радиусе от данного организма"""
        nearby = []
        objects = self.get_nearby_objects(organism.x, organism.y, radius)
        
        for obj in objects:
            if hasattr(obj, 'alive') and obj != organism and obj.alive:
                nearby.append(obj)
                
        return nearby
        
    def get_nearby_food(self, organism, radius):
        """Получает пищу в радиусе от организма"""
        nearby = []
        objects = self.get_nearby_objects(organism.x, organism.y, radius)
        
        for obj in objects:
            if isinstance(obj, dict) and not obj.get('consumed', False):
                nearby.append(obj)
                
        return nearby