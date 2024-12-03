import csv
import networkx as nx
import plotly.graph_objects as go

# Class to represent a course
class Course:
    def __init__(self, class_number, class_name):
        self.class_number = class_number
        self.class_name = class_name
        self.prerequisites = []

    def add_prerequisites(self, prereq_groups):
        """Add prerequisite groups to the course."""
        self.prerequisites.extend(prereq_groups)

    def __repr__(self):
        return f"Course({self.class_number}, {self.class_name})"

# Function to parse course names from a CSV file
def parse_course_names(file_path):
    """Parse course names from a CSV file."""
    course_map = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            course_number, course_name = row[0].strip(), row[1].strip()
            course_map[course_number] = Course(course_number, course_name)
    return course_map

# Function to parse prerequisites from a TSV file
def parse_prerequisites(file_path, course_map):
    """Parse prerequisites from a TSV file and update the course map."""
    with open(file_path, newline='', encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)  # Skip header
        for row in reader:
            course_number = row[0].strip()
            if course_number in course_map:
                prereq_string = row[2].strip()
                prereq_groups = [
                    [item.strip() for item in group.split("OR")]
                    for group in prereq_string.split(",")
                ]
                course_map[course_number].add_prerequisites(prereq_groups)

def visualize_courses_interactive(course_map):
    """Visualize the course dependency graph interactively."""
    G = nx.DiGraph()  # Create a directed graph

    # Add nodes and edges
    for course in course_map.values():
        G.add_node(course.class_number, name=course.class_name)
        for prereq_group in course.prerequisites:
            for prereq in prereq_group:
                G.add_edge(prereq, course.class_number)

    # Generate graph layout with increased spacing
    pos = nx.spring_layout(G, k=0.5, iterations=50)  # Adjust 'k' for node spacing

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
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_name = G.nodes[node].get('name', 'Unknown')  # Use 'Unknown' if 'name' attribute is missing
        node_text.append(f"{node}: {node_name}")  # Tooltip text includes course name

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=list(G.nodes()),  # Display course numbers
        hovertext=node_text,  # Show course names on hover
        hoverinfo="text",
        marker=dict(
            size=30,  # Larger nodes
            color="lightblue",
            line=dict(width=2, color="darkblue")
        ),
        textfont=dict(
            size=12  # Larger font size for better readability
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
            margin=dict(b=0, l=0, r=0, t=50),  # Increased top margin for better title spacing
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )

    # Show the graph
    fig.show()

# Main function
def main():
    # File paths
    course_names_file = "All_Classes_and_Names.csv"
    prerequisites_file = "CE_Sample_Schedule.tsv"

    # Parse data
    course_map = parse_course_names(course_names_file)
    parse_prerequisites(prerequisites_file, course_map)

    # Visualize the dependency graph interactively
    visualize_courses_interactive(course_map)

if __name__ == "__main__":
    main()