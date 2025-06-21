import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
from simulation import EvolutionSimulation

class EvolutionGameGUI:
    """Графический интерфейс для игры 'Эволюция: Простая жизнь'"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Эволюция: Простая жизнь")
        self.root.geometry("1200x800")
        
        # Симуляция
        self.simulation = EvolutionSimulation(width=800, height=600)
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
        self.canvas = tk.Canvas(left_frame, width=800, height=600, bg='#001122')
        self.canvas.pack(pady=5)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Кнопки управления
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Старт/Пауза", command=self._toggle_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Сброс", command=self._reset_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Настройки", command=self._show_settings).pack(side=tk.LEFT, padx=2)
        
        # Правая панель (информация и статистика)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Скорость симуляции
        speed_frame = ttk.LabelFrame(right_frame, text="Скорость симуляции")
        speed_frame.pack(fill=tk.X, pady=5)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(speed_frame, from_=0.1, to=5.0, variable=self.speed_var,
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
        
        # Отрисовка пищи
        for food in self.simulation.get_food_sources():
            x, y = food['x'], food['y']
            size = food['size']
            self.canvas.create_oval(x-size, y-size, x+size, y+size, 
                                  fill='green', outline='darkgreen')
            
        # Отрисовка организмов
        for organism in self.simulation.get_organisms():
            x, y = organism.x, organism.y
            size = organism.genes['size']
            color = self._rgb_to_hex(*organism.get_color())
            
            # Выделение выбранного организма
            outline = 'yellow' if organism == self.selected_organism else 'black'
            outline_width = 3 if organism == self.selected_organism else 1
            
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
        
        stats_text = f"""ОБЩАЯ СТАТИСТИКА

Популяция: {stats['population']}
Поколение: {stats['avg_generation']:.1f}
Всего рождений: {stats['total_births']}
Всего смертей: {stats['total_deaths']}

СРЕДНИЕ ЗНАЧЕНИЯ ГЕНОВ:
Скорость: {stats['avg_speed']:.2f}
Размер: {stats['avg_size']:.2f}
Эффективность: {stats['avg_energy_efficiency']:.2f}

ВРЕМЯ СИМУЛЯЦИИ: {self.simulation.time_step}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
        
    def _update_organism_info(self):
        """Обновление информации о выбранном организме"""
        if self.selected_organism and self.selected_organism.alive:
            org = self.selected_organism
            info = org.get_info()
            
            info_text = f"""ВЫБРАННЫЙ ОРГАНИЗМ

Позиция: ({info['position'][0]:.1f}, {info['position'][1]:.1f})
Энергия: {info['energy']:.1f}
Возраст: {info['age']:.1f}
Поколение: {info['generation']}

ГЕНЫ:
Скорость: {info['genes']['speed']:.2f}
Размер: {info['genes']['size']:.2f}
Эффективность: {info['genes']['energy_efficiency']:.2f}
Порог размножения: {info['genes']['reproduction_threshold']:.1f}
Агрессивность: {info['genes']['aggression']:.2f}
Частота мутаций: {info['genes']['mutation_rate']:.3f}

ЦВЕТ RGB: ({info['genes']['color_r']}, {info['genes']['color_g']}, {info['genes']['color_b']})

Может размножаться: {'Да' if org.can_reproduce() else 'Нет'}
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
        
        # Максимальная популяция
        ttk.Label(settings_window, text="Максимальная популяция:").pack(pady=5)
        max_pop_var = tk.IntVar(value=self.simulation.max_organisms)
        max_pop_scale = ttk.Scale(settings_window, from_=20, to=200, variable=max_pop_var, orient=tk.HORIZONTAL)
        max_pop_scale.pack(fill=tk.X, padx=20)
        
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
                max_organisms=int(max_pop_var.get()),
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