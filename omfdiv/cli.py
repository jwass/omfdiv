import json
from typing import List, Optional

import click
import duckdb
from textual.app import App, ComposeResult
from textual.widgets import Tree


class Division:
    def __init__(self, id_, subtype, has_children, names):
        self.id_ = id_
        self.subtype = subtype
        self.has_children = has_children
        self.names = names

        self._name = None

    @property
    def name(self):
        if self._name is not None:
            return self._name

        name = None
        if self.names is None:
            name = ""
        elif self.names.get("common"):
            try:
                idx = self.names["common"]["key"].index("en")
            except ValueError:
                idx = None
            if idx is not None:
                name = self.names["common"]["value"][idx]
        if name is None:
            name = self.names["primary"]

        self._name = name
        return name


class TreeApp(App):
    def __init__(self, db):
        super().__init__()
        self.db = db

    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("World")
        tree.show_root = False
        tree.root.expand()

        yield tree

    def on_tree_node_expanded(self, event: Tree.NodeExpanded):
        node = event.node
        division = node.data
        divisions = self.query_child_divisions(division)
        divisions.sort(key=lambda d: d.name)
        for division in divisions:
            node.add(
                self.fmt(division.name, division.subtype),
                data=division,
                allow_expand=division.has_children,
            )

    def query_child_divisions(
        self, division: Optional[Division]
    ) -> Optional[List[Division]]:
        if division is None:
            q = "SELECT id, subtype, has_children, names FROM divisions_data where parent_division_id IS NULL;"
            args = []
        else:
            q = "SELECT id, subtype, has_children, names FROM divisions_data where parent_division_id = ?;"
            args = [division.id_]

        self.db.execute(q, args)
        results = self.db.fetchall()
        divisions = []
        for row in results:
            id_, subtype, has_children, names = row
            division = Division(id_, subtype, has_children, names)
            divisions.append(division)
        return divisions

    def fmt(self, name, subtype):
        return f"{name} ({subtype})"


@click.group()
def cli():
    pass


@cli.command()
@click.option("--db", required=False, default="divisions.duckdb")
def ui(db: str):
    con = duckdb.connect(db)
    app = TreeApp(con)
    app.run()


@cli.command()
@click.option("--db", required=False, default="divisions.duckdb")
def builddb(db: str):
    con = duckdb.connect(db)
    con.execute("DROP TABLE IF EXISTS divisions_data;")
    con.execute("SET s3_region = 'us-west-2';")
    con.execute(
        """
    CREATE TABLE divisions_data AS (
        SELECT
            id,
            names,
            subtype,
            a.parent_division_id,
            b.n IS NOT NULL as has_children
        FROM read_parquet('s3://overturemaps-us-west-2/release/2024-07-22.0/theme=divisions/type=division/*') a
        LEFT JOIN (
            SELECT
                parent_division_id,
                COUNT(1) AS n
            FROM read_parquet('s3://overturemaps-us-west-2/release/2024-07-22.0/theme=divisions/type=division/*')
            GROUP BY parent_division_id
        ) b
        ON a.id = b.parent_division_id
    );
    """
    )
    con.execute(
        "CREATE INDEX admins_parent_division_id_idx ON divisions_data (parent_division_id);"
    )


if __name__ == "__main__":
    cli()
