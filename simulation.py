import random
import time
from organism import Organism
from spatial_grid import SpatialGrid

# Опциональный импорт многопроцессорной оптимизации
try:
    from parallel_optimization import (
        ParallelSimulationProcessor, 
        PerformanceMonitor,
        convert_organism_to_data,
        update_organism_from_data
    )
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False
    print("⚠️ Модуль параллельной оптимизации недоступен")

class EvolutionSimulation:
    """Основной класс симуляции эволюции"""
    
    def __init__(self, width=900, height=700):
        self.width = width
        self.height = height
        
        # Параметры симуляции
        self.organisms = []
        self.food_sources = []
        self.generation_count = 0
        self.time_step = 0
        
        # Настройки симуляции
        self.max_organisms = None  # Убираем ограничение популяции
        self.initial_organisms = 20
        self.food_spawn_rate = 0.5  # Увеличиваем частоту появления пищи
        self.max_food = 80  # Больше пищи
        
        # Статистика
        self.stats = {
            'population': 0,
            'predators': 0,
            'herbivores': 0,
            'omnivores': 0,
            'avg_speed': 0,
            'avg_size': 0,
            'avg_energy_efficiency': 0,
            'avg_generation': 0,
            'avg_aggression': 0,
            'avg_mutation_rate': 0,
            'avg_fitness': 0,
            'total_births': 0,
            'total_deaths': 0
        }
        
        # История изменений генов для графиков
        self.gene_history = {
            'speed': [],
            'size': [],
            'energy_efficiency': [],
            'aggression': [],
            'mutation_rate': [],
            'fitness': []
        }
        
        # История популяций по типам для графиков
        self.population_history = {
            'predators': [],
            'herbivores': [],
            'omnivores': [],
            'total': [],
            'time_steps': []
        }
        
        # Пространственная индексация для оптимизации
        self.spatial_grid = SpatialGrid(self.width, self.height, cell_size=80)
        self.use_optimization = True  # Флаг для включения оптимизации
        
        # Многопроцессорная оптимизация
        if PARALLEL_AVAILABLE:
            self.parallel_processor = ParallelSimulationProcessor()
            self.performance_monitor = PerformanceMonitor()
            print(f"🚀 Многопроцессорное ускорение: {self.parallel_processor.num_processes} ядер")
        else:
            self.parallel_processor = None
            self.performance_monitor = None
        
        # Счётчики для профилирования
        self.frame_count = 0
        self.update_time_sum = 0
        
        # Инициализация
        self._spawn_initial_organisms()
        
    def _spawn_initial_organisms(self):
        """Создает начальную популяцию организмов"""
        self.organisms = []
        for _ in range(self.initial_organisms):
            organism = Organism()
            organism.x = random.uniform(50, self.width - 50)
            organism.y = random.uniform(50, self.height - 50)
            self.organisms.append(organism)
            
    def _spawn_food(self):
        """Создает источники пищи"""
        # Удаляем съеденную пищу
        self.food_sources = [food for food in self.food_sources if not food.get('consumed', False)]
        
        # Добавляем новую пищу (растения)
        while len(self.food_sources) < self.max_food and random.random() < self.food_spawn_rate:
            # Разные типы растений
            plant_type = random.choice(['berry', 'grass', 'fruit'])
            
            if plant_type == 'berry':
                food = {
                    'x': random.uniform(10, self.width - 10),
                    'y': random.uniform(10, self.height - 10),
                    'size': random.uniform(1, 3),
                    'energy': random.uniform(15, 30),
                    'type': 'berry',
                    'consumed': False
                }
            elif plant_type == 'grass':
                food = {
                    'x': random.uniform(10, self.width - 10),
                    'y': random.uniform(10, self.height - 10),
                    'size': random.uniform(2, 4),
                    'energy': random.uniform(8, 20),
                    'type': 'grass',
                    'consumed': False
                }
            else:  # fruit
                food = {
                    'x': random.uniform(10, self.width - 10),
                    'y': random.uniform(10, self.height - 10),
                    'size': random.uniform(3, 6),
                    'energy': random.uniform(25, 45),
                    'type': 'fruit',
                    'consumed': False
                }
            
            self.food_sources.append(food)
            
    def _handle_reproduction(self):
        """Обрабатывает размножение организмов"""
        new_organisms = []
        
        for organism in self.organisms:
            if organism.alive and organism.can_reproduce():
                # Естественное размножение без искусственных ограничений
                child = organism.reproduce()
                if child:
                    # Проверяем границы для потомка
                    child.x = max(10, min(self.width - 10, child.x))
                    child.y = max(10, min(self.height - 10, child.y))
                    new_organisms.append(child)
                    self.stats['total_births'] += 1
                        
        self.organisms.extend(new_organisms)
        
    def _remove_dead_organisms(self):
        """Удаляет мертвых организмов"""
        dead_count = sum(1 for org in self.organisms if not org.alive)
        self.stats['total_deaths'] += dead_count
        self.organisms = [org for org in self.organisms if org.alive]
        
    def _update_statistics(self):
        """Обновляет статистику симуляции"""
        if len(self.organisms) == 0:
            return
            
        alive_organisms = [org for org in self.organisms if org.alive]
        
        if len(alive_organisms) == 0:
            return
            
        self.stats['population'] = len(alive_organisms)
        
        # Подсчёт типов организмов
        self.stats['predators'] = sum(1 for org in alive_organisms if org.is_predator())
        self.stats['herbivores'] = sum(1 for org in alive_organisms if org.is_herbivore())
        self.stats['omnivores'] = sum(1 for org in alive_organisms if org.is_omnivore())
        
        # Средние значения генов
        self.stats['avg_speed'] = sum(org.genes['speed'] for org in alive_organisms) / len(alive_organisms)
        self.stats['avg_size'] = sum(org.genes['size'] for org in alive_organisms) / len(alive_organisms)
        self.stats['avg_energy_efficiency'] = sum(org.genes['energy_efficiency'] for org in alive_organisms) / len(alive_organisms)
        self.stats['avg_generation'] = sum(org.generation for org in alive_organisms) / len(alive_organisms)
        self.stats['avg_aggression'] = sum(org.genes['aggression'] for org in alive_organisms) / len(alive_organisms)
        self.stats['avg_mutation_rate'] = sum(org.genes['mutation_rate'] for org in alive_organisms) / len(alive_organisms)
        self.stats['avg_fitness'] = sum(org.fitness for org in alive_organisms) / len(alive_organisms)
        
        # Сохраняем историю для графиков (каждые 10 шагов)
        if self.time_step % 10 == 0:
            # История генов
            self.gene_history['speed'].append(self.stats['avg_speed'])
            self.gene_history['size'].append(self.stats['avg_size'])
            self.gene_history['energy_efficiency'].append(self.stats['avg_energy_efficiency'])
            self.gene_history['aggression'].append(self.stats['avg_aggression'])
            self.gene_history['mutation_rate'].append(self.stats['avg_mutation_rate'])
            self.gene_history['fitness'].append(self.stats['avg_fitness'])
            
            # История популяций по типам
            self.population_history['predators'].append(self.stats['predators'])
            self.population_history['herbivores'].append(self.stats['herbivores'])
            self.population_history['omnivores'].append(self.stats['omnivores'])
            self.population_history['total'].append(self.stats['population'])
            self.population_history['time_steps'].append(self.time_step)
        
        # Определяем новое поколение
        max_generation = max(org.generation for org in alive_organisms)
        if max_generation > self.generation_count:
            self.generation_count = max_generation
            
    def update(self, dt=1.0):
        """Обновляет состояние симуляции на один шаг"""
        import time
        start_time = time.time()
        
        self.time_step += 1
        self.frame_count += 1
        
        # Создаем пищу
        self._spawn_food()
        
        population_size = len([org for org in self.organisms if org.alive])
        
        # Выбираем стратегию обновления в зависимости от размера популяции
        if (PARALLEL_AVAILABLE and self.parallel_processor and 
            self.performance_monitor and 
            self.performance_monitor.should_use_parallel(population_size)):
            # Многопроцессорное обновление для очень больших популяций
            self._parallel_update(dt)
        elif self.use_optimization and population_size > 50:
            # Оптимизированное обновление для больших популяций
            self._optimized_update(dt)
        else:
            # Простое обновление для малых популяций
            self._simple_update(dt)
        
        # Обрабатываем размножение
        self._handle_reproduction()
        
        # Удаляем мертвых
        self._remove_dead_organisms()
        
        # Обновляем статистику (реже для оптимизации)
        if self.time_step % 5 == 0:  # Каждые 5 шагов
            self._update_statistics()
        
        # Если популяция вымерла, перезапускаем
        if len(self.organisms) == 0:
            self._spawn_initial_organisms()
            
        # Профилирование
        self.update_time_sum += time.time() - start_time
        
    def _simple_update(self, dt):
        """Простое обновление без оптимизации"""
        # Для совместимости добавляем старую логику
        for organism in self.organisms:
            # Используем старую логику с полными данными
            organism._legacy_update(dt, self.width, self.height, self.food_sources, self.organisms)
            
    def _optimized_update(self, dt):
        """Оптимизированное обновление с пространственной сеткой"""
        # Очищаем и заполняем пространственную сетку
        self.spatial_grid.clear()
        
        # Добавляем живых организмов в сетку
        alive_organisms = [org for org in self.organisms if org.alive]
        for organism in alive_organisms:
            self.spatial_grid.add_organism(organism)
            
        # Добавляем пищу в сетку
        for food in self.food_sources:
            if not food.get('consumed', False):
                self.spatial_grid.add_food(food)
        
        # Обновляем организмы с оптимизацией
        for organism in alive_organisms:
            organism.update(dt, self.width, self.height, self.spatial_grid)
            
    def _parallel_update(self, dt):
        """Многопроцессорное обновление для очень больших популяций"""
        if not PARALLEL_AVAILABLE or not self.parallel_processor:
            # Fallback к обычному обновлению
            self._optimized_update(dt)
            return
            
        alive_organisms = [org for org in self.organisms if org.alive]
        if len(alive_organisms) < 200:
            # Для малых популяций параллелизм неэффективен
            self._optimized_update(dt)
            return
            
        start_time = time.time()
        
        try:
            # Конвертируем организмы в словари для передачи между процессами
            organisms_data = [convert_organism_to_data(org) for org in alive_organisms]
            
            # Обновляем организмы параллельно
            if not self.parallel_processor.use_parallel:
                self.parallel_processor.start_pool()
                
            updated_data = self.parallel_processor.parallel_update_organisms(
                organisms_data, self.width, self.height, dt
            )
            
            # Применяем изменения обратно к объектам организмов
            for org, data in zip(alive_organisms, updated_data):
                update_organism_from_data(org, data)
                
            # Записываем время для мониторинга
            parallel_time = time.time() - start_time
            if self.performance_monitor:
                self.performance_monitor.add_measurement(
                    len(alive_organisms), 
                    parallel_time=parallel_time
                )
                
        except Exception as e:
            print(f"⚠️ Ошибка параллельного обновления: {e}")
            # Fallback к обычному методу
            self._optimized_update(dt)
            
    def reset(self):
        """Сбрасывает симуляцию к начальному состоянию"""
        self.organisms = []
        self.food_sources = []
        self.generation_count = 0
        self.time_step = 0
        self.stats = {
            'population': 0,
            'predators': 0,
            'herbivores': 0,
            'omnivores': 0,
            'avg_speed': 0,
            'avg_size': 0,
            'avg_energy_efficiency': 0,
            'avg_generation': 0,
            'avg_aggression': 0,
            'avg_mutation_rate': 0,
            'avg_fitness': 0,
            'total_births': 0,
            'total_deaths': 0
        }
        # Очищаем историю генов
        for key in self.gene_history:
            self.gene_history[key] = []
            
        # Очищаем историю популяций
        for key in self.population_history:
            self.population_history[key] = []
        self._spawn_initial_organisms()
        
    def set_parameters(self, initial_organisms=None, food_spawn_rate=None):
        """Устанавливает параметры симуляции"""
        if initial_organisms is not None:
            self.initial_organisms = initial_organisms
        if food_spawn_rate is not None:
            self.food_spawn_rate = food_spawn_rate
            
    def get_organisms(self):
        """Возвращает список живых организмов"""
        return [org for org in self.organisms if org.alive]
        
    def get_food_sources(self):
        """Возвращает список источников пищи"""
        return [food for food in self.food_sources if not food.get('consumed', False)]
        
    def get_statistics(self):
        """Возвращает текущую статистику"""
        return self.stats.copy()
        
    def get_detailed_stats(self):
        """Возвращает подробную статистику по поколениям"""
        if not self.organisms:
            return {}
            
        alive_organisms = [org for org in self.organisms if org.alive]
        if not alive_organisms:
            return {}
            
        # Группируем по поколениям
        generations = {}
        for org in alive_organisms:
            gen = org.generation
            if gen not in generations:
                generations[gen] = []
            generations[gen].append(org)
            
        # Вычисляем статистику по поколениям
        gen_stats = {}
        for gen, orgs in generations.items():
            gen_stats[gen] = {
                'count': len(orgs),
                'avg_speed': sum(org.genes['speed'] for org in orgs) / len(orgs),
                'avg_size': sum(org.genes['size'] for org in orgs) / len(orgs),
                'avg_energy_efficiency': sum(org.genes['energy_efficiency'] for org in orgs) / len(orgs),
                'avg_aggression': sum(org.genes['aggression'] for org in orgs) / len(orgs),
            }
            
        return gen_stats
        
    def get_gene_history(self):
        """Возвращает историю изменений генов"""
        return self.gene_history.copy()
        
    def get_population_history(self):
        """Возвращает историю популяций по типам"""
        return self.population_history.copy()
        
    def get_best_organisms(self, top_n=5):
        """Возвращает самых приспособленных организмов"""
        alive_organisms = [org for org in self.organisms if org.alive]
        if not alive_organisms:
            return []
        return sorted(alive_organisms, key=lambda x: x.fitness, reverse=True)[:top_n]
        
    def get_performance_stats(self):
        """Возвращает статистику производительности"""
        if self.frame_count == 0:
            return {"avg_frame_time": 0, "fps": 0, "optimization": self.use_optimization}
            
        avg_frame_time = self.update_time_sum / self.frame_count
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        # Добавляем информацию о параллельной обработке
        parallel_info = {}
        if PARALLEL_AVAILABLE and self.performance_monitor:
            parallel_info.update({
                "parallel_available": True,
                "cpu_cores": self.parallel_processor.num_processes if self.parallel_processor else 0,
                "parallel_speedup": self.performance_monitor.get_speedup_ratio()
            })
        else:
            parallel_info.update({
                "parallel_available": False,
                "cpu_cores": 1,
                "parallel_speedup": 1.0
            })
        
        return {
            "avg_frame_time": avg_frame_time * 1000,  # В миллисекундах
            "fps": fps,
            "optimization": self.use_optimization,
            "population": len(self.organisms),
            "frame_count": self.frame_count,
            **parallel_info
        }
        
    def toggle_optimization(self):
        """Переключает режим оптимизации"""
        self.use_optimization = not self.use_optimization
        
    def reset_performance_counters(self):
        """Сбрасывает счётчики производительности"""
        self.frame_count = 0
        self.update_time_sum = 0