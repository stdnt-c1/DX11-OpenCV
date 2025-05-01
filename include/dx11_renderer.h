#pragma once
#include <d3d11.h>
#include <opencv2/opencv.hpp>
#include <string>
#include <stdexcept>
#include <memory>

#ifdef _WIN32
    #ifdef DX11_RENDERER_EXPORTS
        #define DX11_API __declspec(dllexport)
    #else
        #define DX11_API __declspec(dllimport)
    #endif
#else
    #define DX11_API
#endif

namespace dx11_renderer {

// Forward declaration
class DX11RendererImpl;

// Status information structure
struct DX11_API RendererStatus {
    bool isInitialized = false;
    int textureWidth = 0;
    int textureHeight = 0;
    float lastProcessingTime = 0.0f;
    std::string lastError;
};

struct DX11_API ProcessingParams {
    float brightness = 1.0f;
    float contrast = 1.0f;
    float saturation = 1.0f;
    float gamma = 1.0f;
};

// Main renderer class using PIMPL to hide implementation details
class DX11_API DX11Renderer {
public:
    DX11Renderer();
    ~DX11Renderer();

    // Disable copy operations
    DX11Renderer(const DX11Renderer&) = delete;
    DX11Renderer& operator=(const DX11Renderer&) = delete;

    // Public interface
    void processFrame(const cv::Mat& inputFrame, cv::Mat& outputFrame);
    void updateProcessingParams(const ProcessingParams& params);
    const RendererStatus& getStatus() const;

private:
    std::unique_ptr<DX11RendererImpl> impl;
};

} // namespace dx11_renderer
