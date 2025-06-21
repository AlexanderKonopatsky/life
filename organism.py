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
                'speed': random.uniform(0.5, 4.0),           # Скорость передвижения
                'size': random.uniform(3, 12),               # Размер организма
                'energy_efficiency': random.uniform(0.3, 1.0), # Эффективность использования энергии
                'reproduction_threshold': random.uniform(80, 150), # Порог размножения
                'aggression': random.uniform(0.0, 1.0),      # Агрессивность (влияет на поведение)
                'mutation_rate': random.uniform(0.01, 0.1),  # Частота мутаций
                'diet_preference': random.uniform(0.0, 1.0), # 0=травоядный, 1=хищник
                'fear_sensitivity': random.uniform(0.0, 1.0), # Чувствительность к угрозам
                'color_r': random.randint(0, 255),           # Цвет (красный)
                'color_g': random.randint(0, 255),           # Цвет (зеленый)  
                'color_b': random.randint(0, 255),           # Цвет (синий)
            }
        else:
            self.genes = genes.copy()
        
        # Состояние организма
        self.energy = 100  # Увеличиваем начальную энергию
        self.age = 0
        self.alive = True
        self.generation = 0
        self.fitness = 0  # Показатель приспособленности
        
        # Поведенческое состояние
        self.target = None  # Цель (пища или добыча)
        self.fleeing_from = None  # От кого убегает
        self.hunt_cooldown = 0  # Перерыв между атаками
        self.last_meal = 0  # Время последнего приёма пищи
        
        # Движение
        self.direction = random.uniform(0, 2 * math.pi)
        self.velocity_x = 0
        self.velocity_y = 0
        
    def is_predator(self):
        """Определяет, является ли организм хищником"""
        return self.genes['diet_preference'] > 0.6
        
    def is_herbivore(self):
        """Определяет, является ли организм травоядным"""
        return self.genes['diet_preference'] < 0.4
        
    def is_omnivore(self):
        """Определяет, является ли организм всеядным"""
        return 0.4 <= self.genes['diet_preference'] <= 0.6
        
    def update(self, dt, world_width, world_height, spatial_grid=None):
        """Обновляет состояние организма на каждом шаге симуляции"""
        if not self.alive:
            return
            
        # Используем пространственную сетку для оптимизации
        if spatial_grid:
            # Увеличиваем возраст
            self.age += dt
            self.last_meal += dt
            if self.hunt_cooldown > 0:
                self.hunt_cooldown -= dt
            
            # Потребление энергии зависит от типа и активности
            base_consumption = (self.genes['size'] * 0.015 + self.genes['speed'] * 0.008) * dt
            
            # Хищники тратят больше энергии
            if self.is_predator():
                base_consumption *= 1.5
            
            self.energy -= base_consumption / self.genes['energy_efficiency']
            
            # Расчёт приспособленности
            self.fitness = self.energy * 0.1 + self.age * 0.05 + (200 - self.last_meal) * 0.02
            
            # Определяем поведение и цели с оптимизированным поиском
            self._update_behavior_optimized(spatial_grid)
            
            # Движение с учётом поведения
            self._move(dt, world_width, world_height)
            
            # Поиск пищи и охота с оптимизацией
            self._optimized_interactions(spatial_grid)
            
            # Проверка на смерть
            if self.energy <= 0 or self.age > 2000:
                self.alive = False
        else:
            # Старый неоптимизированный код для совместимости (вызывается из _simple_update)
            # Базовая логика уже в _legacy_update
            pass
            
    def _legacy_update(self, dt, world_width, world_height, food_sources=None, other_organisms=None):
        """Старая неоптимизированная логика для совместимости"""
        if not self.alive:
            return
            
        # Увеличиваем возраст
        self.age += dt
        self.last_meal += dt
        if self.hunt_cooldown > 0:
            self.hunt_cooldown -= dt
        
        # Потребление энергии зависит от типа и активности
        base_consumption = (self.genes['size'] * 0.015 + self.genes['speed'] * 0.008) * dt
        
        # Хищники тратят больше энергии
        if self.is_predator():
            base_consumption *= 1.5
        
        self.energy -= base_consumption / self.genes['energy_efficiency']
        
        # Расчёт приспособленности
        self.fitness = self.energy * 0.1 + self.age * 0.05 + (200 - self.last_meal) * 0.02
        
        # Поведение (если есть данные)
        if food_sources is not None and other_organisms is not None:
            self._update_behavior(other_organisms, food_sources)
        
        # Движение
        self._move(dt, world_width, world_height)
        
        # Поиск пищи (если есть источники)
        if food_sources is not None and (self.is_herbivore() or self.is_omnivore()):
            self._seek_food(food_sources)
        
        # Охота (если есть другие организмы)  
        if other_organisms is not None and (self.is_predator() or self.is_omnivore()):
            self._hunt(other_organisms)
            
        # Проверка на смерть
        if self.energy <= 0 or self.age > 2000:
            self.alive = False
            
    def _update_behavior(self, other_organisms, food_sources):
        """Обновляет поведенческие цели"""
        self.target = None
        self.fleeing_from = None
        
        # Поиск угроз для травоядных
        if self.is_herbivore() or (self.is_omnivore() and self.genes['fear_sensitivity'] > 0.5):
            closest_predator = None
            min_predator_distance = float('inf')
            
            for other in other_organisms:
                if other != self and other.alive and other.is_predator():
                    distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
                    if distance < min_predator_distance and distance < 50:
                        min_predator_distance = distance
                        closest_predator = other
            
            if closest_predator and min_predator_distance < self.genes['fear_sensitivity'] * 60:
                self.fleeing_from = closest_predator
                return
        
        # Поиск цели для хищников
        if self.is_predator() and self.hunt_cooldown <= 0:
            closest_prey = None
            min_prey_distance = float('inf')
            
            for other in other_organisms:
                if other != self and other.alive and not other.is_predator():
                    # Хищники предпочитают меньших по размеру
                    if other.genes['size'] <= self.genes['size'] * 1.2:
                        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
                        if distance < min_prey_distance and distance < 80:
                            min_prey_distance = distance
                            closest_prey = other
            
            if closest_prey:
                self.target = closest_prey
                return
        
        # Поиск пищи для травоядных и всеядных
        if (self.is_herbivore() or self.is_omnivore()) and food_sources:
            closest_food = None
            min_food_distance = float('inf')
            
            for food in food_sources:
                distance = math.sqrt((self.x - food['x'])**2 + (self.y - food['y'])**2)
                if distance < min_food_distance:
                    min_food_distance = distance
                    closest_food = food
            
            if closest_food and min_food_distance < 100:
                self.target = closest_food
                
    def _move(self, dt, world_width, world_height):
        """Движение организма с учётом поведения"""
        speed = self.genes['speed']
        
        # Убегание от хищника
        if self.fleeing_from:
            # Направление от хищника
            dx = self.x - self.fleeing_from.x
            dy = self.y - self.fleeing_from.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                self.direction = math.atan2(dy, dx)
                speed *= 1.5  # Ускорение при бегстве
        
        # Преследование цели
        elif self.target:
            if isinstance(self.target, dict):  # Пища
                dx = self.target['x'] - self.x
                dy = self.target['y'] - self.y
            else:  # Другой организм
                dx = self.target.x - self.x
                dy = self.target.y - self.y
            
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                self.direction = math.atan2(dy, dx)
                # Хищники ускоряются при охоте
                if self.is_predator():
                    speed *= 1.3
        
        # Случайные изменения направления при отсутствии целей
        else:
            if random.random() < 0.15:
                self.direction += random.uniform(-0.8, 0.8)
        
        # Вычисляем скорость
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
        """Поиск и потребление растительной пищи"""
        for food in food_sources:
            distance = math.sqrt((self.x - food['x'])**2 + (self.y - food['y'])**2)
            if distance < self.genes['size'] + food['size']:
                # Потребляем пищу
                energy_multiplier = 2.0 if self.is_herbivore() else 1.5  # Травоядные эффективнее
                energy_gain = food['energy'] * self.genes['energy_efficiency'] * energy_multiplier
                self.energy += energy_gain
                food['consumed'] = True
                self.last_meal = 0  # Сбрасываем счётчик голода
                break
                
    def _hunt(self, other_organisms):
        """Охота на других организмов"""
        if self.hunt_cooldown > 0:
            return
            
        for prey in other_organisms:
            if prey == self or not prey.alive:
                continue
                
            # Хищники атакуют травоядных и меньших всеядных
            if not prey.is_predator() and prey.genes['size'] <= self.genes['size'] * 1.2:
                distance = math.sqrt((self.x - prey.x)**2 + (self.y - prey.y)**2)
                
                if distance < self.genes['size'] + prey.genes['size']:
                    # Успешная атака зависит от размера, скорости и агрессивности
                    attack_power = (self.genes['size'] + self.genes['speed'] + self.genes['aggression'] * 10) / 3
                    defense_power = (prey.genes['size'] + prey.genes['speed'] + prey.genes['fear_sensitivity'] * 5) / 3
                    
                    if attack_power > defense_power * random.uniform(0.8, 1.2):
                        # Успешная охота
                        energy_gain = prey.energy * 0.6 * self.genes['energy_efficiency']
                        self.energy += energy_gain
                        self.last_meal = 0
                        
                        # Жертва теряет энергию или умирает
                        prey.energy -= prey.energy * 0.8
                        if prey.energy <= 0:
                            prey.alive = False
                            
                        self.hunt_cooldown = 50  # Перерыв между атаками
                        break
                    else:
                        # Неудачная атака
                        self.hunt_cooldown = 20
                        self.energy -= 5  # Тратим энергию на неудачную атаку
                        
    def _update_behavior_optimized(self, spatial_grid):
        """Оптимизированное обновление поведения с пространственной сеткой"""
        self.target = None
        self.fleeing_from = None
        
        # Поиск угроз для травоядных (ограниченный радиус)
        if self.is_herbivore() or (self.is_omnivore() and self.genes['fear_sensitivity'] > 0.5):
            nearby_organisms = spatial_grid.get_nearby_organisms(self, 80)
            
            closest_predator = None
            min_predator_distance = float('inf')
            
            for other in nearby_organisms:
                if other.is_predator():
                    dx = self.x - other.x
                    dy = self.y - other.y
                    distance = dx * dx + dy * dy  # Используем квадрат расстояния
                    
                    if distance < min_predator_distance:
                        min_predator_distance = distance
                        closest_predator = other
            
            if closest_predator and min_predator_distance < (self.genes['fear_sensitivity'] * 60) ** 2:
                self.fleeing_from = closest_predator
                return
        
        # Поиск цели для хищников (ограниченный радиус)
        if self.is_predator() and self.hunt_cooldown <= 0:
            nearby_organisms = spatial_grid.get_nearby_organisms(self, 100)
            
            closest_prey = None
            min_prey_distance = float('inf')
            
            for other in nearby_organisms:
                if not other.is_predator() and other.genes['size'] <= self.genes['size'] * 1.2:
                    dx = self.x - other.x
                    dy = self.y - other.y
                    distance = dx * dx + dy * dy
                    
                    if distance < min_prey_distance:
                        min_prey_distance = distance
                        closest_prey = other
            
            if closest_prey and min_prey_distance < 6400:  # 80^2
                self.target = closest_prey
                return
        
        # Поиск пищи для травоядных и всеядных (ограниченный радиус)
        if self.is_herbivore() or self.is_omnivore():
            nearby_food = spatial_grid.get_nearby_food(self, 120)
            
            if nearby_food:
                closest_food = None
                min_food_distance = float('inf')
                
                for food in nearby_food:
                    dx = self.x - food['x']
                    dy = self.y - food['y']
                    distance = dx * dx + dy * dy
                    
                    if distance < min_food_distance:
                        min_food_distance = distance
                        closest_food = food
                
                if closest_food:
                    self.target = closest_food
                    
    def _optimized_interactions(self, spatial_grid):
        """Оптимизированные взаимодействия с использованием пространственной сетки"""
        # Поиск пищи (растения для травоядных)
        if (self.is_herbivore() or self.is_omnivore()) and isinstance(self.target, dict):
            dx = self.x - self.target['x']
            dy = self.y - self.target['y']
            distance_squared = dx * dx + dy * dy
            collision_distance = self.genes['size'] + self.target['size']
            
            if distance_squared < collision_distance * collision_distance:
                # Потребляем пищу
                energy_multiplier = 2.0 if self.is_herbivore() else 1.5
                energy_gain = self.target['energy'] * self.genes['energy_efficiency'] * energy_multiplier
                self.energy += energy_gain
                self.target['consumed'] = True
                self.last_meal = 0
                self.target = None
        
                         # Охота (для хищников) - только на близких целях
        if (self.is_predator() or self.is_omnivore()) and self.hunt_cooldown <= 0:
            if self.target and hasattr(self.target, 'alive') and self.target.alive:
                dx = self.x - self.target.x
                dy = self.y - self.target.y
                distance_squared = dx * dx + dy * dy
                collision_distance = self.genes['size'] + self.target.genes['size']
                
                if distance_squared < collision_distance * collision_distance:
                    # Расчёт успешности атаки
                    attack_power = (self.genes['size'] + self.genes['speed'] + self.genes['aggression'] * 10) / 3
                    defense_power = (self.target.genes['size'] + self.target.genes['speed'] + self.target.genes['fear_sensitivity'] * 5) / 3
                    
                    if attack_power > defense_power * random.uniform(0.8, 1.2):
                        # Успешная охота
                        energy_gain = self.target.energy * 0.6 * self.genes['energy_efficiency']
                        self.energy += energy_gain
                        self.last_meal = 0
                        
                        # Жертва теряет энергию или умирает
                        self.target.energy -= self.target.energy * 0.8
                        if self.target.energy <= 0:
                            self.target.alive = False
                            
                        self.hunt_cooldown = 50
                    else:
                        # Неудачная атака
                        self.hunt_cooldown = 20
                        self.energy -= 5
                    
                    self.target = None
                      
    def can_reproduce(self):
        """Проверяет, может ли организм размножаться"""
        return self.energy > self.genes['reproduction_threshold'] and self.age > 100
        
    def reproduce(self):
        """Создает потомка с мутированными генами"""
        if not self.can_reproduce():
            return None
            
        # Тратим энергию на размножение (уменьшаем затраты)
        self.energy -= self.genes['reproduction_threshold'] * 0.3
        
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
                    new_genes[gene_name] = min(6.0, new_genes[gene_name])
                elif gene_name == 'size':
                    new_genes[gene_name] = min(20.0, new_genes[gene_name])
                elif gene_name in ['energy_efficiency', 'aggression', 'diet_preference', 'fear_sensitivity']:
                    new_genes[gene_name] = min(1.0, new_genes[gene_name])
                elif gene_name == 'mutation_rate':
                    new_genes[gene_name] = min(0.2, new_genes[gene_name])
        
        # Создаем потомка рядом с родителем
        child_x = self.x + random.uniform(-20, 20)
        child_y = self.y + random.uniform(-20, 20)
        
        child = Organism(child_x, child_y, new_genes)
        child.generation = self.generation + 1
        child.energy = 60  # Увеличиваем начальную энергию потомка
        
        return child
        
    def get_color(self):
        """Возвращает цвет организма для отображения с учётом типа"""
        base_r = int(self.genes['color_r'])
        base_g = int(self.genes['color_g'])
        base_b = int(self.genes['color_b'])
        
        # Модифицируем цвет в зависимости от типа
        if self.is_predator():
            # Хищники - красноватые оттенки
            return (min(255, base_r + 80), max(0, base_g - 40), max(0, base_b - 40))
        elif self.is_herbivore():
            # Травоядные - зеленоватые оттенки
            return (max(0, base_r - 40), min(255, base_g + 80), max(0, base_b - 40))
        else:
            # Всеядные - синеватые оттенки
            return (max(0, base_r - 40), max(0, base_g - 40), min(255, base_b + 80))
            
    def get_type_name(self):
        """Возвращает название типа организма"""
        if self.is_predator():
            return "Хищник"
        elif self.is_herbivore():
            return "Травоядный"
        else:
            return "Всеядный"
        
    def get_info(self):
        """Возвращает информацию об организме"""
        return {
            'position': (self.x, self.y),
            'energy': self.energy,
            'age': self.age,
            'generation': self.generation,
            'genes': self.genes,
            'alive': self.alive,
            'fitness': self.fitness
        }