#!/usr/bin/env python3
"""
Демонстрация экосистемы "Эволюция: Простая жизнь" v2.0
Показывает типы организмов, их поведение и взаимодействия
"""

from simulation import EvolutionSimulation
from organism import Organism
import time

def demo_ecosystem():
    """Демонстрация полной экосистемы"""
    print("🌍 === ДЕМО ЭКОСИСТЕМЫ v2.0 === 🌍\n")
    
    # Создаем симуляцию
    sim = EvolutionSimulation(width=1400, height=1000)
    
    print(f"📏 Размер мира: {sim.width}x{sim.height}")
    print(f"🌱 Максимум растений: {sim.max_food}")
    print(f"🔢 Начальная популяция: {len(sim.get_organisms())}\n")
    
    # Анализируем начальную популяцию
    organisms = sim.get_organisms()
    predators = [org for org in organisms if org.is_predator()]
    herbivores = [org for org in organisms if org.is_herbivore()]
    omnivores = [org for org in organisms if org.is_omnivore()]
    
    print("🧬 АНАЛИЗ НАЧАЛЬНОЙ ПОПУЛЯЦИИ:")
    print(f"🔴 Хищники: {len(predators)} ({len(predators)/len(organisms)*100:.1f}%)")
    print(f"🟢 Травоядные: {len(herbivores)} ({len(herbivores)/len(organisms)*100:.1f}%)")
    print(f"🔵 Всеядные: {len(omnivores)} ({len(omnivores)/len(organisms)*100:.1f}%)")
    
    # Показываем примеры организмов
    if predators:
        pred = predators[0]
        print(f"\n🔴 ПРИМЕР ХИЩНИКА:")
        print(f"   Диета: {pred.genes['diet_preference']:.2f} (>0.6)")
        print(f"   Размер: {pred.genes['size']:.1f}")
        print(f"   Скорость: {pred.genes['speed']:.1f}")
        print(f"   Агрессивность: {pred.genes['aggression']:.2f}")
    
    if herbivores:
        herb = herbivores[0]
        print(f"\n🟢 ПРИМЕР ТРАВОЯДНОГО:")
        print(f"   Диета: {herb.genes['diet_preference']:.2f} (<0.4)")
        print(f"   Размер: {herb.genes['size']:.1f}")
        print(f"   Скорость: {herb.genes['speed']:.1f}")
        print(f"   Страх: {herb.genes['fear_sensitivity']:.2f}")
    
    print(f"\n🌱 РАСТЕНИЯ В МИРЕ: {len(sim.get_food_sources())}")
    food_types = {}
    for food in sim.get_food_sources():
        food_type = food.get('type', 'unknown')
        food_types[food_type] = food_types.get(food_type, 0) + 1
    
    for food_type, count in food_types.items():
        emoji = "🔴" if food_type == "berry" else "🟢" if food_type == "grass" else "🟠"
        print(f"   {emoji} {food_type.title()}: {count}")
    
    print("\n⏰ ЗАПУСК СИМУЛЯЦИИ НА 100 ШАГОВ...\n")
    
    # Симуляция
    for step in range(100):
        sim.update(dt=1.0)
        
        if step % 25 == 0:
            stats = sim.get_statistics()
            print(f"Шаг {step:3d}: "
                  f"Всего {stats['population']:2d} | "
                  f"🔴{stats['predators']:2d} "
                  f"🟢{stats['herbivores']:2d} "
                  f"🔵{stats['omnivores']:2d} | "
                  f"Поколение {stats['avg_generation']:.1f}")
    
    # Финальный анализ
    print(f"\n📊 РЕЗУЛЬТАТЫ СИМУЛЯЦИИ:")
    final_stats = sim.get_statistics()
    
    print(f"📈 Популяция: {sim.initial_organisms} → {final_stats['population']} "
          f"({final_stats['population']/sim.initial_organisms*100:.0f}%)")
    
    print(f"👶 Рождений: {final_stats['total_births']}")
    print(f"💀 Смертей: {final_stats['total_deaths']}")
    print(f"🧬 Поколений: {final_stats['avg_generation']:.1f}")
    
    print(f"\n🏆 ТОП-5 САМЫХ ПРИСПОСОБЛЕННЫХ:")
    best = sim.get_best_organisms(top_n=5)
    for i, org in enumerate(best, 1):
        type_emoji = "🔴" if org.is_predator() else "🟢" if org.is_herbivore() else "🔵"
        print(f"   {i}. {type_emoji} {org.get_type_name()} | "
              f"Фитнес: {org.fitness:6.1f} | "
              f"Энергия: {org.energy:5.1f} | "
              f"Возраст: {org.age:6.1f}")
    
    print(f"\n🔬 ЭВОЛЮЦИОННЫЕ ИЗМЕНЕНИЯ:")
    if final_stats['avg_generation'] > 0:
        print(f"   📏 Размер: {final_stats['avg_size']:.1f}")
        print(f"   ⚡ Скорость: {final_stats['avg_speed']:.1f}")
        print(f"   🛡️ Эффективность: {final_stats['avg_energy_efficiency']:.2f}")
        print(f"   ⚔️ Агрессивность: {final_stats['avg_aggression']:.2f}")
    else:
        print("   🕐 Недостаточно времени для эволюции")
        
    print(f"\n✨ ЭКОСИСТЕМНЫЙ БАЛАНС:")
    total = final_stats['population']
    if total > 0:
        pred_pct = final_stats['predators'] / total * 100
        herb_pct = final_stats['herbivores'] / total * 100
        omni_pct = final_stats['omnivores'] / total * 100
        
        print(f"   🔴 Хищники: {pred_pct:4.1f}% (оптимум ~20%)")
        print(f"   🟢 Травоядные: {herb_pct:4.1f}% (оптимум ~50%)")
        print(f"   🔵 Всеядные: {omni_pct:4.1f}% (оптимум ~30%)")
        
        if 15 <= pred_pct <= 25 and 40 <= herb_pct <= 60:
            print("   ✅ Экосистема сбалансирована!")
        else:
            print("   ⚠️ Экосистема развивается...")

def demo_organism_types():
    """Демонстрация разных типов организмов"""
    print("\n🧬 === ДЕМО ТИПОВ ОРГАНИЗМОВ === 🧬\n")
    
    # Создаем специфические типы
    predator_genes = {
        'speed': 3.5, 'size': 8.0, 'energy_efficiency': 0.7,
        'reproduction_threshold': 120, 'aggression': 0.9, 'mutation_rate': 0.05,
        'diet_preference': 0.9, 'fear_sensitivity': 0.2,
        'color_r': 200, 'color_g': 50, 'color_b': 50
    }
    
    herbivore_genes = {
        'speed': 2.5, 'size': 5.0, 'energy_efficiency': 0.9,
        'reproduction_threshold': 80, 'aggression': 0.1, 'mutation_rate': 0.05,
        'diet_preference': 0.1, 'fear_sensitivity': 0.8,
        'color_r': 50, 'color_g': 200, 'color_b': 50
    }
    
    omnivore_genes = {
        'speed': 3.0, 'size': 6.0, 'energy_efficiency': 0.8,
        'reproduction_threshold': 100, 'aggression': 0.5, 'mutation_rate': 0.05,
        'diet_preference': 0.5, 'fear_sensitivity': 0.5,
        'color_r': 50, 'color_g': 50, 'color_b': 200
    }
    
    predator = Organism(100, 100, predator_genes)
    herbivore = Organism(200, 200, herbivore_genes)
    omnivore = Organism(300, 300, omnivore_genes)
    
    organisms = [predator, herbivore, omnivore]
    
    for org in organisms:
        print(f"{org.get_type_name().upper()} ({org.genes['diet_preference']:.1f}):")
        color = org.get_color()
        print(f"   Цвет: RGB{color}")
        print(f"   Стратегия: {'Охота' if org.is_predator() else 'Бегство' if org.is_herbivore() else 'Адаптация'}")
        print(f"   Энергоэффективность: {org.genes['energy_efficiency']:.1f}")
        print(f"   Агрессивность: {org.genes['aggression']:.1f}")
        print(f"   Чувствительность: {org.genes['fear_sensitivity']:.1f}")
        print()

if __name__ == "__main__":
    try:
        demo_organism_types()
        demo_ecosystem()
        print("\n🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print("🚀 Запустите главную игру: python3 main.py")
        
    except Exception as e:
        print(f"\n❌ Ошибка в демо: {e}")
        raise