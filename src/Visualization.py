# Neue Visualization Klasse
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation


def _scale_radius(real_radius, mode, factor = 10000.0):
    if mode == "linear":
        return float(real_radius * factor)
    elif mode == "sqrt":
        return float(np.sqrt(real_radius) * factor)
    else:
        raise ValueError(f"Unknown mode: {mode}")


def axis_limits(bodies_at_frame):
    all_positions = np.array([body.position for frame in bodies_at_frame for body in frame])
    x_min, y_min = np.min(all_positions, axis=0)
    x_max, y_max = np.max(all_positions, axis=0)
    return x_min, x_max, y_min, y_max


class Visualization:

    def data_adapter(self, history):
        n_frames = len(history)
        # Liste an t-Werte an den frames i
        timestamps = np.array([history[i][0] for i in range(n_frames)])
        # Liste an Körpers an den frames i  (Liste statt np.array: Anzahl variiert pro Frame)
        bodies_at_frame = [history[i][1] for i in range(n_frames)]
        return timestamps, bodies_at_frame

    def _setup(self, ax, bodies_at_frame):
        # Achsen EINMALIG konfigurieren
        x_min, x_max, y_min, y_max = self._limits
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_aspect("equal")

        # so viele Circles anlegen wie max. Koerper in irgendeinem Frame
        n_max = max(len(frame) for frame in bodies_at_frame)
        self._circles = []
        for _ in range(n_max):
            c = plt.Circle((0, 0), 0.0, color="blue", fill=True, animated=True)
            ax.add_patch(c)
            self._circles.append(c)


        self._hit_frame = self.find_hit_frame(bodies_at_frame, "Projectile")
        self._hit_position = self.find_hit_position(bodies_at_frame, "Projectile")
        self._hit_marker, = ax.plot([], [], marker="X", color="red",
                                    markersize=12, linestyle="None", animated=True)
        self._hit_marker.set_visible(False)

        self._time_text = ax.text(0.02, 0.98, "", transform=ax.transAxes,
                                  ha="left", va="top", animated=True)

        return self._circles + [self._time_text,self._hit_marker]

    def draw_frame(self, frame_index, timestamps, bodies_at_frame):
        bodies = bodies_at_frame[frame_index]
        n = len(bodies)
        for i, circle in enumerate(self._circles):
            if i < n:                                      # aktiver Koerper
                body = bodies[i]
                circle.center = (body.position[0], body.position[1])
                circle.set_radius(_scale_radius(body.radius, mode="sqrt"))
                circle.set_visible(True)
            else:                                          # uebrige Circles ausblenden
                circle.set_visible(False)
        self._time_text.set_text(f"t = {timestamps[frame_index]:.2f}")


        self.update_hit_marker(frame_index)
        return self._circles + [self._time_text,self._hit_marker]

    def animate(self, history, interval = 20, step = None):
        timestamps, bodies_at_frame = self.data_adapter(history)
        self._limits = axis_limits(bodies_at_frame)        # nur einmal

        if step is None:
            step = self.auto_step(len(bodies_at_frame))

        fig, ax = plt.subplots()
        artists = self._setup(ax, bodies_at_frame)         # Patches einmal anlegen

        def init():
            return artists

        frames = range(0, len(bodies_at_frame), step)
        anim = FuncAnimation(
            fig,
            self.draw_frame,
            frames = frames,
            fargs = (timestamps, bodies_at_frame),
            init_func = init,
            interval = interval,
            blit = True,
            cache_frame_data = False,
        )

        plt.show()
        return anim







    #subsambling
    def auto_step(self, n_frames , target_frames=300):
        return max(1,n_frames // target_frames)


    #detect hit
    def find_hit_frame(self, bodies_at_frame, projectile_name):

        projectile_was_there = False

        for frame_index in range(len(bodies_at_frame)):
            bodies = bodies_at_frame[frame_index]

            #collect the   names of all bodies in this frame
            names = []
            for body in bodies:
                names.append(body.name)

            if projectile_name in names:
                projectile_was_there = True
            elif projectile_was_there:
                return frame_index
        return None


    def find_hit_position(self, bodies_at_frame, projectile_name):

        hit_frame =  self.find_hit_frame(bodies_at_frame, projectile_name)

        if hit_frame is None:
            return None

    # in hit_frame the projectile is already gone, so look one frame earlier
        last_bodies = bodies_at_frame[hit_frame - 1]
        for body in last_bodies:
            if body.name == projectile_name:
                return (body.position[0], body.position[1])
        return None

    def update_hit_marker(self, frame_index):

        if self._hit_frame is not None and frame_index >= self._hit_frame:
            self._hit_marker.set_data([self._hit_position[0]], [self._hit_position[1]])
            self._hit_marker.set_visible(True)
        return self._hit_marker








