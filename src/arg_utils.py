from __future__ import annotations
from argparse import ArgumentParser
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ARGS_JSON_FILE_PATH = "default-args.json"


class ArgumentError(Exception):
    """
    Simple class, representing an commandline-argument error.

    """

    pass


def gen_arg_parser() -> ArgumentParser:
    """
    Generate argument parser.

    Generate an ArgumentParser for all Chaikin3D arguments.
    Generally, there is a short and long argument (short: -char, long: --words).

    Returns:
        ArgumentParser instance

    """

    parser = ArgumentParser(
        description="Apply the Chaikin algorithm, expanded to the 3D space"
    )

    # polyhedron
    parser.add_argument("-i", "--input", type=str, help="input file", required=True)
    parser.add_argument(
        "-rm",
        "--rotate-mesh",
        help="Rotate the mesh when loading a file",
        action="store_true",
    )
    # chaikin algorithm
    parser.add_argument(
        "-cg",
        "--chaikin-generations",
        type=int,
        default=0,
        help="number of chaikin generations",
    )
    parser.add_argument(
        "-cc", "--chaikin-coef", type=float, default=4.0, help="Chaikin coefficient"
    )
    parser.add_argument("-v", "--verbose", help="verbose mode", action="store_true")
    parser.add_argument("-vv", "--vverbose", help="very-verbose", action="store_true")
    # what to plot
    parser.add_argument(
        "-r",
        "--renderer",
        type=str,
        default="plotly",
        help='renderer ["plotly", "mpl"]',
    )
    parser.add_argument(
        "-p",
        "--plot",
        type=str,
        default="simple",
        help='plot type ["simple", "full", "evolution", "animation"]',
    )
    parser.add_argument(
        "-hme",
        "--hide-main-edges",
        help='Hide the main edges (for plots: "simple", "full" and "evolution")',
        action="store_true",
    )
    parser.add_argument(
        "-sge",
        "--show-graphical-edges",
        help='Show the graphical edges (for plots: "simple", "full" and "evolution")',
        action="store_true",
    )
    # how to plot
    parser.add_argument(
        "-a",
        "--alpha",
        type=float,
        default=0.8,
        help="Alpha/Opacity value for mesh rendering",
    )
    parser.add_argument(
        "-pc", "--polygon-color", type=str, default="lightblue", help="Polygon color"
    )
    parser.add_argument(
        "-nc", "--node-color", type=str, default="green", help="Node color"
    )
    parser.add_argument(
        "-mec",
        "--main-edge-color",
        type=str,
        default="darkred",
        help="Main edge color",
    )
    parser.add_argument(
        "-gec",
        "--graphical-edge-color",
        type=str,
        default="black",
        help="Graphical edge",
    )

    return parser


def read_args(arg_parser: ArgumentParser) -> dict[str, str | bool]:
    """
    Read and parse the command-line arguments.

    Args:
        arg_parser (ArgumentParser): Argument parser.

    Returns:
        A:
            Instance of class 'A', created inside this function.
            You can access the elements of this class by variable name or by using
            bracket notation (value = a["key"]).
            The keys are the command line arguments (spaces are used instead of '-'/'_').

    Raises:
        ArgumentError: The specified renderer is not known

    """

    # parse the command line arguments
    args = vars(arg_parser.parse_args())
    args = dict(
        map(
            lambda kvpair: (kvpair[0].replace("_", " ").replace("-", " "), kvpair[1]),
            args.items(),
        )
    )

    # add 'show-main-edges' value, based on 'hide-main-edges'
    args["show main edges"] = not args["hide main edges"]
    # manual verbosity inheritance
    if args["vverbose"]:
        args["verbose"] = True

    # renderer
    if args["renderer"] == "plotly":
        from plotly_renderer import Renderer
    elif args["renderer"] == "mpl":
        from mpl_renderer import Renderer
    else:
        raise ArgumentError(f'Unkown renderer: {args["renderer"]}')
    args["renderer class"] = Renderer

    A = type(
        "A",
        (),
        dict((k.replace(" ", "_"), v) for k, v in args.items())
        | {"__getitem__": lambda self, value: args[value]},
    )
    return A()
