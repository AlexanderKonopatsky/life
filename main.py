import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
from simulation import EvolutionSimulation

# Опциональный импорт matplotlib для графиков
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.style as style
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class EvolutionGameGUI:
    """Графический интерфейс для игры 'Эволюция: Простая жизнь'"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Эволюция: Простая жизнь")
        self.root.geometry("1200x900")
        
        # Симуляция
        self.simulation = EvolutionSimulation(width=900, height=700)
        self.running = False
        self.simulation_speed = 1.0
        self.selected_organism = None
        
        # Настройка интерфейса
        self._setup_ui()
        
        # Запуск основного цикла отрисовки
        self._update_display()
        
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель (симуляция)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Канвас для симуляции
        self.canvas = tk.Canvas(left_frame, width=900, height=700, bg='#001122')
        self.canvas.pack(pady=5)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Кнопки управления
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Старт/Пауза", command=self._toggle_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Сброс", command=self._reset_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Настройки", command=self._show_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Графики эволюции", command=self._show_evolution_graphs).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Оптимизация", command=self._toggle_optimization).pack(side=tk.LEFT, padx=2)
        
        # Правая панель (информация и статистика)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Скорость симуляции
        speed_frame = ttk.LabelFrame(right_frame, text="Скорость симуляции")
        speed_frame.pack(fill=tk.X, pady=5)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(speed_frame, from_=0.1, to=50.0, variable=self.speed_var,
                                   orient=tk.HORIZONTAL, command=self._update_speed)
        self.speed_scale.pack(fill=tk.X, padx=5, pady=5)
        
        self.speed_label = ttk.Label(speed_frame, text="Скорость: 1.0x")
        self.speed_label.pack()
        
        # Общая статистика
        stats_frame = ttk.LabelFrame(right_frame, text="Статистика")
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=12, width=30, font=('Courier', 9))
        self.stats_text.pack(padx=5, pady=5)
        
        # Информация о выбранном организме
        info_frame = ttk.LabelFrame(right_frame, text="Информация об организме")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.info_text = tk.Text(info_frame, height=15, width=30, font=('Courier', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _toggle_simulation(self):
        """Запуск/остановка симуляции"""
        self.running = not self.running
        if self.running:
            self._run_simulation()
            
    def _run_simulation(self):
        """Запуск симуляции в отдельном потоке"""
        def simulation_loop():
            while self.running:
                self.simulation.update(dt=self.simulation_speed)
                time.sleep(0.05)  # 20 FPS
                
        thread = threading.Thread(target=simulation_loop, daemon=True)
        thread.start()
        
    def _reset_simulation(self):
        """Сброс симуляции"""
        self.running = False
        self.simulation.reset()
        self.selected_organism = None
        
    def _update_speed(self, value):
        """Обновление скорости симуляции"""
        self.simulation_speed = float(value)
        self.speed_label.config(text=f"Скорость: {self.simulation_speed:.1f}x")
        
    def _on_canvas_click(self, event):
        """Обработка клика по канвасу"""
        # Поиск ближайшего организма
        min_distance = float('inf')
        closest_organism = None
        
        for organism in self.simulation.get_organisms():
            distance = math.sqrt((event.x - organism.x)**2 + (event.y - organism.y)**2)
            if distance < min_distance and distance < 20:
                min_distance = distance
                closest_organism = organism
                
        self.selected_organism = closest_organism
        
    def _update_display(self):
        """Обновление отображения"""
        # Очистка канваса
        self.canvas.delete("all")
        
        # Отрисовка пищи (растения)
        for food in self.simulation.get_food_sources():
            x, y = food['x'], food['y']
            size = food['size']
            
            # Разные цвета для разных типов растений
            if food.get('type') == 'berry':
                color = '#8B0000'  # Тёмно-красный
                outline = '#660000'
            elif food.get('type') == 'fruit':
                color = '#FFA500'  # Оранжевый
                outline = '#FF8C00'
            else:  # grass
                color = '#228B22'  # Зелёный
                outline = '#006400'
                
            self.canvas.create_oval(x-size, y-size, x+size, y+size, 
                                  fill=color, outline=outline)
            
        # Отрисовка организмов
        organisms = self.simulation.get_organisms()
        best_organisms = self.simulation.get_best_organisms(top_n=5)
        
        for organism in organisms:
            x, y = organism.x, organism.y
            size = organism.genes['size']
            color = self._rgb_to_hex(*organism.get_color())
            
            # Выделение выбранного организма
            if organism == self.selected_organism:
                outline = 'yellow'
                outline_width = 3
            elif organism in best_organisms:
                # Выделяем лучших организмов зелёной обводкой
                outline = 'lime'
                outline_width = 2
            else:
                outline = 'black'
                outline_width = 1
            
            self.canvas.create_oval(x-size, y-size, x+size, y+size,
                                  fill=color, outline=outline, width=outline_width)
                                  
            # Показ энергии как полоска
            energy_ratio = min(1.0, organism.energy / 100)
            bar_width = size * 2
            bar_height = 3
            bar_x = x - bar_width / 2
            bar_y = y - size - 8
            
            # Фон полоски энергии
            self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                                       fill='darkred', outline='')
            # Энергия
            self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width * energy_ratio, bar_y + bar_height,
                                       fill='red', outline='')
        
        # Обновление статистики
        self._update_statistics()
        
        # Обновление информации о выбранном организме
        self._update_organism_info()
        
        # Планирование следующего обновления
        self.root.after(50, self._update_display)  # 20 FPS
        
    def _rgb_to_hex(self, r, g, b):
        """Преобразование RGB в hex"""
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _update_statistics(self):
        """Обновление статистики"""
        stats = self.simulation.get_statistics()
        
        # Получаем статистику производительности
        perf_stats = self.simulation.get_performance_stats()
        
        stats_text = f"""ЭКОСИСТЕМА

Всего организмов: {stats['population']}
[H] Хищники: {stats['predators']}
[T] Травоядные: {stats['herbivores']}
[O] Всеядные: {stats['omnivores']}

ЭВОЛЮЦИЯ:
Поколение: {stats['avg_generation']:.1f}
Рождений: {stats['total_births']}
Смертей: {stats['total_deaths']}

СРЕДНИЕ ГЕНЫ:
Скорость: {stats['avg_speed']:.2f}
Размер: {stats['avg_size']:.2f}
Эффективность: {stats['avg_energy_efficiency']:.2f}
Агрессивность: {stats['avg_aggression']:.2f}
Приспособленность: {stats['avg_fitness']:.1f}

ПРОИЗВОДИТЕЛЬНОСТЬ:
FPS: {perf_stats['fps']:.1f}
Время кадра: {perf_stats['avg_frame_time']:.1f}мс
Оптимизация: {'ВКЛ' if perf_stats['optimization'] else 'ВЫКЛ'}

ВРЕМЯ: {self.simulation.time_step}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
        
    def _update_organism_info(self):
        """Обновление информации о выбранном организме"""
        if self.selected_organism and self.selected_organism.alive:
            org = self.selected_organism
            info = org.get_info()
            
            # Определяем ранг организма по приспособленности
            best_organisms = self.simulation.get_best_organisms(top_n=len(self.simulation.get_organisms()))
            rank = best_organisms.index(org) + 1 if org in best_organisms else "?"
            
            # Определяем символ для типа
            type_symbol = "[H]" if org.is_predator() else "[T]" if org.is_herbivore() else "[O]"
            
            info_text = f"""{type_symbol} {org.get_type_name().upper()}

Позиция: ({info['position'][0]:.1f}, {info['position'][1]:.1f})
Энергия: {info['energy']:.1f}
Возраст: {info['age']:.1f}
Поколение: {info['generation']}
Ранг: #{rank} из {len(self.simulation.get_organisms())}
Приспособленность: {info['fitness']:.1f}

ОСНОВНЫЕ ГЕНЫ:
Скорость: {info['genes']['speed']:.2f}
Размер: {info['genes']['size']:.2f}
Эффективность: {info['genes']['energy_efficiency']:.2f}
Агрессивность: {info['genes']['aggression']:.2f}

ПОВЕДЕНИЕ:
Диета: {info['genes']['diet_preference']:.2f}
Страх: {info['genes']['fear_sensitivity']:.2f}
Мутации: {info['genes']['mutation_rate']:.3f}

СОСТОЯНИЕ:
Размножение: {'Да' if org.can_reproduce() else 'Нет'}
Цель: {type(org.target).__name__ if org.target else 'Нет'}
Убегает: {'Да' if org.fleeing_from else 'Нет'}
"""
        else:
            info_text = "Нажмите на организм\nдля получения информации"
            
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        
    def _show_settings(self):
        """Показ окна настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки симуляции")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        
        # Начальная популяция
        ttk.Label(settings_window, text="Начальная популяция:").pack(pady=5)
        initial_pop_var = tk.IntVar(value=self.simulation.initial_organisms)
        initial_pop_scale = ttk.Scale(settings_window, from_=5, to=50, variable=initial_pop_var, orient=tk.HORIZONTAL)
        initial_pop_scale.pack(fill=tk.X, padx=20)
        
        # Частота появления пищи
        ttk.Label(settings_window, text="Частота появления пищи:").pack(pady=5)
        food_rate_var = tk.DoubleVar(value=self.simulation.food_spawn_rate)
        food_rate_scale = ttk.Scale(settings_window, from_=0.1, to=1.0, variable=food_rate_var, orient=tk.HORIZONTAL)
        food_rate_scale.pack(fill=tk.X, padx=20)
        
        # Кнопки
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=20)
        
        def apply_settings():
            self.simulation.set_parameters(
                initial_organisms=int(initial_pop_var.get()),
                food_spawn_rate=float(food_rate_var.get())
            )
            settings_window.destroy()
            
        def reset_to_defaults():
            self.running = False
            self.simulation = EvolutionSimulation()
            settings_window.destroy()
            
        ttk.Button(button_frame, text="Применить", command=apply_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="По умолчанию", command=reset_to_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
        
    def _show_evolution_graphs(self):
        """Показ графиков эволюции генов и популяций"""
        # Проверяем размер популяции для предотвращения зависаний
        current_population = len(self.simulation.get_organisms())
        if current_population > 3000:
            messagebox.showwarning("Предупреждение", 
                                 f"Слишком большая популяция ({current_population} организмов)!\n"
                                 f"Отображение графиков может вызвать зависание.\n"
                                 f"Подождите пока популяция уменьшится до безопасного уровня (<3000).")
            return
        
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Графики эволюции и динамика популяций")
        graph_window.geometry("1400x800")
        graph_window.transient(self.root)
        
        # Получаем историю генов и популяций
        gene_history = self.simulation.get_gene_history()
        population_history = self.simulation.get_population_history()
        
        if not gene_history['speed'] and not population_history['total']:
            tk.Label(graph_window, text="Недостаточно данных для построения графиков.\nПодождите некоторое время.").pack(pady=20)
            return

        # Создаем ноутбук для вкладок
        notebook = ttk.Notebook(graph_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Динамика популяций
        if MATPLOTLIB_AVAILABLE and population_history['total']:
            pop_frame = ttk.Frame(notebook)
            notebook.add(pop_frame, text="Динамика популяций")
            self._create_population_graphs(pop_frame, population_history)
        
        # Вкладка 2: Эволюция генов
        if MATPLOTLIB_AVAILABLE and gene_history['speed']:
            genes_frame = ttk.Frame(notebook)
            notebook.add(genes_frame, text="Эволюция генов")
            self._create_gene_graphs(genes_frame, gene_history)
        
        # Вкладка 3: Статистика (текстовая)
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Подробная статистика")
        self._create_text_stats(stats_frame, gene_history, population_history)
        
    def _create_population_graphs(self, parent, population_history):
        """Создает графики динамики популяций"""
        if not MATPLOTLIB_AVAILABLE:
            tk.Label(parent, text="Matplotlib не доступен").pack()
            return
            
        # Настройка стиля
        style.use('dark_background')
        plt.rcParams['figure.facecolor'] = '#2e2e2e'
        plt.rcParams['axes.facecolor'] = '#3e3e3e'
        
        # Создаем фигуру с субплотами
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('Динамика популяций по типам организмов', fontsize=16, color='white')
        
        # Данные для графиков
        time_steps = population_history['time_steps']
        predators = population_history['predators']
        herbivores = population_history['herbivores']
        omnivores = population_history['omnivores']
        total = population_history['total']
        
        # График 1: Абсолютные числа
        ax1.plot(time_steps, predators, 'r-', label='[H] Хищники', linewidth=2, marker='o', markersize=3)
        ax1.plot(time_steps, herbivores, 'g-', label='[T] Травоядные', linewidth=2, marker='s', markersize=3)
        ax1.plot(time_steps, omnivores, 'b-', label='[O] Всеядные', linewidth=2, marker='^', markersize=3)
        ax1.plot(time_steps, total, 'white', linestyle='--', label='Общая популяция', linewidth=2, alpha=0.8)
        
        ax1.set_title('Абсолютная численность популяций', color='white')
        ax1.set_xlabel('Время (шаги симуляции)', color='white')
        ax1.set_ylabel('Количество организмов', color='white')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(colors='white')
        
        # График 2: Процентное соотношение (заполненная область)
        if total and max(total) > 0:
            # Вычисляем проценты
            pred_percent = [p/t*100 if t > 0 else 0 for p, t in zip(predators, total)]
            herb_percent = [h/t*100 if t > 0 else 0 for h, t in zip(herbivores, total)]
            omni_percent = [o/t*100 if t > 0 else 0 for o, t in zip(omnivores, total)]
            
            # Стекированная диаграмма
            ax2.fill_between(time_steps, 0, pred_percent, color='red', alpha=0.7, label='[H] Хищники')
            ax2.fill_between(time_steps, pred_percent, 
                           [p+h for p,h in zip(pred_percent, herb_percent)], 
                           color='green', alpha=0.7, label='[T] Травоядные')
            ax2.fill_between(time_steps, [p+h for p,h in zip(pred_percent, herb_percent)],
                           [p+h+o for p,h,o in zip(pred_percent, herb_percent, omni_percent)],
                           color='blue', alpha=0.7, label='[O] Всеядные')
        
        ax2.set_title('Процентное соотношение типов организмов', color='white')
        ax2.set_xlabel('Время (шаги симуляции)', color='white')
        ax2.set_ylabel('Процент от общей популяции (%)', color='white')
        ax2.set_ylim(0, 100)
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(colors='white')
        
        plt.tight_layout()
        
        # Интеграция с tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _create_gene_graphs(self, parent, gene_history):
        """Создает графики эволюции генов"""
        if not MATPLOTLIB_AVAILABLE:
            tk.Label(parent, text="Matplotlib не доступен").pack()
            return
            
        # Создаем фигуру с субплотами для основных генов
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Эволюция основных генов', fontsize=16, color='white')
        
        # Основные гены для отображения
        genes_to_plot = ['speed', 'size', 'energy_efficiency', 'fitness']
        gene_colors = ['cyan', 'orange', 'lime', 'yellow']
        gene_titles = ['Скорость', 'Размер', 'Эффективность энергии', 'Приспособленность']
        
        # Создаем временную шкалу
        if gene_history['speed']:
            time_points = range(0, len(gene_history['speed']) * 10, 10)
            
            for i, (gene, color, title) in enumerate(zip(genes_to_plot, gene_colors, gene_titles)):
                ax = axes[i // 2, i % 2]
                values = gene_history.get(gene, [])
                
                if values:
                    ax.plot(time_points, values, color=color, linewidth=2, marker='o', markersize=3)
                    ax.set_title(f'{title}', color='white')
                    ax.set_xlabel('Время (шаги)', color='white')
                    ax.set_ylabel('Значение', color='white')
                    ax.grid(True, alpha=0.3)
                    ax.tick_params(colors='white')
                    
                    # Показываем тренд
                    if len(values) > 1:
                        start_val = values[0]
                        end_val = values[-1]
                        change_percent = ((end_val - start_val) / start_val * 100) if start_val != 0 else 0
                        trend_text = f'Изменение: {change_percent:+.1f}%'
                        ax.text(0.02, 0.98, trend_text, transform=ax.transAxes, 
                               verticalalignment='top', color='white', 
                               bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        plt.tight_layout()
        
        # Интеграция с tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def _create_text_stats(self, parent, gene_history, population_history):
        """Создает текстовую статистику"""
        info_text = tk.Text(parent, width=100, height=35, font=('Courier', 10))
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        graph_text = "=== ПОДРОБНАЯ СТАТИСТИКА ЭВОЛЮЦИИ ===\n\n"
        
        # Статистика популяций
        if population_history['total']:
            graph_text += "📊 ДИНАМИКА ПОПУЛЯЦИЙ:\n"
            graph_text += f"Начальная популяция: {population_history['total'][0] if population_history['total'] else 0}\n"
            graph_text += f"Текущая популяция: {population_history['total'][-1] if population_history['total'] else 0}\n"
            
            if population_history['total']:
                current_pred = population_history['predators'][-1] if population_history['predators'] else 0
                current_herb = population_history['herbivores'][-1] if population_history['herbivores'] else 0
                current_omni = population_history['omnivores'][-1] if population_history['omnivores'] else 0
                total_current = population_history['total'][-1] if population_history['total'] else 1
                
                graph_text += f"[H] Хищники: {current_pred} ({current_pred/total_current*100:.1f}%)\n"
                graph_text += f"[T] Травоядные: {current_herb} ({current_herb/total_current*100:.1f}%)\n" 
                graph_text += f"[O] Всеядные: {current_omni} ({current_omni/total_current*100:.1f}%)\n\n"
        
        # Статистика генов
        graph_text += "*** ЭВОЛЮЦИОННЫЕ ТРЕНДЫ ***\n\n"
        for gene_name, values in gene_history.items():
            if not values:
                continue
                
            graph_text += f"{gene_name.upper()}:\n"
            graph_text += f"Начальное значение: {values[0]:.3f}\n"
            graph_text += f"Текущее значение: {values[-1]:.3f}\n"
            if values[0] != 0:
                graph_text += f"Изменение: {((values[-1] - values[0]) / values[0] * 100):+.1f}%\n"
            
            # Простая ASCII визуализация тренда
            if len(values) > 1:
                min_val = min(values)
                max_val = max(values)
                if max_val > min_val:
                    graph_text += "Тренд: "
                    for i, val in enumerate(values[-20:]):  # Последние 20 точек
                        normalized = int((val - min_val) / (max_val - min_val) * 10)
                        graph_text += str(normalized)
                    graph_text += "\n"
            graph_text += "\n"
            
        # Добавляем информацию о лучших организмах
        best_organisms = self.simulation.get_best_organisms(top_n=10)
        if best_organisms:
            graph_text += "*** ТОП-10 САМЫХ ПРИСПОСОБЛЕННЫХ ***\n\n"
            for i, org in enumerate(best_organisms, 1):
                type_symbol = "[H]" if org.is_predator() else "[T]" if org.is_herbivore() else "[O]"
                graph_text += f"{i:2d}. {type_symbol} Приспособленность: {org.fitness:6.1f} | "
                graph_text += f"Поколение: {org.generation:2d} | "
                graph_text += f"Энергия: {org.energy:5.1f} | "
                graph_text += f"Возраст: {org.age:6.1f}\n"
                graph_text += f"     Скорость: {org.genes['speed']:.2f} | "
                graph_text += f"Размер: {org.genes['size']:.2f} | "
                graph_text += f"Эффективность: {org.genes['energy_efficiency']:.2f}\n\n"
        
        info_text.insert(1.0, graph_text)
        info_text.config(state=tk.DISABLED)
        
    def _toggle_optimization(self):
        """Переключает оптимизацию производительности"""
        self.simulation.toggle_optimization()
        perf_stats = self.simulation.get_performance_stats()
        status = "включена" if perf_stats['optimization'] else "выключена"
        messagebox.showinfo("Оптимизация", f"Оптимизация производительности {status}")
         
    def run(self):
        """Запуск игры"""
        self.root.mainloop()

def main():
    """Главная функция"""
    try:
        game = EvolutionGameGUI()
        game.run()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()