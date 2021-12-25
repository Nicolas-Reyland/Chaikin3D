#!/usr/bin/env python3
import sys

sys.path.insert(0, "src/")
from polyhedron import Polyhedron
from wavefront_reader import WaveFrontReader
from arg_utils import gen_arg_parser, read_args
import plotting


def save_poly(poly, figure, output):
    # writing to file
    if not output:
        return
    print(f"Saving file to {output!r}")
    if output.endswith(".obj"):
        with open(output, "w") as f:
            poly.save(f)
    elif output.endswith(".html"):
        assert figure is not None, "Must plot the mesh when saving to html"
        figure.write_html(output)
    else:
        raise ValueError(f'Invalid output: "{output}"')


# Main function
def main():
    """Main function"""

    arg_parser = gen_arg_parser()
    # a : command-line arguments
    a = read_args(arg_parser)

    vprint = print if a.verbose else lambda *args, **kwargs: None

    # create a renderer
    Renderer = a.renderer_class
    renderer = Renderer(verbose=a.verbose)

    # input file
    reader = WaveFrontReader(a.input, True, a.rotate_mesh, a.verbosity)
    poly = reader.to_polyhedron()

    # do chaikin generations before any graphics ?
    if a.plot != "evolution" and a.plot != "animation":
        assert (
            a["chaikin generations"] >= 0
        ), f"Number of generations must be positive ({a.chaikin_generations} >= 0)"
        for _ in range(a.chaikin_generations):
            vprint(" - 3D Chaikin -")
            poly = poly.Chaikin3D(a)
            vprint("Chaikin done")

    # switch the plot type
    if a.plot == "simple":
        poly_dd = renderer.get_polyhedron_draw_data(
            poly, type_="any", alpha=a.alpha, color=a.polygon_color
        )
        if a.show_main_edges:
            main_conn_dd = renderer.get_edges_draw_data(
                poly,
                type_="main",
                line_color=a.main_edge_color,
                node_color=a.node_color,
            )
        else:
            main_conn_dd = list()
        if a.show_graphical_edges:
            graphical_conn_dd = renderer.get_edges_draw_data(
                poly,
                type_="graphical",
                line_color=a.graphical_edge_color,
                node_color=a.node_color,
            )
        else:
            graphical_conn_dd = list()
        fig = renderer.figure(poly_dd + graphical_conn_dd + main_conn_dd)
        save_poly(poly, fig, a.output)
        fig.show()
    elif a.plot == "full":
        fig = plotting.draw_full(renderer, poly, a)
        save_poly(poly, fig, a.output)
    elif a.plot == "evolution":
        fig = plotting.draw_chaikin_evolution(renderer, poly, a)
        save_poly(poly, fig, a.output)
    elif a.plot == "animation":
        plotting.chaikin_animation(renderer, poly, a)
    elif a.plot == "none":
        save_poly(poly, None, a.output)
    else:
        raise ValueError(f'Unrecognized plot type "{a.plot}"')


if __name__ == "__main__":
    main()
