import sys
import gi
import math

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GLib

from .library import Transform, Vec2, State, Arrow

@Gtk.Template(resource_path='/de/egwagi/Libflaps/libflaps_test_window.ui')
class TestWindow(Adw.Bin):
    __gtype_name__ = 'TestWindow'

    content = Gtk.Template.Child("content")
    entry = Gtk.Template.Child("entry")
    start = Gtk.Template.Child("start")
    close = Gtk.Template.Child("close")
    progress = Gtk.Template.Child("progress")
    path = Gtk.Template.Child("path")

    next = Gtk.Template.Child("next")
    previous = Gtk.Template.Child("previous")

    row = Gtk.Template.Child("row")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.obj = None
        self.start.connect("clicked", self.test)
        self.content_objs = []
        self.paths = []
        self.current_path = 0
        self.word = ""

        self.next.connect("clicked", self.next_path)
        self.previous.connect("clicked", self.previous_path)

    def next_path(self, _):
        self.current_path += 1
        if self.current_path >= len(self.paths):
            self.current_path = len(self.paths)-1
        if self.current_path >= len(self.paths)-1:
            self.next.set_sensitive(False)
        else:
            self.next.set_sensitive(True)
        if self.current_path < 0:
            self.current_path = 0
        if self.current_path <= 0:
            self.previous.set_sensitive(False)
        else:
            self.previous.set_sensitive(True)


        self.display_path(self.current_path)
    def previous_path(self, _):
        self.current_path -= 1
        if self.current_path >= len(self.paths):
            self.current_path = len(self.paths)-1
        if self.current_path >= len(self.paths)-1:
            self.next.set_sensitive(False)
        else:
            self.next.set_sensitive(True)
        if self.current_path < 0:
            self.current_path = 0
        if self.current_path <= 0:
            self.previous.set_sensitive(False)
        else:
            self.previous.set_sensitive(True)
        self.display_path(self.current_path)

    def start_test(self, obj):
        self.obj = obj
    def hide_progress(self, _):
        self.progress.set_fraction(0)
    def test(self, _):
        target_timed = Adw.PropertyAnimationTarget.new(self.progress, "fraction")
        animation_timed = Adw.TimedAnimation.new(self.progress, 0, 1, 1500, target_timed)
        animation_timed.connect("done", self.hide_progress)
        animation_timed.play()

        word = self.entry.get_text()

        p = []
        for i in self.obj.states:
            if i.initial:
                new_point = Point()
                new_point.state = i
                new_point.stack = []
                new_point.last_point = None
                p.append(new_point)
        for char in word:
            p = self.advance_state(p, char)
        fins = []
        for i in p:
            fins.append([])
            a = i
            while a != None:
                fins[-1].insert(0, a.state)
                a = a.last_point


        self.paths = fins
        self.current_path = 0
        self.word = word
        if len(self.paths) > 0:
            self.display_path(0)

        if self.contains_finish(p):
            self.row.set_css_classes(["success", "linked"])
            self.entry.set_icon_from_icon_name(1, "object-select-symbolic")
        else:
            self.row.set_css_classes(["error", "linked"])
            self.entry.set_icon_from_icon_name(1, "dialog-error-symbolic")
        self.start.set_icon_name("view-refresh-symbolic")
        self.path.set_reveal_child(True)
    def display_path(self, index):
        for i in self.content_objs:
            self.content.remove(i)
        for i in range(0, len(self.paths[index])):
            s = TestState(self.paths[index][i], self.obj)
            self.content.append(s)
            self.content_objs.append(s)
            if i < len(self.paths[index])-1:
                a = TestArrow(self.word[i])
                self.content.append(a)
                self.content_objs.append(a)
    def contains_finish(self, p):
        for point in p:
            if point.state.final:
                return True
        return False
    def get_all_arrows(self, state):
        arrows = []
        for i in self.obj.arrows:
            if i.start == state:
                arrows.append(i)
        return arrows

    def matches(self, transition, stack, char):
        if transition.label != char:
            return False
        # if transition.stack == "#" and len(stack) != 0 or transition.stack != stack[-1]:
        #     return False
        return True

    def advance_state(self, p, char):
        np = []
        for point in p:
            arrows = self.get_all_arrows(point.state)
            for arrow in arrows:
                for transition in arrow.transitions:
                    if self.matches(
                        transition,
                        point.stack,
                        char):

                        new_point = Point()
                        new_point.state = arrow.end
                        new_point.stack = point.stack.copy()
                        new_point.last_point = point
                        np.append(new_point)
        return np







class Point():
    def __init__(self):
        self.state = None
        self.stack = []
        self.last_point = None



class TestState(Gtk.Button):
    __gtype_name__ = 'TestState'
    def __init__(self, state, obj, **kwargs):
        super().__init__(**kwargs)
        self.set_halign(Gtk.Align.CENTER)
        self.set_label(state.label)
        self.add_css_class("pill")
        self.set_valign(Gtk.Align.CENTER)
        self.obj = obj
        self.state = state
        self.connect("clicked", self.highlight)
    def highlight(self, _):
        for i in self.obj.states:
            i.test_active = False
        self.state.test_active = True

class TestArrow(Gtk.Box):
    __gtype_name__ = 'TestArrow'
    def __init__(self, char, **kwargs):
        super().__init__(**kwargs)
        self.set_halign(Gtk.Align.CENTER)
        self.append(Gtk.Image.new_from_icon_name("value-decrease-symbolic"))
        self.append(Gtk.Label.new(char))
        self.append(Gtk.Image.new_from_icon_name("go-next-symbolic"))

