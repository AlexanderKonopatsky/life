#!/usr/bin/env python3
"""
Асинхронная обёртка для симуляции
Запускает логику симуляции в отдельном потоке, независимо от GUI
"""

import threading
import time
import copy
from simulation import EvolutionSimulation

class AsyncSimulation:
    """Асинхронная симуляция, работающая в фоновом потоке"""
    
    def __init__(self):
        self.simulation = EvolutionSimulation()
        
        # Состояние потока
        self.simulation_thread = None
        self.is_running = False
        self.should_stop = False
        
        # Синхронизация данных
        self.data_lock = threading.Lock()
        self.cached_organisms = []
        self.cached_food = []
        
        # Инициализируем статистику значениями по умолчанию
        self.cached_stats = {
            'population': 0,
            'predators': 0,
            'herbivores': 0,
            'omnivores': 0,
            'avg_generation': 0,
            'total_births': 0,
            'total_deaths': 0,
            'avg_speed': 0.0,
            'avg_size': 0.0,
            'avg_energy_efficiency': 0.0,
            'avg_aggression': 0.0,
            'avg_fitness': 0.0
        }
        
        self.cached_performance = {
            'fps': 0.0,
            'avg_frame_time': 0.0,
            'optimization': True,
            'cpu_cores': 1,
            'parallel_available': False,
            'async_mode': True,
            'async_simulation_fps': 0.0,
            'simulation_steps': 0,
            'speed_multiplier': 1.0
        }
        
        # Настройки производительности
        self.target_simulation_fps = 60  # Логика работает на 60 FPS
        self.speed_multiplier = 1.0
        
        # Статистика
        self.actual_simulation_fps = 0
        self.simulation_steps = 0
        self.last_fps_time = time.time()
        
        # Инициализируем кэш данными из симуляции
        self._update_cached_data()
        
    def start(self):
        """Запускает фоновую симуляцию"""
        if self.is_running:
            return
            
        self.is_running = True
        self.should_stop = False
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        print("🚀 Асинхронная симуляция запущена")
        
    def stop(self):
        """Останавливает фоновую симуляцию"""
        if not self.is_running:
            return
            
        self.should_stop = True
        self.is_running = False
        
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=2.0)
            
        print("⏹️ Асинхронная симуляция остановлена")
        
    def pause(self):
        """Приостанавливает симуляцию"""
        self.is_running = False
        
    def resume(self):
        """Возобновляет симуляцию"""
        if not self.should_stop and not self.is_running:
            self.is_running = True
        
    def reset(self):
        """Сбрасывает симуляцию"""
        was_running = self.is_running
        self.stop()
        
        self.simulation = EvolutionSimulation()
        self._update_cached_data()
        
        if was_running:
            self.start()
        
    def set_speed(self, speed):
        """Устанавливает скорость симуляции"""
        self.speed_multiplier = max(0.1, min(50.0, speed))
        
    def set_parameters(self, **kwargs):
        """Устанавливает параметры симуляции"""
        with self.data_lock:
            self.simulation.set_parameters(**kwargs)
            
    def _simulation_loop(self):
        """Основной цикл симуляции в отдельном потоке"""
        frame_time = 1.0 / self.target_simulation_fps
        last_update = time.time()
        
        while not self.should_stop:
            current_time = time.time()
            
            if self.is_running:
                # ИСПРАВЛЕНО: используем фиксированный dt для стабильности
                # dt должно быть постоянным для предсказуемой физики
                base_dt = frame_time  # 1/60 = 0.0167 секунд
                dt = base_dt * self.speed_multiplier
                
                try:
                    # Обновляем симуляцию
                    self.simulation.update(dt)
                    
                    # ИСПРАВЛЕНО: обновляем кэш реже для лучшей производительности
                    if self.simulation_steps % 5 == 0:  # Каждые 5 шагов - компромисс между частотой и производительностью
                        self._update_cached_data_fast()
                    
                    self.simulation_steps += 1
                    
                    # Обновляем статистику FPS симуляции
                    self._update_simulation_fps()
                    
                except Exception as e:
                    print(f"❌ Ошибка в симуляции: {e}")
                    # Продолжаем работу, но замедляемся
                    time.sleep(0.1)
            
            last_update = current_time
            
            # Контроль частоты кадров симуляции
            elapsed = time.time() - current_time
            sleep_time = max(0, frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    def _update_cached_data(self):
        """Обновляет кэшированные данные для GUI (thread-safe)"""
        try:
            with self.data_lock:
                # Кэшируем организмы (делаем поверхностную копию для безопасности)
                organisms = self.simulation.get_organisms()
                self.cached_organisms = [
                    {
                        'x': org.x, 'y': org.y, 
                        'size': org.genes['size'],
                        'color': org.get_color(),
                        'energy': org.energy,
                        'fitness': org.fitness,
                        'type': org.get_type_name(),
                        'generation': org.generation,
                        'age': org.age,
                        'alive': org.alive,
                        'genes': dict(org.genes),  # Копия генов
                        'original': org  # Ссылка на оригинал для детальной информации
                    }
                    for org in organisms if org.alive
                ]
                
                # Кэшируем пищу
                food_sources = self.simulation.get_food_sources()
                self.cached_food = [
                    {
                        'x': food['x'], 'y': food['y'],
                        'size': food['size'], 'type': food.get('type', 'grass')
                    }
                    for food in food_sources if not food.get('consumed', False)
                ]
                
                # Кэшируем статистику
                self.cached_stats = dict(self.simulation.get_statistics())
                self.cached_performance = dict(self.simulation.get_performance_stats())
                
                # Добавляем статистику асинхронной симуляции
                self.cached_performance.update({
                    'async_simulation_fps': self.actual_simulation_fps,
                    'async_mode': True,
                    'simulation_steps': self.simulation_steps,
                    'speed_multiplier': self.speed_multiplier
                })
                
        except Exception as e:
            print(f"⚠️ Ошибка обновления кэша: {e}")
            
    def _update_cached_data_fast(self):
        """Быстрое обновление кэшированных данных - только критически важные поля"""
        try:
            # Используем trylock чтобы не блокировать симуляцию
            if self.data_lock.acquire(blocking=False):
                try:
                    # Кэшируем только основные данные для отрисовки
                    organisms = self.simulation.get_organisms()
                    self.cached_organisms = [
                        {
                            'x': org.x, 'y': org.y, 
                            'size': org.genes['size'],
                            'color': org.get_color(),
                            'energy': org.energy,
                            'original': org  # Минимум данных для быстроты
                        }
                        for org in organisms if org.alive
                    ]
                    
                    # Кэшируем пищу (быстро)
                    food_sources = self.simulation.get_food_sources()
                    self.cached_food = [
                        {
                            'x': food['x'], 'y': food['y'],
                            'size': food['size'], 'type': food.get('type', 'grass')
                        }
                        for food in food_sources if not food.get('consumed', False)
                    ]
                    
                    # Обновляем только основную статистику
                    stats = self.simulation.get_statistics()
                    self.cached_stats.update({
                        'population': stats.get('population', 0),
                        'predators': stats.get('predators', 0),
                        'herbivores': stats.get('herbivores', 0),
                        'omnivores': stats.get('omnivores', 0)
                    })
                    
                    # Обновляем производительность
                    self.cached_performance.update({
                        'async_simulation_fps': self.actual_simulation_fps,
                        'simulation_steps': self.simulation_steps,
                        'speed_multiplier': self.speed_multiplier
                    })
                    
                finally:
                    self.data_lock.release()
                    
        except Exception as e:
            print(f"⚠️ Ошибка быстрого обновления кэша: {e}")
            
    def _update_simulation_fps(self):
        """Обновляет статистику FPS симуляции"""
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:  # Каждую секунду
            time_elapsed = current_time - self.last_fps_time
            self.actual_simulation_fps = self.simulation_steps / time_elapsed
            
            self.simulation_steps = 0
            self.last_fps_time = current_time
    
    # Методы для безопасного доступа к данным из GUI потока
    
    def get_organisms_snapshot(self):
        """Возвращает снимок организмов для GUI (thread-safe)"""
        try:
            with self.data_lock:
                return list(self.cached_organisms)  # Возвращаем копию
        except:
            return []  # Безопасное значение по умолчанию
    
    def get_food_snapshot(self):
        """Возвращает снимок пищи для GUI (thread-safe)"""
        try:
            with self.data_lock:
                return list(self.cached_food)  # Возвращаем копию
        except:
            return []  # Безопасное значение по умолчанию
            
    def get_statistics_snapshot(self):
        """Возвращает снимок статистики для GUI (thread-safe)"""
        try:
            with self.data_lock:
                return dict(self.cached_stats)  # Возвращаем копию
        except:
            # Безопасные значения по умолчанию
            return {
                'population': 0, 'predators': 0, 'herbivores': 0, 'omnivores': 0,
                'avg_generation': 0, 'total_births': 0, 'total_deaths': 0,
                'avg_speed': 0.0, 'avg_size': 0.0, 'avg_energy_efficiency': 0.0,
                'avg_aggression': 0.0, 'avg_fitness': 0.0
            }
            
    def get_performance_snapshot(self):
        """Возвращает снимок производительности для GUI (thread-safe)"""
        try:
            with self.data_lock:
                return dict(self.cached_performance)  # Возвращаем копию
        except:
            # Безопасные значения по умолчанию
            return {
                'fps': 0.0, 'avg_frame_time': 0.0, 'optimization': True,
                'cpu_cores': 1, 'parallel_available': False, 'async_mode': True,
                'async_simulation_fps': 0.0, 'simulation_steps': 0, 'speed_multiplier': 1.0
            }
    
    def get_population_history(self):
        """Возвращает историю популяций"""
        with self.data_lock:
            return self.simulation.get_population_history()
            
    def get_gene_history(self):
        """Возвращает историю генов"""
        with self.data_lock:
            return self.simulation.get_gene_history()
            
    def get_best_organisms_snapshot(self, top_n=5):
        """Возвращает снимок лучших организмов"""
        with self.data_lock:
            # Сортируем кэшированные организмы по приспособленности
            sorted_organisms = sorted(self.cached_organisms, 
                                    key=lambda x: x['fitness'], reverse=True)
            return sorted_organisms[:top_n]
    
    def find_organism_by_position(self, x, y, max_distance=20):
        """Находит организм по позиции (для кликов мышью)"""
        with self.data_lock:
            min_distance = float('inf')
            closest_organism = None
            
            for org_data in self.cached_organisms:
                distance = ((x - org_data['x'])**2 + (y - org_data['y'])**2)**0.5
                if distance < min_distance and distance < max_distance:
                    min_distance = distance
                    closest_organism = org_data['original']  # Возвращаем ссылку на оригинал
                    
            return closest_organism
    
    def get_organism_info(self, organism):
        """Получает подробную информацию об организме"""
        if organism and organism.alive:
            with self.data_lock:
                return organism.get_info()
        return None
    
    def get_status(self):
        """Возвращает статус асинхронной симуляции"""
        return {
            'is_running': self.is_running,
            'should_stop': self.should_stop,
            'thread_alive': self.simulation_thread.is_alive() if self.simulation_thread else False,
            'population': len(self.cached_organisms),
            'simulation_fps': self.actual_simulation_fps,
            'speed_multiplier': self.speed_multiplier
        }

# Singleton для глобального доступа
_async_simulation_instance = None

def get_async_simulation():
    """Получает глобальный экземпляр асинхронной симуляции"""
    global _async_simulation_instance
    if _async_simulation_instance is None:
        _async_simulation_instance = AsyncSimulation()
    return _async_simulation_instance

if __name__ == "__main__":
    # Простой тест асинхронной симуляции
    print("🧪 Тестирование асинхронной симуляции...")
    
    async_sim = AsyncSimulation()
    async_sim.start()
    
    try:
        for i in range(20):
            time.sleep(0.5)
            status = async_sim.get_status()
            organisms = async_sim.get_organisms_snapshot()
            
            print(f"Шаг {i+1}: {len(organisms)} организмов, "
                  f"Симуляция FPS: {status['simulation_fps']:.1f}, "
                  f"Скорость: {status['speed_multiplier']}x")
                  
            if i == 10:
                print("🚀 Увеличиваем скорость до 5x")
                async_sim.set_speed(5.0)
                
    except KeyboardInterrupt:
        print("\n⏹️ Прерывание пользователем")
    finally:
        async_sim.stop()
        print("✅ Тест завершен")