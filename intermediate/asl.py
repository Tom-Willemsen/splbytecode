from intermediate.ast import AstNode, Goto, Label


def flatten_ast(node):
    """
    Flattens an AST into a list of instructions.
    :param node: the root node of the ast
    :return: a flattened list of instructions
    """
    def is_tree_item_before_children(tree):
        return isinstance(tree, Label)

    assert isinstance(node, AstNode)
    result = []

    if is_tree_item_before_children(node):
        result.append(node)

    for child_node in node.get_children():
        result.extend(flatten_ast(child_node))

    if not is_tree_item_before_children(node):
        result.append(node)

    return result
