#include "dx11_renderer.h"
#include <d3dcompiler.h>
#include <directxmath.h>
#include <stdexcept>
#include <vector>

// Include DirectXTK
#include <SimpleMath.h>
#include <WICTextureLoader.h>

namespace dx11_renderer {

class DX11RendererImpl {
public:
    DX11RendererImpl() {
        try {
            initializeDevice();
            createConstantBuffer();
            createShaders();
            status.isInitialized = true;
        }
        catch (const std::exception& e) {
            status.lastError = e.what();
            cleanupResources();
        }
    }

    ~DX11RendererImpl() {
        cleanupResources();
    }

    void initializeDevice() {
        D3D_FEATURE_LEVEL featureLevel = D3D_FEATURE_LEVEL_11_0;
        UINT createDeviceFlags = D3D11_CREATE_DEVICE_SINGLETHREADED;
#ifdef _DEBUG
        createDeviceFlags |= D3D11_CREATE_DEVICE_DEBUG;
#endif

        HRESULT hr = D3D11CreateDevice(
            nullptr,                    // Use default adapter
            D3D_DRIVER_TYPE_HARDWARE,  // Use hardware acceleration
            nullptr,                    // No software rasterizer
            createDeviceFlags,
            &featureLevel,
            1,
            D3D11_SDK_VERSION,
            &device,
            nullptr,
            &context
        );

        if (FAILED(hr)) {
            throw std::runtime_error("Failed to create DirectX 11 device");
        }
    }

    void createConstantBuffer() {
        D3D11_BUFFER_DESC bufferDesc = {};
        bufferDesc.ByteWidth = sizeof(ProcessingParams);
        bufferDesc.Usage = D3D11_USAGE_DYNAMIC;
        bufferDesc.BindFlags = D3D11_BIND_CONSTANT_BUFFER;
        bufferDesc.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;

        D3D11_SUBRESOURCE_DATA initData = {};
        initData.pSysMem = &params;

        HRESULT hr = device->CreateBuffer(&bufferDesc, &initData, &constBuffer);
        if (FAILED(hr)) {
            throw std::runtime_error("Failed to create constant buffer");
        }
    }

    void createShaders() {
        const char* shaderCode = R"(
        cbuffer ProcessingParams : register(b0) {
            float brightness;
            float contrast;
            float saturation;
            float gamma;
        };

        Texture2D<float4> inputTexture : register(t0);
        RWTexture2D<float4> outputTexture : register(u0);

        [numthreads(8, 8, 1)]
        void main(uint3 DTid : SV_DispatchThreadID) {
            float4 color = inputTexture[DTid.xy];
            
            // Apply brightness
            color.rgb *= brightness;
            
            // Apply contrast
            float3 lumCoeff = float3(0.2126, 0.7152, 0.0722);
            float luminance = dot(color.rgb, lumCoeff);
            color.rgb = lerp(luminance, color.rgb, contrast);
            
            // Apply saturation
            float3 desaturated = float3(luminance, luminance, luminance);
            color.rgb = lerp(desaturated, color.rgb, saturation);
            
            // Apply gamma correction
            color.rgb = pow(color.rgb, 1.0 / gamma);
            
            outputTexture[DTid.xy] = color;
        }
    )";

        ID3DBlob* shaderBlob = nullptr;
        ID3DBlob* errorBlob = nullptr;

        HRESULT hr = D3DCompile(
            shaderCode, strlen(shaderCode),
            nullptr, nullptr, nullptr,
            "main", "cs_5_0",
            D3DCOMPILE_ENABLE_STRICTNESS, 0,
            &shaderBlob, &errorBlob
        );

        if (FAILED(hr)) {
            std::string errorMsg = "Shader compilation failed: ";
            if (errorBlob) {
                errorMsg += static_cast<const char*>(errorBlob->GetBufferPointer());
                errorBlob->Release();
            }
            if (shaderBlob) shaderBlob->Release();
            throw std::runtime_error(errorMsg);
        }

        hr = device->CreateComputeShader(
            shaderBlob->GetBufferPointer(),
            shaderBlob->GetBufferSize(),
            nullptr,
            &computeShader
        );

        shaderBlob->Release();
        if (FAILED(hr)) {
            throw std::runtime_error("Failed to create compute shader");
        }
    }

    void createTextures(int width, int height) {
        // Release existing textures
        if (inputTextureSRV) { inputTextureSRV->Release(); inputTextureSRV = nullptr; }
        if (outputTextureUAV) { outputTextureUAV->Release(); outputTextureUAV = nullptr; }
        if (inputTexture) { inputTexture->Release(); inputTexture = nullptr; }
        if (outputTexture) { outputTexture->Release(); outputTexture = nullptr; }

        // Create texture description
        D3D11_TEXTURE2D_DESC texDesc = {};
        texDesc.Width = width;
        texDesc.Height = height;
        texDesc.MipLevels = 1;
        texDesc.ArraySize = 1;
        texDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
        texDesc.SampleDesc.Count = 1;
        texDesc.Usage = D3D11_USAGE_DEFAULT;
        texDesc.BindFlags = D3D11_BIND_SHADER_RESOURCE;

        // Create input texture
        HRESULT hr = device->CreateTexture2D(&texDesc, nullptr, &inputTexture);
        if (FAILED(hr)) {
            throw std::runtime_error("Failed to create input texture");
        }

        // Create SRV for input texture
        hr = device->CreateShaderResourceView(inputTexture, nullptr, &inputTextureSRV);
        if (FAILED(hr)) {
            throw std::runtime_error("Failed to create input texture view");
        }

        // Create output texture
        texDesc.BindFlags = D3D11_BIND_UNORDERED_ACCESS;
        hr = device->CreateTexture2D(&texDesc, nullptr, &outputTexture);
        if (FAILED(hr)) {
            throw std::runtime_error("Failed to create output texture");
        }

        // Create UAV for output texture
        hr = device->CreateUnorderedAccessView(outputTexture, nullptr, &outputTextureUAV);
        if (FAILED(hr)) {
            throw std::runtime_error("Failed to create output texture UAV");
        }

        status.textureWidth = width;
        status.textureHeight = height;
    }

    void cleanupResources() {
        if (outputTextureUAV) { outputTextureUAV->Release(); outputTextureUAV = nullptr; }
        if (inputTextureSRV) { inputTextureSRV->Release(); inputTextureSRV = nullptr; }
        if (outputTexture) { outputTexture->Release(); outputTexture = nullptr; }
        if (inputTexture) { inputTexture->Release(); inputTexture = nullptr; }
        if (computeShader) { computeShader->Release(); computeShader = nullptr; }
        if (constBuffer) { constBuffer->Release(); constBuffer = nullptr; }
        if (context) { context->Release(); context = nullptr; }
        if (device) { device->Release(); device = nullptr; }
    }

    void processFrame(const cv::Mat& inputFrame, cv::Mat& outputFrame) {
        if (!status.isInitialized) {
            throw std::runtime_error("Renderer not initialized");
        }

        // Update textures if size changed
        if (inputFrame.cols != status.textureWidth || inputFrame.rows != status.textureHeight) {
            createTextures(inputFrame.cols, inputFrame.rows);
        }

        // Update constant buffer
        D3D11_MAPPED_SUBRESOURCE mappedResource;
        HRESULT hr = context->Map(constBuffer, 0, D3D11_MAP_WRITE_DISCARD, 0, &mappedResource);
        if (SUCCEEDED(hr)) {
            memcpy(mappedResource.pData, &params, sizeof(ProcessingParams));
            context->Unmap(constBuffer, 0);
        }

        // Update input texture
        context->UpdateSubresource(inputTexture, 0, nullptr, inputFrame.data, inputFrame.step[0], 0);

        // Set shader resources
        context->CSSetShader(computeShader, nullptr, 0);
        context->CSSetConstantBuffers(0, 1, &constBuffer);
        context->CSSetShaderResources(0, 1, &inputTextureSRV);
        context->CSSetUnorderedAccessViews(0, 1, &outputTextureUAV, nullptr);

        // Dispatch compute shader
        UINT x = (inputFrame.cols + 7) / 8;
        UINT y = (inputFrame.rows + 7) / 8;
        context->Dispatch(x, y, 1);

        // Copy result back to CPU
        outputFrame.create(inputFrame.rows, inputFrame.cols, CV_8UC4);
        D3D11_BOX box = { 0, 0, 0, static_cast<UINT>(inputFrame.cols), static_cast<UINT>(inputFrame.rows), 1 };
        context->CopySubresourceRegion(outputTexture, 0, 0, 0, 0, inputTexture, 0, &box);
        context->CopyResource(outputTexture, inputTexture);

        D3D11_MAPPED_SUBRESOURCE mapped;
        hr = context->Map(outputTexture, 0, D3D11_MAP_READ, 0, &mapped);
        if (SUCCEEDED(hr)) {
            const BYTE* src = static_cast<const BYTE*>(mapped.pData);
            BYTE* dst = outputFrame.data;
            for (int i = 0; i < outputFrame.rows; ++i) {
                memcpy(dst, src, outputFrame.cols * 4);
                src += mapped.RowPitch;
                dst += outputFrame.step[0];
            }
            context->Unmap(outputTexture, 0);
        }
    }

    void updateProcessingParams(const ProcessingParams& newParams) {
        params = newParams;
    }

    const RendererStatus& getStatus() const {
        return status;
    }

private:
    ID3D11Device* device = nullptr;
    ID3D11DeviceContext* context = nullptr;
    ID3D11Buffer* constBuffer = nullptr;
    ID3D11ComputeShader* computeShader = nullptr;
    ID3D11ShaderResourceView* inputTextureSRV = nullptr;
    ID3D11UnorderedAccessView* outputTextureUAV = nullptr;
    ID3D11Texture2D* inputTexture = nullptr;
    ID3D11Texture2D* outputTexture = nullptr;

    RendererStatus status;
    ProcessingParams params;
};

// Main class implementation
DX11Renderer::DX11Renderer() : impl(std::make_unique<DX11RendererImpl>()) {}
DX11Renderer::~DX11Renderer() = default;

void DX11Renderer::processFrame(const cv::Mat& inputFrame, cv::Mat& outputFrame) {
    impl->processFrame(inputFrame, outputFrame);
}

void DX11Renderer::updateProcessingParams(const ProcessingParams& params) {
    impl->updateProcessingParams(params);
}

const RendererStatus& DX11Renderer::getStatus() const {
    return impl->getStatus();
}

} // namespace dx11_renderer
