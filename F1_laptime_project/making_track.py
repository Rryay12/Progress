import matplotlib.pyplot as plt
import math

import pygame

def generate_track(centerline, width=100):
    inner = []
    outer = []
    n = len(centerline)
    for i in range(n):
        p1 = centerline[i - 1]
        p2 = centerline[i]
        p3 = centerline[(i + 1) % n]

        # Calculate the direction between p1 and p3 (smoothed)
        dx = p3[0] - p1[0]
        dy = p3[1] - p1[1]
        length = math.hypot(dx, dy)
        if length == 0:
            perp_dx, perp_dy = 0, 0
        else:
            perp_dx = -dy / length
            perp_dy = dx / length

        offset_x = perp_dx * width / 2
        offset_y = perp_dy * width / 2

        inner.append((p2[0] - offset_x, p2[1] - offset_y))
        outer.append((p2[0] + offset_x, p2[1] + offset_y))
    
    return inner, outer

class RaceTrack:
    def __init__(self,inner_points,outer_points):
        self.inner_points = inner_points
        self.outer_points = outer_points
        
        self.track_color = (50,50,50)
        self.border_color = (255,90,90)
        self.inner_color = (255,255,255)
    
    def plot_track(self,surface):
        pygame.draw.polygon(surface,self.track_color,self.outer_points,0)
        pygame.draw.polygon(surface,self.inner_color,self.inner_points,0)
        pygame.draw.lines(surface,self.border_color,True,self.inner_points,5)
        pygame.draw.lines(surface,self.border_color,True,self.outer_points,5)


def plot_track(pts):
    pygame.init()
    inner,outer = generate_track(pts)
    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900
        
    track = RaceTrack(inner,outer)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    track.plot_track(screen)
    pygame.display.update()
    input("end?")
    

points = []

fig, ax = plt.subplots()
ax.set_xlim(100, 1500)
ax.set_ylim(100, 800)
ax.set_title('Click to add points. Press Enter to finish, "r" to reset.')

line, = ax.plot([], [], marker='o', linestyle='-', color='b')

def on_click(event):
    if event.inaxes != ax:
        return
    x, y = event.xdata, event.ydata
    points.append((x, y))
    xs, ys = zip(*points)
    line.set_data(xs, ys)
    fig.canvas.draw()

def on_key(event):
    if event.key == 'enter':
        print("Points:")
        for p in points:
            print(f"({p[0]:.1f}, {p[1]:.1f}),")
        plt.close()
        plot_track(points)
        
    elif event.key == 'r':
        points.clear()
        line.set_data([], [])
        fig.canvas.draw()
        print("Points reset.")

fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('key_press_event', on_key)

plt.show()
