import cairo
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Adw, GLib
from datetime import datetime, timedelta, time
from pathlib import Path
import csv

class Chart(Gtk.DrawingArea):
    def __init__(self):
        self.selected_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        super().__init__()
        self.set_draw_func(self.draw_chart)

    def update_for_date(self, date: datetime):
        self.selected_date = date
        self.queue_draw()

    def get_data(self):
        print('reload date', self.selected_date)
        log_dir = Path(GLib.get_user_data_dir()) / "com.mmaaxx.BatteryLogger"
        minute_log = log_dir / "battery_log.csv"

        target_date = self.selected_date.date()
        now = datetime.now()
        current_time = now.time() if target_date == now.date() else time(23, 59)

        interval_data = [{} for _ in range(144)]

        if not minute_log.exists():
            return [{'v': 0, 's': 'l'} for _ in range(144)]

        with open(minute_log, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    timestamp = datetime.fromisoformat(row['timestamp'])
                    if timestamp.date() != target_date:
                        continue

                    hour = timestamp.hour
                    minute = timestamp.minute
                    index = hour * 6 + minute // 10

                    percent = float(row['percent'])
                    charging = int(row['charging'].strip())

                    if 'values' not in interval_data[index]:
                        interval_data[index] = {
                            'values': [],
                            'charging_flags': []
                        }

                    interval_data[index]['values'].append(percent)
                    interval_data[index]['charging_flags'].append(charging)

                except Exception as e:
                    print(f"Error parsing row: {row} — {e}")

        result = []
        last_known = {'v': 0, 's': 'l'}

        for i in range(144):
            interval_time = time(i // 6, (i % 6) * 10)
            if interval_time > current_time:
                last_known = {'v': 0, 's': 'l'}
            elif 'values' in interval_data[i]:
                values = interval_data[i]['values']
                charging_flags = interval_data[i]['charging_flags']
                avg_percent = round(sum(values) / len(values), 2)
                last_known = {
                    'v': avg_percent,
                    's': 'c' if 1 in charging_flags else 's' if 2 in charging_flags else 'l'
                }
            else:
                last_known = {
                    'v': last_known['v'],
                    's': 's' if last_known['s'] == 's' else 'l'
                }

            result.append(dict(last_known))

        return result

    def draw_chart(self, area, context, width, height):
        values = self.get_data()
        # Задній фон
        if Adw.StyleManager.get_default().get_dark():
            context.set_source_rgba(0.25, 0.25, 0.25, 1)  # Темно-сірий
        else:
            context.set_source_rgba(0.9, 0.9, 0.9, 1)  # Світло-сірий

        radius = 20
        x_margin = 50
        y_margin = 40

        context.new_sub_path()
        context.arc(radius, radius, radius, 3.14, 1.5 * 3.14)
        context.arc(width - radius, radius, radius, 1.5 * 3.14, 0)
        context.arc(width - radius, height - radius, radius, 0, 0.5 * 3.14)
        context.arc(radius, height - radius, radius, 0.5 * 3.14, 3.14)
        context.close_path()
        context.fill()

        # Вирахування відступів
        available_width = width - 2 * x_margin
        available_height = height - 2 * y_margin
        bar_width = available_width / len(values) * 0.7
        spacing = available_width / len(values)
        x_offset = x_margin
        y_offset = y_margin

        # Сітка
        context.set_source_rgba(0.8, 0.8, 0.8, 1)
        context.set_line_width(1)

        for i in range(0, len(values)+6, 6):
            x = x_offset + i * spacing
            context.move_to(x, y_offset)
            context.line_to(x, y_offset + available_height)
        context.stroke()

        # Cтовпчики
        for i, val in enumerate(values):
            x = x_offset + i * spacing + (spacing - bar_width) / 2
            bar_height = available_height * val['v'] / 100
            y = y_offset + available_height - bar_height

            # Закруглений прямокутник
            radius = min(bar_width * 0.5, bar_height / 2)
            context.new_sub_path()
            context.arc(x + radius, y + radius, radius, 3.14, 1.5 * 3.14)
            context.line_to(x + bar_width - radius, y)
            context.arc(x + bar_width - radius, y + radius, radius, 1.5 * 3.14, 0)
            context.line_to(x + bar_width, y + bar_height)
            context.line_to(x, y + bar_height)
            context.line_to(x, y + radius)
            context.close_path()

            if val['s'] == 'l':
                context.set_source_rgba(0.75, 0.81, 0.88, 1)
            if val['s'] == 'c':
                context.set_source_rgba(0.40, 0.82, 0.47, 1)
            if val['s'] == 's':
                context.set_source_rgba(0.09, 0.69, 0.76, 1)
            context.fill()

        # Позначка зараз
        now = datetime.now()
        if self.selected_date.date() == now.date():
            context.set_source_rgba(0, 0, 0, 1)
            context.set_line_width(3)

            i = now.hour * 6 + now.minute // 10  + 1
            x = x_offset + i * spacing
            context.move_to(x, y_offset)
            context.line_to(x, y_offset + available_height)
            context.stroke()

            triangle_size = 10  # розмір трикутника в пікселях
            context.move_to(x, y_offset + available_height - triangle_size * 2)  # вершина трикутника
            context.line_to(x - triangle_size, y_offset + available_height)  # ліва точка
            context.line_to(x + triangle_size, y_offset + available_height)  # права точка
            context.close_path()
            context.fill()

            # Тренд
            if i >= 3:
                charge_now = values[i - 1]['v']
                charge_prev = values[i - 3]['v']  # 2 точки = 20 хв

                delta = charge_now - charge_prev
                if delta < 0:
                    speed_per_min = delta / 20  # % за хвилину
                    minutes_to_zero = charge_now / abs(speed_per_min)
                    columns = int(minutes_to_zero / 10)
                    max_columns = 144 - i
                    columns = min(columns, max_columns)

                    x0 = x_offset + i * spacing
                    x1 = x_offset + (i + columns) * spacing

                    y0 = y_offset + (1 - charge_now / 100.0) * available_height

                    minutes_till_end = max_columns * 10
                    end_charge = charge_now + speed_per_min * minutes_till_end
                    end_charge = max(0.0, end_charge)
                    y1 = y_offset + (1 - end_charge / 100.0) * available_height

                    context.set_source_rgba(0.75, 0.81, 0.88, 0.2)
                    context.move_to(x0, y0)
                    context.line_to(x1, y1)
                    context.line_to(x1, y_offset + available_height)
                    context.line_to(x0, y_offset + available_height)
                    context.close_path()
                    context.fill()

        # Легенда
        if Adw.StyleManager.get_default().get_dark():
            context.set_source_rgba(0.8, 0.8, 0.8, 1)
        else:
            context.set_source_rgba(0.3, 0.3, 0.3, 1)
        context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        context.set_font_size(16)

        # 100% (вгорі праворуч)
        context.move_to(width - x_margin + 5, y_margin)
        context.show_text("100%")

        # 0% (внизу праворуч)
        context.move_to(width - x_margin + 5, height - y_margin)
        context.show_text("0%")

        # Знизу зліва: 0 годин
        context.move_to(x_offset, height - y_margin + 16)
        context.show_text("0")

        # Знизу по центру: 12 годин
        context.move_to(width / 2, height - y_margin + 16)
        context.show_text("12")

