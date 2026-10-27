import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

x = []
y = []
t = []

try:
    with open("src/simulation/trajectory.txt", "r") as file:
        for line in file:
            line = line.strip().split(";")
            if len(line) > 4:
                t.append(float(line[0]))
                x.append(float(line[3]))
                y.append(float(line[4]))
except Exception as e:
    print(f"Error, {e}")

if not x or not y:
    print("Warning: Lists x and y are empty! Check the path to the files.")
else:
    plt.style.use("dark_background")
    fig, axis = plt.subplots(facecolor="black")

    axis.set_xlim([min(x), max(x)])
    axis.set_ylim([min(y), max(y)])

    axis.plot(x, y, color='#1e293b', linewidth=2, label='Full Trajectory', zorder=1)
    animated_plot, = axis.plot([], [], color='#3e83ab', linewidth=3, label='Active path', zorder=2)
    animated_point, = axis.plot([], [], color="red", marker="o", label="Head", zorder=3)

    axis.grid(linestyle='dashed', color='#64748b')


    axis.set_facecolor("#0B132B")

    axis.set_title("Ballistic Missile Trajectory Animation", fontsize=16, color='#3e83ab')

    axis.set_xlabel("X Distance (m)", fontsize=12, color="gray")
    axis.set_ylabel("Y Atitude (m)", fontsize=12, color="gray")

    axis.spines['bottom'].set_color('#1e293b')
    axis.spines['bottom'].set_linewidth(1.5)
    axis.spines['top'].set_color('#1e293b')
    axis.spines['top'].set_linewidth(1.5)
    axis.spines['left'].set_color('#1e293b')
    axis.spines['left'].set_linewidth(1.5)
    axis.spines['right'].set_color('#1e293b')
    axis.spines['right'].set_linewidth(1.5)
    axis.legend(loc='upper right', facecolor='#0f172a', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=10)

    telemetry_box = axis.text(
        0.01, 0.98, '', transform=axis.transAxes, fontsize=10,
        family='monospace', color='#f8fafc',
        verticalalignment='top', horizontalalignment='left',  # Притискаємо до самого кутка
        bbox=dict(facecolor='#0f172a', alpha=0.9, edgecolor='#334155', boxstyle='round,pad=0.5')
    )

    def update(frame):
        animated_plot.set_data(x[:frame], y[:frame])
        animated_point.set_data([x[frame]], [y[frame]])

        current_time = t[frame] if frame < len(t) else t[-1]
        telemetry_box.set_text(
            f"TIME: {current_time:6.2f} s\n"
            f"X:    {x[frame]:8.2f} m\n"
            f"Y:    {y[frame]:8.2f} m"
        )

        return animated_plot, animated_point,

    dt = int((t[1] - t[0]) * 1000)

    animation = FuncAnimation(fig=fig, func=update, frames=len(x), interval=dt)


plt.show()