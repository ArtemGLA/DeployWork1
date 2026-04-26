CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
LDFLAGS =

SRC_DIR = src
TEST_DIR = tests
BUILD_DIR = build

SOURCES = $(SRC_DIR)/validator.cpp
HEADERS = $(SRC_DIR)/validator.h
MAIN = $(SRC_DIR)/main.cpp
TEST_SRC = $(TEST_DIR)/test_validator.cpp

TARGET = validator_demo
TEST_TARGET = test_validator

.PHONY: all clean test

all: $(TARGET)

$(TARGET): $(SOURCES) $(MAIN) $(HEADERS)
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -I$(SRC_DIR) $(SOURCES) $(MAIN) -o $(TARGET) $(LDFLAGS)

test: $(TEST_TARGET)
	./$(TEST_TARGET)

$(TEST_TARGET): $(SOURCES) $(TEST_SRC) $(HEADERS)
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -I$(SRC_DIR) $(SOURCES) $(TEST_SRC) -o $(TEST_TARGET) $(LDFLAGS)

clean:
	rm -rf $(BUILD_DIR) $(TARGET) $(TEST_TARGET)
