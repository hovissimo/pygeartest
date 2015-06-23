from math import pi

from ruckbin import get_one_pixel, Saved, frange, p2c

def draw_circle(context, center, radius, *args, **kwargs):
    with Saved(context) as c:
        x, y = center
        c.arc(x, y, radius, 0, 2*pi)
        _stroke(c, *args, **kwargs)

def draw_x(context, point, pixel_radius=4, *args, **kwargs):
    with Saved(context) as c:
        x, y = point
        one_pixel = get_one_pixel(c)
        offset = pixel_radius * one_pixel;

        c.move_to(x - offset, y + offset) #upper left
        c.line_to(x + offset, y - offset) #lower right

        c.move_to(x + offset, y + offset) #upper right
        c.line_to(x - offset, y - offset) #lower left

        _stroke(c, *args, **kwargs)

def draw_parametric_fn(context, fn, steps=32, tmin=0, tmax=1, *args, **kwargs):
    with Saved(context) as c:
        # move to initial position
        c.move_to(*fn(tmin)) # line up the head of the curve
        for t in frange(tmin, tmax, tmax/(steps)):
            c.line_to(*p2c(fn(t))) # draw the steps
        c.line_to(*p2c(fn(tmax))) # draw to the tail of the curve (frange doesn't include tmax)

        _stroke(c, *args, **kwargs)

def draw_line(context, frum, to, *args, **kwargs):
    with Saved(context) as c:
        c.move_to(frum[0], frum[1])
        c.line_to(to[0], to[1])
        _stroke(c, *args, **kwargs)

def _stroke(context, color=(0,0,0), thickness=None, dash_pattern=(), dash_offset=0):
    if not thickness:
        thickness = get_one_pixel(context)
    context.set_dash(dash_pattern, dash_offset)
    context.set_source_rgb(*color)
    context.set_line_width(thickness)
    context.stroke()
