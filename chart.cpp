#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <algorithm> // For std::find
using namespace std;

// Helper function to trim whitespace from a string
string trim(const string& str) {
    size_t first = str.find_first_not_of(" \t\n\r");
    if (first == string::npos) return ""; // Empty or whitespace-only string
    size_t last = str.find_last_not_of(" \t\n\r");
    return str.substr(first, last - first + 1);
}

vector<string> splitByWord(const string& str, const string& word) {
    vector<string> tokens;
    size_t start = 0, end;

    while ((end = str.find(word, start)) != string::npos) {
        // Extract substring before the "word"
        string token = str.substr(start, end - start);
        tokens.push_back(trim(token));
        start = end + word.length(); // Move past the "word"
    }

    // Add the last part of the string
    tokens.push_back(trim(str.substr(start)));
    return tokens;
}

// Helper function to split a string by a delimiter
vector<string> split(const string& str, char delimiter) {
    vector<string> tokens;
    string token;
    istringstream tokenStream(str);
    while (getline(tokenStream, token, delimiter)) {
        tokens.push_back(trim(token));
    }
    return tokens;
}

// Struct to represent a course
struct Course {
    string classNumber;                // Unique course identifier (e.g., "MATH 115")
    string className;                  // Full name of the course (e.g., "Calculus I")
    vector<vector<string>> prerequisites; // List of prerequisites with alternatives

    // Default constructor
    Course() : classNumber(""), className("") {}

    // Constructor to initialize a course
    Course(string number, string name) : classNumber(number), className(name) {}

    // Method to display course details
    void display() const {
        cout << "Course: " << classNumber << " - " << className << endl;
        cout << "Prerequisites: ";
        for (const auto& group : prerequisites) {
            cout << "[";
            for (const auto& prereq : group) {
                cout << prereq << "";
            }
            cout << "]";
        }
        cout << endl;
    }
};

// Function to read class names and create a map of Course objects
map<string, Course> parseClassNames(const string& filename) {
    map<string, Course> courseMap;  // Map to store course number and Course object
    ifstream file(filename);       // Open the file

    if (!file.is_open()) {
        cerr << "Error: Could not open file " << filename << endl;
        return courseMap; // Return empty map
    }

    string line;

    // Skip the header
    getline(file, line);

    // Read each line and populate the map
    while (getline(file, line)) {
        istringstream iss(line);
        string classNumber, className;

        // Read course number and name, assuming they are separated by a comma
        getline(iss, classNumber, ',');
        getline(iss, className, ',');

        // Trim whitespace
        classNumber = trim(classNumber);
        className = trim(className);

        // Create a Course object and insert it into the map
        Course course(classNumber, className);
        courseMap[classNumber] = course;
    }
    file.close();
    return courseMap;
}

// Function to parse prerequisites and add them to the respective courses
void parsePrerequisites(const string& filename, map<string, Course>& courseMap) {
    ifstream file(filename); // Open the prerequisites file
    if (!file.is_open()) {
        cerr << "Error: Could not open file " << filename << endl;
        return;
    }

    string line;

    // Skip the header
    getline(file, line);

    // Read each line and populate the prerequisites for the courses
    while (getline(file, line)) {
        istringstream iss(line);
        string classNumber, className, prereqString;

        // Read course number, name, and prerequisites
        getline(iss, classNumber, '\t');
        getline(iss, className, '\t');
        getline(iss, prereqString, '\t');

        // Trim whitespace
        classNumber = trim(classNumber);
        prereqString = trim(prereqString);

        // Find the course in the map
        auto it = courseMap.find(classNumber);
        if (it != courseMap.end()) {
            Course& course = it->second;

            // Parse prerequisites (split by ",")
            vector<string> andGroups = split(prereqString, ',');
            for (string group : andGroups) {
                // Parse "OR" conditions within each group
                vector<string> options = splitByWord(group, "OR");
                course.prerequisites.push_back(options);
            }
        }
    }
    file.close();
}

// Main function
int main() {
    string classNamesFile = "All_Classes_and_Names1.csv"; // Adjust path as needed
    string prerequisitesFile = "CE_Sample_Schedule.tsv"; // Adjust path as needed

    // Parse the class names file
    map<string, Course> courseMap = parseClassNames(classNamesFile);

    // Parse the prerequisites file and update the courses
    parsePrerequisites(prerequisitesFile, courseMap);

    // Display the courses with their prerequisites
    for (const auto& [classNumber, course] : courseMap) {
        course.display();
        cout << endl;
    }

    return 0;
}