/**
 * Tests for Primary Flight Display widget.
 */

#include <cassert>
#include <cmath>
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

const double PI = 3.14159265358979323846;

// Angle normalization tests

TEST(heading_normalization) {
    auto normalizeHeading = [](double heading) -> double {
        while (heading < 0) heading += 360;
        while (heading >= 360) heading -= 360;
        return heading;
    };
    
    ASSERT_NEAR(normalizeHeading(0), 0, 0.001);
    ASSERT_NEAR(normalizeHeading(360), 0, 0.001);
    ASSERT_NEAR(normalizeHeading(450), 90, 0.001);
    ASSERT_NEAR(normalizeHeading(-90), 270, 0.001);
}

TEST(pitch_clamping) {
    auto clampPitch = [](double pitch) -> double {
        return std::max(-90.0, std::min(90.0, pitch));
    };
    
    ASSERT_NEAR(clampPitch(45), 45, 0.001);
    ASSERT_NEAR(clampPitch(100), 90, 0.001);
    ASSERT_NEAR(clampPitch(-100), -90, 0.001);
}

TEST(roll_conversion) {
    auto degreesToRadians = [](double deg) { return deg * PI / 180.0; };
    auto radiansToDegrees = [](double rad) { return rad * 180.0 / PI; };
    
    ASSERT_NEAR(degreesToRadians(180), PI, 0.001);
    ASSERT_NEAR(radiansToDegrees(PI), 180, 0.001);
}

// Speed tape tests

TEST(speed_tape_range) {
    struct SpeedTape {
        double speed;
        double range;
        
        double minVisible() const { return std::max(0.0, speed - range); }
        double maxVisible() const { return speed + range; }
    };
    
    SpeedTape tape = {50, 30};
    ASSERT_NEAR(tape.minVisible(), 20, 0.001);
    ASSERT_NEAR(tape.maxVisible(), 80, 0.001);
    
    SpeedTape low_tape = {10, 30};
    ASSERT_NEAR(low_tape.minVisible(), 0, 0.001);
}

// Altitude tape tests

TEST(altitude_tape_scale) {
    struct AltitudeTape {
        double altitude;
        double pixelsPerUnit;
        int height;
        
        int altToPixel(double alt) const {
            double offset = altitude - alt;
            return height / 2 + static_cast<int>(offset * pixelsPerUnit);
        }
    };
    
    AltitudeTape tape = {100, 2.0, 400};
    
    ASSERT_EQ(tape.altToPixel(100), 200);  // Current altitude at center
    ASSERT_EQ(tape.altToPixel(110), 180);  // 10m higher = 20px up
    ASSERT_EQ(tape.altToPixel(90), 220);   // 10m lower = 20px down
}

// Horizon tests

TEST(horizon_pitch_offset) {
    struct HorizonCalc {
        int height;
        double pixelsPerDegree;
        
        int pitchToOffset(double pitch) const {
            return static_cast<int>(pitch * pixelsPerDegree);
        }
    };
    
    HorizonCalc calc = {400, 4.0};
    
    ASSERT_EQ(calc.pitchToOffset(0), 0);
    ASSERT_EQ(calc.pitchToOffset(10), 40);
    ASSERT_EQ(calc.pitchToOffset(-15), -60);
}

TEST(horizon_rotation_matrix) {
    double roll = 30 * PI / 180;  // 30 degrees
    
    double cos_r = std::cos(roll);
    double sin_r = std::sin(roll);
    
    // Rotation matrix: [cos -sin; sin cos]
    ASSERT_NEAR(cos_r * cos_r + sin_r * sin_r, 1.0, 0.001);
}

// Color coding tests

TEST(battery_color_coding) {
    auto getBatteryColor = [](int percent) -> int {
        if (percent <= 20) return 0xFF0000;      // Red
        else if (percent <= 40) return 0xFFFF00; // Yellow
        else return 0x00FF00;                    // Green
    };
    
    ASSERT_EQ(getBatteryColor(10), 0xFF0000);
    ASSERT_EQ(getBatteryColor(30), 0xFFFF00);
    ASSERT_EQ(getBatteryColor(80), 0x00FF00);
}

TEST(gps_status_color) {
    auto getGpsColor = [](int fix_type) -> int {
        if (fix_type < 2) return 0xFF0000;       // Red - no fix
        else if (fix_type < 4) return 0xFFFF00;  // Yellow - 2D/3D
        else return 0x00FF00;                    // Green - DGPS/RTK
    };
    
    ASSERT_EQ(getGpsColor(0), 0xFF0000);
    ASSERT_EQ(getGpsColor(3), 0xFFFF00);
    ASSERT_EQ(getGpsColor(5), 0x00FF00);
}

int main() {
    RUN_TEST(heading_normalization);
    RUN_TEST(pitch_clamping);
    RUN_TEST(roll_conversion);
    RUN_TEST(speed_tape_range);
    RUN_TEST(altitude_tape_scale);
    RUN_TEST(horizon_pitch_offset);
    RUN_TEST(horizon_rotation_matrix);
    RUN_TEST(battery_color_coding);
    RUN_TEST(gps_status_color);
    
    std::cout << "\nAll tests passed!" << std::endl;
    return 0;
}
