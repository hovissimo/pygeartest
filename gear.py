from math import pi, cos, atan, sqrt

import cairo

from ruckbin import get_graphing_context, draw_axes, get_one_pixel, Saved, p2c, Polar
from drawing import draw_circle, draw_line, draw_x, draw_parametric_fn

WIDTH, HEIGHT = 900, 900
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)

x_center, y_center, zoom_radius = 0, 0, 7
bounds = (x_center - zoom_radius, y_center - zoom_radius, x_center + zoom_radius, y_center + zoom_radius)

c = get_graphing_context(surface, bounds)
draw_axes(c, bounds)

'''
Notes:

    Pitch circle:
        Engaged gears should be mounted such that the pitch circles are tangent to each other. The pitch circle lies
        between the outer circle and the root circle.
    Outer/root circles:
        These circles are at the tops and bottoms of each tooth.
    Base circle:
        The circle used to define the involute curve.
    Involute curve:
        The curve that defines the tooth profile.  Read on Wikipedia.
    Circular pitch:
        Measure in length.end
        Defined as pitch circumference divided by number of teeth. In other words, the arc distance along the pitch
        circle from the point on one tooth to the corresponding point on the next too.

'''

one_pixel = get_one_pixel(c)

def involute(t, base_radius):
    r = base_radius * sqrt(1.0 + t**2.0)
    phi = t - atan(t)
    return Polar(r, phi)

def gear_profile(
        circular_pitch, # pitch circumference / number of teeth
        number_of_teeth,
        pressure_angle,
        clearance,
        ):
    pressure_angle = 2*pi*pressure_angle/360 #convert to rads

    # The radius at which the pitch of the circle is measured.  It's near, but not at, halfway up each tooth.
    pitch_radius = circular_pitch * number_of_teeth / pi / 2
    pitch_color    = (1.0, 0.5, 0.2) #orange

    # The outer radius of the gear. Corresponds to the tips of the teeth.
    outside_radius = pitch_radius + circular_pitch / pi - clearance
    outside_color  = (0.2, 0.5, 0.7) #blue

    # The inner radius of the teeth. Corresponds to the troughs between the teeth.
    base_radius = pitch_radius * cos(pressure_angle)
    base_color     = (0.6, 0.3, 0.7) #purple

    # The radius of the involute curve which defines the tooth profile. Can be larger or smaller than the base radius.
    root_radius = pitch_radius * 2 - outside_radius - clearance
    root_color  = (0.2, 0.5, 0.7) #blue
    tooth_thickness = circular_pitch/2
    #angle_to_phi_base

    def fn(t):
        return involute(t, base_radius)


    draw_circle(c, (0, 0), pitch_radius  , color=pitch_color  , thickness=one_pixel/4)
    draw_circle(c, (0, 0), root_radius   , color=root_color   , thickness=one_pixel/4)
    draw_circle(c, (0, 0), base_radius   , color=base_color   , thickness=one_pixel/4)
    draw_circle(c, (0, 0), outside_radius, color=outside_color, thickness=one_pixel/4)

    for i in range(number_of_teeth):
        with Saved(c):
            angle = i*2*pi/number_of_teeth
            print(angle)
            c.rotate(angle)

            # Solve for the parametric input that corresponds to the intersection of the OUTER circle and the involute
            to = sqrt(outside_radius**2.0 / base_radius**2.0 - 1.0) # actually plus or minus sqrt, I'm ignoring the minus

            # xo is the intersection of the outside circle and the involute, in cartesion coordinates
            xo = p2c(fn(to))
            draw_line(c, (0,0), xo, outside_color, thickness=one_pixel/3)

            # Solve for the parametric input that corresponds to the intersection of the PITCH circle and the involute
            tp = sqrt(pitch_radius**2.0 / base_radius**2.0 - 1.0)
            xp = p2c(fn(tp))
            print(fn(to), fn(tp))
            draw_line(c, (0,0), xp, pitch_color, thickness=one_pixel/3)

            # Solve for the parametric input the corresponds to the beginning of the tooth profile
            if base_radius < root_radius:
                # The root radius is larger than the base radius
                tr = sqrt(root_radius**2 / base_radius**2 - 1) # actually plus or minus sqrt, I'm ignoring the minus?
            else: # If the base radius is larger, than we just start at 0
                tr = 0
            xr = p2c(fn(tr))
            draw_line(c, (0,0), xr, root_color)

            # Draw one involute curve (CCW)
            draw_parametric_fn(c, fn, tmin=tr, tmax=to, thickness=one_pixel, color=base_color)

            # We also need to draw the other (CW) curve

            c.move_to(0, 0)
            c.line_to(*p2c((root_radius, 0)))

            c.set_line_width(one_pixel)
            c.set_source_rgb(1,0,0)
            c.stroke()

gear_profile(
    5,
    7,
    20,
    0
)

surface.write_to_png('gear.png')
