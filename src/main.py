# main.py
#
# Copyright 2023 Michael
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi
import math
from . import lib_io
from . import lib_draw

from .lib_menu import PDAArrowMenu, PDAStateMenu, FSMArrowMenu, FSMStateMenu

from .library import Transform, Vec2, State, Arrow
from .test import TestWindow
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GLib

from .lib_toolbar import HeaderBar


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        GLib.set_application_name("Lib Flaps")

        self.header = HeaderBar(self)
        self.set_titlebar(self.header)
        #self.set_title("LibFlaps")
        self.set_default_size(800, 800)

        self.open_button = Gtk.Button(label="Open")
        # self.header.pack_start(self.open_button)
        self.open_button.connect("clicked", self.show_open_dialog)

        self.save_button = Gtk.Button(label="Save")
        # self.header.pack_start(self.save_button)
        self.save_button.connect("clicked", self.show_save_dialog)


        self.overlay = Gtk.Overlay()
        self.set_child(self.overlay)

        self.wrapper = Gtk.Box()
        self.wrapper.set_orientation(Gtk.Orientation.VERTICAL)
        self.test_window = TestWindow()
        self.wrapper.append(self.test_window)

        self.overlay.set_child(self.wrapper)


        self.fixed = Gtk.Fixed()
        self.overlay.add_overlay(self.fixed)

        self.arrow_menu = FSMArrowMenu()
        self.fixed.put(self.arrow_menu, 100, 100)
        self.arrow_menu.set_visible(False)

        self.state_menu = FSMStateMenu()
        self.fixed.put(self.state_menu, 100, 100)
        self.fixed.set_visible(False)

        self.type = "fsm"


        self.canvas = Gtk.DrawingArea()
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_draw_func(self.draw, None)
        self.wrapper.append(self.canvas)


        self.transform = Transform()
        self.transform.scale = 3

        self.states = []
        self.arrows = []




        # initialize input controllers

        evkc = Gtk.GestureClick.new()
        evkc.connect("pressed", self.mousedown)
        evkc.connect("released", self.mouseup)
        self.canvas.add_controller(evkc)
        evkc.set_button(0)

        evkm = Gtk.EventControllerMotion.new()
        evkm.connect("motion", self.mousemove)
        self.canvas.add_controller(evkm)

        evks = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.BOTH_AXES)
        evks.connect("scroll", self.scroll)
        self.add_controller(evks)

        evkp = Gtk.EventControllerKey.new()
        evkp.connect("key-pressed", self.key_press)
        evkp.connect("key-released", self.key_release)
        self.add_controller(evkp)

        self.active_element = None
        self.hovered_element = None
        self.selected = False
        self.moved = False
        self.preview_arrow = None

        self.left_down = False
        self.middle_down = False
        self.right_down = False
        self.mouse_start = Vec2()

        self.control = False
        self.shift = False


        self.radius = 10
        self.arrow_radius = 7

        self.line_width = 1
        self.arrow_width = 2
        self.arrow_height = 2
        self.self_arrow_offset = Vec2(0, -5)


        self.header.connect("state-flags-changed", self.apply_theme)
        self.apply_theme()


    def apply_theme(self, _bla = None, _bli = None):
        gset = Gtk.Settings.get_default ()
        prefdark = gset.get_property ("gtk-application-prefer-dark-theme")
        if prefdark:
            self.background_color = [0.14, 0.14, 0.14]
            self.foreground_color = [1, 1, 1]
        else:
            self.background_color = [0.98, 0.98, 0.98]
            self.foreground_color = [0, 0, 0]




    def test(self):
        self.test_window.start_test(self)



    def scroll(self, _, dx, dy):
        org_middle =  Vec2(self.transform.dims.x / 2, self.transform.dims.y / 2).to_world(self.transform)
        self.transform.scale *= 1.2 if dy > 0 else 0.8
        new_middle =  Vec2(self.transform.dims.x / 2, self.transform.dims.y / 2).to_world(self.transform)
        self.transform.offset = self.transform.offset.plus(new_middle.minus(org_middle))
        self.canvas.queue_draw()



    def key_press(self, event, keyval, keycode, state):
        if keyval == Gdk.KEY_q and state & Gdk.ModifierType.CONTROL_MASK:
            self.close()
        if keyval == Gdk.KEY_Control_L:
            self.control = True
        if keyval == Gdk.KEY_Shift_L:
            self.shift = True
    def key_release(self, event, keyval, keycode, state):
        self.control = False
        self.shift = False



    # called every time the mouse is pressed
    def mousedown(self, gesture, data, x, y):
        pos = Vec2(x, y).to_world(self.transform)

        self.mouse_start = Vec2(x, y)
        self.moved = False

        match (gesture.get_current_button()):
            case 1:
                self.left_down = True
                state = self.get_state(pos)
                arrow = self.get_arrow(pos)

                if self.shift:
                    pos = Vec2(x, y).to_world(self.transform)
                    if state != None:
                        self.preview_arrow = PreviewArrow()
                        self.preview_arrow.start = state
                        self.preview_arrow.end = pos
                elif state != None and not self.shift and not self.control:
                    self.select(state)
                elif arrow != None and not self.shift and not self.control:
                    self.select(arrow)
                elif not self.control and not self.shift:
                    state = State()
                    state.position = Vec2(x, y).to_world(self.transform)
                    state.label = "q"+str(len(self.states))

                    self.active_element = state
                    self.states.append(state)

            case 2:
                self.middle_down = True
                state = self.get_state(pos)
                if state == None:
                    return
                if self.shift:
                    state.initial = not state.initial
                else:
                    state.final = not state.final

            case 3:
                self.right_down = True
                state = self.get_state(pos)
                if state:
                    i = 0
                    while i < len(self.arrows):
                        if self.arrows[i].start == state or self.arrows[i].end == state:
                            self.arrows.remove(self.arrows[i])
                        else:
                            i += 1
                    self.states.remove(state)
                arrow = self.get_arrow(pos)
                if arrow:
                    self.arrows.remove(arrow)

        self.canvas.queue_draw()



    # called every time the mouse is moved
    def mousemove(self, motion, x, y):
        pos = Vec2(x, y).to_world(self.transform)

        # move the view if the middle mouse button is pressed
        if self.middle_down:
            self.transform.offset.x += (x - self.mouse_start.x) / self.transform.scale
            self.transform.offset.y += (y - self.mouse_start.y) / self.transform.scale
        # move the preview arrow
        if self.shift and self.preview_arrow != None:
            self.preview_arrow.end = self.preview_arrow.end.plus(Vec2(x, y).minus(self.mouse_start).divided(self.transform.scale))
        # move the selected state
        if self.selected and self.active_element.type == "state":
            self.active_element.position = self.active_element.position.plus(Vec2(x, y).minus(self.mouse_start).divided(self.transform.scale))

        # set the hovered element
        arrow = self.get_arrow(pos)
        state = self.get_state(pos)
        self.hovered_element = arrow if arrow != None else state if state != None else None
        self.moved = True

        # save mouse position for the next move
        self.mouse_start = Vec2(x, y)

        self.canvas.queue_draw()




    # called every time the mouse is released
    def mouseup(self, gesture, data, x, y):
        pos = Vec2(x, y).to_world(self.transform)

        # open arrow and state context menus
        if self.left_down and not self.moved:
            self.fixed.set_visible(True)
            if self.active_element.type == "state":
                self.state_menu.show(self, self.active_element, x, y)
            if self.active_element.type == "arrow":
                self.arrow_menu.show(self, self.active_element, x, y)

        # turn the preview arrow into a real arrow
        if self.preview_arrow != None:
            state = self.get_state(self.preview_arrow.end)
            if state != None:
                arrow = Arrow()
                arrow.start = self.preview_arrow.start
                arrow.end = state
                self.arrows.append(arrow)
                self.active_element = arrow
                self.fixed.set_visible(True)
                self.arrow_menu.show(self, self.active_element, x, y)

        # reset input variables
        self.preview_arrow = None

        self.left_down = False
        self.middle_down = False
        self.right_down = False

        self.selected = False
        self.active_element = None

        self.canvas.queue_draw()



# utility input functions

    # mark a state or arrow as selected
    def select(self, w):
        self.active_element = w
        self.selected = True

    # get a state at some position, None otherwise
    def get_state(self, pos):
        for state in self.states:
            rad = state.position.minus(pos).length()
            if rad < self.radius:
                return state
        return None

    # get an arrow at some position, None otherwise
    def get_arrow(self, pos):
        lib_draw.update_arrows(self)
        for arrow in self.arrows:
            arr = arrow.start.position.plus(arrow.end.position).times(0.5)
            if arrow.offset != 0 and arrow.start != arrow.end:
                arr = arr.plus(Vec2(0, math.sqrt(arrow.offset*arrow.offset)*5).rotated(arrow.end.position.minus(arrow.start.position).angle()))
            if arrow.start == arrow.end:
                arr = arrow.start.position.plus(self.self_arrow_offset).minus(Vec2(0, self.radius+5))
            rad = arr.minus(pos).length()
            if rad < self.arrow_radius:
                return arrow
        return None






    def draw(self, area, ctx, w, h, _):
        lib_draw.draw(self, area, ctx, w, h, _)

    def show_open_dialog(self):
        lib_io.open(self)
    def show_save_dialog(self):
        lib_io.save(self)


    def about(self):
        dialog = Adw.AboutWindow(transient_for=self)
        dialog.set_application_name=("App name")
        dialog.set_version("1.1")
        dialog.set_developer_name("Michael Hammer")
        dialog.set_license_type(Gtk.License(Gtk.License.GPL_3_0))
        dialog.set_comments("An application for creating, editing and viewing Finite-state machines and Pushdown automatons.")
        dialog.set_website("https://github.com/qwertzuiopy/LibFlaps")
        dialog.set_issue_url("https://github.com/qwertzuiopy/LibFlaps")
        #dialog.add_credit_section("Contributors", ["Michael_Hammer egwagi.de/Transistor"])
        # dialog.set_translator_credits("Name1 url")
        dialog.set_copyright("© 2022 Michael Hammer")
        dialog.set_developers(["Michael Hammer"])
        dialog.show()

    def center(self):
        current = self.transform.dims.divided(2).to_world(self.transform)
        self.transform.offset = self.transform.offset.plus(current.minus(self.states[0].position))

        org_middle =  Vec2(self.transform.dims.x / 2, self.transform.dims.y / 2).to_world(self.transform)
        self.transform.scale = 3
        new_middle =  Vec2(self.transform.dims.x / 2, self.transform.dims.y / 2).to_world(self.transform)
        self.transform.offset = self.transform.offset.plus(new_middle.minus(org_middle))

        self.canvas.queue_draw()

    def switch_type(self, w):
        self.type = w
        self.fixed.remove(self.arrow_menu)
        self.fixed.remove(self.state_menu)
        match self.type:
            case "fsm":
                self.arrow_menu = FSMArrowMenu()
                self.fixed.put(self.arrow_menu, 100, 100)
                self.arrow_menu.set_visible(False)
                self.state_menu = FSMStateMenu()
                self.fixed.put(self.state_menu, 100, 100)
                self.fixed.set_visible(False)
            case "pda":
                self.arrow_menu = PDAArrowMenu()
                self.fixed.put(self.arrow_menu, 100, 100)
                self.arrow_menu.set_visible(False)
                self.state_menu = PDAStateMenu()
                self.fixed.put(self.state_menu, 100, 100)
                self.fixed.set_visible(False)



class PreviewArrow:
    def __init__(self):
        self.start = None
        self.end = Vec2()
        self.label = "a"




class LibFlaps(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

def main(version):
    app = LibFlaps(application_id="de.egwagi.LibFlaps")
    app.run(sys.argv)

