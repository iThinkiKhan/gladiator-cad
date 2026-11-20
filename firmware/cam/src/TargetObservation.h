#pragma once
#include <stddef.h>
#include <stdint.h>

namespace target {

constexpr int maxWidth = 100;
constexpr int maxHeight = 75;
constexpr int maxPixels = maxWidth * maxHeight;
constexpr uint32_t freshnessMs = 700;

enum class Color : uint8_t { background, magenta, cyan };
enum class Status : uint8_t { missing, found, ambiguous, frameError };

struct Observation {
    Status status = Status::missing;
    float x = 0;
    float y = 0;
};

inline Color classify(int r, int g, int b) {
    constexpr int minimumLevel = 70;
    constexpr int contrast = 36;
    if (r >= minimumLevel && b >= minimumLevel && r - g >= contrast && b - g >= contrast)
        return Color::magenta;
    if (g >= minimumLevel && b >= minimumLevel && g - r >= contrast && b - r >= contrast)
        return Color::cyan;
    return Color::background;
}

struct Patch {
    int left, right, top, bottom;

    int width() const { return right - left + 1; }
    int height() const { return bottom - top + 1; }
};

inline bool matches(const Patch &top, const Patch &bottom) {
    const int gap = bottom.top - top.bottom - 1;
    if (gap < 0 || 2 * gap > top.height()) return false;
    if (top.height() * 2 < bottom.height() || bottom.height() * 2 < top.height()) return false;
    const int first = top.left > bottom.left ? top.left : bottom.left;
    const int last = top.right < bottom.right ? top.right : bottom.right;
    const int overlap = last - first + 1;
    return overlap * 4 >= top.width() * 3 && overlap * 4 >= bottom.width() * 3;
}

// The decoder fills the mask. Flood fill consumes it and reuses the queue for each patch.
struct Detector {
    Color mask[maxPixels];
    uint16_t queue[maxPixels];

    Observation detect(int width, int height) {
        Observation result;
        if (width <= 0 || width > maxWidth || height <= 0 || height > maxHeight) {
            result.status = Status::frameError;
            return result;
        }

        constexpr int maxPatches = 12;
        Patch patches[2][maxPatches];
        int counts[2] = {};
        for (int i = 0; i < width * height; ++i) {
            const Color color = mask[i];
            if (color == Color::background) continue;
            Patch patch{i % width, i % width, i / width, i / width};
            int tail = 1;
            queue[0] = i;
            mask[i] = Color::background;
            for (int head = 0; head < tail; ++head) {
                const int cell = queue[head];
                const int x = cell % width, y = cell / width;
                if (x < patch.left) patch.left = x;
                if (x > patch.right) patch.right = x;
                if (y < patch.top) patch.top = y;
                if (y > patch.bottom) patch.bottom = y;
                if (x > 0) enqueue(cell - 1, color, tail);
                if (x + 1 < width) enqueue(cell + 1, color, tail);
                if (y > 0) enqueue(cell - width, color, tail);
                if (y + 1 < height) enqueue(cell + width, color, tail);
            }
            if (patch.left == 0 || patch.top == 0 || patch.right == width - 1 || patch.bottom == height - 1)
                continue;
            const int w = patch.width(), h = patch.height();
            if (w < 4 || h < 4 || w > h * 2 || h > w * 2 || tail * 10 < w * h * 6) continue;
            const int slot = color == Color::magenta ? 0 : 1;
            if (counts[slot] == maxPatches) {
                result.status = Status::ambiguous;
                return result;
            }
            patches[slot][counts[slot]++] = patch;
        }

        for (int i = 0; i < counts[0]; ++i) {
            for (int j = 0; j < counts[1]; ++j) {
                const Patch &top = patches[0][i], &bottom = patches[1][j];
                if (!matches(top, bottom)) continue;
                if (result.status == Status::found) {
                    result = Observation{};
                    result.status = Status::ambiguous;
                    return result;
                }
                result.status = Status::found;
                // Offsets are fractions of the half-width and half-height of the camera image.
                result.x = (top.left + top.right + bottom.left + bottom.right + 2) / (2.f * width) - 1.f;
                result.y = (top.top + bottom.bottom + 1) / float(height) - 1.f;
            }
        }
        return result;
    }

private:
    void enqueue(int cell, Color color, int &tail) {
        if (mask[cell] != color) return;
        mask[cell] = Color::background;
        queue[tail++] = cell;
    }
};

inline bool fresh(uint32_t now, uint32_t captured) {
    return now - captured <= freshnessMs;
}

} // namespace target
