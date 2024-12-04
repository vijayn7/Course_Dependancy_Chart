import csv
import networkx as nx
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from itertools import cycle

# Define a function to generate colors dynamically
def generate_colors():
    """Generate a cycle of colors for dynamically assigning group colors."""
    colors = [
        "blue", "red", "green", "yellow", "purple", "orange",
        "cyan", "magenta", "lime", "pink", "teal", "brown"
    ]
    return cycle(colors)

# Class to represent a course
class Course:
    def __init__(self, class_number, name, group, credits, completed):
        self.class_number = class_number
        self.name = name
        self.group = group
        self.credits = int(credits)
        self.completed = completed.lower() == "true"  # Convert to boolean
        self.prerequisites = []

    def __repr__(self):
        return f"Course({self.class_number}, {self.name}, {self.group}, {self.credits}, {self.completed}, {self.prerequisites})"

# Function to parse class details and groups from `classes.csv`
def parse_classes(file_path):
    """Parse course details, groups, and credits from a CSV file."""
    courses = {}
    group_colors = {}
    color_generator = generate_colors()

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_number = row["Class Number:"].strip()
            name = row["Class Name:"].strip()
            group = row["Group:"].strip()  # Extract group information
            credits = row["Credits:"].strip()
            completed = row["Completed:"].strip()

            # Assign a color to the group if not already assigned
            if group not in group_colors:
                group_colors[group] = next(color_generator)

            # Create a course object and store it
            courses[class_number] = Course(class_number, name, group, credits, completed)

    return courses, group_colors

# Function to parse group credits from `groups.csv`
def parse_group_credits(file_path):
    """Parse required credits for each group from `groups.csv`."""
    group_credits = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            group = row["Group:"].strip()
            credits_required = int(row["Credits Needed:"].strip())
            group_credits[group] = credits_required
    return group_credits

# Function to parse prerequisites from `prereqs.tsv`
def parse_prerequisites(file_path, courses):
    """Parse prerequisites from a TSV file and update courses."""
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

# Create the graph figure dynamically
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
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#888"),
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

    # Add group labels
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

    # Combine traces and layout
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Interactive Course Dependency Graph with Toggle",
            titlefont_size=20,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=group_labels
        )
    )

    return fig

# Main function with Dash app
def main():
    # File paths
    classes_file = "./mnt/data/classes.csv"
    groups_file = "./mnt/data/groups.csv"
    prereqs_file = "./mnt/data/prereqs.tsv"

    # Parse course details and groups
    courses, group_colors = parse_classes(classes_file)
    group_credits = parse_group_credits(groups_file)
    parse_prerequisites(prereqs_file, courses)

    # Initialize Dash app
    app = Dash(__name__)

    app.layout = html.Div([
        dcc.Graph(id="course-graph", config={"displayModeBar": False}),
        html.Div(id="click-data", style={"display": "none"})  # Hidden div to store click data
    ])

    @app.callback(
        Output("course-graph", "figure"),
        [Input("course-graph", "clickData")]
    )
    def toggle_completion(click_data):
        if click_data:
            node_id = click_data["points"][0]["text"]  # Extract clicked node ID
            if node_id in courses:
                courses[node_id].completed = not courses[node_id].completed  # Toggle completion status
        return create_figure(courses, group_colors, group_credits)

    # Initial rendering
    app.run_server(debug=True)

if __name__ == "__main__":
    main()