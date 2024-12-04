import csv
import networkx as nx
import plotly.graph_objects as go
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

# Visualize the dependency graph interactively
def visualize_courses_interactive(courses, group_colors, group_credits):
    """Visualize the course dependency graph interactively with labels above nodes."""
    G = nx.DiGraph()  # Create a directed graph

    # Add nodes and edges
    group_completed_credits = {group: 0 for group in group_credits}  # Initialize completed credits per group
    for course in courses.values():
        G.add_node(course.class_number, group=course.group, name=course.name, credits=course.credits, completed=course.completed)
        if course.completed:
            group_completed_credits[course.group] += course.credits  # Accumulate completed credits
        for prereq_group in course.prerequisites:
            for prereq in prereq_group:
                if prereq in courses:  # Add edge only if prerequisite exists
                    G.add_edge(prereq, course.class_number)

    # Define horizontal positions for each group
    group_order = list(group_colors.keys())
    group_positions = {group: i for i, group in enumerate(group_order)}

    # Generate positions for nodes
    pos = {}
    group_counters = {group: 0 for group in group_order}  # Track vertical position within each group
    vertical_spacing = 3  # Adjust vertical spacing between nodes
    for node in G.nodes():
        group = G.nodes[node].get("group", "Unknown")
        x = group_positions[group] * 5  # Spread groups horizontally
        y = group_counters[group] * -vertical_spacing  # Space nodes vertically within each group
        group_counters[group] += 1
        pos[node] = (x, y)

    # Add group labels with credits progress
    # Add group labels with credits progress
    group_labels = []
    for group, x in group_positions.items():
        completed = group_completed_credits.get(group, 0)
        required = group_credits.get(group, 0)
        group_labels.append((x * 5, 2, f"{group}<br>({completed}/{required} credits completed)"))  # Line break added

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

    # Create node traces with updated label positions
    node_x = []
    node_y = []
    node_text = []
    node_hovertext = []
    node_color = []
    node_border_color = []  # Add a border color for completed nodes
    node_size = []  # Different size for completed nodes
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        group = G.nodes[node].get("group", "Unknown")
        name = G.nodes[node].get("name", "Unknown")
        credits = G.nodes[node].get("credits", "0")
        completed = G.nodes[node].get("completed", False)

        node_text.append(node)  # Only display course number
        node_hovertext.append(f"{node}: {name} ({credits} credits)")  # Show course name and credits on hover
        node_color.append(group_colors.get(group, "gray"))  # Default to gray if group not found

        # Highlight completed nodes
        if completed:
            node_border_color.append("gold")
            node_size.append(30)  # Larger size for completed nodes
        else:
            node_border_color.append("black")
            node_size.append(20)  # Default size for uncompleted nodes

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,  # Display course numbers only
        hovertext=node_hovertext,  # Display course name and credits on hover
        hoverinfo="text",
        textposition="top center",  # Position text above nodes
        marker=dict(
            size=node_size,  # Set node size dynamically
            color=node_color,
            opacity=0.8,  # Set opacity for semi-transparent squares
            symbol="square",  # Rectangle shape
            line=dict(width=3, color=node_border_color)  # Set border color dynamically
        ),
        textfont=dict(
            size=14,  # Adjust text size for readability
            color="black"  # Set text color to black
        )
    )

    # Add group labels as annotations
    annotations = [
        dict(
            x=x, y=y, text=label, showarrow=False,
            font=dict(size=16, color="black"),
            xanchor="center", yanchor="bottom"
        ) for x, y, label in group_labels
    ]

    # Combine traces and layout
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Interactive Course Dependency Graph with Dynamic Group Colors and Credits Progress",
            titlefont_size=20,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=annotations  # Add group labels
        )
    )

    # Show the graph
    fig.show()

# Main function
def main():
    # File paths
    classes_file = "./mnt/data/classes.csv"
    groups_file = "./mnt/data/groups.csv"
    prereqs_file = "./mnt/data/prereqs.tsv"

    # Parse course details and groups
    courses, group_colors = parse_classes(classes_file)

    # Parse group credits
    group_credits = parse_group_credits(groups_file)

    # Parse prerequisites
    parse_prerequisites(prereqs_file, courses)

    # Visualize the dependency graph interactively
    visualize_courses_interactive(courses, group_colors, group_credits)


if __name__ == "__main__":
    main()