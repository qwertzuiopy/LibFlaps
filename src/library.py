import sys
import gi
import math
from enum import Enum

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GLib


class MachineType(Enum):
    FSM = 1
    PDA = 2
    TM = 3


class Transform:
    def __init__(self):
        self.offset = Vec2(0, 0)
        self.scale = 2
        self.dims = Vec2(0, 0)

class Vec2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
    def to_screen(self, transform):
        return Vec2(
                (self.x+transform.offset.x)*transform.scale,
                (self.y+transform.offset.y)*transform.scale
                )
    def to_world(self, transform):
        return Vec2(
                self.x/transform.scale-transform.offset.x,
                self.y/transform.scale-transform.offset.y
                )

    def rotated(self, alpha):
        return Vec2(
                self.x * math.cos(alpha) - self.y * math.sin(alpha),
                self.x * math.sin(alpha) + self.y * math.cos(alpha)
                )
    def angle(self):
        return math.atan2(self.y, self.x)

    def plus(self, vec):
        return Vec2(
                self.x + vec.x,
                self.y + vec.y
                )
    def minus(self, vec):
        return Vec2(
                self.x - vec.x,
                self.y - vec.y
                )
    def divided(self, num):
        return Vec2(
                self.x / num,
                self.y / num
                )
    def times(self, num):
        return Vec2(
                self.x * num,
                self.y * num
                )
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    def normalized(self):
        return self.times(1.0/self.length())
    def rounded(self):
        return Vec2(
                round(self.x),
                round(self.y)
                )
    def copy(self):
        return Vec2(self.x, self.y)

class State:
    def __init__(self):
        self.position = Vec2()
        self.label = "q0"
        self.type = "state"
        self.initial = False
        self.final = False
        self.test_active = False
    def copy(self):
        s = State()
        s.position = self.position.copy()
        s.label = self.label
        s.type = self.type
        s.initial = self.initial
        s.final = self.final
        s.test_active = self.test_active
        return s


class Arrow():
    def __init__(self):
        self.type = "arrow"
        self.start = None
        self.end = None
        self.offset = 0
        self.transitions = [ArrowTransition()]
class ArrowTransition():
    def __init__(self):
        self.label = "ε"
        self.stack = "#"
        self.stack_op = 2 # 0: push 1: pop 2: nop
        self.stack_push = ""


def sign(n):
    return 1 if n > 0 else -1 if n < 0 else 0 if n == 0 else math.nan

# there is a new Adwaita widget for this, but it is not available yet
class SwitchRow(Adw.ActionRow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_selectable(False)
        self.switch = Gtk.Switch()
        self.switch.set_vexpand(False)
        self.switch.set_valign(Gtk.Align.CENTER)
        self.add_suffix(self.switch)



# used in lib_io for saving to json
def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
            for key, value in obj.__dict__.items()
            if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj
        
