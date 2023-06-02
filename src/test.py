
import sys
import gi
import math

from .library import Vec2, State, Arrow

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GLib

class TState():
    def __init__(self):
        self.states = []
        self.failed = False
    def follow(self, arrow):
        t = TState()
        t.failed = self.failed
        t.states = self.states.copy()
        t.states.append(arrow.end)
        return t
    def copy(self):
        ts = TState()
        ts.states = self.states.copy()
        ts.failed = self.failed
        return ts

class Test(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.did_pass = False;

        self.clamp = Adw.Clamp()
        self.set_child(self.clamp)

        self.header = Gtk.HeaderBar()
        self.header.set_css_classes(["flat"])
        self.set_title("Testing")
        self.set_titlebar(self.header)

        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list.set_css_classes(["boxed-list"])
        self.list.set_margin_top(0)
        self.list.set_margin_bottom(10)
        self.list.set_margin_start(10)
        self.list.set_margin_end(10)
        self.clamp.set_child(self.list)

        self.input = Adw.EntryRow()
        self.input.set_title("Input")
        self.input.connect("entry-activated", self.run_input)
        self.list.append(self.input)

        self.output = Adw.ActionRow()
        self.output.set_title("test")
        # output.set_css_classes(["success"])
        self.output.set_css_classes(["error"])
        self.icon = Gtk.Image.new_from_icon_name("dialog-error")
        self.output.add_suffix(self.icon)
        self.list.append(self.output)

        self.states = []
        self.arrows = []
        print("hallo")
    def run_input(self, _):
        input = self.input.get_text()


        if not self.did_pass:
            self.passed()
        else:
            self.failed()

        ts = [TState()]
        for s in self.states:
            if s.initial:
                ts[0].states = [s]
                print(s)
        print(ts[0].states)
        for i in range(0, len(input)):
            for t in ts:
                ts = ts + self.advance(t, input[i])
                ts.remove(t)
        print(len(ts))
        for path in ts:
            if path.failed:
                print("oops")
                continue
            path_string = path.states[0].label
            for i in range(1, len(path.states)):
                path_string += " -> " + path.states[i].label
            self.output.set_title(path_string)
            p = path.states[len(path.states)-1]
            if p.final:
                self.passed()
                return
        self.failed()
        print(input)
        return
    def advance(self, state, word):
        if state.failed:
            return [state.copy()]
        arrows = []
        for arrow in self.arrows:
            if not arrow.start == state.states[len(state.states)-1]:
                print("start did not match"+str(state.states[0]))
                continue

            labels = arrow.label.split(",")
            for i in range(0, len(labels)):
                labels[i] = labels[i].strip()

            passed = False
            for label in labels:
                if label == word:
                    passed = True
                    break
            if not passed:
                continue

            arrows.append(arrow)

        if len(arrows) == 0:
            print("no arrows")
            s = state.copy()
            s.failed = True
            return [s]

        states = []
        for arrow in arrows:
            states.append(state.follow(arrow))
        return states

    def passed(self):
        self.did_pass = True
        self.output.remove(self.icon)
        self.icon = Gtk.Image.new_from_icon_name("emblem-ok")
        self.output.set_css_classes(["success"])
        self.output.add_suffix(self.icon)
    def failed(self):
        self.did_pass = False
        self.output.remove(self.icon)
        self.output.set_css_classes(["error"])
        self.icon = Gtk.Image.new_from_icon_name("dialog-error")
        self.output.add_suffix(self.icon)
