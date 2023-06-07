import sys
import gi
import math
from . import library

from .library import Transform, Vec2, State, Arrow
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GLib

def draw(window, area, ctx, w, h, _):
    window.transform.dims = Vec2(w, h)

    set_source_bg(window, ctx)
    ctx.paint()


    for state in window.states:
        draw_state(window, ctx, state)


    update_arrows(window)

    for arrow in window.arrows:
        draw_arrow(window, ctx, arrow)

    if window.preview_arrow != None:
        arrow = window.preview_arrow

        state_offset = arrow.end.minus(arrow.start.position).normalized().times(window.radius+2)

        start = arrow.start.position.plus(state_offset).to_screen(window.transform)
        end = arrow.end.minus(state_offset).to_screen(window.transform)

        set_source_fg(window, ctx)
        ctx.set_line_width(window.line_width * window.transform.scale)
        ctx.move_to(start.x, start.y)
        ctx.line_to(end.x, end.y)
        ctx.stroke()

        draw_arrow_tip(window, ctx,
                    arrow.end.minus(state_offset),
                    arrow.end.minus(arrow.start.position).angle(),
                    arrow
                )
def draw_arrow_tip(window, ctx, position, angle, arrow):
    position = position.to_screen(window.transform)

    ctx.save()
    ctx.translate(position.x, position.y)
    ctx.rotate(angle)
    ctx.scale(window.transform.scale, window.transform.scale)

    if window.hovered_element == arrow:
        set_source_highlight(window, ctx)
    else:
        set_source_fg(window, ctx)
    ctx.set_line_width(window.line_width)
    ctx.move_to(-window.arrow_width, -window.arrow_height)
    ctx.line_to(0, 0)
    ctx.line_to(-window.arrow_width, window.arrow_height)

    ctx.stroke()

    ctx.restore()

def arrow_label(window, ctx, position, arrow):
    position = position.to_screen(window.transform)

    ctx.select_font_face("Sans")
    ctx.set_font_size(7*window.transform.scale)

    for t in arrow.transitions:
        index = arrow.transitions.index(t)
        if arrow.offset == 0 and arrow.start != arrow.end:
            offset = Vec2(0,
                index*window.transform.scale*10 - (len(arrow.transitions)-1)*window.transform.scale*5)
        elif arrow.start == arrow.end:
            offset = Vec2(0,
                -index*window.transform.scale*10-window.transform.scale*2)
        else:
            offset = Vec2(0,
                index*window.transform.scale*10+window.transform.scale*2)
        if library.sign(offset.rotated(arrow.end.position.minus(arrow.start.position).angle()).y) != library.sign(offset.y):
            offset.y = -offset.y
        if window.type == "pda":
            text = str(t.label)+", "+str(t.stack)+"; "
            match t.stack_op:
                case 0:
                    text += "push("+str(t.stack_push)+")"
                case 1:
                    text += "pop()"
                case 2:
                    text += "nop"
        else:
            text = str(t.label)
        (x, y, width, height, dx, dy) = ctx.text_extents(text)

        set_source_bg(window, ctx)
        ctx.rectangle(position.x-width/2-5+offset.x, position.y-height/2-5+offset.y, width+10, height+10)
        ctx.fill()

        ctx.save()

        if window.hovered_element == arrow:
            set_source_highlight(window, ctx)
        else:
            set_source_fg(window, ctx)
        ctx.translate(position.x, position.y)
        ctx.translate(offset.x, offset.y)
        ctx.move_to(-width/2, height/2)
        ctx.show_text(text)
        ctx.restore()

def stroke_self_arrow(window, ctx, point, arrow):
    start = point.plus(Vec2(0, 2+window.radius).rotated( 0.2 - 3.1415926))
    end = point.plus(Vec2(0, 2+window.radius).rotated(-0.2 - 3.1415926))

    center = end.plus(start).times(1/2).plus(window.self_arrow_offset.times(window.transform.scale))

    start = start.to_screen(window.transform)
    center = center.to_screen(window.transform)
    end = end.to_screen(window.transform)

    a = Vec2(5*window.transform.scale, 15*window.transform.scale).rotated(center.minus(start).angle()).plus(center)
    b = Vec2(5*window.transform.scale, -15*window.transform.scale).rotated(center.minus(end).angle()).plus(center)

    if window.hovered_element == arrow:
        set_source_highlight(window, ctx)
    else:
        set_source_fg(window, ctx)

    ctx.set_line_width(window.line_width * window.transform.scale)
    ctx.move_to(start.x, start.y)
    ctx.curve_to(a.x, a.y, b.x, b.y, end.x, end.y)
    ctx.stroke()

    draw_arrow_tip(window, ctx, end.to_world(window.transform), -0.35 + 3.1415926/2, arrow)
    arrow_label(window, ctx, center.to_world(window.transform).plus(Vec2(0, 7)), arrow)

def update_arrows(window):
    for a in window.arrows:
        a.offset = 0
    for a in window.arrows:
        for b in window.arrows:
            if a.start != b.end or a.end != b.start:
                continue
            if a.offset == 0:
                a.offset = 1
            if b.offset == 0:
                b.offset = -1



def set_source_bg(window, ctx):
    ctx.set_source_rgb(window.background_color[0], window.background_color[1], window.background_color[2])

def set_source_fg(window, ctx):
    ctx.set_source_rgb(window.foreground_color[0], window.foreground_color[1], window.foreground_color[2])
def set_source_highlight(window, ctx):
    ctx.set_source_rgb(53/255, 132/255, 228/255)


def draw_state(window, ctx, state):
    set_source_fg(window, ctx)

    if window.hovered_element == state:
        set_source_highlight(window, ctx)

    radius = window.radius*window.transform.scale
    pos = state.position.to_screen(window.transform)

    # draw basic circle
    ctx.set_line_width(window.line_width * window.transform.scale)
    ctx.new_path()
    ctx.arc(pos.x, pos.y, radius, 0, 2 * 3.1415926)
    ctx.stroke()

    # another circle if final
    if state.final:
        ctx.new_path()
        ctx.arc(pos.x, pos.y, radius+1.5*window.transform.scale, 0, 2 * 3.1415926)
        ctx.stroke()

    # a triangle if initial
    if state.initial:
        ctx.new_path()
        ctx.move_to(pos.x-(window.radius+3)*window.transform.scale, pos.y)
        ctx.line_to(pos.x-(window.radius+8)*window.transform.scale, pos.y-5*window.transform.scale)
        ctx.line_to(pos.x-(window.radius+8)*window.transform.scale, pos.y+5*window.transform.scale)
        ctx.fill()


    # draw the label
    ctx.select_font_face("Sans")
    ctx.set_font_size(10*window.transform.scale)
    (x, y, width, height, dx, dy) = ctx.text_extents(state.label)

    # a loop to decrease the font size until the label fits in the circle
    f = 1
    while width > (window.radius*2-0.5)*window.transform.scale:
        f -= 0.01
        ctx.set_font_size(10*window.transform.scale*f)
        (x, y, width, height, dx, dy) = ctx.text_extents(state.label)

    ctx.move_to(pos.x-width/2, pos.y+height/2)
    ctx.show_text(state.label)


def draw_arrow(window, ctx, arrow):
    if arrow.start == arrow.end:
        stroke_self_arrow(window, ctx, arrow.start.position, arrow)
        return
    side_offset = Vec2(0, math.sqrt(arrow.offset*arrow.offset*25)).rotated(arrow.end.position.minus(arrow.start.position).angle())
    state_offset = arrow.end.position.minus(arrow.start.position).normalized().times(window.radius+2)

    start = arrow.start.position.plus(state_offset).plus(side_offset).to_screen(window.transform)
    end = arrow.end.position.minus(state_offset).plus(side_offset).to_screen(window.transform)

    if window.hovered_element == arrow:
        set_source_highlight(window, ctx)
    else:
        set_source_fg(window, ctx)

    ctx.set_line_width(window.line_width * window.transform.scale)
    ctx.move_to(start.x, start.y)
    ctx.line_to(end.x, end.y)
    ctx.stroke()

    draw_arrow_tip(window, ctx,
                arrow.end.position.plus(side_offset).minus(state_offset),
                arrow.end.position.minus(arrow.start.position).angle(),
                arrow
            )


    arrow_label(window, ctx, arrow.start.position.plus(arrow.end.position).times(1/2).plus(side_offset), arrow)

