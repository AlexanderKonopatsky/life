#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы симуляции без GUI
"""

from simulation import EvolutionSimulation
from organism import Organism
import time

def test_basic_simulation():
    """Тест базовой функциональности симуляции"""
    print("=== Тест симуляции эволюции ===")
    
    # Создаем симуляцию
    sim = EvolutionSimulation(width=400, height=300)
    
    print(f"Начальная популяция: {len(sim.get_organisms())}")
    
    # Запускаем симуляцию на несколько шагов
    for step in range(50):
        sim.update(dt=1.0)
        
        if step % 10 == 0:
            stats = sim.get_statistics()
            print(f"Шаг {step}: популяция={stats['population']}, "
                  f"поколение={stats['avg_generation']:.1f}, "
                  f"средняя скорость={stats['avg_speed']:.2f}")
            
    print("\n=== Результаты тестирования ===")
    stats = sim.get_statistics()
    print(f"Финальная популяция: {stats['population']}")
    print(f"Среднее поколение: {stats['avg_generation']:.1f}")
    print(f"Всего рождений: {stats['total_births']}")
    print(f"Всего смертей: {stats['total_deaths']}")
    print(f"Средняя скорость: {stats['avg_speed']:.2f}")
    print(f"Средний размер: {stats['avg_size']:.2f}")
    print(f"Средняя эффективность: {stats['avg_energy_efficiency']:.2f}")

def test_organism_genetics():
    """Тест генетики организмов"""
    print("\n=== Тест генетики организмов ===")
    
    # Создаем родительский организм
    parent = Organism(100, 100)
    parent.energy = 80  # Достаточно энергии для размножения
    parent.age = 60    # Достаточный возраст
    
    print("Родительские гены:")
    for gene, value in parent.genes.items():
        print(f"  {gene}: {value:.3f}")
        
    # Создаем потомка
    child = parent.reproduce()
    
    if child:
        print("\nГены потомка:")
        for gene, value in child.genes.items():
            print(f"  {gene}: {value:.3f}")
            
        print("\nМутации:")
        for gene in parent.genes:
            if gene in ['color_r', 'color_g', 'color_b']:
                diff = abs(int(child.genes[gene]) - int(parent.genes[gene]))
            else:
                diff = abs(child.genes[gene] - parent.genes[gene])
            print(f"  {gene}: изменение на {diff:.3f}")
    else:
        print("Размножение не удалось")

def test_evolution_trends():
    """Тест эволюционных трендов"""
    print("\n=== Тест эволюционных трендов ===")
    
    sim = EvolutionSimulation(width=600, height=400)
    sim.set_parameters(max_organisms=50, initial_organisms=15, food_spawn_rate=0.2)
    
    print("Наблюдение эволюции в условиях скудных ресурсов...")
    
    generations_data = []
    
    for step in range(100):
        sim.update(dt=1.0)
        
        if step % 20 == 0:
            stats = sim.get_statistics()
            generations_data.append({
                'step': step,
                'population': stats['population'],
                'avg_speed': stats['avg_speed'],
                'avg_efficiency': stats['avg_energy_efficiency'],
                'avg_generation': stats['avg_generation']
            })
            
    print("\nЭволюционные изменения:")
    print("Шаг\tПоп.\tСкор.\tЭфф.\tПокол.")
    for data in generations_data:
        print(f"{data['step']}\t{data['population']}\t{data['avg_speed']:.2f}\t{data['avg_efficiency']:.2f}\t{data['avg_generation']:.1f}")

if __name__ == "__main__":
    try:
        test_basic_simulation()
        test_organism_genetics()
        test_evolution_trends()
        print("\n✅ Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        raise