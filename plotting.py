from __future__ import annotations
from math import sqrt

# functions
def draw_full(renderer: Renderer, poly: Polyhedron, a: A) -> None:
    """
    Draw nine different representations of the same mesh (poly)

    Draw nine representations of the same mesh. Their attributes are as follows (in order) :
     * (1, 1)
       - main connections
     * (1, 2)
       - graphical connections
     * (1, 3)
       - main connections
       - graphical connections
     * (2, 1)
       - main connections
       - only main faces (translucent)
     * (2, 2)
       - graphical connections
       - only graphical faces (translucent)
     * (2, 3)
       - all faces (solid)
     * (3, 1)
       - all faces (translucent)
     * (3, 2)
       - main connections
       - all faces (translucent)
     * (3, 3)
       - all connections
       - all faces (translucent)
    They are drawn left to right, top to bottom.

    Args:
        renderer (Renderer)  : renderer for the mesh
        poly     (Polyhedron): polyhedron (mesh) to draw
        a        (A)         : this variable contains all the cmd-line arguments

    """

    main_conn_dd = renderer.get_connections_draw_data(
        poly, type_="main", line_color=a.main_connection_color, node_color=a.node_color
    )
    graphical_conn_dd = renderer.get_connections_draw_data(
        poly,
        type_="graphical",
        line_color=a.graphical_connection_color,
        node_color=a.node_color,
    )
    main_poly_dd = renderer.get_polyhedron_draw_data(
        poly, type_="main", alpha=0.6, color=a.polygon_color
    )
    graphical_poly_dd = renderer.get_polyhedron_draw_data(
        poly, type_="graphical", alpha=0.6, color=a.polygon_color
    )
    alpha_poly_dd = renderer.get_polyhedron_draw_data(
        poly, alpha=0.6, color=a.polygon_color
    )
    solid_poly_dd = renderer.get_polyhedron_draw_data(
        poly, alpha=1, color=a.polygon_color
    )
    all_connection_dd = graphical_conn_dd + main_conn_dd

    renderer.init_subplots(
        3,
        3,
        subplot_titles=[
            "Main connections",
            "Graphical connections",
            "All connections",
            "Faces using main connections",
            "Faces using graphical connections",
            "All faces (solid)",
            "All faces",
            "All faces + main connections",
            "All faces + all connections",
        ],
    )

    # - add from least important to most important (adding the lists of data, not subplot order) -> visual overwriting -
    # draw only main faces (translucent)
    for sub_mpoly_dd in main_poly_dd:
        renderer.add_to_subplot(sub_mpoly_dd, custom_row=2, custom_col=1)
    # draw only graphical faces (translucent)
    for sub_gpoly_dd in graphical_poly_dd:
        renderer.add_to_subplot(sub_gpoly_dd, custom_row=2, custom_col=2)
    # draw all faces (solid)
    for sub_poly_dd in solid_poly_dd:
        renderer.add_to_subplot(sub_poly_dd, custom_row=2, custom_col=3)
    # draw all faces (translucent)
    for sub_apoly_dd in alpha_poly_dd:
        renderer.add_to_subplot(sub_apoly_dd, custom_row=3, custom_col=1)
        renderer.add_to_subplot(sub_apoly_dd, custom_row=3, custom_col=2)
        renderer.add_to_subplot(sub_apoly_dd, custom_row=3, custom_col=3)
    # draw graphical connections
    for gconn_dd in graphical_conn_dd:
        renderer.add_to_subplot(gconn_dd, custom_row=1, custom_col=3)
        renderer.add_to_subplot(gconn_dd, custom_row=1, custom_col=2)
        renderer.add_to_subplot(gconn_dd, custom_row=3, custom_col=3)
        renderer.add_to_subplot(gconn_dd, custom_row=2, custom_col=2)
    # draw main connections
    for mconn_dd in main_conn_dd:
        renderer.add_to_subplot(mconn_dd, custom_row=1, custom_col=1)
        renderer.add_to_subplot(mconn_dd, custom_row=1, custom_col=3)
        renderer.add_to_subplot(mconn_dd, custom_row=3, custom_col=2)
        renderer.add_to_subplot(mconn_dd, custom_row=3, custom_col=3)
        renderer.add_to_subplot(mconn_dd, custom_row=2, custom_col=1)

    renderer.draw_subplots()


def draw_chaikin_evolution(renderer: Renderer, poly: Polyhedron, a: A) -> None:
    """
    Draw six different Chaikin generations of the same mesh

    Draw six the same mesh, but everytime it gets drawn, the Chaikin3D algorithm
    is applied to it. Starting with generation zero (original polyhedron), we
    end at generation 5.

    Args:
        renderer (Renderer)  : renderer for the mesh
        poly     (Polyhedron): polyhedron (mesh) to draw
        a        (A)         : this variable contains all the cmd-line arguments

    Raises:
        AssertionError: Invalid number of Chaikin generations

    """

    # find best row-col combination
    assert (
        a.chaikin_generations > 0
    ), f"Number of generations must be more than zero ({a.chaikin_generations} > 0)"
    near = sqrt(a.chaikin_generations + 1)
    cols = int(near) + (0 if near == int(near) else 1)
    rows = cols if cols ** (cols - 1) <= a.chaikin_generations else cols - 1
    print("cols", cols, "rows", rows)
    renderer.init_subplots(
        rows,
        cols,
        subplot_titles=[
            "Chaikin Gen {}".format(i) for i in range(a.chaikin_generations + 1)
        ],
    )
    for i in range(a.chaikin_generations + 1):
        print(f"Generation: {i}/{a.chaikin_generations}")
        # get values
        alpha_poly_dd = renderer.get_polyhedron_draw_data(
            poly, alpha=a.alpha, color=a.polygon_color
        )
        if a.show_main_connections:
            main_conn_dd = renderer.get_connections_draw_data(
                poly,
                type_="main",
                line_color=a.main_connection_color,
                node_color=a.node_color,
            )
        if a.show_graphical_connections:
            graphical_conn_dd = renderer.get_connections_draw_data(
                poly,
                type_="graphical",
                line_color=a.graphical_connection_color,
                node_color=a.node_color,
            )
        # add to subplot
        for sub_apoly_dd in alpha_poly_dd:
            renderer.add_to_subplot(sub_apoly_dd)
        if a.show_main_connections:
            for mconn_dd in main_conn_dd:
                renderer.add_to_subplot(mconn_dd)
        if a.show_graphical_connections:
            for gconn_dd in graphical_conn_dd:
                renderer.add_to_subplot(gconn_dd)
        # go to next plot
        renderer.next_subplot()
        # Chaikin
        poly = poly.Chaikin3D(a.chaikin_coef, a.verbose)

    renderer.draw_subplots()


def chaikin_animation(
    renderer: Renderer, poly: Polyhedron, n: int, coef: float, alpha: float = 0.6
) -> None:
    """
    Not working yet.

    """

    frames: list[go.Frame] = []
    old_poly = Polyhedron(poly.nodes.copy())
    for gen in range(n):
        print("Generation: {}".format(gen))
        alpha_poly_dd = renderer.get_polyhedron_draw_data(
            poly, alpha=alpha, color=polygon_color
        )
        if smc:
            main_conn_dd = renderer.get_connections_draw_data(
                poly, type_="main", line_color=main_conn_color, node_color=node_color
            )
        else:
            main_conn_dd = []
        if sgc:
            graphical_conn_dd = renderer.get_connections_draw_data(
                poly,
                type_="graphical",
                line_color=graph_conn_color,
                node_color=node_color,
            )
        else:
            graphical_conn_dd = []
        frames.append(
            go.Frame(
                data=alpha_poly_dd + graphical_conn_dd + main_conn_dd,
                name="Chaikin Gen {}".format(gen),
            )
        )
        if gen < n:
            poly = poly.Chaikin3D(coef, verbose, FILE_MODE)
    fig = go.Figure(frames=frames)
    # add first frame
    alpha_poly_dd = renderer.get_polyhedron_draw_data(
        poly, alpha=alpha, color=polygon_color
    )
    if smc:
        main_conn_dd = renderer.get_connections_draw_data(
            poly, type_="main", line_color=main_conn_color, node_color=node_color
        )
    else:
        main_conn_dd = []
    if sgc:
        graphical_conn_dd = renderer.get_connections_draw_data(
            poly, type_="graphical", line_color=graph_conn_color, node_color=node_color
        )
    else:
        graphical_conn_dd = []
    # fig.add_trace(alpha_poly_dd + graphical_conn_dd + main_conn_dd)
    #
    frame_args = lambda duration: {
        "frame": {"duration": duration},
        "mode": "immediate",
        "fromcurrent": True,
        "transition": {"duration": duration, "easing": "linear"},
    }
    #
    sliders = [
        {
            "pad": {"b": 10, "t": 60},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": [
                {
                    "args": [[f.name], frame_args(0)],
                    "label": str(k),
                    "method": "animate",
                }
                for k, f in enumerate(fig.frames)
            ],
        }
    ]
    # Layout
    fig.update_layout(
        title="Chaikin Algorithm in 3 dimensions",
        width=600,
        height=600,
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, frame_args(50)],
                        "label": "&#9654;",  # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;",  # pause symbol
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
        ],
        sliders=sliders,
    )

    fig.show()
