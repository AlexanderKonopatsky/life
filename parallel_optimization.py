"""
Модуль многопроцессорной оптимизации для симуляции эволюции
Использует все ядра CPU для обработки больших популяций (1000+ организмов)
"""
# type: ignore

import multiprocessing as mp
import math
import time
from typing import List, Dict, Any
import concurrent.futures

# Опциональный импорт NumPy для векторизации
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy не установлен - векторизация недоступна")

class ParallelSimulationProcessor:
    """Многопроцессорный обработчик симуляции"""
    
    def __init__(self, num_processes=None):
        # Автоматически определяем количество процессов
        if num_processes is None:
            self.num_processes = max(1, mp.cpu_count() - 1)  # Оставляем 1 ядро для GUI
        else:
            self.num_processes = num_processes
            
        self.process_pool = None
        self.use_parallel = False
        
        print(f"🚀 Параллельный процессор инициализирован: {self.num_processes} процессов")
        
    def should_use_parallel(self, population_size):
        """Определяет нужна ли параллельная обработка"""
        # Включаем параллелизм при популяции > 200 и наличии >= 2 ядер
        return population_size > 200 and self.num_processes > 1
        
    def start_pool(self):
        """Запускает пул процессов"""
        if self.process_pool is None:
            self.process_pool = mp.Pool(processes=self.num_processes)
            self.use_parallel = True
            
    def stop_pool(self):
        """Останавливает пул процессов"""
        if self.process_pool:
            self.process_pool.close()
            self.process_pool.join()
            self.process_pool = None
            self.use_parallel = False
            
    def parallel_update_organisms(self, organisms_data, world_width, world_height, dt):
        """Параллельное обновление организмов"""
        if not self.use_parallel or len(organisms_data) < 200:
            # Для малых популяций используем обычный режим
            return self._sequential_update(organisms_data, world_width, world_height, dt)
            
        # Разбиваем организмы на чанки для процессов
        chunk_size = max(50, len(organisms_data) // self.num_processes)
        chunks = [organisms_data[i:i + chunk_size] for i in range(0, len(organisms_data), chunk_size)]
        
        try:
            # Обрабатываем чанки параллельно
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.num_processes) as executor:
                futures = [
                    executor.submit(_update_organism_chunk, chunk, world_width, world_height, dt, i)
                    for i, chunk in enumerate(chunks)
                ]
                
                # Собираем результаты
                updated_organisms = []
                for future in concurrent.futures.as_completed(futures):
                    try:
                        chunk_result = future.result(timeout=1.0)  # Таймаут 1 сек
                        updated_organisms.extend(chunk_result)
                    except concurrent.futures.TimeoutError:
                        print("⚠️ Таймаут параллельной обработки, возврат к последовательной")
                        return self._sequential_update(organisms_data, world_width, world_height, dt)
                        
                return updated_organisms
                
        except Exception as e:
            print(f"⚠️ Ошибка параллельной обработки: {e}")
            return self._sequential_update(organisms_data, world_width, world_height, dt)
            
    def _sequential_update(self, organisms_data, world_width, world_height, dt):
        """Последовательное обновление для совместимости"""
        return _update_organism_chunk(organisms_data, world_width, world_height, dt, 0)

class VectorizedOperations:
    """Векторизованные операции с NumPy для ускорения"""
    
    @staticmethod
    def calculate_distances_vectorized(positions1, positions2):
        """Быстрый расчет расстояний между двумя наборами точек"""
        if not NUMPY_AVAILABLE:
            return []
            
        pos1 = np.array(positions1)
        pos2 = np.array(positions2)
        
        # Векторизованный расчет квадратов расстояний
        diff = pos1[:, np.newaxis] - pos2[np.newaxis, :]
        distances_squared = np.sum(diff**2, axis=2)
        
        return distances_squared
        
    @staticmethod
    def find_nearby_organisms_vectorized(org_positions, search_radius=80):
        """Векторизованный поиск близких организмов"""
        if not NUMPY_AVAILABLE:
            return []
            
        positions = np.array(org_positions)
        
        if len(positions) == 0:
            return []
            
        # Матрица расстояний
        distances_sq = VectorizedOperations.calculate_distances_vectorized(positions, positions)
        
        # Найдем соседей в радиусе
        radius_sq = search_radius * search_radius
        nearby_mask = (distances_sq < radius_sq) & (distances_sq > 0)
        
        return nearby_mask
        
    @staticmethod
    def update_energies_vectorized(organisms_data, dt):
        """Векторизованное обновление энергии"""
        if not NUMPY_AVAILABLE or not organisms_data:
            return
            
        # Извлекаем данные в массивы NumPy
        sizes = np.array([org['size'] for org in organisms_data])
        speeds = np.array([org['speed'] for org in organisms_data])
        efficiencies = np.array([org['energy_efficiency'] for org in organisms_data])
        is_predator = np.array([org['is_predator'] for org in organisms_data])
        ages = np.array([org['age'] for org in organisms_data])
        max_lifespans = np.array([org['max_lifespan'] for org in organisms_data])
        
        # Векторизованный расчет потребления энергии
        base_consumption = (sizes * 0.015 + speeds * 0.008) * dt
        base_consumption[is_predator] *= 1.5
        
        # Векторизованный расчет модификатора старения
        age_ratios = ages / max_lifespans
        age_modifiers = np.ones_like(age_ratios)
        
        # Молодые (0-30%)
        young_mask = age_ratios < 0.3
        age_modifiers[young_mask] = 0.7 + age_ratios[young_mask] * 1.0
        
        # Старые (70-100%)
        old_mask = age_ratios >= 0.7
        decline = (age_ratios[old_mask] - 0.7) / 0.3
        age_modifiers[old_mask] = 1.0 - decline * 0.4
        
        # Финальный расчет энергии
        modified_efficiencies = efficiencies * age_modifiers
        energy_deltas = -base_consumption / np.maximum(0.1, modified_efficiencies)
        
        # Применяем изменения обратно к организмам
        for i, org in enumerate(organisms_data):
            org['energy'] += energy_deltas[i]
            org['age'] += dt

def _update_organism_chunk(organisms_chunk, world_width, world_height, dt, chunk_id):
    """Обновляет чанк организмов (выполняется в отдельном процессе)"""
    
    updated_organisms = []
    
    for org_data in organisms_chunk:
        if not org_data.get('alive', True):
            continue
            
        # Простое обновление для параллельной обработки
        org_data['age'] += dt
        
        # Потребление энергии
        base_consumption = (org_data['size'] * 0.015 + org_data['speed'] * 0.008) * dt
        if org_data.get('is_predator', False):
            base_consumption *= 1.5
            
        # Эффект старения
        age_ratio = org_data['age'] / org_data.get('max_lifespan', 800)
        if age_ratio < 0.3:
            age_modifier = 0.7 + age_ratio * 1.0
        elif age_ratio < 0.7:
            age_modifier = 1.0
        else:
            decline = (age_ratio - 0.7) / 0.3
            age_modifier = 1.0 - decline * 0.4
            
        efficiency = org_data['energy_efficiency'] * age_modifier
        org_data['energy'] -= base_consumption / max(0.1, efficiency)
        
        # Движение (упрощенное)
        speed = org_data['speed'] * age_modifier
        
        # Простое случайное движение для параллельной обработки
        import random
        if 'direction' not in org_data:
            org_data['direction'] = random.uniform(0, 2 * math.pi)
            
        if random.random() < 0.15:
            org_data['direction'] += random.uniform(-0.8, 0.8)
            
        # Обновление позиции
        org_data['x'] += math.cos(org_data['direction']) * speed * dt
        org_data['y'] += math.sin(org_data['direction']) * speed * dt
        
        # Границы мира
        if org_data['x'] < 0 or org_data['x'] > world_width:
            org_data['direction'] = np.pi - org_data['direction']
            org_data['x'] = max(0, min(world_width, org_data['x']))
            
        if org_data['y'] < 0 or org_data['y'] > world_height:
            org_data['direction'] = -org_data['direction']
            org_data['y'] = max(0, min(world_height, org_data['y']))
            
        # Проверка на смерть
        if org_data['energy'] <= 0 or org_data['age'] > org_data.get('max_lifespan', 800):
            org_data['alive'] = False
        else:
            # Расчет приспособленности
            org_data['fitness'] = (org_data['energy'] * 0.1 + 
                                 org_data['age'] * 0.05 + 
                                 (200 - org_data.get('last_meal', 0)) * 0.02)
            
        updated_organisms.append(org_data)
        
    return updated_organisms

def convert_organism_to_data(organism):
    """Конвертирует объект организма в словарь для параллельной обработки"""
    return {
        'x': organism.x,
        'y': organism.y,
        'energy': organism.energy,
        'age': organism.age,
        'alive': organism.alive,
        'generation': organism.generation,
        'fitness': organism.fitness,
        'max_lifespan': organism.max_lifespan,
        'speed': organism.genes['speed'],
        'size': organism.genes['size'],
        'energy_efficiency': organism.genes['energy_efficiency'],
        'is_predator': organism.is_predator(),
        'direction': getattr(organism, 'direction', 0),
        'last_meal': getattr(organism, 'last_meal', 0),
        'genes': organism.genes.copy()
    }

def update_organism_from_data(organism, data):
    """Обновляет объект организма из данных параллельной обработки"""
    organism.x = data['x']
    organism.y = data['y']
    organism.energy = data['energy']
    organism.age = data['age']
    organism.alive = data['alive']
    organism.fitness = data['fitness']
    organism.direction = data.get('direction', organism.direction)
    organism.last_meal = data.get('last_meal', organism.last_meal)

class PerformanceMonitor:
    """Мониторинг производительности параллельной обработки"""
    
    def __init__(self):
        self.parallel_times = []
        self.sequential_times = []
        self.population_sizes = []
        
    def add_measurement(self, population_size, parallel_time=None, sequential_time=None):
        """Добавляет измерение производительности"""
        self.population_sizes.append(population_size)
        if parallel_time is not None:
            self.parallel_times.append(parallel_time)
        if sequential_time is not None:
            self.sequential_times.append(sequential_time)
            
    def get_speedup_ratio(self):
        """Возвращает коэффициент ускорения"""
        if len(self.parallel_times) > 0 and len(self.sequential_times) > 0:
            avg_parallel = sum(self.parallel_times) / len(self.parallel_times)
            avg_sequential = sum(self.sequential_times) / len(self.sequential_times)
            return avg_sequential / avg_parallel if avg_parallel > 0 else 1.0
        return 1.0
        
    def should_use_parallel(self, population_size):
        """Адаптивное решение об использовании параллелизма"""
        # Эвристика: используем параллелизм если популяция > 300
        # и если предыдущие измерения показывают ускорение
        if population_size < 300:
            return False
            
        if len(self.parallel_times) < 3:
            return True  # Пробуем параллелизм для накопления статистики
            
        return self.get_speedup_ratio() > 1.1  # Используем если ускорение > 10%