#!/usr/bin/env python3
"""
Диагностика производительности асинхронной симуляции
Помогает найти узкие места в новой архитектуре
"""

import time
import threading
from async_simulation import AsyncSimulation

class PerformanceDiagnostic:
    """Диагностика производительности асинхронной симуляции"""
    
    def __init__(self):
        self.async_sim = AsyncSimulation()
        self.monitoring = False
        self.stats = {
            'gui_frame_times': [],
            'cache_update_times': [],
            'simulation_fps_history': [],
            'population_history': []
        }
        
    def monitor_gui_performance(self, duration_seconds=30):
        """Мониторинг производительности GUI"""
        print(f"🔍 Мониторинг GUI производительности в течение {duration_seconds} секунд...")
        
        self.async_sim.start()
        self.monitoring = True
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while time.time() - start_time < duration_seconds and self.monitoring:
                frame_start = time.time()
                
                # Симулируем работу GUI - получение данных
                try:
                    organisms_data = self.async_sim.get_organisms_snapshot()
                    food_data = self.async_sim.get_food_snapshot()
                    stats_data = self.async_sim.get_statistics_snapshot()
                    perf_data = self.async_sim.get_performance_snapshot()
                    
                    # Записываем статистику
                    population = len(organisms_data)
                    sim_fps = perf_data.get('async_simulation_fps', 0)
                    
                    self.stats['population_history'].append(population)
                    self.stats['simulation_fps_history'].append(sim_fps)
                    
                except Exception as e:
                    print(f"⚠️ Ошибка получения данных: {e}")
                
                frame_time = time.time() - frame_start
                self.stats['gui_frame_times'].append(frame_time * 1000)  # в мс
                
                frame_count += 1
                
                # Симулируем GUI FPS (30 FPS = 33.33ms на кадр)
                time.sleep(max(0, 0.0333 - frame_time))
                
                # Выводим прогресс каждые 5 секунд
                if frame_count % 150 == 0:  # примерно каждые 5 секунд при 30 FPS
                    elapsed = time.time() - start_time
                    avg_gui_time = sum(self.stats['gui_frame_times'][-150:]) / 150
                    current_pop = population
                    current_sim_fps = sim_fps
                    
                    print(f"  {elapsed:.1f}с: GUI {avg_gui_time:.1f}мс/кадр, Популяция: {current_pop}, Сим FPS: {current_sim_fps:.1f}")
                    
        except KeyboardInterrupt:
            print("\n⏹️ Мониторинг прерван пользователем")
        finally:
            self.monitoring = False
            self.async_sim.stop()
            
        return self._analyze_results()
    
    def _analyze_results(self):
        """Анализ результатов мониторинга"""
        if not self.stats['gui_frame_times']:
            print("❌ Нет данных для анализа")
            return {
                'avg_gui_time_ms': 0,
                'max_gui_time_ms': 0,
                'avg_population': 0,
                'max_population': 0,
                'avg_sim_fps': 0,
                'slow_frames_count': 0
            }
            
        gui_times = self.stats['gui_frame_times']
        pop_history = self.stats['population_history']
        sim_fps_history = self.stats['simulation_fps_history']
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ:")
        print("=" * 50)
        
        # Анализ GUI производительности
        avg_gui_time = sum(gui_times) / len(gui_times)
        max_gui_time = max(gui_times)
        min_gui_time = min(gui_times)
        
        print(f"GUI ПРОИЗВОДИТЕЛЬНОСТЬ:")
        print(f"  Среднее время кадра: {avg_gui_time:.2f}мс")
        print(f"  Минимальное время: {min_gui_time:.2f}мс")
        print(f"  Максимальное время: {max_gui_time:.2f}мс")
        print(f"  Целевое время (30 FPS): 33.33мс")
        
        if avg_gui_time > 33.33:
            print(f"  ⚠️ GUI работает медленнее целевого FPS!")
        else:
            print(f"  ✅ GUI производительность в норме")
            
        # Анализ популяции
        avg_pop = 0
        max_pop = 0
        min_pop = 0
        if pop_history:
            avg_pop = sum(pop_history) / len(pop_history)
            max_pop = max(pop_history)
            min_pop = min(pop_history)
            
            print(f"\nПОПУЛЯЦИЯ:")
            print(f"  Средняя: {avg_pop:.0f} организмов")
            print(f"  Минимальная: {min_pop}")
            print(f"  Максимальная: {max_pop}")
            
        # Анализ симуляции
        valid_fps = []
        avg_sim_fps = 0
        if sim_fps_history:
            valid_fps = [fps for fps in sim_fps_history if fps > 0]
            if valid_fps:
                avg_sim_fps = sum(valid_fps) / len(valid_fps)
                print(f"\nСИМУЛЯЦИЯ:")
                print(f"  Средний FPS: {avg_sim_fps:.1f}")
                print(f"  Целевой FPS: 60")
                
                if avg_sim_fps < 50:
                    print(f"  ⚠️ Симуляция работает медленнее целевого FPS!")
                else:
                    print(f"  ✅ Симуляция производительность в норме")
        
        # Поиск проблемных участков
        print(f"\n🔍 АНАЛИЗ ПРОБЛЕМ:")
        
        slow_frames = [t for t in gui_times if t > 50]  # Кадры дольше 50мс
        if slow_frames:
            print(f"  ⚠️ Обнаружено {len(slow_frames)} медленных GUI кадров (>{50}мс)")
            print(f"  Самый медленный кадр: {max(slow_frames):.2f}мс")
        else:
            print(f"  ✅ Нет критически медленных GUI кадров")
            
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        
        if avg_gui_time > 40:
            print(f"  🔧 GUI слишком медленный - нужна оптимизация отрисовки")
            
        if max_pop > 500:
            print(f"  🔧 При популяции >{max_pop} возможны лаги - усилить прореживание отрисовки")
            
        if valid_fps and avg_sim_fps < 50:
            print(f"  🔧 Симуляция работает медленно - проверить оптимизацию алгоритмов")
            
        return {
            'avg_gui_time_ms': avg_gui_time,
            'max_gui_time_ms': max_gui_time,
            'avg_population': avg_pop,
            'max_population': max_pop,
            'avg_sim_fps': avg_sim_fps,
            'slow_frames_count': len(slow_frames)
        }

def quick_diagnostic():
    """Быстрая диагностика на 15 секунд"""
    print("⚡ БЫСТРАЯ ДИАГНОСТИКА ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 50)
    
    diagnostic = PerformanceDiagnostic()
    results = diagnostic.monitor_gui_performance(duration_seconds=15)
    
    print(f"\n🎯 КРАТКИЕ ВЫВОДЫ:")
    if results['avg_gui_time_ms'] < 35:
        print("✅ GUI производительность отличная")
    elif results['avg_gui_time_ms'] < 50:
        print("⚠️ GUI производительность приемлемая")
    else:
        print("🚨 GUI производительность критична")
        
    if results['avg_sim_fps'] > 55:
        print("✅ Симуляция работает отлично")
    elif results['avg_sim_fps'] > 45:
        print("⚠️ Симуляция работает приемлемо")
    else:
        print("🚨 Симуляция работает медленно")

def stress_test():
    """Стресс-тест с большой популяцией"""
    print("🔥 СТРЕСС-ТЕСТ С БОЛЬШОЙ ПОПУЛЯЦИЕЙ")
    print("=" * 50)
    
    diagnostic = PerformanceDiagnostic()
    
    # Создаем большую популяцию
    print("Создание большой популяции...")
    for i in range(300):  # Создаем 300 организмов
        from organism import Organism
        import random
        x = random.uniform(50, 850)
        y = random.uniform(50, 650)
        organism = Organism(x, y)
        organism.energy = random.uniform(120, 200)
        diagnostic.async_sim.simulation.organisms.append(organism)
    
    print(f"Создано {len(diagnostic.async_sim.simulation.organisms)} организмов")
    
    # Мониторим производительность
    results = diagnostic.monitor_gui_performance(duration_seconds=20)
    
    print(f"\n🔥 РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТА:")
    print(f"Максимальная популяция: {results['max_population']}")
    print(f"Производительность GUI: {results['avg_gui_time_ms']:.1f}мс")
    print(f"Медленных кадров: {results['slow_frames_count']}")

if __name__ == "__main__":
    print("🧪 ВЫБЕРИТЕ ТИП ДИАГНОСТИКИ:")
    print("1. Быстрая диагностика (15 секунд)")
    print("2. Стресс-тест с большой популяцией")
    print("3. Полный мониторинг (30 секунд)")
    
    try:
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            quick_diagnostic()
        elif choice == "2":
            stress_test()
        elif choice == "3":
            diagnostic = PerformanceDiagnostic()
            diagnostic.monitor_gui_performance(duration_seconds=30)
        else:
            print("Запуск быстрой диагностики...")
            quick_diagnostic()
            
    except KeyboardInterrupt:
        print("\n⏹️ Диагностика прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка диагностики: {e}")