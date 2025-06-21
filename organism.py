import random
import math

class Organism:
    """Класс представляющий простой организм с набором генов"""
    
    def __init__(self, x=None, y=None, genes=None):
        # Позиция организма
        self.x = x if x is not None else random.uniform(0, 800)
        self.y = y if y is not None else random.uniform(0, 600)
        
        # Гены организма (если не переданы, генерируются случайно)
        if genes is None:
            self.genes = {
                'speed': random.uniform(0.5, 3.0),           # Скорость передвижения
                'size': random.uniform(2, 8),                # Размер организма
                'energy_efficiency': random.uniform(0.3, 1.0), # Эффективность использования энергии
                'reproduction_threshold': random.uniform(50, 100), # Порог размножения
                'aggression': random.uniform(0.0, 1.0),      # Агрессивность (влияет на поведение)
                'mutation_rate': random.uniform(0.01, 0.1),  # Частота мутаций
                'color_r': random.randint(0, 255),           # Цвет (красный)
                'color_g': random.randint(0, 255),           # Цвет (зеленый)  
                'color_b': random.randint(0, 255),           # Цвет (синий)
            }
        else:
            self.genes = genes.copy()
        
        # Состояние организма
        self.energy = 50
        self.age = 0
        self.alive = True
        self.generation = 0
        
        # Движение
        self.direction = random.uniform(0, 2 * math.pi)
        self.velocity_x = 0
        self.velocity_y = 0
        
    def update(self, dt, world_width, world_height, food_sources, other_organisms):
        """Обновляет состояние организма на каждом шаге симуляции"""
        if not self.alive:
            return
            
        # Увеличиваем возраст
        self.age += dt
        
        # Потребление энергии базовое
        energy_consumption = (self.genes['size'] * 0.1 + self.genes['speed'] * 0.05) * dt
        self.energy -= energy_consumption / self.genes['energy_efficiency']
        
        # Движение
        self._move(dt, world_width, world_height)
        
        # Поиск пищи
        self._seek_food(food_sources)
        
        # Взаимодействие с другими организмами
        self._interact_with_others(other_organisms)
        
        # Проверка на смерть
        if self.energy <= 0 or self.age > 1000:
            self.alive = False
            
    def _move(self, dt, world_width, world_height):
        """Движение организма"""
        # Случайные изменения направления
        if random.random() < 0.1:
            self.direction += random.uniform(-0.5, 0.5)
            
        # Вычисляем скорость
        speed = self.genes['speed']
        self.velocity_x = math.cos(self.direction) * speed
        self.velocity_y = math.sin(self.direction) * speed
        
        # Обновляем позицию
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Отражение от границ
        if self.x < 0 or self.x > world_width:
            self.direction = math.pi - self.direction
            self.x = max(0, min(world_width, self.x))
            
        if self.y < 0 or self.y > world_height:
            self.direction = -self.direction
            self.y = max(0, min(world_height, self.y))
            
    def _seek_food(self, food_sources):
        """Поиск и потребление пищи"""
        for food in food_sources:
            distance = math.sqrt((self.x - food['x'])**2 + (self.y - food['y'])**2)
            if distance < self.genes['size'] + food['size']:
                # Потребляем пищу
                energy_gain = food['energy'] * self.genes['energy_efficiency']
                self.energy += energy_gain
                food['consumed'] = True
                break
                
    def _interact_with_others(self, other_organisms):
        """Взаимодействие с другими организмами"""
        for other in other_organisms:
            if other == self or not other.alive:
                continue
                
            distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
            
            # Если организмы близко
            if distance < self.genes['size'] + other.genes['size']:
                # Агрессивное взаимодействие
                if self.genes['aggression'] > 0.7 and other.genes['aggression'] > 0.7:
                    # Борьба - более крупный и быстрый побеждает
                    if self.genes['size'] * self.genes['speed'] > other.genes['size'] * other.genes['speed']:
                        self.energy += other.energy * 0.3
                        other.energy -= other.energy * 0.5
                    else:
                        other.energy += self.energy * 0.3
                        self.energy -= self.energy * 0.5
                        
    def can_reproduce(self):
        """Проверяет, может ли организм размножаться"""
        return self.energy > self.genes['reproduction_threshold'] and self.age > 50
        
    def reproduce(self):
        """Создает потомка с мутированными генами"""
        if not self.can_reproduce():
            return None
            
        # Тратим энергию на размножение
        self.energy -= self.genes['reproduction_threshold'] * 0.7
        
        # Создаем мутированные гены
        new_genes = {}
        for gene_name, gene_value in self.genes.items():
            if gene_name in ['color_r', 'color_g', 'color_b']:
                # Цветовые гены мутируют по-особому
                new_genes[gene_name] = max(0, min(255, int(gene_value + random.gauss(0, 20))))
            else:
                # Обычные гены мутируют с нормальным распределением
                mutation_strength = self.genes['mutation_rate']
                mutation = random.gauss(0, gene_value * mutation_strength)
                new_genes[gene_name] = max(0.1, gene_value + mutation)
                
                # Ограничения на значения генов
                if gene_name == 'speed':
                    new_genes[gene_name] = min(5.0, new_genes[gene_name])
                elif gene_name == 'size':
                    new_genes[gene_name] = min(15.0, new_genes[gene_name])
                elif gene_name in ['energy_efficiency', 'aggression']:
                    new_genes[gene_name] = min(1.0, new_genes[gene_name])
                elif gene_name == 'mutation_rate':
                    new_genes[gene_name] = min(0.2, new_genes[gene_name])
        
        # Создаем потомка рядом с родителем
        child_x = self.x + random.uniform(-20, 20)
        child_y = self.y + random.uniform(-20, 20)
        
        child = Organism(child_x, child_y, new_genes)
        child.generation = self.generation + 1
        child.energy = 30  # Начальная энергия потомка
        
        return child
        
    def get_color(self):
        """Возвращает цвет организма для отображения"""
        return (
            int(self.genes['color_r']),
            int(self.genes['color_g']),
            int(self.genes['color_b'])
        )
        
    def get_info(self):
        """Возвращает информацию об организме"""
        return {
            'position': (self.x, self.y),
            'energy': self.energy,
            'age': self.age,
            'generation': self.generation,
            'genes': self.genes,
            'alive': self.alive
        }