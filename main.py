import csv
import networkx as nx
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, ctx
from itertools import cycle


def generate_colors():
    """Generate a cycle of colors for dynamically assigning group colors."""
    colors = [
        "blue", "red", "green", "yellow", "purple", "orange",
        "cyan", "magenta", "lime", "pink", "teal", "brown"
    ]
    return cycle(colors)


class Course:
    def __init__(self, class_number, name, group, credits, completed):
        self.class_number = class_number
        self.name = name
        self.group = group
        self.credits = int(credits)
        self.completed = completed.lower() == "true"
        self.prerequisites = []

    def __repr__(self):
        return f"Course({self.class_number}, {self.name}, {self.group}, {self.credits}, {self.completed}, {self.prerequisites})"


def parse_classes(file_path):
    courses = {}
    group_colors = {}
    color_generator = generate_colors()

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_number = row["Class Number:"].strip()
            name = row["Class Name:"].strip()
            group = row["Group:"].strip()
            credits = row["Credits:"].strip()
            completed = row["Completed:"].strip()

            if group not in group_colors:
                group_colors[group] = next(color_generator)

            courses[class_number] = Course(class_number, name, group, credits, completed)

    return courses, group_colors


def parse_group_credits(file_path):
    group_credits = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            group = row["Group:"].strip()
            credits_required = int(row["Credits Needed:"].strip())
            group_credits[group] = credits_required
    return group_credits


def parse_prerequisites(file_path, courses):
    with open(file_path, newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            class_number = row["Class Number:"].strip()
            prerequisites = row["Prerequisites:"].strip()
            if class_number in courses:
                prereq_groups = [
                    [item.strip() for item in group.split("OR")]
                    for group in prerequisites.split(",") if prerequisites
                ]
                courses[class_number].prerequisites.extend(prereq_groups)


def create_figure(courses, group_colors, group_credits):
    """Create the Plotly figure with the current state of the graph."""
    G = nx.DiGraph()  # Create a directed graph
    group_completed_credits = {group: 0 for group in group_credits}

    # Add nodes and edges
    for course in courses.values():
        G.add_node(course.class_number, group=course.group, name=course.name, credits=course.credits, completed=course.completed)
        if course.completed:
            group_completed_credits[course.group] += course.credits
        for prereq_group in course.prerequisites:
            for prereq in prereq_group:
                if prereq in courses:  # Add edge only if prerequisite exists
                    G.add_edge(prereq, course.class_number)

    # Define horizontal positions for each group
    group_order = list(group_colors.keys())
    group_positions = {group: i for i, group in enumerate(group_order)}
    pos = {}
    group_counters = {group: 0 for group in group_order}
    vertical_spacing = 3

    for node in G.nodes():
        group = G.nodes[node].get("group", "Unknown")
        x = group_positions[group] * 5
        y = group_counters[group] * -vertical_spacing
        group_counters[group] += 1
        pos[node] = (x, y)

    # Create edge traces
    satisfied_edge_x = []
    satisfied_edge_y = []
    unsatisfied_edge_x = []
    unsatisfied_edge_y = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]

        if courses[edge[0]].completed:
            satisfied_edge_x.extend([x0, x1, None])
            satisfied_edge_y.extend([y0, y1, None])
        else:
            unsatisfied_edge_x.extend([x0, x1, None])
            unsatisfied_edge_y.extend([y0, y1, None])

    satisfied_edge_trace = go.Scatter(
        x=satisfied_edge_x,
        y=satisfied_edge_y,
        line=dict(width=2, color="green"),
        hoverinfo="none",
        mode="lines"
    )

    unsatisfied_edge_trace = go.Scatter(
        x=unsatisfied_edge_x,
        y=unsatisfied_edge_y,
        line=dict(width=2, color="red"),
        hoverinfo="none",
        mode="lines"
    )

    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_hovertext = []
    node_color = []
    node_border_color = []
    node_size = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        group = G.nodes[node].get("group", "Unknown")
        name = G.nodes[node].get("name", "Unknown")
        credits = G.nodes[node].get("credits", 0)
        completed = G.nodes[node].get("completed", False)

        node_text.append(node)
        node_hovertext.append(f"{node}: {name} ({credits} credits)")
        node_color.append(group_colors.get(group, "gray"))

        if completed:
            node_border_color.append("gold")
            node_size.append(30)
        else:
            node_border_color.append("black")
            node_size.append(20)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        hovertext=node_hovertext,
        hoverinfo="text",
        textposition="top center",
        marker=dict(
            size=node_size,
            color=node_color,
            opacity=0.8,
            symbol="square",
            line=dict(width=3, color=node_border_color)
        )
    )

    group_labels = [
        dict(
            x=group_positions[group] * 5,
            y=2,
            text=f"{group}<br>({group_completed_credits.get(group, 0)}/{group_credits.get(group, 0)} credits completed)",
            showarrow=False,
            font=dict(size=16, color="black"),
            xanchor="center", yanchor="bottom"
        ) for group in group_colors
    ]

    fig = go.Figure(
        data=[satisfied_edge_trace, unsatisfied_edge_trace, node_trace],
        layout=go.Layout(
            title="Interactive Course Dependency Graph with Reset Button",
            titlefont_size=20,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=50),
            height=1000,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=group_labels
        )
    )

    return fig


def main():
    # File paths
    classes_file = "./mnt/data/classes.csv"
    groups_file = "./mnt/data/groups.csv"
    prereqs_file = "./mnt/data/prereqs.tsv"

    # Parse course details and groups
    courses, group_colors = parse_classes(classes_file)
    group_credits = parse_group_credits(groups_file)
    parse_prerequisites(prereqs_file, courses)

    original_courses = {key: course.completed for key, course in courses.items()}

    app = Dash(__name__)

    app.layout = html.Div([
        dcc.Graph(id="course-graph", config={"displayModeBar": False}),
        html.Button("Reset", id="reset-button", n_clicks=0),
    ])

    @app.callback(
        Output("course-graph", "figure"),
        [Input("course-graph", "clickData"), Input("reset-button", "n_clicks")]
    )
    def update_graph(click_data, reset_clicks):
        triggered_id = ctx.triggered_id
        if triggered_id == "reset-button":
            for key in courses:
                courses[key].completed = original_courses[key]
        elif triggered_id == "course-graph" and click_data:
            node_id = click_data["points"][0]["text"]
            if node_id in courses:
                courses[node_id].completed = not courses[node_id].completed
        return create_figure(courses, group_colors, group_credits)

    app.run_server(debug=True)


if __name__ == "__main__":
    main()