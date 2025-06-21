#!/usr/bin/env python3
"""
Тест графиков динамики популяций
Демонстрирует новую функциональность отслеживания типов организмов
"""

from simulation import EvolutionSimulation
import time

def test_population_tracking():
    """Тестирует систему отслеживания популяций по типам"""
    print("🧪 ТЕСТ ОТСЛЕЖИВАНИЯ ПОПУЛЯЦИЙ ПО ТИПАМ")
    print("=" * 50)
    
    # Создаём симуляцию
    sim = EvolutionSimulation(width=900, height=700)
    
    # Запускаем симуляцию на некоторое время
    print("Запуск симуляции для накопления данных...")
    
    for step in range(200):
        sim.update(dt=1.0)
        
        # Показываем прогресс каждые 20 шагов
        if step % 20 == 0:
            stats = sim.get_statistics()
            print(f"Шаг {step:3d}: 🔴{stats['predators']:2d} 🟢{stats['herbivores']:2d} 🔵{stats['omnivores']:2d} | Всего: {stats['population']:2d}")
    
    # Получаем историю популяций
    pop_history = sim.get_population_history()
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ОТСЛЕЖИВАНИЯ:")
    print(f"Точек данных: {len(pop_history['time_steps'])}")
    print(f"Временной интервал: {pop_history['time_steps'][0] if pop_history['time_steps'] else 0} - {pop_history['time_steps'][-1] if pop_history['time_steps'] else 0}")
    
    if pop_history['total']:
        print(f"\nДинамика популяций:")
        print(f"Начальная популяция: {pop_history['total'][0]}")
        print(f"Конечная популяция: {pop_history['total'][-1]}")
        
        print(f"\nТекущий состав:")
        final_pred = pop_history['predators'][-1] if pop_history['predators'] else 0
        final_herb = pop_history['herbivores'][-1] if pop_history['herbivores'] else 0  
        final_omni = pop_history['omnivores'][-1] if pop_history['omnivores'] else 0
        final_total = pop_history['total'][-1] if pop_history['total'] else 1
        
        print(f"🔴 Хищники: {final_pred} ({final_pred/final_total*100:.1f}%)")
        print(f"🟢 Травоядные: {final_herb} ({final_herb/final_total*100:.1f}%)")
        print(f"🔵 Всеядные: {final_omni} ({final_omni/final_total*100:.1f}%)")
        
        # Анализ тенденций
        print(f"\n📈 АНАЛИЗ ТЕНДЕНЦИЙ:")
        if len(pop_history['predators']) >= 2:
            pred_change = pop_history['predators'][-1] - pop_history['predators'][0]
            herb_change = pop_history['herbivores'][-1] - pop_history['herbivores'][0]
            omni_change = pop_history['omnivores'][-1] - pop_history['omnivores'][0]
            
            print(f"🔴 Хищники: {pred_change:+d} ({'растёт' if pred_change > 0 else 'падает' if pred_change < 0 else 'стабильно'})")
            print(f"🟢 Травоядные: {herb_change:+d} ({'растёт' if herb_change > 0 else 'падает' if herb_change < 0 else 'стабильно'})")
            print(f"🔵 Всеядные: {omni_change:+d} ({'растёт' if omni_change > 0 else 'падает' if omni_change < 0 else 'стабильно'})")
    
    return pop_history

def demonstrate_population_balance():
    """Демонстрирует баланс популяций в экосистеме"""
    print(f"\n🌍 ДЕМОНСТРАЦИЯ БАЛАНСА ЭКОСИСТЕМЫ")
    print("=" * 50)
    
    sim = EvolutionSimulation()
    
    # Настраиваем условия для демонстрации баланса
    sim.food_spawn_rate = 0.3  # Ограниченные ресурсы
    
    print("Запуск симуляции с ограниченными ресурсами...")
    print("Время  | 🔴Хищ | 🟢Трав | 🔵Всеяд | Всего | Пища")
    print("-" * 50)
    
    for step in range(300):
        sim.update(dt=1.0)
        
        if step % 30 == 0:
            stats = sim.get_statistics()
            food_count = len([f for f in sim.get_food_sources() if not f.get('consumed', False)])
            
            print(f"{step:4d}   | {stats['predators']:4d} | {stats['herbivores']:4d}  | {stats['omnivores']:5d}  | {stats['population']:4d}  | {food_count:3d}")
    
    pop_history = sim.get_population_history()
    
    # Анализ стабильности экосистемы
    if len(pop_history['total']) >= 3:
        print(f"\n🔍 АНАЛИЗ СТАБИЛЬНОСТИ ЭКОСИСТЕМЫ:")
        
        # Вычисляем коэффициент вариации для каждого типа
        import statistics
        
        if pop_history['predators']:
            pred_cv = statistics.stdev(pop_history['predators']) / statistics.mean(pop_history['predators']) if statistics.mean(pop_history['predators']) > 0 else 0
            herb_cv = statistics.stdev(pop_history['herbivores']) / statistics.mean(pop_history['herbivores']) if statistics.mean(pop_history['herbivores']) > 0 else 0
            omni_cv = statistics.stdev(pop_history['omnivores']) / statistics.mean(pop_history['omnivores']) if statistics.mean(pop_history['omnivores']) > 0 else 0
            
            print(f"Коэффициент вариации (стабильность):")
            print(f"🔴 Хищники: {pred_cv:.3f} ({'стабильно' if pred_cv < 0.5 else 'нестабильно'})")
            print(f"🟢 Травоядные: {herb_cv:.3f} ({'стабильно' if herb_cv < 0.5 else 'нестабильно'})")
            print(f"🔵 Всеядные: {omni_cv:.3f} ({'стабильно' if omni_cv < 0.5 else 'нестабильно'})")
    
    return sim

def create_sample_data():
    """Создаёт образец данных для демонстрации графиков"""
    print(f"\n📊 СОЗДАНИЕ ОБРАЗЦА ДАННЫХ ДЛЯ ГРАФИКОВ")
    print("=" * 50)
    
    # Создаём симуляцию и накапливаем данные
    sim = EvolutionSimulation()
    
    # Быстро накапливаем данные
    for step in range(500):
        sim.update(dt=1.0)
        
        if step % 100 == 0:
            stats = sim.get_statistics()
            print(f"Прогресс: {step}/500 шагов, популяция: {stats['population']}")
    
    pop_history = sim.get_population_history()
    gene_history = sim.get_gene_history()
    
    print(f"\n✅ ДАННЫЕ ГОТОВЫ ДЛЯ ГРАФИКОВ:")
    print(f"📊 Точек популяций: {len(pop_history['time_steps'])}")
    print(f"🧬 Точек генов: {len(gene_history['speed']) if gene_history['speed'] else 0}")
    print(f"⏰ Временной интервал: {pop_history['time_steps'][-1] if pop_history['time_steps'] else 0} шагов")
    
    # Показываем финальную статистику
    if pop_history['total']:
        final_stats = sim.get_statistics()
        print(f"\nФинальный состав популяции:")
        print(f"🔴 Хищники: {final_stats['predators']} ({final_stats['predators']/final_stats['population']*100:.1f}%)")
        print(f"🟢 Травоядные: {final_stats['herbivores']} ({final_stats['herbivores']/final_stats['population']*100:.1f}%)")
        print(f"🔵 Всеядные: {final_stats['omnivores']} ({final_stats['omnivores']/final_stats['population']*100:.1f}%)")
    
    print(f"\n🎨 Теперь можно открыть игру и посмотреть красивые графики:")
    print(f"   python3 main.py -> Кнопка 'Графики эволюции'")
    
    return sim

if __name__ == "__main__":
    print("🎯 ТЕСТИРОВАНИЕ НОВЫХ ГРАФИКОВ ПОПУЛЯЦИЙ")
    print("=" * 60)
    
    try:
        # Тест 1: Базовое отслеживание
        pop_history = test_population_tracking()
        
        # Тест 2: Баланс экосистемы
        sim = demonstrate_population_balance()
        
        # Тест 3: Создание данных для графиков
        final_sim = create_sample_data()
        
        print(f"\n🎉 ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ!")
        print(f"Новая функциональность готова к использованию!")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        raise