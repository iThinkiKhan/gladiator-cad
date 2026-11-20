#include <cassert>
#include <cmath>
#include "../cam/src/TargetObservation.h"

namespace {
constexpr int width = 80, height = 60;
target::Detector detector{};

void patch(int left, int top, target::Color color) {
    for (int y = top; y < top + 10; ++y)
        for (int x = left; x < left + 10; ++x)
            detector.mask[y * width + x] = color;
}

void marker(int left, int top) {
    patch(left, top, target::Color::magenta);
    patch(left, top + 12, target::Color::cyan);
}
}

int main() {
    using target::Color;
    using target::Status;
    assert(target::classify(224, 38, 166) == Color::magenta);
    assert(target::classify(24, 157, 201) == Color::cyan);
    assert(target::classify(234, 234, 234) == Color::background);
    assert(target::classify(24, 23, 29) == Color::background);

    marker(35, 19);
    auto result = detector.detect(width, height);
    assert(result.status == Status::found && std::abs(result.x) < 0.001f && std::abs(result.y) < 0.001f);
    marker(55, 4);
    result = detector.detect(width, height);
    assert(result.status == Status::found && std::abs(result.x - 0.5f) < 0.001f && std::abs(result.y + 0.5f) < 0.001f);
    marker(15, 34);
    result = detector.detect(width, height);
    assert(result.status == Status::found && std::abs(result.x + 0.5f) < 0.001f && std::abs(result.y - 0.5f) < 0.001f);

    result = detector.detect(width, height);
    assert(result.status == Status::missing && result.x == 0 && result.y == 0);
    patch(35, 19, Color::magenta);
    assert(detector.detect(width, height).status == Status::missing);
    patch(35, 19, Color::cyan);
    patch(35, 31, Color::magenta);
    assert(detector.detect(width, height).status == Status::missing);
    patch(35, 19, Color::magenta);
    patch(35, 39, Color::cyan);
    assert(detector.detect(width, height).status == Status::missing);
    marker(0, 19);
    assert(detector.detect(width, height).status == Status::missing);

    marker(20, 19);
    marker(50, 19);
    result = detector.detect(width, height);
    assert(result.status == Status::ambiguous && result.x == 0 && result.y == 0);
    assert(detector.detect(target::maxWidth + 1, height).status == Status::frameError);
    assert(target::fresh(1700, 1000) && !target::fresh(1701, 1000));
    assert(target::fresh(10, UINT32_MAX - 10));
}
