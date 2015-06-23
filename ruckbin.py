from math import cos, sin, atan, sqrt
from collections import namedtuple

import cairo

Polar = namedtuple('Polar', ('radius', 'radians'))

class Saved():
    def __init__(self, cr):
        self.cr = cr
    def __enter__(self):
        self.cr.save()
        return self.cr
    def __exit__(self, type, value, traceback):
        self.cr.restore()

def get_one_pixel(context):
    return context.device_to_user_distance(1, 0)[0]

def frange(start, stop, step, inclusive=False):
    ''' A version of range that supports float increments.

    Yield values starting at 'start' and proceeding towards 'stop' in 'step' increments. The sign of 'step' is ignored.

    >>> [round(t, 2) for t in frange(0, 1, 0.2)]
    [0, 0.2, 0.4, 0.6, 0.8]

    >>> [round(t, 2) for t in frange(3, -2, 0.4)]
    [3, 2.6, 2.2, 1.8, 1.4, 1.0, 0.6, 0.2, -0.2, -0.6, -1.0, -1.4, -1.8]
    '''
    step = abs(step)
    if start < stop:
        while start < stop:
            yield start
            start += step
    else:
        while start > stop:
            yield start
            start -= step

def p2c(polar):
    r, phi = polar
    return r*cos(phi), r*sin(phi)

def get_graphing_context(surface, bounds=(-5, -5, 5, 5)):
    c = cairo.Context(surface)
    xmin, ymin, xmax, ymax = bounds

    # transform so that mins and maxes fit
    c.scale(
        surface.get_width() / ( xmax - xmin),
        surface.get_height() / ( ymax - ymin )
    )
    c.scale(1, -1)
    c.translate(-xmin, -ymax)
    return c

def draw_axes(context, bounds=(-5, -5, 5, 5), increment=1):
    xmin, ymin, xmax, ymax = bounds
    with Saved(context) as c:
        one_pixel = c.device_to_user_distance(1, 0)[0]
        c.set_line_width(one_pixel)

        # X axis
        c.move_to(xmin, 0)
        c.line_to(xmax, 0)
        if (increment):
            for step in frange(xmin, xmax, increment):
                c.move_to(step, -one_pixel*2)
                c.line_to(step,  one_pixel*2)

        c.set_source_rgba(1, 0, 0, 0.6)
        c.stroke()

        # Y axis
        c.move_to(0, ymin)
        c.line_to(0, ymax)
        if (increment):
            for step in frange(xmin, xmax, increment):
                c.move_to(-one_pixel*2, step)
                c.line_to( one_pixel*2, step)

        c.set_source_rgba(0, 1, 0, 0.3)
        c.stroke()

def this_needs_a_name(fn, tmin, tmax, threshold):
    "Recursively divide the largest segment until all segments are smaller than threshold"
    def dist(ta, tb):
        pa, pb = fn(ta), fn(tb)
        return (pb[0]-pa[0])**2 + (pb[1]-pa[1])**2
    d, l = {}, []

    d[dist(tmin, tmax)] = tmin, tmax
    l.append(tmin)
    l.append(tmax)

    longest = max(d)
    while longest > threshold:
        # split max(d)
        ta, tc = d[longest]
        tb = (tc - ta)/2 + ta #tb is the new midpoint between tc and ta
        l.append(tb)
        d[dist(ta, tb)] = ta, tb
        d[dist(tb, tc)] = tb, tc
        del d[longest]
        longest = max(d)
        print(longest)

    return sorted(l)
