#!/usr/bin/env python3
"""
Тест многопроцессорной производительности для симуляции эволюции
Сравнивает производительность с параллелизмом и без него
"""

import time
import multiprocessing as mp
from simulation import EvolutionSimulation
from organism import Organism
import random

def create_test_population(sim, target_size):
    """Создает тестовую популяцию заданного размера"""
    print(f"Создание популяции из {target_size} организмов...")
    
    # Быстро создаем организмы
    for _ in range(target_size):
        x = random.uniform(50, sim.width - 50)
        y = random.uniform(50, sim.height - 50)
        organism = Organism(x, y)
        organism.energy = random.uniform(100, 200)  # Много энергии
        organism.age = random.uniform(0, 300)
        sim.organisms.append(organism)
    
    alive_count = len([org for org in sim.organisms if org.alive])
    print(f"Создано {alive_count} живых организмов")
    return alive_count

def benchmark_processing_modes(population_sizes, steps=50):
    """Тестирует разные режимы обработки на различных размерах популяций"""
    
    print("🚀 ТЕСТ МНОГОПРОЦЕССОРНОЙ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 60)
    print(f"Доступно CPU ядер: {mp.cpu_count()}")
    
    results = []
    
    for pop_size in population_sizes:
        print(f"\n📊 ТЕСТ ПОПУЛЯЦИИ: {pop_size} организмов")
        print("-" * 40)
        
        # Создаем симуляцию
        sim = EvolutionSimulation()
        actual_size = create_test_population(sim, pop_size)
        
        if actual_size < pop_size * 0.8:  # Если меньше 80% от цели
            print(f"⚠️ Недостаточно организмов для теста ({actual_size} < {pop_size})")
            continue
        
        # Тест БЕЗ параллелизма (принудительно отключаем)
        sim.parallel_processor = None
        sim.performance_monitor = None
        sim.reset_performance_counters()
        
        print("🔸 Тест БЕЗ параллелизма...")
        start_time = time.time()
        
        for step in range(steps):
            sim.update(dt=1.0)
            if step % 10 == 0:
                alive = len([org for org in sim.organisms if org.alive])
                print(f"  Шаг {step}: {alive} организмов")
        
        sequential_time = time.time() - start_time
        seq_stats = sim.get_performance_stats()
        
        # Пересоздаем популяцию для параллельного теста
        sim = EvolutionSimulation()
        create_test_population(sim, pop_size)
        
        # Проверяем доступность параллелизма
        has_parallel = hasattr(sim, 'parallel_processor') and sim.parallel_processor is not None
        
        if has_parallel:
            print("🔸 Тест С параллелизмом...")
            sim.reset_performance_counters()
            
            start_time = time.time()
            
            for step in range(steps):
                sim.update(dt=1.0)
                if step % 10 == 0:
                    alive = len([org for org in sim.organisms if org.alive])
                    print(f"  Шаг {step}: {alive} организмов")
            
            parallel_time = time.time() - start_time
            par_stats = sim.get_performance_stats()
        else:
            print("⚠️ Параллелизм недоступен")
            parallel_time = sequential_time
            par_stats = seq_stats
        
        # Результаты
        speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0
        
        print(f"\n📈 РЕЗУЛЬТАТЫ для {actual_size} организмов:")
        print(f"  Последовательно: {sequential_time:.2f}с (FPS: {seq_stats['fps']:.1f})")
        if has_parallel:
            print(f"  Параллельно:     {parallel_time:.2f}с (FPS: {par_stats['fps']:.1f})")
            print(f"  УСКОРЕНИЕ:       {speedup:.1f}x")
            
            if speedup > 2.0:
                print("  🎉 ОТЛИЧНОЕ ускорение!")
            elif speedup > 1.3:
                print("  👍 ХОРОШЕЕ ускорение")
            elif speedup > 1.1:
                print("  ✅ Умеренное ускорение")
            else:
                print("  😐 Минимальное ускорение")
        else:
            print("  📴 Параллелизм недоступен")
            
        results.append({
            'population': actual_size,
            'sequential_time': sequential_time,
            'parallel_time': parallel_time,
            'speedup': speedup,
            'has_parallel': has_parallel
        })
    
    return results

def detailed_parallel_analysis():
    """Детальный анализ параллельной производительности"""
    print("\n🔬 ДЕТАЛЬНЫЙ АНАЛИЗ ПАРАЛЛЕЛИЗМА")
    print("=" * 50)
    
    # Тестируем прогрессивно увеличивающиеся популяции
    test_sizes = [200, 500, 800, 1200, 1500, 2000]
    
    results = benchmark_processing_modes(test_sizes, steps=30)
    
    if not results:
        print("❌ Нет результатов для анализа")
        return
    
    print(f"\n📊 СВОДНАЯ ТАБЛИЦА:")
    print("-" * 60)
    print("Популяция | Послед. | Паралл. | Ускорение | Статус")
    print("-" * 60)
    
    total_speedup = 0
    parallel_tests = 0
    
    for result in results:
        pop = result['population']
        seq = result['sequential_time']
        par = result['parallel_time']
        speedup = result['speedup']
        has_par = result['has_parallel']
        
        status = "✅ Парал." if has_par and speedup > 1.1 else "⚠️ Медл." if has_par else "❌ Недост."
        
        print(f"{pop:8d} | {seq:6.2f}с | {par:6.2f}с | {speedup:7.1f}x | {status}")
        
        if has_par:
            total_speedup += speedup
            parallel_tests += 1
    
    print("-" * 60)
    
    if parallel_tests > 0:
        avg_speedup = total_speedup / parallel_tests
        print(f"СРЕДНЕЕ УСКОРЕНИЕ: {avg_speedup:.1f}x")
        
        if avg_speedup > 2.5:
            print("🏆 ПРЕВОСХОДНАЯ многопроцессорная оптимизация!")
        elif avg_speedup > 1.8:
            print("🎯 ОТЛИЧНАЯ многопроцессорная оптимизация!")
        elif avg_speedup > 1.3:
            print("👍 ХОРОШАЯ многопроцессорная оптимизация")
        else:
            print("😐 Параллелизм работает, но ускорение небольшое")
            
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print(f"  • Параллелизм эффективен при популяции > 500 организмов")
        print(f"  • Максимальное ускорение достигается при > 1000 организмов")
        print(f"  • Доступно {mp.cpu_count()} CPU ядер для параллельной обработки")
        print(f"  • Для оптимальной производительности используйте скорость 5x-15x")
    else:
        print("❌ Параллелизм недоступен или неэффективен")

def quick_parallel_demo():
    """Быстрая демонстрация параллелизма"""
    print("⚡ БЫСТРАЯ ДЕМОНСТРАЦИЯ ПАРАЛЛЕЛИЗМА")
    print("=" * 50)
    
    results = benchmark_processing_modes([800], steps=20)
    
    if results:
        result = results[0]
        if result['has_parallel'] and result['speedup'] > 1.1:
            print(f"\n🎉 Параллелизм работает! Ускорение: {result['speedup']:.1f}x")
            print(f"   Ваш процессор ({mp.cpu_count()} ядер) эффективно используется")
        else:
            print(f"\n😐 Параллелизм доступен, но ускорение минимально")
    else:
        print("\n❌ Не удалось протестировать параллелизм")

if __name__ == "__main__":
    print("🧪 ВЫБЕРИТЕ РЕЖИМ ТЕСТИРОВАНИЯ:")
    print("1. Быстрая демонстрация (1 минута)")
    print("2. Детальный анализ (5 минут)")
    print("3. Только проверка доступности")
    
    try:
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            quick_parallel_demo()
        elif choice == "2":
            detailed_parallel_analysis()
        elif choice == "3":
            print(f"CPU ядер: {mp.cpu_count()}")
            
            try:
                from parallel_optimization import ParallelSimulationProcessor
                processor = ParallelSimulationProcessor()
                print(f"Параллелизм: ✅ ДОСТУПЕН ({processor.num_processes} процессов)")
            except ImportError:
                print("Параллелизм: ❌ НЕДОСТУПЕН")
        else:
            print("Запуск быстрой демонстрации...")
            quick_parallel_demo()
            
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка тестирования: {e}")