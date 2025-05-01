#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "dx11_renderer.h"
#include <vector>

namespace py = pybind11;
using namespace dx11_renderer;

PYBIND11_MODULE(_core, m) {
    m.doc() = "DirectX 11 accelerated image processing module";

    py::class_<ProcessingParams>(m, "ProcessingParams")
        .def(py::init<>())
        .def_readwrite("brightness", &ProcessingParams::brightness)
        .def_readwrite("contrast", &ProcessingParams::contrast)
        .def_readwrite("saturation", &ProcessingParams::saturation)
        .def_readwrite("gamma", &ProcessingParams::gamma);

    py::class_<RendererStatus>(m, "RendererStatus")
        .def(py::init<>())
        .def_readonly("isInitialized", &RendererStatus::isInitialized)
        .def_readonly("textureWidth", &RendererStatus::textureWidth)
        .def_readonly("textureHeight", &RendererStatus::textureHeight)
        .def_readonly("lastProcessingTime", &RendererStatus::lastProcessingTime)
        .def_readonly("lastError", &RendererStatus::lastError);

    py::class_<DX11Renderer>(m, "DX11Renderer")
        .def(py::init<>())
        .def("process_frame", [](DX11Renderer& self, py::array_t<uint8_t, py::array::c_style> input) {
            if (input.ndim() != 3 || input.shape(2) != 3) {
                throw std::runtime_error("Input must be a BGR image (height, width, 3)");
            }

            cv::Mat inputMat(
                static_cast<int>(input.shape(0)),
                static_cast<int>(input.shape(1)),
                CV_8UC3,
                const_cast<uint8_t*>(input.data())
            );

            cv::Mat outputMat;
            self.processFrame(inputMat, outputMat);

            // Create shape and strides containers
            std::vector<py::ssize_t> shape = {
                outputMat.rows,
                outputMat.cols,
                outputMat.channels()
            };
            
            std::vector<py::ssize_t> strides = {
                static_cast<py::ssize_t>(outputMat.step[0]),
                static_cast<py::ssize_t>(outputMat.step[1]),
                static_cast<py::ssize_t>(1)
            };

            // Create and return numpy array
            return py::array_t<uint8_t>(
                py::array::ShapeContainer(shape.begin(), shape.end()),
                py::array::StridesContainer(strides.begin(), strides.end()),
                outputMat.data
            );
        })
        .def("update_processing_params", &DX11Renderer::updateProcessingParams)
        .def_property_readonly("status", &DX11Renderer::getStatus);
}
