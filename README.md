# 🛸 3D Multi-Drone Trajectory Visualization in a Maze Environment

This project visualizes the 3D trajectories of multiple drones navigating through a maze using animated matplotlib 3D plots. It parses trajectory data from a CSV file and animates the motion of each drone with spinning propellers, trail history, and dynamic camera views.

![Drone Animation](drone_6view_transition.gif)

---

## 📁 Files Included

- `main.py` – Main Python script for loading data, rendering drones and maze, and generating the animation.
- `traj_eval_Ours.csv` – CSV file containing multi-agent trajectory data. Each row represents a drone’s `(x, y, z)` position at a timestep.
- `drone_6view_transition.mp4` – A sample output video showing the animated simulation with view transitions.
- `README.md` – Project documentation.

---

## 📌 Features

- 🧠 Intelligent camera view interpolation and motion (Top, Bottom, Front views).
- 🧭 Accurate rendering of drone positions with spinning rotors.
- 🟫 3D maze environment with obstacle rendering.
- ✈️ Smooth trails to visualize historical paths.
- 🎥 FFmpeg-powered animation export to `.mp4` or `.gif`.

---

## 🧪 Dependencies

Install the required Python libraries:

```bash
pip install pandas matplotlib numpy

# On Ubuntu/Debian:
sudo apt install ffmpeg
# Or via Homebrew on macOS:
brew install ffmpeg

The input CSV file must contain the following columns:

timestep	agent_id	x	y	z

Each row corresponds to one drone's position at a specific timestep.

Run the script to visualize and save the animation:

bash

python drone_visualizer.py
By default, it reads traj_eval_Ours.csv, renders the drones in a 3D maze, and saves an animation to drone_6view_transition.mp4.

You can also uncomment the GIF saving line for a lightweight animation output.

📊 Customization
Maze Layout: Edit the MAZE_OBSTACLES list to modify maze wall positions.

Drone Appearance: Adjust constants like DRONE_SIZE, ARM_LENGTH, and PROPELLER_SIZE to change how drones are rendered.

View Transitions: Customize view_sequence for different camera angle transitions.