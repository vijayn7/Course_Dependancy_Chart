import csv

# Class to represent a course
class Course:
    def __init__(self, course_number, course_name):
        self.course_number = course_number  # Unique course identifier
        self.course_name = course_name      # Full name of the course
        self.prerequisites = []            # List of prerequisites (AND and OR groups)

    def add_prerequisites(self, prereq_groups):
        """Add prerequisite groups to the course."""
        self.prerequisites.extend(prereq_groups)

    def __str__(self):
        """Display the course information."""
        prereq_str = "Prerequisites: " + ", ".join(
            f"[{' or '.join(group)}]" for group in self.prerequisites
        )
        return f"Course: {self.course_number} - {self.course_name}\n{prereq_str}\n"


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


# Function to display all courses and their prerequisites
def display_courses(course_map):
    """Display all courses and their prerequisites."""
    for course in course_map.values():
        print(course)


# Main function
def main():
    # File paths
    course_names_file = "All_Classes_and_Names.csv"
    prerequisites_file = "CE_Sample_Schedule.tsv"

    # Parse data
    course_map = parse_course_names(course_names_file)
    parse_prerequisites(prerequisites_file, course_map)

    # Display the dependency graph
    display_courses(course_map)


if __name__ == "__main__":
    main()