#pragma once
// Included after Maintenance.h and CameraControl.h in the CAM implementation.

constexpr uint32_t targetIntervalMs = 250;
constexpr uint32_t targetMaxLeaseMs = 30000;

struct TargetStream {
    uint32_t renewed = 0;
    uint32_t duration = 0;
    uint32_t generation = 0;
    uint32_t sample = 0;
    uint32_t captured = 0;
    target::Observation observation;
    bool hasSample = false;

    bool active(uint32_t now) const { return now - renewed < duration; }
} targetStream;

target::Detector *targetDetector = nullptr;

struct TargetDecode {
    const camera_fb_t &frame;
    int width, height;
    bool dimensionsMatch;
    int pixels;
};

size_t readTargetJpeg(void *arg, size_t index, uint8_t *buffer, size_t length) {
    const auto &frame = static_cast<TargetDecode *>(arg)->frame;
    if (index > frame.len || length > frame.len - index) return 0;
    if (buffer) memcpy(buffer, frame.buf + index, length);
    return length;
}

bool writeTargetPixels(void *arg, uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint8_t *rgb) {
    auto &decode = *static_cast<TargetDecode *>(arg);
    if (!rgb) {
        if (x == 0 && y == 0) decode.dimensionsMatch = w == decode.width && h == decode.height;
        return true;
    }
    if (!decode.dimensionsMatch || x + w > decode.width || y + h > decode.height) return false;
    decode.pixels += w * h;
    for (int row = y; row < y + h; ++row) {
        for (int col = x; col < x + w; ++col) {
            targetDetector->mask[row * decode.width + col] = target::classify(rgb[0], rgb[1], rgb[2]);
            rgb += 3;
        }
    }
    return true;
}

target::Observation observeTarget(const camera_fb_t &frame) {
    target::Observation error;
    error.status = target::Status::frameError;
    if (frame.format != PIXFORMAT_JPEG || !frame.len) return error;
    const bool large = frame.width > 400;
    const size_t divisor = large ? 8 : 4;
    const size_t width = frame.width / divisor, height = frame.height / divisor;
    if (!width || width > target::maxWidth || !height || height > target::maxHeight) return error;
    TargetDecode decode{frame, int(width), int(height), false, 0};
    if (esp_jpg_decode(frame.len, large ? JPG_SCALE_8X : JPG_SCALE_4X,
                       readTargetJpeg, writeTargetPixels, &decode) != ESP_OK ||
        !decode.dimensionsMatch || decode.pixels != decode.width * decode.height) return error;
    return targetDetector->detect(decode.width, decode.height);
}

void targetTask(void *) {
    for (;;) {
        xSemaphoreTake(stateMutex, portMAX_DELAY);
        const bool enabled = targetStream.active(millis()) && !otaUpdating && !pendingVerification;
        if (!enabled) {
            targetStream.duration = 0;
            targetStream.hasSample = false;
        }
        const uint32_t generation = targetStream.generation;
        xSemaphoreGive(stateMutex);
        if (enabled && cameraReady && !otaUpdating && !pendingVerification &&
            xSemaphoreTake(cameraMutex, pdMS_TO_TICKS(20)) == pdTRUE) {
            camera_fb_t *frame = esp_camera_fb_get();
            xSemaphoreGive(cameraMutex);

            target::Observation observation;
            observation.status = target::Status::frameError;
            uint32_t captured = millis();
            if (frame) {
                captured = uint32_t(uint64_t(frame->timestamp.tv_sec) * 1000 + frame->timestamp.tv_usec / 1000);
                if (target::fresh(millis(), captured) && !otaUpdating) observation = observeTarget(*frame);
                esp_camera_fb_return(frame);
            }

            xSemaphoreTake(stateMutex, portMAX_DELAY);
            if (targetStream.generation == generation && targetStream.active(millis()) && !otaUpdating) {
                ++targetStream.sample;
                targetStream.captured = captured;
                targetStream.observation = observation;
                targetStream.hasSample = true;
            }
            xSemaphoreGive(stateMutex);
        }
        vTaskDelay(pdMS_TO_TICKS(targetIntervalMs));
    }
}

esp_err_t targetHandler(httpd_req_t *req) {
    if (req->method == HTTP_POST) {
        if (!camAuthorize(req)) return ESP_OK;
        char body[64] = {};
        StaticJsonDocument<96> input;
        if (!req->content_len || req->content_len >= sizeof(body))
            return camReply(req, "400 Bad Request", "{\"error\":\"Expected leaseMs from 0 to 30000\"}");
        if (!camReadExact(req, reinterpret_cast<uint8_t *>(body), req->content_len, millis())) return ESP_FAIL;
        if (deserializeJson(input, body, req->content_len) || !input["leaseMs"].is<uint32_t>() ||
            input["leaseMs"].as<uint32_t>() > targetMaxLeaseMs)
            return camReply(req, "400 Bad Request", "{\"error\":\"Expected leaseMs from 0 to 30000\"}");
        const uint32_t duration = input["leaseMs"].as<uint32_t>();
        if (duration && (otaUpdating || pendingVerification || !cameraReady))
            return camReply(req, "503 Service Unavailable", "{\"error\":\"Camera unavailable\"}");
        if (duration && !targetDetector) {
            void *memory = heap_caps_malloc(sizeof(target::Detector), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
            if (memory) targetDetector = new (memory) target::Detector;
            if (!targetDetector || xTaskCreatePinnedToCore(targetTask, "cam-target", 4096, nullptr, 1, nullptr, 1) != pdPASS) {
                heap_caps_free(targetDetector);
                targetDetector = nullptr;
                return camReply(req, "503 Service Unavailable", "{\"error\":\"Target observer unavailable\"}");
            }
        }

        xSemaphoreTake(stateMutex, portMAX_DELAY);
        const uint32_t now = millis();
        if (!duration || !targetStream.active(now)) {
            ++targetStream.generation;
            targetStream.hasSample = false;
        }
        targetStream.duration = duration;
        targetStream.renewed = now;
        xSemaphoreGive(stateMutex);
    }

    xSemaphoreTake(stateMutex, portMAX_DELAY);
    const auto snapshot = targetStream;
    const uint32_t now = millis();
    xSemaphoreGive(stateMutex);

    StaticJsonDocument<384> reply;
    reply["bootId"] = bootId;
    reply["marker"] = "magenta-cyan-v1";
    if (!snapshot.active(now)) {
        reply["state"] = "off";
    } else if (otaUpdating || pendingVerification || !cameraReady) {
        reply["state"] = "unavailable";
    } else {
        reply["leaseRemainingMs"] = snapshot.duration - (now - snapshot.renewed);
        if (!snapshot.hasSample) {
            reply["state"] = "waiting";
        } else {
            reply["sample"] = snapshot.sample;
            reply["ageMs"] = now - snapshot.captured;
            if (!target::fresh(now, snapshot.captured)) {
                reply["state"] = "stale";
            } else {
                switch (snapshot.observation.status) {
                    case target::Status::found:
                        reply["state"] = "found";
                        reply["x"] = snapshot.observation.x;
                        reply["y"] = snapshot.observation.y;
                        break;
                    case target::Status::missing: reply["state"] = "missing"; break;
                    case target::Status::ambiguous: reply["state"] = "ambiguous"; break;
                    case target::Status::frameError: reply["state"] = "frameError"; break;
                }
            }
        }
    }
    char json[384];
    serializeJson(reply, json, sizeof(json));
    return camReply(req, "200 OK", json);
}
