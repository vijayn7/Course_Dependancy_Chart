import csv
import networkx as nx
import plotly.graph_objects as go


# Define colors for each group
GROUP_COLORS = {
    "CoE Common Core": "blue",
    "CE Program Core Courses": "red",
    "Core Electives": "green",
    "Upper Level CE Electives": "yellow",
    "Unknown": "gray"  # Default color for unknown groups
}


# Class to represent a course
class Course:
    def __init__(self, class_number, prerequisites, group):
        self.class_number = class_number
        self.prerequisites = prerequisites
        self.group = group
        self.name = "Unknown"  # Will be updated with the name from the CSV file

    def __repr__(self):
        return f"Course({self.class_number}, {self.prerequisites}, {self.group}, {self.name})"


# Function to parse course names and map them to class numbers
def parse_course_names(file_path):
    """Parse course names from a CSV file."""
    course_names = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_number = row["Class Number:"].strip()
            class_name = row["Class Name:"].strip()
            course_names[class_number] = class_name
    return course_names


# Function to parse courses and prerequisites from the TSV file
def parse_courses(file_path, course_names):
    """Parse courses from a TSV file and update course names."""
    course_map = {}
    with open(file_path, newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            class_number = row["Class Number:"].strip()
            prerequisites = row["Prerequisites:"].strip()
            group = row["Group:"].strip()

            # Parse prerequisites into groups
            prereq_groups = [
                [item.strip() for item in group.split("OR")]
                for group in prerequisites.split(",") if prerequisites
            ]

            # Create a Course object and add to the map
            course = Course(class_number, prereq_groups, group)
            course.name = course_names.get(class_number, "Unknown")  # Fetch course name from CSV
            course_map[class_number] = course
    return course_map


# Visualize the dependency graph interactively
def visualize_courses_interactive(course_map):
    """Visualize the course dependency graph interactively with labels above nodes."""
    G = nx.DiGraph()  # Create a directed graph

    # Add nodes and edges
    for course in course_map.values():
        G.add_node(course.class_number, group=course.group, name=course.name)
        for prereq_group in course.prerequisites:
            for prereq in prereq_group:
                if prereq in course_map:  # Add edge only if prerequisite exists
                    G.add_edge(prereq, course.class_number)

    # Define horizontal positions for each group
    group_order = ["CoE Common Core", "CE Program Core Courses", "Core Electives", "Upper Level CE Electives", "Unknown"]
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

    # Add group labels
    group_labels = []
    for group, x in group_positions.items():
        group_labels.append((x * 5, 2, group))  # Position labels above their group (y=2)

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
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        group = G.nodes[node].get("group", "Unknown")
        name = G.nodes[node].get("name", "Unknown")
        node_text.append(node)  # Only display course number
        node_hovertext.append(f"{node}: {name}")  # Show course name on hover
        node_color.append(GROUP_COLORS.get(group, "gray"))  # Default to gray if group not found

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,  # Display course numbers only
        hovertext=node_hovertext,  # Display course name on hover
        hoverinfo="text",
        textposition="top center",  # Position text above nodes
        marker=dict(
            size=20,  # Uniform node size
            color=node_color,
            opacity=0.8,  # Set opacity for semi-transparent squares
            symbol="square",  # Rectangle shape
            line=dict(width=2, color="darkblue")
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
            title="Interactive Course Dependency Graph with Labels Above Nodes",
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
    csv_file_path = "/Users/vnannapu/Desktop/course dependancy chart/All_Classes_and_Names.csv"
    tsv_file_path = "/Users/vnannapu/Desktop/course dependancy chart/CE_Sample_Schedule.tsv"

    # Parse course names
    course_names = parse_course_names(csv_file_path)

    # Parse courses and prerequisites
    course_map = parse_courses(tsv_file_path, course_names)

    # Visualize the dependency graph interactively
    visualize_courses_interactive(course_map)


if __name__ == "__main__":
    main()