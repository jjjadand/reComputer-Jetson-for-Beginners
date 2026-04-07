import cv2
import numpy as np
from typing import List, Optional, Tuple

from interactive_cv_utils import (
    build_canvas,
    load_image_from_script_dir,
    noop,
    odd_kernel_from_slider,
    prepare_preview,
)


WINDOW_NAME = "Interactive Morphology Demo"
MORPH_OPERATION_NAMES = [
    "Erode",
    "Dilate",
    "Opening",
    "Closing",
]
KERNEL_SHAPE_NAMES = [
    "Rect",
    "Ellipse",
    "Cross",
]


def build_structuring_element(shape_index: int, kernel_size: int) -> np.ndarray:
    shape_map = {
        0: cv2.MORPH_RECT,
        1: cv2.MORPH_ELLIPSE,
        2: cv2.MORPH_CROSS,
    }
    return cv2.getStructuringElement(shape_map.get(shape_index, cv2.MORPH_RECT), (kernel_size, kernel_size))


def apply_morphology(
    image,
    operation_index: int,
    threshold_value: int,
    kernel_slider: int,
    iterations_slider: int,
    shape_index: int,
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    _, mask = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY_INV)

    kernel_size = odd_kernel_from_slider(kernel_slider, minimum=1)
    iterations = max(1, iterations_slider)
    kernel = build_structuring_element(shape_index, kernel_size)

    if operation_index == 0:
        result = cv2.erode(mask, kernel, iterations=iterations)
    elif operation_index == 1:
        result = cv2.dilate(mask, kernel, iterations=iterations)
    elif operation_index == 2:
        result = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=iterations)
    else:
        result = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=iterations)

    mode_lines = [
        f"Current operation: {MORPH_OPERATION_NAMES[operation_index]}",
        "Binary mask source: fixed Binary Inv threshold on the grayscale image.",
        f"Kernel shape: {KERNEL_SHAPE_NAMES[shape_index]}",
        f"Kernel size: {kernel_size} x {kernel_size}",
        f"Iterations: {iterations}",
    ]
    return mask, result, mode_lines


def render_frame(
    image,
    operation_index: int,
    threshold_value: int,
    kernel_slider: int,
    iterations_slider: int,
    shape_index: int,
):
    mask, result, mode_lines = apply_morphology(
        image,
        operation_index,
        threshold_value,
        kernel_slider,
        iterations_slider,
        shape_index,
    )

    kernel_size = odd_kernel_from_slider(kernel_slider, minimum=1)
    iterations = max(1, iterations_slider)
    status_lines = [
        "Operation slider: 0 Erode | 1 Dilate | 2 Opening | 3 Closing",
        "Kernel shape slider: 0 Rect | 1 Ellipse | 2 Cross",
        f"Threshold slider: {threshold_value}",
        f"Kernel slider: {kernel_slider} -> {kernel_size}",
        f"Iterations slider: {iterations_slider} -> {iterations}",
        *mode_lines,
        "Controls: drag sliders to update in real time, press q or Esc to quit.",
    ]
    return build_canvas(
        [
            ("Original", image),
            ("Binary Mask", mask),
            (MORPH_OPERATION_NAMES[operation_index], result),
        ],
        status_lines,
    )


def main() -> None:
    image = load_image_from_script_dir(__file__, "imgs/test.png")
    preview_image, _ = prepare_preview(image)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 1500, 900)
    cv2.createTrackbar("Operation", WINDOW_NAME, 2, len(MORPH_OPERATION_NAMES) - 1, noop)
    cv2.createTrackbar("Threshold", WINDOW_NAME, 170, 255, noop)
    cv2.createTrackbar("Kernel Size", WINDOW_NAME, 2, 15, noop)
    cv2.createTrackbar("Iterations", WINDOW_NAME, 1, 10, noop)
    cv2.createTrackbar("Kernel Shape", WINDOW_NAME, 0, len(KERNEL_SHAPE_NAMES) - 1, noop)

    last_state: Optional[Tuple[int, int, int, int, int]] = None

    while True:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

        state = (
            cv2.getTrackbarPos("Operation", WINDOW_NAME),
            cv2.getTrackbarPos("Threshold", WINDOW_NAME),
            cv2.getTrackbarPos("Kernel Size", WINDOW_NAME),
            cv2.getTrackbarPos("Iterations", WINDOW_NAME),
            cv2.getTrackbarPos("Kernel Shape", WINDOW_NAME),
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
