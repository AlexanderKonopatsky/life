#!/usr/bin/env python3
"""
Детальный профайлер производительности симуляции
Помогает найти узкие места и bottlenecks
"""

import time
import random
import cProfile
import pstats
import io
from simulation import EvolutionSimulation
from organism import Organism

class PerformanceProfiler:
    """Профайлер для анализа производительности симуляции"""
    
    def __init__(self):
        self.timings = {}
        
    def create_large_population(self, sim, target_size):
        """Быстро создает большую популяцию для тестирования"""
        print(f"Создание популяции {target_size} организмов...")
        
        # Создаем организмы напрямую без симуляции размножения
        for i in range(target_size):
            x = random.uniform(50, sim.width - 50)
            y = random.uniform(50, sim.height - 50)
            organism = Organism(x, y)
            organism.energy = random.uniform(120, 200)  # Высокая энергия
            organism.age = int(random.uniform(0, 100))  # Молодые
            sim.organisms.append(organism)
            
        alive_count = len([org for org in sim.organisms if org.alive])
        print(f"Создано {alive_count} живых организмов")
        return alive_count
        
    def profile_simulation_step(self, population_size, steps=10):
        """Профилирует один шаг симуляции"""
        print(f"\n🔍 ПРОФИЛИРОВАНИЕ {population_size} ОРГАНИЗМОВ")
        print("=" * 50)
        
        # Создаем симуляцию с заданной популяцией
        sim = EvolutionSimulation()
        actual_size = self.create_large_population(sim, population_size)
        
        # Прогреваем систему
        for _ in range(3):
            sim.update(dt=1.0)
        
        print(f"Тестирование {steps} шагов...")
        
        # Профилируем с cProfile
        profiler = cProfile.Profile()
        
        start_time = time.time()
        profiler.enable()
        
        for step in range(steps):
            sim.update(dt=1.0)
            
        profiler.disable()
        total_time = time.time() - start_time
        
        # Анализируем результаты
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)  # Топ 20 функций
        
        profile_output = s.getvalue()
        
        print(f"\n⏱️ ОБЩИЕ РЕЗУЛЬТАТЫ:")
        print(f"Общее время: {total_time:.3f}с")
        print(f"Время на шаг: {total_time/steps:.3f}с")
        print(f"FPS: {steps/total_time:.1f}")
        
        final_population = len([org for org in sim.organisms if org.alive])
        print(f"Финальная популяция: {final_population}")
        
        return {
            'population_size': actual_size,
            'total_time': total_time,
            'time_per_step': total_time / steps,
            'fps': steps / total_time,
            'profile_data': profile_output
        }
        
    def detailed_timing_analysis(self, population_size):
        """Детальный анализ времени по компонентам"""
        print(f"\n🕐 ДЕТАЛЬНЫЙ АНАЛИЗ ВРЕМЕНИ ({population_size} организмов)")
        print("=" * 60)
        
        sim = EvolutionSimulation()
        self.create_large_population(sim, population_size)
        
        # Прогреваем
        for _ in range(3):
            sim.update(dt=1.0)
        
        components = {
            'spawn_food': 0,
            'update_organisms': 0,
            'handle_reproduction': 0,
            'remove_dead': 0,
            'update_statistics': 0,
            'other': 0
        }
        
        num_tests = 20
        print(f"Тестирование {num_tests} шагов...")
        
        for step in range(num_tests):
            step_start = time.time()
            
            # Мониторим каждый компонент отдельно
            
            # 1. Spawn food
            start = time.time()
            sim._spawn_food()
            components['spawn_food'] += time.time() - start
            
            # 2. Update organisms  
            start = time.time()
            population_size_current = len([org for org in sim.organisms if org.alive])
            
            if hasattr(sim, 'parallel_processor') and sim.parallel_processor and population_size_current > 100:
                sim._parallel_update(1.0)
            elif sim.use_optimization:
                sim._optimized_update(1.0)
            else:
                sim._simple_update(1.0)
                
            components['update_organisms'] += time.time() - start
            
            # 3. Handle reproduction
            start = time.time()
            sim._handle_reproduction()
            components['handle_reproduction'] += time.time() - start
            
            # 4. Remove dead
            start = time.time() 
            sim._remove_dead_organisms()
            components['remove_dead'] += time.time() - start
            
            # 5. Update statistics
            start = time.time()
            if step % 5 == 0:
                sim._update_statistics()
            components['update_statistics'] += time.time() - start
            
            # 6. Other overhead
            step_total = time.time() - step_start
            measured_total = sum(components.values())
            components['other'] += max(0, step_total - measured_total)
        
        # Выводим результаты
        total_time = sum(components.values())
        print(f"\nРАСПРЕДЕЛЕНИЕ ВРЕМЕНИ (всего {total_time:.3f}с):")
        print("-" * 50)
        
        sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
        
        for component, time_spent in sorted_components:
            percentage = (time_spent / total_time) * 100 if total_time > 0 else 0
            avg_time = time_spent / num_tests * 1000  # мс на шаг
            
            print(f"{component:20s}: {time_spent:.3f}с ({percentage:5.1f}%) | {avg_time:.1f}мс/шаг")
            
        print("-" * 50)
        print(f"ИТОГО: {total_time:.3f}с (100.0%)")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        
        if components['update_organisms'] > total_time * 0.7:
            print("  ⚠️ Обновление организмов занимает >70% времени - нужна оптимизация алгоритмов")
        
        if components['spawn_food'] > total_time * 0.1:
            print("  ⚠️ Создание пищи занимает >10% времени - можно кэшировать")
            
        if components['update_statistics'] > total_time * 0.1:
            print("  ⚠️ Обновление статистики занимает >10% времени - нужно реже обновлять")
            
        if components['handle_reproduction'] > total_time * 0.2:
            print("  ⚠️ Размножение занимает >20% времени - можно оптимизировать")
            
        print(f"  ✅ Для {population_size} организмов оптимальное время шага: <{50/population_size*1000:.1f}мс")
        
        return components
        
    def compare_optimization_modes(self, population_size):
        """Сравнивает разные режимы оптимизации"""
        print(f"\n🏁 СРАВНЕНИЕ РЕЖИМОВ ОПТИМИЗАЦИИ ({population_size} организмов)")
        print("=" * 70)
        
        modes = [
            ("Без оптимизации", False, False),
            ("Пространственная оптимизация", True, False), 
            ("Многопроцессорность", True, True)
        ]
        
        results = {}
        
        for mode_name, use_spatial, use_parallel in modes:
            print(f"\n🔸 Тестирование: {mode_name}")
            
            sim = EvolutionSimulation()
            self.create_large_population(sim, population_size)
            
            # Настраиваем режим
            sim.use_optimization = use_spatial
            if not use_parallel:
                sim.parallel_processor = None
                sim.performance_monitor = None
            
            # Прогреваем
            for _ in range(3):
                sim.update(dt=1.0)
            
            # Тестируем
            steps = 15
            start_time = time.time()
            
            for step in range(steps):
                sim.update(dt=1.0)
                if step % 5 == 0:
                    alive = len([org for org in sim.organisms if org.alive])
                    print(f"  Шаг {step}: {alive} организмов")
            
            test_time = time.time() - start_time
            fps = steps / test_time
            
            results[mode_name] = {
                'time': test_time,
                'fps': fps,
                'time_per_step': test_time / steps
            }
            
            print(f"  Результат: {test_time:.2f}с ({fps:.1f} FPS)")
        
        # Сравнительная таблица
        print(f"\n📊 СРАВНИТЕЛЬНАЯ ТАБЛИЦА:")
        print("-" * 70)
        print("Режим                        | Время  | FPS   | мс/шаг | Ускорение")
        print("-" * 70)
        
        baseline_time = results[list(results.keys())[0]]['time']
        
        for mode_name, data in results.items():
            speedup = baseline_time / data['time']
            ms_per_step = data['time_per_step'] * 1000
            
            print(f"{mode_name:28s} | {data['time']:5.2f}с | {data['fps']:4.1f} | {ms_per_step:5.1f}  | {speedup:6.1f}x")
        
        print("-" * 70)
        
        # Рекомендации
        best_mode = max(results.items(), key=lambda x: x[1]['fps'])
        print(f"\n🏆 ЛУЧШИЙ РЕЖИМ: {best_mode[0]} ({best_mode[1]['fps']:.1f} FPS)")
        
        return results

def run_comprehensive_analysis():
    """Запускает комплексный анализ производительности"""
    profiler = PerformanceProfiler()
    
    print("🔬 КОМПЛЕКСНЫЙ АНАЛИЗ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 60)
    
    test_sizes = [200, 500, 1000, 1500]
    
    for size in test_sizes:
        print(f"\n{'='*20} ПОПУЛЯЦИЯ {size} {'='*20}")
        
        # 1. Базовое профилирование
        profile_result = profiler.profile_simulation_step(size, steps=15)
        
        # 2. Детальный анализ времени
        timing_analysis = profiler.detailed_timing_analysis(size)
        
        # 3. Сравнение режимов оптимизации
        mode_comparison = profiler.compare_optimization_modes(size)
        
        print(f"\n📋 КРАТКИЕ ВЫВОДЫ ДЛЯ {size} ОРГАНИЗМОВ:")
        if profile_result['fps'] < 10:
            print("  ⚠️ КРИТИЧНО: FPS < 10 - нужна срочная оптимизация")
        elif profile_result['fps'] < 20:
            print("  ⚠️ МЕДЛЕННО: FPS < 20 - желательна оптимизация")
        else:
            print("  ✅ ПРИЕМЛЕМО: FPS > 20")
            
        # Топ узкое место
        top_bottleneck = max(timing_analysis.items(), key=lambda x: x[1])
        print(f"  🎯 Основное узкое место: {top_bottleneck[0]} ({top_bottleneck[1]/sum(timing_analysis.values())*100:.1f}%)")

def quick_performance_check():
    """Быстрая проверка производительности"""
    print("⚡ БЫСТРАЯ ПРОВЕРКА ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 50)
    
    profiler = PerformanceProfiler()
    
    # Тестируем проблемную популяцию
    problem_size = 1000
    print(f"Тестирование популяции {problem_size} организмов...")
    
    result = profiler.profile_simulation_step(problem_size, steps=10)
    
    print(f"\n📊 РЕЗУЛЬТАТ:")
    print(f"FPS: {result['fps']:.1f}")
    print(f"Время на шаг: {result['time_per_step']*1000:.1f}мс")
    
    if result['fps'] < 5:
        print("🚨 КРИТИЧЕСКАЯ проблема производительности!")
    elif result['fps'] < 15:
        print("⚠️ Производительность ниже оптимальной")
    else:
        print("✅ Производительность приемлемая")
    
    # Показываем топ bottlenecks из профайлера
    lines = result['profile_data'].split('\n')
    print(f"\n🔍 ТОП ФУНКЦИЙ ПО ВРЕМЕНИ:")
    for i, line in enumerate(lines[5:15]):  # Пропускаем заголовки
        if line.strip() and 'ncalls' not in line:
            print(f"  {line}")

if __name__ == "__main__":
    print("🧪 ВЫБЕРИТЕ ТИП АНАЛИЗА:")
    print("1. Быстрая проверка (1 минута)")
    print("2. Комплексный анализ (10 минут)")
    print("3. Только детальный анализ времени")
    
    try:
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            quick_performance_check()
        elif choice == "2":
            run_comprehensive_analysis()
        elif choice == "3":
            profiler = PerformanceProfiler()
            size = int(input("Введите размер популяции: "))
            profiler.detailed_timing_analysis(size)
        else:
            print("Запуск быстрой проверки...")
            quick_performance_check()
            
    except KeyboardInterrupt:
        print("\n⏹️ Анализ прерван пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка анализа: {e}")