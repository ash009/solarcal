import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation

import mpld3

from skyfield.api import load


planets = load('de421.bsp')

earth, moon = planets['earth'], planets['moon']

# Cartoon settings
sun_rad = 0.2
earth_rad = 0.05
earth_moon_scale = 50

# Real:
# Sun radius is actually about 0.00465 au
# which is 109x earth's
#sun_rad = 0.00465
#earth_rad = sun_rad / 109
#earth_moon_scale = 1

ts = load.timescale()
t = ts.now()
year = int(t.utc_strftime('%Y'))


fig, ax = plt.subplots()

ax.set_facecolor('k')

def addEarth(t, rad, color='b', showMoon=False, patch='circle'):
    patches=[]
    ex, ey, ez = earth.at(t).ecliptic_position().au

    if showMoon:
        mx, my, mz = moon.at(t).ecliptic_position().au
        
        # Move the moon farther away from earth (50x scale)
        mx = ex + earth_moon_scale * (mx - ex)
        my = ey + earth_moon_scale * (my - ey)
        
        # Moon is approx 1/4 radius of Earth
        moon_obj = mpatches.Circle((mx, my), rad / 4, color='w')
        patches.append(ax.add_patch(moon_obj))

    if patch == 'circle':
        earth_obj = mpatches.Circle((ex, ey), rad, color=color)
    elif patch == 'line':
        earth_obj = mpatches.ConnectionPatch((0,0),(ex,ey), "data", color=color, linewidth=rad)

    patches.append(ax.add_patch(earth_obj))
    return patches

def setup_bg():
    # Plot lines for calendar
    for i in range(1,13):
        col=(0, 1, 0, i / 12) #(r, g, b, a)
        radius=.5
        # 20th of each month is close to equinox/solstice
        addEarth(ts.utc(year,i,20), radius, color=col, patch='line')

    sun_obj = mpatches.Circle((0,0), sun_rad, color='y')
    ax.add_patch(sun_obj)

    ax.axis('equal')
    #ax.autoscale()
    ax.set_ylim(-1.3,1.3)

def init():
    return []

def animate(i):
    return addEarth(ts.tt(jd=t.tt + i), earth_rad, showMoon=True)

setup_bg()
# Draw earth and moon position now
animate(0)

# to animate:
ani = animation.FuncAnimation(fig, animate, range(0, 365), init_func=init, blit=True)

#plt.show()
mpld3.show()
