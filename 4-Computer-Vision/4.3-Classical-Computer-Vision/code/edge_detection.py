import cv2
import numpy as np
from typing import List, Optional, Tuple

from interactive_cv_utils import (
    build_canvas,
    load_image_from_script_dir,
    noop,
    normalize_to_uint8,
    odd_kernel_from_slider,
    optional_blur_kernel_from_slider,
    prepare_preview,
)


WINDOW_NAME = "Interactive Edge Detection Demo"
EDGE_MODE_NAMES = [
    "Canny",
    "Sobel X",
    "Sobel Y",
    "Sobel XY",
    "Laplacian",
]


def build_edge_response(
    gray_image: np.ndarray,
    mode_index: int,
    low_threshold: int,
    high_threshold: int,
    blur_slider: int,
    derivative_slider: int,
) -> Tuple[np.ndarray, List[str]]:
    blur_kernel = optional_blur_kernel_from_slider(blur_slider)
    processed_gray = gray_image.copy()
    if blur_kernel > 0:
        processed_gray = cv2.GaussianBlur(processed_gray, (blur_kernel, blur_kernel), 0)

    derivative_kernel = odd_kernel_from_slider(derivative_slider, minimum=1)
    magnitude_threshold = high_threshold

    if mode_index == 0:
        canny_high = max(low_threshold + 1, high_threshold)
        aperture_size = max(3, min(7, derivative_kernel))
        edges = cv2.Canny(
            processed_gray,
            low_threshold,
            canny_high,
            apertureSize=aperture_size,
            L2gradient=True,
        )
        mode_lines = [
            "Current mode: Canny",
            f"Active thresholds: low={low_threshold}, high={canny_high}",
            f"Aperture size: {aperture_size}",
        ]
        return edges, mode_lines

    if mode_index == 1:
        response = cv2.Sobel(processed_gray, cv2.CV_32F, 1, 0, ksize=derivative_kernel)
        mode_name = "Sobel X"
    elif mode_index == 2:
        response = cv2.Sobel(processed_gray, cv2.CV_32F, 0, 1, ksize=derivative_kernel)
        mode_name = "Sobel Y"
    elif mode_index == 3:
        grad_x = cv2.Sobel(processed_gray, cv2.CV_32F, 1, 0, ksize=derivative_kernel)
        grad_y = cv2.Sobel(processed_gray, cv2.CV_32F, 0, 1, ksize=derivative_kernel)
        response = cv2.magnitude(grad_x, grad_y)
        mode_name = "Sobel XY"
    else:
        response = cv2.Laplacian(processed_gray, cv2.CV_32F, ksize=derivative_kernel)
        mode_name = "Laplacian"

    normalized = normalize_to_uint8(np.abs(response))
    filtered = normalized.copy()
    filtered[normalized < magnitude_threshold] = 0
    mode_lines = [
        f"Current mode: {mode_name}",
        f"Derivative kernel: {derivative_kernel}",
        f"Magnitude threshold: {magnitude_threshold}",
        f"Low-threshold slider is ignored in {mode_name}.",
    ]
    return filtered, mode_lines


def render_frame(
    image: np.ndarray,
    mode_index: int,
    low_threshold: int,
    high_threshold: int,
    blur_slider: int,
    derivative_slider: int,
) -> np.ndarray:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edge_result, mode_lines = build_edge_response(
        gray_image,
        mode_index,
        low_threshold,
        high_threshold,
        blur_slider,
        derivative_slider,
    )

    derivative_kernel = odd_kernel_from_slider(derivative_slider, minimum=1)
    blur_kernel = optional_blur_kernel_from_slider(blur_slider)
    if mode_index == 0:
        derivative_text = max(3, min(7, derivative_kernel))
    else:
        derivative_text = derivative_kernel

    status_lines = [
        "Mode slider: 0 Canny | 1 Sobel X | 2 Sobel Y | 3 Sobel XY | 4 Laplacian",
        f"Low threshold slider: {low_threshold}",
        f"High / magnitude slider: {high_threshold}",
        f"Pre-blur slider: {blur_slider} -> {blur_kernel}",
        f"Derivative kernel slider: {derivative_slider} -> {derivative_text}",
        *mode_lines,
        "Controls: drag sliders to update in real time, press q or Esc to quit.",
    ]
    return build_canvas(
        [
            ("Original", image),
            (EDGE_MODE_NAMES[mode_index], edge_result),
        ],
        status_lines,
    )


def main() -> None:
    image = load_image_from_script_dir(__file__, "imgs/test.png")
    preview_image, _ = prepare_preview(image)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 1500, 900)
    cv2.createTrackbar("Mode", WINDOW_NAME, 0, len(EDGE_MODE_NAMES) - 1, noop)
    cv2.createTrackbar("Low Threshold", WINDOW_NAME, 50, 255, noop)
    cv2.createTrackbar("High Threshold", WINDOW_NAME, 150, 255, noop)
    cv2.createTrackbar("Pre-Blur", WINDOW_NAME, 0, 10, noop)
    cv2.createTrackbar("Derivative Kernel", WINDOW_NAME, 1, 3, noop)

    last_state: Optional[Tuple[int, int, int, int, int]] = None

    while True:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

        state = (
            cv2.getTrackbarPos("Mode", WINDOW_NAME),
            cv2.getTrackbarPos("Low Threshold", WINDOW_NAME),
            cv2.getTrackbarPos("High Threshold", WINDOW_NAME),
            cv2.getTrackbarPos("Pre-Blur", WINDOW_NAME),
            cv2.getTrackbarPos("Derivative Kernel", WINDOW_NAME),
        )

        if state != last_state:
            frame = render_frame(preview_image, *state)
            cv2.imshow(WINDOW_NAME, frame)
            last_state = state

        key = cv2.waitKey(30) & 0xFF
        if key in (27, ord("q")):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
