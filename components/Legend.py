import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
from loader import load_translation

class Legend(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.t = load_translation()

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.append(self._create_item("legend_charging", self.t['legend_charging']))
        self.append(self._create_item("legend_discharging", self.t['legend_discharging']))
        self.append(self._create_item("legend_save", self.t['legend_save_mode']))

    def _create_item(self, css_class, label_text):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        circle = Gtk.Box()
        circle.set_size_request(12, 12)
        circle.set_css_classes(["legend_circle", css_class])

        label = Gtk.Label(label=label_text)

        box.append(circle)
        box.append(label)
        return box
