from __future__ import annotations
from argparse import ArgumentParser
import json
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
        description="Apply the Chaikin algorithm, expanded for the 3D space"
    )

    # polyhedron
    parser.add_argument("-i", "--input", type=str, help="input file (df. None)")
    parser.add_argument(
        "-e",
        "--evaluate",
        type=str,
        help='python str to evaluate right after the loading phase (df. "")',
    )
    parser.add_argument(
        "-rm",
        "--rotate-mesh",
        type=str,
        help="Rotate the mesh when loading a file (df. false)",
    )
    # chaikin algorithm
    parser.add_argument(
        "-cg",
        "--chaikin-generations",
        type=int,
        help="number of chaikin generations (df. 0)",
    )
    parser.add_argument(
        "-cc", "--chaikin-coef", type=float, help="Chaikin coefficient (df. 4)"
    )
    parser.add_argument(
        "-v", "--verbose", type=str, help="verbose (boolean) (df. false)"
    )
    # what to plot
    parser.add_argument(
        "-r", "--renderer", type=str, help='renderer ["plotly", "mpl"] (df. plotly)'
    )
    parser.add_argument(
        "-p",
        "--plot",
        type=str,
        help='plot type ["simple", "full", "evolution", "animation"] (df. simple)',
    )
    parser.add_argument(
        "-smc",
        "--show-main-connections",
        type=str,
        help='Show the main connections (for plots: "simple", "full" and "evolution") (df. true)',
    )
    parser.add_argument(
        "-sgc",
        "--show-graphical-connections",
        type=str,
        help='Show the graphical connections (for plots: "simple", "full" and "evolution") (df. false)',
    )
    # how to plot
    parser.add_argument(
        "-a",
        "--alpha",
        type=float,
        help="Alpha/Opacity value for mesh rendering (df. 0.8)",
    )
    parser.add_argument(
        "-pc", "--polygon-color", type=str, help='Polygon color (df. "lightblue")'
    )
    parser.add_argument(
        "-nc", "--node-color", type=str, help='Node color (df. "green")'
    )
    parser.add_argument(
        "-mcc",
        "--main-connection-color",
        type=str,
        help='Main connection color (df. "darkred")',
    )
    parser.add_argument(
        "-gcc",
        "--graphical-connection-color",
        type=str,
        help='Graphical connection (df. "black")',
    )
    # other
    parser.add_argument(
        "-t",
        "--test",
        type=str,
        help="Only used with '-i'. The input file should be tested for many attributes (df. false)",
    )

    return parser


def read_args(arg_parser: ArgumentParser) -> dict[str, str]:
    """
    A short description.

    A bit longer description.

    Args:
        variable (type): description

    Returns:
        type: description

    Raises:
        ArgumentError: The specified option is not compatible with the '-t'/'--test' option
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

    with open(os.path.join(ROOT_DIR, DEFAULT_ARGS_JSON_FILE_PATH), "r") as f:
        default_args = json.load(f)

    # - Arguments -
    def read_arg(key: str, boolexpr: bool = False):
        if not args[key]:
            args[key] = default_args[key]
        elif (
            boolexpr
        ):  # elif: in the default_args dict, the values are already 'pythonic' values; no need to parse
            args[key] = parse_bool_expr(args[key])

    # polyhedron
    print(args)
    read_arg("input")
    read_arg("evaluate")
    read_arg("rotate mesh", True)
    # chaikin
    read_arg("chaikin generations")
    read_arg("verbose", True)
    read_arg("chaikin coef")
    # what to plot
    read_arg("renderer")
    read_arg("plot")
    read_arg("show main connections", True)
    read_arg("show graphical connections", True)
    # how to plot
    read_arg("alpha")
    read_arg("polygon color")
    read_arg("node color")
    read_arg("main connection color")
    read_arg("graphical connection color")

    # Test Mode
    read_arg("test", True)
    if args["test"]:
        invalid_option = [""]
        for invalid_option in invalid_options:
            if args[invalid_option] is not None:
                raise ArgumentError(
                    f"Cannot use this option with '-t'/'--test': {invalid_option}"
                )

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


def parse_bool_expr(bexpr: str) -> bool:
    """
    Converts a string to a bool

    Parses an string expression containing representing a boolean value into a real python boolean value.

    Args:
        bexpr (str): string representation of a boolean value

    Returns:
        bool: boolean value of its string representation 'bexpr'

    Raises:
        ValueError: given string is not a known/supported boolean expression

    """

    if bexpr.lower() in ["1", "t", "true"]:
        return True
    if bexpr.lower() in ["0", "f", "false"]:
        return False
    raise ValueError(f"Unrecognized value for supposed boolean: {bexpr}")
