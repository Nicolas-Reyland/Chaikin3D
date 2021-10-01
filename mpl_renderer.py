# Polyhedron rendering
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
from polyhedron import Polyhedron

DO_CHAIKIN = True


def gen_random_color():
    s = "#"
    import random

    choices = "0123456789abcdef"
    for _ in range(6):
        s += random.choice(choices)
    return s


class Renderer:
    def __init__(self):
        self.fig = plt.figure()
        self.ax = Axes3D(
            self.fig,
            (0, 0, 1, 1),  # rect
            proj_type="persp",  # perspective 'persp' || orthogonal 'ortho'
            auto_add_to_figure=False,  # avoid deprecation warning (added manually later on)
            **{"xmargin": 0.5, "ymargin": 0.5, "zmargin": 0.234}
            # the x,y & z margins are not equal because we cannot get propoer scaling in mlp for 3D (known issues)
            # so we rescale here manually, as well as adding a little bit of margin
        )
        # need this or else the margin will break everything (visually)
        self.ax.autoscale()
        # adding manually to the figure
        self.fig.add_axes(self.ax)

    def draw_polyhedron(
        self, polyhedron: Polyhedron, alpha: float = 0.8, draw_text: bool = True
    ):
        for triangle in polyhedron:
            collection = Poly3DCollection(triangle)
            collection.set_edgecolor("#000")
            collection.set_facecolor(gen_random_color())
            collection.set_alpha(alpha)
            collection.set_zsort("average")
            if draw_text:
                for (x, y, z) in triangle:
                    if not DO_CHAIKIN:
                        pos_z = z - 0.05 if z == 0 else z + 0.05
                    else:
                        pos_z = z
                    self.ax.text(
                        x,
                        y,
                        pos_z,
                        "({:.2f}, {:.2f}, {:.2f})".format(x, y, z),
                        (1, 1, 1),
                    )
            self.ax.add_collection3d(collection)
        plt.show()
