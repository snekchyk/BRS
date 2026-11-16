import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import ctypes
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(current_dir, '..', 'simulation', 'simulation.dll')

lib = ctypes.CDLL(dll_path)

ptr_double = ctypes.POINTER(ctypes.c_double)
lib.run_simulation.argtypes = [
    ctypes.c_double, ctypes.c_double, ctypes.c_double, 
    ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
    ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), 
    ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), 
    ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), 
    ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double)
]

lib.run_simulation.restype = ctypes.c_int

t_ptr = ptr_double()
x_ptr = ptr_double()
y_ptr = ptr_double()

vx_ptr = ptr_double()
vy_ptr = ptr_double()
ax_ptr = ptr_double()
ay_ptr = ptr_double()
Ep_ptr = ptr_double()
Ek_ptr = ptr_double()
m_ptr = ptr_double()
fuel_ptr = ptr_double()

ptrs = lib.run_simulation(0.0, 0.0, 60.0, 500.0, 20000.0, 50.0, 500.0, ctypes.byref(t_ptr), ctypes.byref(x_ptr), ctypes.byref(y_ptr), ctypes.byref(vx_ptr), ctypes.byref(vy_ptr), ctypes.byref(ax_ptr), ctypes.byref(ay_ptr), ctypes.byref(Ep_ptr), ctypes.byref(Ek_ptr), ctypes.byref(m_ptr), ctypes.byref(fuel_ptr))


if (ptrs <= 0):
    print("Error")
else:
    print("Success")

    t = np.ctypeslib.as_array(t_ptr, shape=(ptrs,))
    x = np.ctypeslib.as_array(x_ptr, shape=(ptrs,))
    y = np.ctypeslib.as_array(y_ptr, shape=(ptrs,))
    vx = np.ctypeslib.as_array(vx_ptr, shape=(ptrs,))
    vy = np.ctypeslib.as_array(vy_ptr, shape=(ptrs,))
    ax = np.ctypeslib.as_array(ax_ptr, shape=(ptrs,))
    ay = np.ctypeslib.as_array(ay_ptr, shape=(ptrs,))
    Ep = np.ctypeslib.as_array(Ep_ptr, shape=(ptrs,))
    Ek = np.ctypeslib.as_array(Ek_ptr, shape=(ptrs,))
    m = np.ctypeslib.as_array(m_ptr, shape=(ptrs,))
    fuel = np.ctypeslib.as_array(fuel_ptr, shape=(ptrs,))

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
        verticalalignment='top', horizontalalignment='left',
        bbox=dict(facecolor='#0f172a', alpha=0.9, edgecolor='#334155', boxstyle='round,pad=0.5')
    )
    def update(frame):
        animated_plot.set_data(x[:frame], y[:frame])
        animated_point.set_data([x[frame]], [y[frame]])
        current_time = t[frame] if frame < len(t) else t[-1]
        
        speed = np.sqrt(vx[frame]**2 + vy[frame]**2)
        telemetry_box.set_text(
            f"TIME: {current_time:6.2f} s\n"
            f"X:          {x[frame]:8.2f} m\n"
            f"Y:          {y[frame]:8.2f} m\n"
            f"Velocity: {speed:8.2f} m/s\n"
            f"VX:   {vx[frame]:8.2f} m/s\n"
            f"VY:   {vy[frame]:8.2f} m/s\n"
            f"AX:   {ax[frame]:8.2f} m/s²\n"
            f"AY:   {ay[frame]:8.2f} m/s²\n"
            f"Ep:   {Ep[frame]:8.0f} J\n"
            f"Ek:   {Ek[frame]:8.0f} J\n"
            f"M:    {m[frame]:8.2f} kg\n"
            f"FUEL: {fuel[frame]:8.2f} kg"
        )
        return animated_plot, animated_point,
    dt = int((t[1] - t[0]) * 1000)
    animation = FuncAnimation(fig=fig, func=update, frames=len(x), interval=dt)

    plt.show()

print("Cleaning up memory...")
lib.free_memory(t_ptr)
lib.free_memory(x_ptr)
lib.free_memory(y_ptr)
lib.free_memory(vx_ptr)
lib.free_memory(vy_ptr)
lib.free_memory(ax_ptr)
lib.free_memory(ay_ptr)
lib.free_memory(Ep_ptr)
lib.free_memory(Ek_ptr)
lib.free_memory(m_ptr)
lib.free_memory(fuel_ptr)
print("Memory cleaned. Done!")