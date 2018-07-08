import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
import mpld3
from skyfield.api import load
import numpy as np
import argparse

html_file='index.html'

planets = load('de421.bsp')
earth, moon = planets['earth'], planets['moon']

# Setup time
ts = load.timescale()
t = ts.now()
year = int(t.utc_strftime('%Y'))

# Setup plot
fig, (ax, ax2) = plt.subplots(1,2)
ax.axis('equal')
ax.set_xlim(-1.3,1.3)
ax.set_facecolor('k')
ax2.axis('equal')
ax2.set_xlim(-1.3,1.3)
ax2.set_facecolor('k')

class SolarModel():
    def __init__(self, mode='cartoon'):
        if mode == 'cartoon':
            self.sun_rad = 0.2
            self.earth_rad = 0.05
            # Moon is approx 1/4 radius of Earth
            self.moon_rad = self.earth_rad / 4
            self.earth_moon_scale = 50
        else:
            # Real:
            # Sun radius is actually about 0.00465 au
            # which is 109x earth's
            self.sun_rad = 0.00465
            self.earth_rad = sun_rad / 109
            self.moon_rad = self.earth_rad / 4
            self.earth_moon_scale = 1

    def earthPosition(self, t):
        return earth.at(t).ecliptic_position().au

    def moonPosition(self, t, scale=True):
        mpos = moon.at(t).ecliptic_position().au

        if scale:
            epos = self.earthPosition(t)
            # Move the moon farther away from earth based on earth_moon_scale
            mpos = epos + self.earth_moon_scale * (mpos - epos)

        return mpos

    def animate(self, i):
        patches = []
        time = ts.tt(jd=t.tt + i)
        patches.append(addEarth(self, time))
        patches.append(addMoon(self, time))
        patches.extend(moonPhase(self, time))
        return patches


def addEarth(model, t):
    color = 'b'
    ex, ey, ez = model.earthPosition(t)
    earth_obj = mpatches.Circle((ex, ey), model.earth_rad, color=color)
    return ax.add_patch(earth_obj)

def addMoon(model, t):
    color = 'w'
    mx, my, mz = model.moonPosition(t)
    moon_obj = mpatches.Circle((mx, my), model.moon_rad, color=color)
    return ax.add_patch(moon_obj)

def moonPhase(model, t):
    patches = []
    # Compute sun, moon, earth angle at t
    reflect_color = '0.9'
    shadow_color = '0.1'
    phase_rad = 0.5
    mpos = model.moonPosition(t, scale=False)
    epos = model.earthPosition(t)
    v_em = mpos - epos
    v_em = v_em / np.linalg.norm(v_em)
    v_ms = -1 * mpos
    v_ms = v_ms / np.linalg.norm(v_ms)
    # z component of cross product tells which side of moon is lit
    cx, cy, cz = np.cross(v_em, v_ms)
    # dot product determines how far over the shadow is, and if center is lit or shaded
    cosine = np.dot(v_em, v_ms)
    # Start with fully shadowed moon
    patches.append(ax2.add_patch(mpatches.Circle((0,0), phase_rad, color=shadow_color)))

    if cz < 0:
        patches.append(ax2.add_patch(mpatches.Wedge((0,0), phase_rad, -90, 90, color=reflect_color)))
    else:
        patches.append(ax2.add_patch(mpatches.Wedge((0,0), phase_rad, 90, 270, color=reflect_color)))

    if cosine > 0:
        patches.append(ax2.add_patch(mpatches.Ellipse((0,0), cosine * 2 * phase_rad, 2 * phase_rad, color=shadow_color)))
    else:
        patches.append(ax2.add_patch(mpatches.Ellipse((0,0), cosine * 2 * phase_rad, 2 * phase_rad, color=reflect_color)))

    return patches

def setup_bg(model):
    # Plot lines for calendar
    for i in range(1,13):
        color = (0, 1, 0, i / 12) #(r, g, b, a)
        linewidth = .5
        # 20th of each month is close to equinox/solstice
        time = ts.utc(year, i, 20)
        ex, ey, ez = model.earthPosition(time)
        line_obj = mpatches.ConnectionPatch((0,0), (ex, ey), "data", color=color, linewidth=linewidth)
        ax.add_patch(line_obj)

    sun_obj = mpatches.Circle((0,0), model.sun_rad, color='y')
    ax.add_patch(sun_obj)
    ax2.add_patch(mpatches.Circle((0,0), 0.5, color='0.1'))


def init():
    return []

def write_html():
    with open(html_file, 'w') as f:
#        f.write('<meta http-equiv="refresh" content="30">')
        mpld3.save_html(plt.gcf(), f)

def main(args):
    if args.real:
        mode = 'real'
    else:
        mode = 'cartoon'

    global t
    if args.offset != 0:
        t = ts.tt(jd=t.tt + args.offset)

    model = SolarModel(mode=mode)
    setup_bg(model)

    if args.animate:
        ani = animation.FuncAnimation(fig, model.animate, range(0, 365), init_func=init, blit=True)
    else:
        # Draw earth and moon position now
        model.animate(0)

    #moonPhase(model, t)

    # Display the plot
    plt.show()
    #mpld3.show()
    #write_html()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solar/Lunar Calendar")
    parser.add_argument('--animate', action='store_true', default=False)
    parser.add_argument('--real', action='store_true', default=False)
    parser.add_argument('--offset', type=int, default=0)
    args = parser.parse_args()
    main(args)
