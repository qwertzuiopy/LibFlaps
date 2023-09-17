import sys
import gi
import math

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GLib

@Gtk.Template(resource_path='/de/egwagi/Libflaps/libflaps_toolbar.ui')
class HeaderBar(Adw.Bin):
    __gtype_name__ = 'HeaderBar'
    def __init__(self, window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        open_button = Gtk.Template.Child("open_button")

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.about)
        window.add_action(about_action)

        test_action = Gio.SimpleAction.new("test", None)
        test_action.connect("activate", self.test)
        window.add_action(test_action)

        center_action = Gio.SimpleAction.new("center", None)
        center_action.connect("activate", self.center)
        window.add_action(center_action)

        zoom_in_action = Gio.SimpleAction.new("zoom-in", None)
        zoom_in_action.connect("activate", self.zoom_in)
        window.add_action(zoom_in_action)
        zoom_out_action = Gio.SimpleAction.new("zoom-out", None)
        zoom_out_action.connect("activate", self.zoom_out)
        window.add_action(zoom_out_action)

        self.type_action = Gio.SimpleAction.new_stateful("type", GLib.VariantType.new("s"), GLib.Variant("s", "fsm"))
        self.type_action.connect("change_state", self.changed_type)
        window.add_action(self.type_action)

        self.window = window

    @Gtk.Template.Callback("show_open_dialog")
    def show_open_dialog(self, button):
        self.window.show_open_dialog(button)

    @Gtk.Template.Callback("show_save_dialog")
    def show_save_dialog(self, button):
        self.window.show_save_dialog(button)

    def about(self, _1 = None, _2 = None):
        self.window.about()
    def test(self, _1 = None, _2 = None):
        self.window.test()
    def center(self, _1 = None, _2 = None):
        self.window.center()

    def changed_type(self, _, w):
        self.type_action.set_state(w)
        w = w.get_string()
        self.window.switch_type(w)



    def zoom_in(self, _1 = None, _2 = None):
        self.window.scroll(None, 0, 1)
    def zoom_out(self, _1 = None, _2 = None):
        self.window.scroll(None, 0, -1)
