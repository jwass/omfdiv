import json

import duckdb
import networkx as nx
from textual.app import App, ComposeResult
from textual.widgets import Tree


class TreeApp(App):
    def __init__(self, g):
        super().__init__()
        self.g = g

    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("World")
        tree.root.expand()

        roots = [n for n in self.g.nodes if not self.g.in_edges(n)]
        roots.sort(key=lambda k: self.division_name(k))
        visited = set()

        for root in roots:
            tree.root.add(self.division_name(root), data=root)
        yield tree

    def on_tree_node_expanded(self, event: Tree.NodeExpanded):
        node = event.node
        division_id = node.data
        if division_id is None:
            return
        children = list(self.g.neighbors(division_id))
        children.sort(key=lambda k: self.division_name(k))
        for c in children:
            node.add(self.division_name(c), data=c)

    def division_name(self, id_):
        if "names" not in self.g.nodes[id_]:
            print(f"WHAT! No name in {id_}")
            name = "MISSING"
        else:
            names = self.g.nodes[id_]["names"]
            if names.get("common") and names["common"].get("en"):
                name = names["common"]["en"]
            else:
                name = names.get("primary")
        return name

def main():
    g = nx.DiGraph()
    i = 0
    with open("/Users/jwasserman/divisions.json") as f:
        for line in f:
            r = json.loads(line)
            g.add_node(r["id"], names=r["names"])
            if r["parent_division_id"]:
                g.add_edge(r["parent_division_id"], r["id"])

            i += 1

    app = TreeApp(g)
    app.run()


if __name__ == "__main__":
    main()
