import sys
import gi
import json
from . import library
from .library import Transform, Vec2, State, Arrow, ArrowTransition
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GLib

dialog = Gtk.FileDialog()

def open(window):
    print(window)
    dialog.open(window, None, open_response, window)

def open_response(dialog, result, window):
    try:
        file = dialog.open_finish(result)
        if file is not None:
            file.load_contents_async(None, parse_response, window)
            print(f"File path is {file.get_path()}")
    except GLib.Error as error:
        print(f"Error opening file: {error.message}")

def parse_response(file, result, window):
    contents = file.load_contents_finish(result)

    info = file.query_info("standard::display-name", Gio.FileQueryInfoFlags.NONE)
    if info:
        display_name = info.get_attribute_string("standard::display-name")
    else:
        display_name = file.get_basename()

    if not contents[0]:
        path = file.peek_path()
        print(f"Unable to open {path}: {contents[1]}")
    try:
        text = contents[1].decode('utf-8')
    except UnicodeError as err:
        path = file.peek_path()
        print(f"Unable to load the contents of {path}: the file is not encoded with UTF-8")
        return


    s_object = json.loads(text)
    print(s_object)
    window.states = []
    window.arrows = []

    for s_s in s_object["states"]:
        s = State()
        s.label = s_s["label"]
        s.position = Vec2(s_s["x"], s_s["y"])
        s.initial = s_s["initial"]
        s.final = s_s["final"]
        window.states.append(s)
    for s_a in s_object["arrows"]:
        a = Arrow()
        a.start = window.states[s_a["start"]]
        a.end = window.states[s_a["end"]]
        a.transitions = []
        for s_t in s_a["transitions"]:
            t = ArrowTransition()
            t.label = s_t["label"]
            t.stack = s_t["stack"]
            t.stack_push = s_t["stack_push"]
            t.stack_op = s_t["stack_op"]
            a.transitions.append(t)
        window.arrows.append(a)

    window.set_title(display_name + " - LibFlaps")
    window.canvas.queue_draw()


def save(window):
    dialog.save(window, None, construct_save, window)

def construct_save(source, result, window):
    file = dialog.save_finish(result)

    s_object = Save()
    for t in window.states:
        s_state = SaveState(t)
        s_object.states.append(s_state)

    for a in window.arrows:
        s_arrow = SaveArrow()
        s_arrow.start = window.states.index(a.start)
        s_arrow.end = window.states.index(a.end)
        for t in a.transitions:
            s_transition = SaveTransition()
            s_transition.label = t.label
            s_transition.stack = t.stack
            s_transition.stack_push = t.stack_push
            s_transition.stack_op = t.stack_op
            s_arrow.transitions.append(s_transition)
        s_object.arrows.append(s_arrow)
    text = json.dumps(library.todict(s_object))

    bytes = GLib.Bytes.new(text.encode('utf-8'))
    file.replace_contents_bytes_async(bytes,
                                None,
                                False,
                                Gio.FileCreateFlags.NONE,
                                None,
                                save_file_complete, window)
def save_file_complete(file, result, window):
    info = file.query_info("standard::display-name",
        Gio.FileQueryInfoFlags.NONE)
    if info:
        display_name = info.get_attribute_string("standard::display-name")
    else:
        display_name = file.get_basename()

    window.set_title(display_name + " - LibFlaps")
    window.canvas.queue_draw()


