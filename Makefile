# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -std=c++17

# Source files
SRC = chart.cpp

# Object files
OBJ = $(SRC:.cpp=.o)

# Output executable
TARGET = chart

# Default target
all: $(TARGET)

# Build the target executable
$(TARGET): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJ)

# Compile source files into object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean the build
clean:
	rm -f $(OBJ) $(TARGET)

# Rebuild the project
rebuild: clean all