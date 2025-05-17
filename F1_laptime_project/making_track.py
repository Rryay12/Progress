import matplotlib.pyplot as plt

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
    elif event.key == 'r':
        points.clear()
        line.set_data([], [])
        fig.canvas.draw()
        print("Points reset.")

fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('key_press_event', on_key)

plt.show()
