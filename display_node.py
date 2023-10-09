import matplotlib.pyplot as plt


def show_tree(node):
    draw_tree(node, mode="all")
    plt.show()


def draw_tree(node, left_edge=0, right_edge=500, depth=1, mode="all"):
    """Recursively draws the tree until depth TOTAL_DEPTH."""
    HEIGHT = 500
    TOTAL_DEPTH = 7
    if depth == TOTAL_DEPTH:
        return

    nodes_to_visit = node.children

    node.x = int((right_edge - left_edge) / 2 + left_edge)
    node.y = int(HEIGHT - HEIGHT / TOTAL_DEPTH * depth)
    if node.board.turn_player.id == node.board.player1.id:
        color = "g"
    else:
        color = "r"

    if node.move == "chance" and node.parent is not None:
        move_str = "chance " + str(node.parent.board.deck[0])
    else:
        move_str = str(node.move)

    plt.text(node.x + 5, node.y + 5, move_str + ", " + str(node.board.turn_player))
    plt.text(node.x - 5, node.y - 5, str(node.wins) + "/" + str(node.n))
    if nodes_to_visit is None:
        plt.scatter(node.x, node.y, c=color, marker="s")
        return

    if depth == TOTAL_DEPTH - 1:
        plt.scatter(node.x, node.y, c=color, marker="v")
    else:
        plt.scatter(node.x, node.y, c=color)
    # Spaces the child nodes properly.
    length_per_child = (right_edge - left_edge) // len(nodes_to_visit)
    for i, child in enumerate(nodes_to_visit):
        node.children[i].draw_tree(left_edge + i * length_per_child, left_edge + (i + 1) * length_per_child,
                                   depth + 1, mode=mode)

    # Connects parents to their children with lines.
    if depth != TOTAL_DEPTH - 1:
        for i, child in enumerate(nodes_to_visit):
            plt.plot([node.x, node.children[i].x], [node.y, node.children[i].y], "k")
