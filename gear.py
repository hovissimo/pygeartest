from math import pi, cos, atan, sqrt

import cairo

from ruckbin import get_graphing_context, draw_axes, get_one_pixel, Saved, p2c, Polar
from drawing import draw_circle, draw_line, draw_x, draw_parametric_fn

WIDTH, HEIGHT = 900, 900
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)

x_center, y_center, zoom_radius = 8, 0, 2
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
    "Return the polar coordinates of a point along the involute curve generated from a circle of given base_radius."
    r = base_radius * sqrt(1.0 + t**2.0)
    phi = t - atan(t)
    return Polar(r, phi)

def gear_profile(
        circular_pitch, # pitch circumference / number of teeth
        number_of_teeth,
        pressure_angle,
        clearance,
        ):
    pressure_angle = 2 * pi * pressure_angle / 360 #convert to rads
    angle_per_tooth = 2*pi/number_of_teeth

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
    tooth_thickness = circular_pitch / 2
    #angle_to_phi_base

    def fn(t):
        return involute(t, base_radius)

    draw_circle(c, (0, 0), pitch_radius  , color=pitch_color  , thickness=one_pixel/6)
    draw_circle(c, (0, 0), root_radius   , color=root_color   , thickness=one_pixel/6)
    draw_circle(c, (0, 0), base_radius   , color=base_color   , thickness=one_pixel/6)
    #draw_circle(c, (0, 0), outside_radius, color=outside_color, thickness=one_pixel/6)

    for i in range(number_of_teeth):
        with Saved(c):
            tooth_angle = i * angle_per_tooth
            print("\nAdding tooth at angle {}".format(tooth_angle))
            c.rotate(tooth_angle)

            # Solve for the parametric input that corresponds to the intersection of the OUTER circle and the involute
            to = sqrt(outside_radius**2.0 / base_radius**2.0 - 1.0) # actually plus or minus sqrt, I'm ignoring the minus

            # xo is the intersection of the outside circle and the involute, in cartesion coordinates
            #xo = fn(to)
            #draw_line(c, (0,0), p2c(*xo), outside_color, thickness=one_pixel/6)

            # Solve for the parametric input that corresponds to the intersection of the PITCH circle and the involute
            tp = sqrt(pitch_radius**2.0 / base_radius**2.0 - 1.0)
            xp = p2c(*fn(tp))
            draw_line(c, (0,0), xp, pitch_color, thickness=one_pixel/6)
            draw_line(c, (0,0), xp, pitch_color, thickness=one_pixel/6)

            # Figure out the angle to the tooth symmetry line
            mirror_angle = fn(tp).angle + angle_per_tooth/4
            draw_line(c, (0,0), p2c(pitch_radius, mirror_angle), (0.0, 0.8, 0.8), thickness=one_pixel/6)

            draw_line(c, (0,0), p2c(fn(tp).radius, mirror_angle * 2 - fn(tp).angle), pitch_color, thickness=one_pixel/6)

            # Solve for the parametric input the corresponds to the beginning of the tooth profile
            if base_radius < root_radius:
                # The root radius is larger than the base radius
                tr = sqrt(root_radius**2 / base_radius**2 - 1) # actually plus or minus sqrt
                # Don't neglect to negate tr for the other negative side of the involute!
            else: # If the base radius is larger, than we just start at 0
                tr = 0

            # We also need to draw the sides under the involute in this case
            draw_line(c,
                      frum = p2c(root_radius, fn(tr).angle),
                      to = p2c(*fn(tr)),
                      color = root_color,
                      thickness = one_pixel)
            draw_line(c,
                      frum = p2c(root_radius, mirror_angle*2 + fn(-tr).angle),
                      to = p2c(fn(-tr).radius, mirror_angle*2 - fn(-tr).angle),
                      color = root_color,
                      thickness = one_pixel)

            # Draw the root segment
            draw_line(c,
                      frum = p2c(root_radius, fn(-tr).angle + mirror_angle*2),
                      to = p2c(root_radius, fn(tr).angle + angle_per_tooth),
                      color = root_color,
                      thickness = one_pixel)


            # Draw one involute curve (CCW)
            draw_parametric_fn(c, fn, tmin=tr, tmax=to, thickness=one_pixel, color=base_color)

            # Draw the connection at the tooth tip
            tip_angle_distance = 2*mirror_angle - fn(to).angle
            draw_parametric_fn(c,
                               lambda t: Polar(outside_radius, t),
                               tmin = fn(to).angle,
                               tmax = tip_angle_distance,
                               thickness = one_pixel*2/3,
                               color = (0, 0.6, 0.8))

            # We also need to draw the other (CW) curve
            c.rotate(mirror_angle*2)
            draw_parametric_fn(c, fn, tmin=-tr, tmax=-to, thickness=one_pixel, color=base_color)

            '''
            c.move_to(0, 0)
            c.line_to(*p2c(root_radius, 0))

            c.set_line_width(one_pixel)
            c.set_source_rgb(1,0,0)
            c.stroke()
            '''

gear_profile(
    2,
    25,
    20,
    0
)

surface.write_to_png('gear.png')
