import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import numpy as np
import matplotlib.colors as mcolors
import math
from matplotlib.animation import FuncAnimation


# === CONFIGURATION ===
CSV_FILE = "traj_eval_Ours.csv"
MAZE_OBSTACLES = [  # (x1, y1, x2, y2)
    (3, 3, 6, 4), (3, 4, 4, 16), (3, 17, 6, 16),
    (8, 7, 12, 8), (8, 13, 12, 12),
    (11, 3, 12, 8), (11, 17, 12, 12),
    (10, 3, 17, 4), (10, 17, 17, 16),
    (14, 9, 16, 11), (16, 7, 17, 13)
]

DRONE_SIZE = 30
ARM_LENGTH = 0.3
PROPELLER_SIZE = 10
BODY_RADIUS = 0.2

# === LOAD TRAJECTORY DATA ===
df = pd.read_csv(CSV_FILE)
NUM_DRONES = df["agent_id"].nunique()
TIMESTEPS = df["timestep"].max() + 1
# === TRAIL HISTORY ===
trail_history = [ [] for _ in range(NUM_DRONES) ]


# Shape: (T, N, 3)
trajectories = np.zeros((TIMESTEPS, NUM_DRONES, 3))
for t in range(TIMESTEPS):
    timestep_data = df[df["timestep"] == t]
    for _, row in timestep_data.iterrows():
        trajectories[int(row["timestep"]), int(row["agent_id"])] = [row["x"], row["y"], row["z"]]

goals = trajectories[-1]  # final positions

# === DRONE COLORS ===
colors = list(mcolors.TABLEAU_COLORS.values())
while len(colors) < NUM_DRONES:
    colors += colors
colors = colors[:NUM_DRONES]

# === VISUALIZATION SETUP ===
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim(0, 20)
ax.set_ylim(0, 20)
ax.set_zlim(0, 6)
ax.set_axis_off()

# === MAZE DRAWING ===
def draw_maze(ax):
    for x1, y1, x2, y2 in MAZE_OBSTACLES:
        xs, ys = np.meshgrid([x1, x2], [y1, y2])
        zs = np.ones_like(xs)
        ax.plot_surface(xs, ys, zs * 0, alpha=0.8, color="burlywood")
        ax.plot_surface(xs, ys, zs * 6, alpha=0.8, color="burlywood")
        xs, zs = np.meshgrid([x1, x2], [0, 6])
        ax.plot_surface(xs, ys[0]*np.ones_like(xs), zs, alpha=0.8, color="burlywood")
        ax.plot_surface(xs, ys[1]*np.ones_like(xs), zs, alpha=0.8, color="burlywood")
        ys, zs = np.meshgrid([y1, y2], [0, 6])
        ax.plot_surface(xs[0]*np.ones_like(ys), ys, zs, alpha=0.8, color="burlywood")
        ax.plot_surface(xs[1]*np.ones_like(ys), ys, zs, alpha=0.8, color="burlywood")

# === DRONE DRAWING === rotors sphere
# def draw_drone(ax, pos, color):
#     x, y, z = pos

#     # Body
#     ax.scatter(x, y, z, color=color, s=DRONE_SIZE, edgecolors='black')

#     # Arms and Propellers
#     for dx, dy in [(-ARM_LENGTH, -ARM_LENGTH), (ARM_LENGTH, -ARM_LENGTH),
#                    (-ARM_LENGTH, ARM_LENGTH), (ARM_LENGTH, ARM_LENGTH)]:
#         x_arm = [x, x + dx]
#         y_arm = [y, y + dy]
#         z_arm = [z, z]
#         ax.plot(x_arm, y_arm, z_arm, color=color, linewidth=1)
#         ax.scatter(x + dx, y + dy, z, s=PROPELLER_SIZE, color=color, marker='o')

#  rotors cross fixed
# def draw_drone(ax, pos, color): 
#     x, y, z = pos

#     # Draw the main body
#     ax.scatter(x, y, z, color=color, s=DRONE_SIZE, edgecolors='black', zorder=10)

#     # Fixed rotor arm offsets from center (flat on xy-plane)
#     rotor_offsets = np.array([
#         [-ARM_LENGTH, -ARM_LENGTH],
#         [ ARM_LENGTH, -ARM_LENGTH],
#         [-ARM_LENGTH,  ARM_LENGTH],
#         [ ARM_LENGTH,  ARM_LENGTH]
#     ])

#     for dx, dy in rotor_offsets:
#         # Rotor position (absolute)
#         rotor_x = x + dx
#         rotor_y = y + dy
#         rotor_z = z

#         # Draw arm
#         ax.plot([x, rotor_x], [y, rotor_y], [z, rotor_z], color=color, linewidth=1.5)

#         # Draw cross blades for rotor (two short perpendicular lines)
#         blade_length = 0.3

#         # Blade 1 (x-direction)
#         ax.plot(
#             [rotor_x - blade_length / 2, rotor_x + blade_length / 2],
#             [rotor_y, rotor_y],
#             [rotor_z, rotor_z],
#             color='black',
#             linewidth=1,
#             alpha=0.9,
#             zorder=5
#         )

#         # Blade 2 (y-direction)
#         ax.plot(
#             [rotor_x, rotor_x],
#             [rotor_y - blade_length / 2, rotor_y + blade_length / 2],
#             [rotor_z, rotor_z],
#             color='black',
#             linewidth=1,
#             alpha=0.9,
#             zorder=5
#         )


def draw_drone(ax, pos, color, frame=0):
    x, y, z = pos
    ax.scatter(x, y, z, color=color, s=DRONE_SIZE, edgecolors='black', zorder=10)

    rotor_offsets = np.array([
        [-ARM_LENGTH, -ARM_LENGTH],
        [ ARM_LENGTH, -ARM_LENGTH],
        [-ARM_LENGTH,  ARM_LENGTH],
        [ ARM_LENGTH,  ARM_LENGTH]
    ])

    blade_length = 0.4
    spin_speed = 0.4  # radians per frame

    for dx, dy in rotor_offsets:
        rotor_x = x + dx
        rotor_y = y + dy
        rotor_z = z

        # Draw fixed arm
        ax.plot([x, rotor_x], [y, rotor_y], [z, rotor_z], color=color, linewidth=1.5)

        # Blade rotation (simulate spinning)
        angle = frame * spin_speed
        cos_a, sin_a = np.cos(angle), np.sin(angle)

        # Blade 1 (rotated X)
        dx1, dy1 = blade_length / 2 * cos_a, blade_length / 2 * sin_a
        ax.plot([rotor_x - dx1, rotor_x + dx1], [rotor_y - dy1, rotor_y + dy1], [rotor_z, rotor_z],
                color='black', linewidth=1, alpha=0.9)

        # Blade 2 (perpendicular)
        dx2, dy2 = -dy1, dx1
        ax.plot([rotor_x - dx2, rotor_x + dx2], [rotor_y - dy2, rotor_y + dy2], [rotor_z, rotor_z],
                color='black', linewidth=1, alpha=0.9)


# === GOAL MARKERS ===
def draw_goals(ax):
    for i in range(NUM_DRONES):
        gx, gy, gz = goals[i]
        ax.scatter(gx, gy, gz, marker='X', color=colors[i], s=50, edgecolors='black')

# Define the 6 key views
# view_sequence = [
#     (90, 0),    # Top
#     (-90, 0),   # Bottom
#     (0, 0),     # Front
#     (0, 180),   # Back
#     (0, 90),    # Left
#     (0, -90)    # Right
# ]
view_sequence = [
    ("Top",    90,   0),
    ("Bottom", -90,  0),
    ("Front",  0,    0),
]

num_views = len(view_sequence)
frames_per_view = TIMESTEPS // num_views


# #  Interpolation function
# def interpolate_view(frame):
#     seg = frame // frames_per_view
#     seg_frame = frame % frames_per_view

#     if seg >= num_views - 1:
#         return view_sequence[-1]  # Hold last view

#     elev1, azim1 = view_sequence[seg]
#     elev2, azim2 = view_sequence[seg + 1]

#     # Linear interpolation between views
#     alpha = seg_frame / frames_per_view
#     elev = elev1 * (1 - alpha) + elev2 * alpha
#     azim = azim1 * (1 - alpha) + azim2 * alpha
#     return elev, azim

def smoothstep(t):
    return 3 * t**2 - 2 * t**3

def interpolate_view(frame):
    seg = frame // frames_per_view
    seg_frame = frame % frames_per_view

    if seg >= num_views - 1:
        return view_sequence[-1]  # Hold last view

    elev1, azim1 = view_sequence[seg]
    elev2, azim2 = view_sequence[seg + 1]

    # Compute smooth interpolation weight
    t = seg_frame / frames_per_view
    alpha = smoothstep(t)

    # Interpolate azimuth/elevation
    elev = elev1 * (1 - alpha) + elev2 * alpha
    azim = azim1 * (1 - alpha) + azim2 * alpha
    return elev, azim


# === ANIMATION FUNCTION ===
def update(frame):
    ax.cla()
    view_index = min(frame // frames_per_view, num_views - 1)
    view_name, base_elev, base_azim = view_sequence[view_index]

    # Slow sin-based perturbation (one full wave per view)
    t = (frame % frames_per_view) / frames_per_view
    sway = np.sin(4 * np.pi * t)  # Range [-1, 1]

    # Apply subtle sway to both elevation and azimuth
    elev = base_elev + sway * 8      # Max ±5° vertical tilt
    azim = base_azim + sway * 8      # Max ±5° horizontal pan
    ax.view_init(elev=elev, azim=azim)


    # Draw 3D title and label in fixed screen coords
    ax.set_title(f"{view_name} View", fontsize=14, weight='bold', pad=20)
    ax.text2D(0.05, 0.95, f"{view_name} View", transform=ax.transAxes,
            fontsize=12, color='black', weight='bold', alpha=0.8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray"))




    ax.set_title(f"{view_name} View", fontsize=12, weight='bold')

    # Apply rotating camera view
    ax.view_init(elev=elev, azim=azim)

    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    ax.set_zlim(0, 6)
    ax.set_axis_off()
    ax.set_title(f"Frame {frame}/{TIMESTEPS}")

    draw_maze(ax)
    draw_goals(ax)

    positions = trajectories[frame]

    for i in range(NUM_DRONES):
        pos = positions[i]
        trail_history[i].append(pos)

        # Draw fading trail
        trail = np.array(trail_history[i])
        if len(trail) > 1:
            for j in range(1, len(trail)):
                alpha = j / len(trail)  # fade from 0.0 (old) to 1.0 (new)
                ax.plot(
                    trail[j-1:j+1, 0],
                    trail[j-1:j+1, 1],
                    trail[j-1:j+1, 2],
                    color=colors[i],
                    alpha=alpha,
                    linewidth=1.5
                )

        # Draw drone
        draw_drone(ax, pos, colors[i], frame)



# === ANIMATE ===
# ani = animation.FuncAnimation(fig, update, frames=TIMESTEPS, interval=30)
ani = animation.FuncAnimation(
    fig,
    update,
    frames=range(0, TIMESTEPS, 2),  # or just TIMESTEPS
    interval=0,
    repeat=False  # <<< THIS stops it from looping
)
ani.save("drone_6view_transition.mp4", writer="ffmpeg", fps=5, dpi=80)
# ani.save("drone_simulation.gif", writer="pillow", fps=20)

plt.show()
