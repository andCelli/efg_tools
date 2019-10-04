import pptree


class CustomNode(pptree.Node):
    def __init__(self, name, seq_id, parent=None):
        super().__init__(name, parent)
        self.seq_id = seq_id


class PrettyTree:
    def __init__(self, treeplex, real_plan):
        self.real_plan = real_plan

        self.root_seq = CustomNode(f"{treeplex.empty_sequence}, {real_plan[treeplex.empty_sequence]}", treeplex.empty_sequence)

        def explore(parent_node):
            for child in treeplex.get_child_information_sets(parent_node.seq_id):
                for seq in child.get_children_as_list():
                    new_node = CustomNode(f"{seq}, {real_plan[seq]}", seq, parent_node)
                    explore(new_node)

        explore(self.root_seq)

    def print(self):
        pptree.print_tree(self.root_seq)
