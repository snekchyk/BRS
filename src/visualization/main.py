import ctypes
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import sys

#Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
#Get dll file path
dll_path = os.path.join(current_dir, '..', 'simulation', 'simulation.dll')
#Load compiled C library into Python's memory. To be able to ue that.
lib = ctypes.CDLL(dll_path)

# Create a shorthand for a C-style pointer to a double
ptr_double = ctypes.POINTER(ctypes.c_double)
# Specify input types (7 doubles) and output types (11 double pointers) for the C function
lib.run_simulation.argtypes = [
    ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,

    ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double), ctypes.POINTER(ptr_double)
]

# Specify the function's return type as a C integer
lib.run_simulation.restype = ctypes.c_int

print("  ---  Hello  ---  ")

# Promt the user to input simulation parametres and parse them as float
try:
    x_inp = float(input("Enter initial x coordinate (m): "))
    y_inp = float(input("Enter initial y coordinate (m): "))
    angle_inp = float(input("Enter angle (degree): "))
    dry_m_inp = float(input("Enter dry mass (kg): "))
    thrust_inp = float(input("Enter thrust (N): "))
    burn_rate_inp = float(input("Enter burn rate (kg/s): "))
    fuel_inp = float(input("Enter fuel (kg): "))
except:
    print("Error. Please enter valid values.")
    sys.exit(1)

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

ptrs = lib.run_simulation(
    x_inp, y_inp, angle_inp, dry_m_inp, thrust_inp, burn_rate_inp, fuel_inp,
    ctypes.byref(t_ptr), ctypes.byref(x_ptr), ctypes.byref(y_ptr),
    ctypes.byref(vx_ptr), ctypes.byref(vy_ptr), ctypes.byref(ax_ptr),
    ctypes.byref(ay_ptr), ctypes.byref(Ep_ptr), ctypes.byref(Ek_ptr),
    ctypes.byref(m_ptr), ctypes.byref(fuel_ptr)
)

if ptrs <= 0:
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
    
    dt = t[1] - t[0] if len(t) > 1 else 0.01
    speed_multiplier = 1.0
    target_frames = 300
    k = max(1, len(x) // target_frames)
    animation_interval = max(1, int((k * dt * 1000) / speed_multiplier))

    #Stylization and creating first window
    plt.style.use("dark_background")
    fig, axis = plt.subplots(facecolor="black")
    axis.set_xlim([min(x), max(x)])
    axis.set_ylim([min(y), max(y)])
    axis.plot(x[::k], y[::k], color='#1e293b', linewidth=2, label='Full Trajectory', zorder=1)
    animated_plot, = axis.plot([], [], color='#3e83ab', linewidth=3, label='Active path', zorder=2)
    animated_point, = axis.plot([], [], color="red", marker="o", label="Head", zorder=3)
    axis.grid(linestyle='dashed', color='#64748b')
    axis.set_facecolor("#0B132B")
    axis.set_title("Ballistic Missile Trajectory Animation", fontsize=16, color='#3e83ab')
    axis.set_xlabel("X Distance (m)", fontsize=12, color="gray")
    axis.set_ylabel("Y Altitude (m)", fontsize=12, color="gray")
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
        verticalalignment='top', horizontalalignment='left'
    )

    #Stylization and creating second window
    fig2, axs = plt.subplots(2, 2, figsize=(12, 8), facecolor="black")
    fig2.suptitle("Graphics", color='#3e83ab')

    line_speed, = axs[0, 0].plot([], [], color='cyan', linewidth=2)
    axs[0, 0].set_title("Velocity over time", color="white")

    line_alt, = axs[0, 1].plot([], [], color='lime')
    axs[0, 1].set_title("Altitude over time", color="white")

    line_ax, = axs[1, 0].plot([], [], color='orange', label='AX')
    line_ay, = axs[1, 0].plot([], [], color='red', label='AY')
    axs[1, 0].set_title("Acceleration over time", color="white")

    line_Ek, = axs[1, 1].plot([], [], color="magenta", linewidth=2, label="Kinetic Energy [Ek]")
    line_Ep, = axs[1, 1].plot([], [], color="blue", linewidth=2, label="Potential Energy [Ep]")
    line_Etot, = axs[1, 1].plot([], [], color="yellow", linewidth=2, label="Total Energy[E]")
    axs[1, 1].set_title("Energy over time", color="white")


    for a in axs.flat:
        a.set_facecolor("#0B132B")
        a.grid(color='gray')
        a.tick_params(colors='white')
        for spine in a.spines.values():
            spine.set_color("#1e293b")
            spine.set_linewidth(1.5)
        a.set_xlabel("Time (s)", color='gray')

    axs[1, 0].legend(facecolor='#0f172a', edgecolor='#334155', labelcolor='white')
    axs[1, 1].legend(facecolor='#0f172a', edgecolor='#334155', labelcolor='white')
    total_E = Ek + Ep


    #Updating

    speed_arr = np.sqrt(vx * vx + vy * vy)

    def update(frame):

        idx = min(frame, len(x) - 1)

        animated_plot.set_data(x[:idx + 1:k], y[:idx + 1:k])
        animated_point.set_data([x[idx]], [y[idx]])
        current_time = t[idx] if idx < len(t) else t[-1]
        
        curr_speed = speed_arr[idx]
        telemetry_box.set_text(
            f"TIME: {current_time:6.2f} s\n"
            f"X:      {x[idx]:8.2f} m\n"
            f"Y:      {y[idx]:8.2f} m\n"
            f"Velocity: {curr_speed:8.2f} m/s\n"
            f"VX:   {vx[idx]:8.2f} m/s\n"
            f"VY:   {vy[idx]:8.2f} m/s\n"
            f"AX:   {ax[idx]:8.2f} m/s²\n"
            f"AY:   {ay[idx]:8.2f} m/s²\n"
            f"Ep:   {Ep[idx]:8.0f} J\n"
            f"Ek:   {Ek[idx]:8.0f} J\n"
            f"M:    {m[idx]:8.2f} kg\n"
            f"FUEL: {fuel[idx]:8.2f} kg"
        )

        line_speed.set_data(t[:idx+1], speed_arr[:idx+1])
        line_alt.set_data(t[:idx+1], y[:idx+1])
        line_ax.set_data(t[:idx+1], ax[:idx+1])
        line_ay.set_data(t[:idx+1], ay[:idx+1])
        line_Ek.set_data(t[:idx+1], Ek[:idx+1])
        line_Ep.set_data(t[:idx+1], Ep[:idx+1])
        line_Etot.set_data(t[:idx+1], total_E[:idx+1])

        for a in axs.flat:
            a.relim()
            a.autoscale_view()

        fig2.canvas.draw_idle()

        return animated_plot, animated_point, telemetry_box, line_speed, line_alt, line_ax, line_ay, line_Ek, line_Ep, line_Etot

    frame_indices = list(range(0, len(x), k))
    if frame_indices[-1] != len(x) - 1:
        frame_indices.append(len(x) - 1)

    animation = FuncAnimation(
        fig=fig,
        func=update,
        frames=frame_indices,
        interval=animation_interval,
        blit=False,
        repeat=False
    )

    plt.show()


#Cleaning memory
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