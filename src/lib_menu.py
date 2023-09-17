import sys
import gi
import math
from . import lib_io

from .library import Transform, Vec2, State, Arrow, ArrowTransition, SwitchRow
# from .test import Test
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GLib


class PDAStateMenu(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_visible(False)

        self.wrapper = Gtk.ListBox()
        self.append(self.wrapper)
        self.wrapper.set_css_classes(["boxed-list"])

        self.control_box = Adw.EntryRow()
        self.control_box.set_size_request(200, 0)
        self.control_box.connect("changed", self.apply)
        self.control_box.set_selectable(False)
        self.wrapper.append(self.control_box)

        self.final = SwitchRow()
        self.final.set_title("Final")
        self.wrapper.append(self.final)

        self.initial = SwitchRow()
        self.initial.set_title("Initial")
        self.wrapper.append(self.initial)

        self.confirm = Adw.ActionRow()
        self.confirm.set_title("OK")
        self.confirm.set_activatable(True)
        self.confirm.set_selectable(False)
        self.confirm.connect("activated", self.close)
        self.confirm.set_css_classes(["accent"])
        self.wrapper.append(self.confirm)


        self.delete = Gtk.Button()
        self.delete.set_icon_name("edit-delete")
        self.delete.set_halign(Gtk.Align.END)
        self.delete.set_css_classes(["flat", "circular"])
        self.delete.connect("clicked", self.remove)
        self.confirm.add_suffix(self.delete)

        self.set_hexpand(False)
        self.set_vexpand(False)

    def show(self, window, state, x, y):
        self.state = state
        self.window = window

        size = Vec2(
            self.wrapper.get_preferred_size().minimum_size.width,
            self.wrapper.get_preferred_size().minimum_size.height
            )

        position = Vec2(x-size.x/2, y-size.y/2)
        position.x = min(position.x, self.window.transform.dims.x - size.x - 20)
        position.x = max(position.x, 20)
        position.y = min(position.y, self.window.transform.dims.y - size.y - 20)
        position.y = max(position.y, 20)
        position = position.rounded()

        self.set_visible(True)
        self.window.fixed.move(self, position.x, position.y)

        self.doapply = False

        self.control_box.set_text(self.state.label)
        self.initial.switch.set_active(self.state.initial)
        self.final.switch.set_active(self.state.final)

        self.doapply = True
    def apply(self, _ = None):
        if not self.doapply:
            return
        self.state.final = self.final.switch.get_active()
        self.state.initial = self.initial.switch.get_active()
        self.state.label = self.control_box.get_text()
        self.window.canvas.queue_draw()

    def remove(self, _ = None):
        self.window.states.remove(self.state)
        self.window.canvas.queue_draw()
        self.close()

    def close(self, _ = None):
        self.apply()
        self.window.fixed.set_visible(False)
        self.set_visible(False)





class PDAArrowMenu(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_visible(False)
        self.arrow = None

        self.window = None


        self.wrapper = Gtk.ListBox()
        self.append(self.wrapper)


        self.transitions = []
        self.wrapper.set_css_classes(["boxed-list"])

        self.confirm = Adw.ActionRow()
        self.confirm.set_title("OK")
        self.confirm.set_activatable(True)
        self.confirm.set_selectable(False)
        self.confirm.connect("activated", self.close)
        self.confirm.set_css_classes(["accent"])
        self.wrapper.append(self.confirm)

        self.add = Gtk.Button()
        self.add.set_icon_name("list-add")
        self.add.connect("clicked", self.add_transition)
        self.add.set_css_classes(["flat", "circular"])
        self.confirm.add_prefix(self.add)

        self.delete = Gtk.Button()
        self.delete.set_icon_name("edit-delete")
        self.delete.connect("clicked", self.remove)
        self.delete.set_css_classes(["flat", "circular"])
        self.confirm.add_suffix(self.delete)

        self.set_hexpand(False)
        self.set_vexpand(False)

    def show(self, window, arrow, x, y):
        # cleanup
        for t in self.transitions:
            self.wrapper.remove(t)


        self.arrow = arrow
        self.transitions = []
        self.window = window

        for t in self.arrow.transitions:
            uit = PDAArrowEntry(self)
            uit.transition = t
            uit.update_ui()
            self.wrapper.prepend(uit)
            self.transitions.append(uit)

        size = Vec2(
            self.wrapper.get_preferred_size().minimum_size.width,
            self.wrapper.get_preferred_size().minimum_size.height
            )

        position = Vec2(x-size.x/2, y-size.y/2)
        position.x = min(position.x, self.window.transform.dims.x - size.x - 20)
        position.x = max(position.x, 20)
        position.y = min(position.y, self.window.transform.dims.y - size.y - 20)
        position.y = max(position.y, 20)
        position = position.rounded()

        self.set_visible(True)
        self.window.fixed.move(self, position.x, position.y)
    def remove(self, _):
        self.window.arrows.remove(self.arrow)
        self.window.canvas.queue_draw()
        self.close(None)

    def add_transition(self, _):
        transition = PDAArrowEntry(self)
        self.transitions.append(transition)
        self.wrapper.prepend(transition)
        self.arrow.transitions.append(transition.transition)

    def close(self, _):
        self.window.fixed.set_visible(False)
        self.set_visible(False)

class PDAArrowEntry(Gtk.ListBoxRow):
    def __init__(self, arrow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arrow = arrow

        self.set_selectable(False)
        self.set_activatable(False)

        self.wrapper = Gtk.Box()
        self.wrapper.set_margin_top(5)
        self.wrapper.set_margin_bottom(5)
        self.wrapper.set_margin_start(5)
        self.wrapper.set_margin_end(5)
        self.wrapper.set_spacing(5)
        self.set_child(self.wrapper)

        self.input = Gtk.Entry()
        self.input.set_size_request(50, 0)
        self.input.set_placeholder_text("char")
        self.input.connect("changed", self.apply)
        self.wrapper.append(self.input)

        self.stack = Gtk.Entry()
        self.stack.set_size_request(50, 0)
        self.stack.set_placeholder_text("stack")
        self.stack.connect("changed", self.apply)
        self.wrapper.append(self.stack)

        self.operation = Gtk.DropDown.new_from_strings(["push", "pop", "nop"])
        self.operation.connect("notify::selected", self.apply)
        self.wrapper.append(self.operation)

        self.stack_push = Gtk.Entry()
        self.stack_push.set_size_request(50, 0)
        self.stack_push.set_placeholder_text("push")
        self.stack_push.connect("changed", self.apply)
        self.wrapper.append(self.stack_push)

        self.delete = Gtk.Button()
        self.delete.set_icon_name("edit-delete")
        self.delete.connect("clicked", self.remove)
        self.wrapper.append(self.delete)

        self.transition = ArrowTransition()

        self.doapply = True

    def remove(self, _):
        self.arrow.wrapper.remove(self)
        self.arrow.transitions.remove(self)
        self.arrow.arrow.transitions.remove(self.transition)

    def apply(self, _1 = None, _2 = None):
        if not self.doapply:
            return
        self.arrow.window.canvas.queue_draw()
        self.transition.label = self.input.get_text()
        self.transition.stack = self.stack.get_text()
        self.transition.stack_push = self.stack_push.get_text()
        self.transition.stack_op = self.operation.get_selected()
        if self.transition.stack_op == 0:
            self.stack_push.set_visible(True)
        else:
            self.stack_push.set_visible(False)
    def update_ui(self):
        self.doapply = False
        self.input.set_text(self.transition.label)
        self.stack.set_text(self.transition.stack)
        self.stack_push.set_text(self.transition.stack_push)
        self.operation.set_selected(self.transition.stack_op)
        if self.transition.stack_op == 0:
            self.stack_push.set_visible(True)
        else:
            self.stack_push.set_visible(False)
        self.doapply = True
























class FSMStateMenu(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_visible(False)

        self.wrapper = Gtk.ListBox()
        self.append(self.wrapper)
        self.wrapper.set_css_classes(["boxed-list"])

        self.control_box = Adw.EntryRow()
        self.control_box.set_size_request(200, 0)
        self.control_box.connect("changed", self.apply)
        self.control_box.set_selectable(False)
        self.wrapper.append(self.control_box)

        self.final = SwitchRow()
        self.final.set_title("Final")
        self.wrapper.append(self.final)

        self.initial = SwitchRow()
        self.initial.set_title("Initial")
        self.wrapper.append(self.initial)

        self.confirm = Adw.ActionRow()
        self.confirm.set_title("OK")
        self.confirm.set_activatable(True)
        self.confirm.set_selectable(False)
        self.confirm.connect("activated", self.close)
        self.confirm.set_css_classes(["accent"])
        self.wrapper.append(self.confirm)


        self.delete = Gtk.Button()
        self.delete.set_icon_name("edit-delete")
        self.delete.set_halign(Gtk.Align.END)
        self.delete.set_css_classes(["flat", "circular"])
        self.delete.connect("clicked", self.remove)
        self.confirm.add_suffix(self.delete)

        self.set_hexpand(False)
        self.set_vexpand(False)

    def show(self, window, state, x, y):
        self.state = state
        self.window = window

        size = Vec2(
            self.wrapper.get_preferred_size().minimum_size.width,
            self.wrapper.get_preferred_size().minimum_size.height
            )

        position = Vec2(x-size.x/2, y-size.y/2)
        position.x = min(position.x, self.window.transform.dims.x - size.x - 20)
        position.x = max(position.x, 20)
        position.y = min(position.y, self.window.transform.dims.y - size.y - 20)
        position.y = max(position.y, 20)
        position = position.rounded()

        self.set_visible(True)
        self.window.fixed.move(self, position.x, position.y)

        self.doapply = False

        self.control_box.set_text(self.state.label)
        self.initial.switch.set_active(self.state.initial)
        self.final.switch.set_active(self.state.final)

        self.doapply = True
    def apply(self, _ = None):
        if not self.doapply:
            return
        self.state.final = self.final.switch.get_active()
        self.state.initial = self.initial.switch.get_active()
        self.state.label = self.control_box.get_text()
        self.window.canvas.queue_draw()

    def remove(self, _ = None):
        self.window.states.remove(self.state)
        self.window.canvas.queue_draw()
        self.close()

    def close(self, _ = None):
        self.apply()
        self.window.fixed.set_visible(False)
        self.set_visible(False)





class FSMArrowMenu(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_visible(False)
        self.arrow = None

        self.window = None


        self.wrapper = Gtk.ListBox()
        self.append(self.wrapper)


        self.transitions = []
        self.wrapper.set_css_classes(["boxed-list"])

        self.confirm = Adw.ActionRow()
        self.confirm.set_title("OK")
        self.confirm.set_size_request(200, 0)
        self.confirm.set_activatable(True)
        self.confirm.set_selectable(False)
        self.confirm.connect("activated", self.close)
        self.confirm.set_css_classes(["accent"])
        self.wrapper.append(self.confirm)

        self.add = Gtk.Button()
        self.add.set_icon_name("list-add")
        self.add.connect("clicked", self.add_transition)
        self.add.set_css_classes(["flat", "circular"])
        self.confirm.add_prefix(self.add)

        self.delete = Gtk.Button()
        self.delete.set_icon_name("edit-delete")
        self.delete.connect("clicked", self.remove)
        self.delete.set_css_classes(["flat", "circular"])
        self.confirm.add_suffix(self.delete)

        self.set_hexpand(False)
        self.set_vexpand(False)

    def show(self, window, arrow, x, y):
        # cleanup
        for t in self.transitions:
            self.wrapper.remove(t)


        self.arrow = arrow
        self.transitions = []
        self.window = window

        for t in self.arrow.transitions:
            uit = FSMArrowEntry(self)
            uit.transition = t
            uit.update_ui()
            self.wrapper.prepend(uit)
            self.transitions.append(uit)

        size = Vec2(
            self.wrapper.get_preferred_size().minimum_size.width,
            self.wrapper.get_preferred_size().minimum_size.height
            )

        position = Vec2(x-size.x/2, y-size.y/2)
        position.x = min(position.x, self.window.transform.dims.x - size.x - 20)
        position.x = max(position.x, 20)
        position.y = min(position.y, self.window.transform.dims.y - size.y - 20)
        position.y = max(position.y, 20)
        position = position.rounded()

        self.set_visible(True)
        self.window.fixed.move(self, position.x, position.y)
    def remove(self, _):
        self.window.arrows.remove(self.arrow)
        self.window.canvas.queue_draw()
        self.close(None)

    def add_transition(self, _):
        transition = FSMArrowEntry(self)
        self.transitions.append(transition)
        self.wrapper.prepend(transition)
        self.arrow.transitions.append(transition.transition)

    def close(self, _):
        self.window.fixed.set_visible(False)
        self.set_visible(False)

class FSMArrowEntry(Gtk.ListBoxRow):
    def __init__(self, arrow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arrow = arrow

        self.set_selectable(False)
        self.set_activatable(False)

        self.wrapper = Gtk.Box()
        self.wrapper.set_margin_top(5)
        self.wrapper.set_margin_bottom(5)
        self.wrapper.set_margin_start(5)
        self.wrapper.set_margin_end(5)
        self.wrapper.set_spacing(5)
        self.set_child(self.wrapper)

        self.input = Gtk.Entry()
        self.input.set_size_request(50, 0)
        self.input.set_placeholder_text("char")
        self.input.connect("changed", self.apply)
        self.wrapper.append(self.input)

        self.delete = Gtk.Button()
        self.delete.set_icon_name("edit-delete")
        self.delete.connect("clicked", self.remove)
        self.wrapper.append(self.delete)

        self.transition = ArrowTransition()

        self.doapply = True

    def remove(self, _):
        self.arrow.wrapper.remove(self)
        self.arrow.transitions.remove(self)
        self.arrow.arrow.transitions.remove(self.transition)

    def apply(self, _1 = None, _2 = None):
        if not self.doapply:
            return
        self.arrow.window.canvas.queue_draw()
        self.transition.label = self.input.get_text()
    def update_ui(self):
        self.doapply = False
        self.input.set_text(self.transition.label)
        self.doapply = True

