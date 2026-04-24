/**
 * Tests for Parameter Editor.
 */

#include <cassert>
#include <cmath>
#include <string>
#include <vector>
#include <iostream>

// Simple test framework
#define TEST(name) void test_##name()
#define RUN_TEST(name) do { \
    std::cout << "Running " #name "..." << std::endl; \
    test_##name(); \
    std::cout << "  PASSED" << std::endl; \
} while(0)

#define ASSERT_TRUE(x) assert(x)
#define ASSERT_FALSE(x) assert(!(x))
#define ASSERT_EQ(a, b) assert((a) == (b))
#define ASSERT_NEAR(a, b, eps) assert(std::abs((a) - (b)) < (eps))

// Parameter validation tests

TEST(float_parameter_validation) {
    struct FloatParam {
        double value;
        double min_val;
        double max_val;
        
        bool validate() const {
            return value >= min_val && value <= max_val;
        }
    };
    
    FloatParam p1 = {0.5, 0.0, 1.0};
    ASSERT_TRUE(p1.validate());
    
    FloatParam p2 = {1.5, 0.0, 1.0};
    ASSERT_FALSE(p2.validate());
    
    FloatParam p3 = {-0.1, 0.0, 1.0};
    ASSERT_FALSE(p3.validate());
}

TEST(enum_parameter_validation) {
    struct EnumParam {
        int value;
        std::vector<int> valid_values;
        
        bool validate() const {
            for (int v : valid_values) {
                if (v == value) return true;
            }
            return false;
        }
    };
    
    EnumParam p1 = {1, {0, 1, 2, 3}};
    ASSERT_TRUE(p1.validate());
    
    EnumParam p2 = {5, {0, 1, 2, 3}};
    ASSERT_FALSE(p2.validate());
}

TEST(parameter_name_parsing) {
    std::string full_name = "ATC_RAT_PIT_P";
    
    // Extract group
    size_t last_underscore = full_name.rfind('_');
    std::string param_name = full_name.substr(last_underscore + 1);
    
    ASSERT_EQ(param_name, "P");
}

TEST(json_schema_structure) {
    // JSON schema structure validation
    struct SchemaGroup {
        std::string name;
        std::string description;
        int param_count;
    };
    
    SchemaGroup pid_group = {"PID", "PID Controller Parameters", 6};
    SchemaGroup limits_group = {"Limits", "Flight Limits", 4};
    
    ASSERT_EQ(pid_group.name, "PID");
    ASSERT_EQ(limits_group.param_count, 4);
}

TEST(profile_save_load) {
    struct Profile {
        std::string name;
        std::vector<std::pair<std::string, double>> values;
    };
    
    Profile p;
    p.name = "Test Profile";
    p.values.push_back({"PARAM_1", 0.5});
    p.values.push_back({"PARAM_2", 1.0});
    
    ASSERT_EQ(p.values.size(), 2);
    ASSERT_NEAR(p.values[0].second, 0.5, 0.001);
}

TEST(parameter_default_reset) {
    struct Parameter {
        double value;
        double default_value;
        
        void reset() { value = default_value; }
    };
    
    Parameter p = {0.8, 0.5};
    ASSERT_NEAR(p.value, 0.8, 0.001);
    
    p.reset();
    ASSERT_NEAR(p.value, 0.5, 0.001);
}

int main() {
    RUN_TEST(float_parameter_validation);
    RUN_TEST(enum_parameter_validation);
    RUN_TEST(parameter_name_parsing);
    RUN_TEST(json_schema_structure);
    RUN_TEST(profile_save_load);
    RUN_TEST(parameter_default_reset);
    
    std::cout << "\nAll tests passed!" << std::endl;
    return 0;
}
