import os

import gi

from components.Legend import Legend

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Adw, Gio, Gdk, GLib
from datetime import datetime, timedelta
from loader import load_translation
from components.chart import Chart
from typing import cast

Adw.init()

class BatteryApp(Adw.Application):
    def __init__(self):
        self.app_name = "com.mmaaxx.batterylogger"
        self.settings = Gio.Settings.new(self.app_name)

        self.gtk_builder = Gtk.Builder()
        ui_path = os.path.join(os.path.dirname(__file__), "main.ui")
        self.gtk_builder.add_from_file(ui_path)

        self.load_css()

        self.t = load_translation()

        self.selected_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        super().__init__(application_id=self.app_name)
        self.connect("activate", self.on_activate)

        self.scrolled_window_dates = self.gtk_builder.get_object("scrolled_window_dates")
        self.date_stack = self.gtk_builder.get_object("date_stack")

    def on_activate(self, app):
        self.window = self.build_main_window(app)
        self.window.connect("close-request", self.on_close)
        self.window.present()

        GLib.timeout_add(100, self.after_load)

    def build_main_window(self, app):
        win = cast(Adw.ApplicationWindow, self.gtk_builder.get_object("main_window"))
        win.set_application(app)
        win.set_title(self.t['title'])

        width = self.settings.get_int("width") or 800
        height = self.settings.get_int("height") or 600
        win.set_default_size(width, height)

        self.build_ui()
        return win

    def build_ui(self):
        # Заголовок
        header_bar = self.gtk_builder.get_object('header_bar')
        header_bar.set_title_widget(Gtk.Label(label=self.t['title']))
        main_box = self.gtk_builder.get_object('main_box')

        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(13, -1, -1):  # Від старішого до новішого
            date = today - timedelta(days=i)
            button = Gtk.Button(label=date.strftime("%d"))
            if self.selected_date == date:
                button.add_css_class("selected")
            else:
                button.remove_css_class("selected")
            button.connect("clicked", self.on_date_button_clicked, date)
            self.date_stack.append(button)

        battery_chart_label = self.gtk_builder.get_object('battery_chart_label')
        battery_chart_label.set_label(self.t['battery_chart'])

        chart_container = self.gtk_builder.get_object('chart_container')
        placeholder = self.gtk_builder.get_object('battery_chart_placeholder')
        chart_container.remove(placeholder)
        self.chart = Chart()
        self.chart.set_hexpand(True)
        self.chart.set_content_height(500)
        chart_container.append(self.chart)

        legend = Legend()
        main_box.append(legend)

    def on_date_button_clicked(self, button, date):
        self.selected_date = date
        self.chart.update_for_date(date)
        for child in self.date_stack:
            child.remove_css_class("selected")

        button.add_css_class("selected")
        print('selected_date',date)

    def on_close(self, *args):
        w, h = self.window.get_default_size()
        self.settings.set_int("width", w)
        self.settings.set_int("height", h)
        return False

    def load_css(self):
        css_provider = Gtk.CssProvider()
        style_path = os.path.join(os.path.dirname(__file__), "style.css")
        css_provider.load_from_path(style_path)

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def after_load(self):
        hadjustment = self.scrolled_window_dates.get_hadjustment()
        if hadjustment:
            hadjustment.set_value(hadjustment.get_upper() - hadjustment.get_page_size())
        return False  # прибрати з циклу

app = BatteryApp()
app.run()


