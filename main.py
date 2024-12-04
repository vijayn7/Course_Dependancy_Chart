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

    def __repr__(self):
        return f"Course({self.class_number}, {self.prerequisites}, {self.group})"


# Function to parse courses and prerequisites from the TSV file
def parse_courses(file_path):
    """Parse courses from a TSV file."""
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
            course_map[class_number] = Course(class_number, prereq_groups, group)
    return course_map


# Visualize the dependency graph interactively with group-based colors
def visualize_courses_interactive(course_map):
    """Visualize the course dependency graph interactively."""
    G = nx.DiGraph()  # Create a directed graph

    # Add nodes and edges
    for course in course_map.values():
        G.add_node(course.class_number, group=course.group)
        for prereq_group in course.prerequisites:
            for prereq in prereq_group:
                if prereq in course_map:  # Add edge only if prerequisite exists
                    G.add_edge(prereq, course.class_number)

    # Generate graph layout
    pos = nx.spring_layout(G, k=0.5, iterations=50)

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
    node_color = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        group = G.nodes[node].get("group", "Unknown")
        node_text.append(f"{node} ({group})")
        node_color.append(GROUP_COLORS.get(group, "gray"))  # Default to gray if group not found

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=list(G.nodes()),  # Display course numbers
        hovertext=node_text,  # Show course and group on hover
        hoverinfo="text",
        marker=dict(
            size=30,
            color=node_color,
            line=dict(width=2, color="darkblue")
        ),
        textfont=dict(
            size=12
        )
    )

    # Combine traces and layout
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Interactive Course Dependency Graph",
            titlefont_size=20,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )

    # Show the graph
    fig.show()


# Main function
def main():
    # File path for the updated TSV file
    tsv_file_path = "CE_Sample_Schedule.tsv"

    # Parse courses
    course_map = parse_courses(tsv_file_path)

    # Visualize the dependency graph interactively
    visualize_courses_interactive(course_map)


if __name__ == "__main__":
    main()