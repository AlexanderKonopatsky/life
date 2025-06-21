#!/usr/bin/env python3
"""
Тест производительности оптимизированной симуляции
Сравнивает производительность с оптимизацией и без неё
"""

from simulation import EvolutionSimulation
from organism import Organism
import time
import random

def create_large_population(sim, target_population):
    """Создаёт большую популяцию для тестирования"""
    print(f"Создание популяции из {target_population} организмов...")
    
    # Добавляем организмы до нужного размера
    while len(sim.get_organisms()) < target_population:
        # Создаём организмы с разными характеристиками
        for _ in range(min(50, target_population - len(sim.get_organisms()))):
            x = random.uniform(50, sim.width - 50)
            y = random.uniform(50, sim.height - 50)
            organism = Organism(x, y)
            organism.energy = random.uniform(80, 150)  # Достаточно энергии
            organism.age = random.uniform(0, 200)
            sim.organisms.append(organism)
            
        # Делаем несколько шагов для размножения
        for _ in range(10):
            sim.update(dt=1.0)
            
        alive_count = len([org for org in sim.organisms if org.alive])
        print(f"  Текущая популяция: {alive_count}")
        
        if alive_count == 0:  # Если все умерли, начинаем заново
            sim._spawn_initial_organisms()

def benchmark_simulation(population_size, steps=100):
    """Бенчмарк симуляции с заданным размером популяции"""
    print(f"\n🔬 ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ - {population_size} организмов")
    print("=" * 60)
    
    # Создаём симуляцию
    sim = EvolutionSimulation(width=900, height=700)
    
    # Создаём большую популяцию
    create_large_population(sim, population_size)
    
    final_population = len([org for org in sim.organisms if org.alive])
    print(f"Финальная популяция для теста: {final_population}")
    
    # Тест БЕЗ оптимизации
    print(f"\n📊 ТЕСТ БЕЗ оптимизации:")
    sim.use_optimization = False
    sim.reset_performance_counters()
    
    start_time = time.time()
    for step in range(steps):
        sim.update(dt=1.0)
        if step % 20 == 0:
            current_pop = len([org for org in sim.organisms if org.alive])
            print(f"  Шаг {step}: популяция {current_pop}")
    
    unoptimized_time = time.time() - start_time
    unoptimized_stats = sim.get_performance_stats()
    
    # Тест С оптимизацией
    print(f"\n⚡ ТЕСТ С оптимизацией:")
    sim.use_optimization = True
    sim.reset_performance_counters()
    
    start_time = time.time()
    for step in range(steps):
        sim.update(dt=1.0)
        if step % 20 == 0:
            current_pop = len([org for org in sim.organisms if org.alive])
            print(f"  Шаг {step}: популяция {current_pop}")
    
    optimized_time = time.time() - start_time
    optimized_stats = sim.get_performance_stats()
    
    # Результаты
    print(f"\n📈 РЕЗУЛЬТАТЫ ({population_size} организмов, {steps} шагов):")
    print("-" * 50)
    print(f"БЕЗ оптимизации:")
    print(f"  Общее время: {unoptimized_time:.2f}с")
    print(f"  Время/кадр: {unoptimized_stats['avg_frame_time']:.1f}мс")
    print(f"  FPS: {unoptimized_stats['fps']:.1f}")
    
    print(f"\nС оптимизацией:")
    print(f"  Общее время: {optimized_time:.2f}с") 
    print(f"  Время/кадр: {optimized_stats['avg_frame_time']:.1f}мс")
    print(f"  FPS: {optimized_stats['fps']:.1f}")
    
    if unoptimized_time > 0:
        speedup = unoptimized_time / optimized_time
        print(f"\n🚀 УСКОРЕНИЕ: {speedup:.1f}x")
        
        if speedup > 1.5:
            print("✅ Значительное улучшение производительности!")
        elif speedup > 1.1:
            print("✅ Умеренное улучшение производительности")
        else:
            print("⚠️ Минимальное улучшение")
    
    return {
        'population': final_population,
        'unoptimized_time': unoptimized_time,
        'optimized_time': optimized_time,
        'speedup': unoptimized_time / optimized_time if optimized_time > 0 else 1
    }

def run_full_benchmark():
    """Запускает полный бенчмарк с разными размерами популяции"""
    print("🏁 ПОЛНЫЙ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 60)
    
    # Тестируем разные размеры популяций
    test_sizes = [100, 300, 500, 800, 1000]
    results = []
    
    for size in test_sizes:
        try:
            result = benchmark_simulation(size, steps=50)
            results.append(result)
        except Exception as e:
            print(f"❌ Ошибка при тесте {size} организмов: {e}")
            continue
    
    # Итоговая сводка
    print(f"\n🏆 ИТОГОВАЯ СВОДКА:")
    print("=" * 60)
    print("Популяция | Без опт. | С опт. | Ускорение")
    print("-" * 45)
    
    total_speedup = 0
    valid_tests = 0
    
    for result in results:
        pop = result['population']
        unopt = result['unoptimized_time']
        opt = result['optimized_time'] 
        speedup = result['speedup']
        
        print(f"{pop:8d} | {unopt:7.2f}с | {opt:6.2f}с | {speedup:7.1f}x")
        
        total_speedup += speedup
        valid_tests += 1
    
    if valid_tests > 0:
        avg_speedup = total_speedup / valid_tests
        print("-" * 45)
        print(f"СРЕДНЕЕ УСКОРЕНИЕ: {avg_speedup:.1f}x")
        
        if avg_speedup > 3:
            print("🎉 ОТЛИЧНАЯ оптимизация!")
        elif avg_speedup > 2:
            print("🎯 ХОРОШАЯ оптимизация!")
        elif avg_speedup > 1.5:
            print("👍 НЕПЛОХАЯ оптимизация")
        else:
            print("🤔 Нужна дополнительная оптимизация")

def quick_demo():
    """Быстрая демонстрация оптимизации"""
    print("⚡ БЫСТРАЯ ДЕМОНСТРАЦИЯ ОПТИМИЗАЦИИ")
    print("=" * 50)
    
    sim = EvolutionSimulation()
    
    # Создаём популяцию ~200 организмов
    create_large_population(sim, 200)
    current_pop = len([org for org in sim.organisms if org.alive])
    
    print(f"\nТестирование с {current_pop} организмами...")
    
    # Тест без оптимизации (10 шагов)
    sim.use_optimization = False
    sim.reset_performance_counters()
    
    start = time.time()
    for _ in range(10):
        sim.update()
    unopt_time = time.time() - start
    
    # Тест с оптимизацией (10 шагов)
    sim.use_optimization = True
    sim.reset_performance_counters()
    
    start = time.time()
    for _ in range(10):
        sim.update()
    opt_time = time.time() - start
    
    print(f"\nРезультаты (10 кадров):")
    print(f"Без оптимизации: {unopt_time:.3f}с")
    print(f"С оптимизацией:  {opt_time:.3f}с")
    
    if opt_time > 0:
        speedup = unopt_time / opt_time
        print(f"Ускорение: {speedup:.1f}x")

if __name__ == "__main__":
    import sys
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "quick":
            quick_demo()
        elif len(sys.argv) > 1 and sys.argv[1] == "full":
            run_full_benchmark()
        else:
            # По умолчанию один тест
            benchmark_simulation(500, steps=30)
            
        print(f"\n🎮 Запустите главную игру: python3 main.py")
        print(f"📊 Используйте кнопку 'Оптимизация' для переключения")
        
    except KeyboardInterrupt:
        print(f"\n⛔ Тест прерван пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        raise