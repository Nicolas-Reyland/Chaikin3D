#!/usr/bin/env python3
from polyhedron import Polyhedron
from wavefront_reader import WaveFrontReader
from arg_utils import gen_arg_parser, read_args
import plotting


# Main function
def main():
    """Main function"""

    arg_parser = gen_arg_parser()
    # a : command-line arguments
    a = read_args(arg_parser)

    # create a renderer
    Renderer = a.renderer_class
    renderer = Renderer()

    # input file
    if a.input:
        reader = WaveFrontReader(a.input, True, a.rotate_mesh, a.verbose)
        poly = reader.to_polyhedron()

    # evaluate
    if a.evaluate:
        raise NotImplementedError("You should not use this option. It has been disabled.")
        # evaluate the code
        compiled_evaluation_string = compile(
            a.evaluate, "evaluation_string", mode="exec"
        )
        exec(compiled_evaluation_string)
        del compiled_evaluation_string
        # checks on the "poly" variable
        if "poly" not in vars():
            raise Exception(
                'You have to define a variable named "poly" in your evaluation string, when not giving an input file'
            )
        if type(poly) != Polyhedron:
            raise TypeError('The "poly" variable does not have the type "Polyhedron"')

    # do we have a polyhedron
    if not a.input and not a.evaluate:
        raise Exception(
            'You have to give a polyhedron! Either through the "-i", "-e" or both options! (see README)'
        )

    # do chaikin generations before any graphics ?
    if a.plot != "evolution" and a.plot != "animation":
        assert (
            a["chaikin generations"] >= 0
        ), f"Number of generations must be positive ({a.chaikin_generations} >= 0)"
        for _ in range(a.chaikin_generations):
            print(" - 3D Chaikin -")
            poly = poly.Chaikin3D(a.chaikin_coef, a.verbose)
            print("Chaikin done")

    # switch the plot type
    if a.plot == "simple":
        poly_dd = renderer.get_polyhedron_draw_data(
            poly, type_="any", alpha=a.alpha, color=a.polygon_color
        )
        if a.show_main_connections:
            main_conn_dd = renderer.get_connections_draw_data(
                poly,
                type_="main",
                line_color=a.main_connection_color,
                node_color=a.node_color,
            )
        else:
            main_conn_dd = list()
        if a.show_graphical_connections:
            graphical_conn_dd = renderer.get_connections_draw_data(
                poly,
                type_="graphical",
                line_color=a.graphical_connection_color,
                node_color=a.node_color,
            )
        else:
            graphical_conn_dd = list()
        renderer.draw(poly_dd + graphical_conn_dd + main_conn_dd)
    elif a.plot == "full":
        plotting.draw_full(renderer, poly, a)
    elif a.plot == "evolution":
        plotting.draw_chaikin_evolution(renderer, poly, a)
    elif plot == "animation":
        plotting.chaikin_animation(renderer, poly, a)
    else:
        raise ValueError(f'Unrecognized plot type "{a.plot}"')


if __name__ == "__main__":
    main()
