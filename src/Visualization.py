# Neue Visualization Klasse
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from Constants import MOON_START_X


def _scale_radius(real_radius, mode, size_factor):
    if mode == "linear":
        return float(real_radius * size_factor)
    elif mode == "sqrt":
        return float(np.sqrt(real_radius) * size_factor)
    else:
        raise ValueError(f"Unknown mode: {mode}")


def axis_limits(bodies_at_frame, pad=0.05):
    # only x, y for all frames so we have fixed axis
    view_limit = 6e8 # roughly 1.5 of the moons radius
    all_positions = np.array([body["position"][:2]
                              for frame in bodies_at_frame for body in frame])
    x_min = max(np.min(all_positions[:, 0]), -view_limit)
    x_max = min(np.max(all_positions[:, 0]),  view_limit)
    y_min = max(np.min(all_positions[:, 1]), -view_limit)
    y_max = min(np.max(all_positions[:, 1]), view_limit)

    span_x = x_max - x_min
    span_y = y_max - y_min
    # logic for when one or two axis are two small
    if span_x == 0 and span_y == 0:
        span_x = span_y = 1.0
    elif span_x == 0:
        span_x = span_y
    elif span_y == 0:
        span_y = span_x

    # add some padding relative to the size of the axis
    px, py = span_x * pad, span_y * pad

    return x_min - px, x_max + px, y_min - py, y_max + py


class Visualization:

    def __init__(self):
        self.fig = None
        self.ax = None
        self.anim = None
        self._circles = []
        self._time_text = None
        self._limits = None
        self._collisions = []
        self._hit_marker = None

    def data_adapter(self, history):
        # histroy in dict format
        timestamps = np.array([snap["t"] for snap in history])
        bodies_at_frame = [snap["bodies"] for snap in history]
        return timestamps, bodies_at_frame

    def _setup(self, bodies_at_frame):
        self.ax.clear()

        x_min, x_max, y_min, y_max = self._limits
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_aspect("equal")

        # create so many circles for the max number of bodies at any frame
        n_max = max(len(frame) for frame in bodies_at_frame)
        self._circles = []
        for _ in range(n_max):
            c = plt.Circle((0, 0), 0.0, color="blue", fill=True, animated=True)
            self.ax.add_patch(c)
            self._circles.append(c)

        # find collisions independent of the names
        self._collisions = self.find_collisions(bodies_at_frame)
        self._hit_marker, = self.ax.plot([], [], marker="X", color="red",
                                          markersize=12, linestyle="None", animated=True)

        self._time_text = self.ax.text(0.02, 0.98, "", transform=self.ax.transAxes,
                                  ha="left", va="top", animated=True)

        return self._circles + [self._time_text, self._hit_marker]

    def draw_frame(self, frame_index, timestamps, bodies_at_frame, size_factor):
        bodies = bodies_at_frame[frame_index]
        n = len(bodies)
        for i, circle in enumerate(self._circles):
            # activ body
            if i < n:
                body = bodies[i]
                circle.center = (body["position"][0], body["position"][1])
                colors = {"Earth": "blue", "Moon": "gray", "Projectile": "black"}
                circle.set_color(colors.get(body["name"], "blue"))
                min_r = (self._limits[1] - self._limits[0]) * 0.01  # 1% of axis-width
                circle.set_radius(max(min_r, _scale_radius(body["radius"], mode="sqrt", size_factor=size_factor)))
                circle.set_visible(True)
            else:
                # just hide the body instead of deleting it
                circle.set_visible(False)

        self._time_text.set_text(f"t = {timestamps[frame_index]:.2f}")

        self.update_hit_marker(frame_index)
        return self._circles + [self._time_text,self._hit_marker]

    def animate(self, history, size_factor = 15000.0, interval = 20, step = None):
        timestamps, bodies_at_frame = self.data_adapter(history)
        # set the limits only once
        self._limits = axis_limits(bodies_at_frame)

        if step is None:
            step = self.auto_step(len(bodies_at_frame))

        if self.fig is None:
            self.fig, self.ax = plt.subplots()

        if self.anim is not None and self.anim.event_source is not None:
            # stops the current running animation
            self.anim.event_source.stop()

        artists = self._setup(bodies_at_frame)


        # frames = range(0, len(bodies_at_frame), step)
        self.anim = FuncAnimation(
            self.fig,
            self.draw_frame,
            frames = range(0, len(bodies_at_frame), step),
            fargs = (timestamps, bodies_at_frame, size_factor),
            init_func = lambda: artists,
            interval = interval,
            blit = True,
            cache_frame_data = False,
        )

        self.fig.canvas.draw_idle()
        return self.anim

    #subsampling
    def auto_step(self, n_frames , target_frames=300):
        return max(1, n_frames // target_frames)


    def find_collisions(self, bodies_at_frame):
        # a collision = names vanish between two frames
        # returns (frame_indes, (x, y)) at the collision

        events = []
        for i in range (1, len(bodies_at_frame)):
            prev_names = {b["name"] for b in bodies_at_frame[i - 1]}
            cur_names = {b["name"] for b in bodies_at_frame[i]}

            vanished = prev_names - cur_names
            if not vanished:
                continue

            appeared = cur_names - prev_names
            if appeared:
                pts = [(b["position"][0], b["position"][1])
                       for b in bodies_at_frame[i] if b["name"] in appeared]
            else:
                pts = [(b["position"][0], b["position"][1])
                       for b in bodies_at_frame[i - 1] if b["name"] in vanished]

            x = float(np.mean([p[0] for p in pts]))
            y = float(np.mean([p[1] for p in pts]))
            events.append((i, (x, y)))
        return events


    def update_hit_marker(self, frame_index):
        # show all collisions until this time
        xs = [pos[0] for (f, pos) in self._collisions if f <= frame_index]
        ys = [pos[1] for (f, pos) in self._collisions if f <= frame_index]
        self._hit_marker.set_data(xs, ys)
        return self._hit_marker