import cv2
import numpy as np
from typing import List, Optional, Tuple

from interactive_cv_utils import (
    build_canvas,
    ensure_color,
    load_image_from_script_dir,
    noop,
    odd_kernel_from_slider,
    optional_blur_kernel_from_slider,
    prepare_preview,
)


WINDOW_NAME = "Interactive Thresholding Demo"
THRESHOLD_MODE_NAMES = [
    "Binary",
    "Binary Inv",
    "Trunc",
    "ToZero",
    "ToZero Inv",
    "Adaptive Mean",
    "Adaptive Gaussian",
    "Otsu",
]


def apply_threshold(
    gray_image: np.ndarray,
    mode_index: int,
    threshold_value: int,
    max_value: int,
    block_slider: int,
    c_slider: int,
    blur_slider: int,
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    blur_kernel = optional_blur_kernel_from_slider(blur_slider)
    processed_gray = gray_image.copy()
    if blur_kernel > 0:
        processed_gray = cv2.GaussianBlur(processed_gray, (blur_kernel, blur_kernel), 0)

    block_size = odd_kernel_from_slider(block_slider, minimum=3)
    c_value = c_slider - 20

    if mode_index == 0:
        _, thresholded = cv2.threshold(
            processed_gray,
            threshold_value,
            max_value,
            cv2.THRESH_BINARY,
        )
        mode_lines = [
            "Current mode: Binary",
            "Active parameters: threshold value and max value.",
        ]
    elif mode_index == 1:
        _, thresholded = cv2.threshold(
            processed_gray,
            threshold_value,
            max_value,
            cv2.THRESH_BINARY_INV,
        )
        mode_lines = [
            "Current mode: Binary Inv",
            "Active parameters: threshold value and max value.",
        ]
    elif mode_index == 2:
        _, thresholded = cv2.threshold(
            processed_gray,
            threshold_value,
            max_value,
            cv2.THRESH_TRUNC,
        )
        mode_lines = [
            "Current mode: Trunc",
            "Active parameters: threshold value. Max value is ignored by OpenCV for truncation.",
        ]
    elif mode_index == 3:
        _, thresholded = cv2.threshold(
            processed_gray,
            threshold_value,
            max_value,
            cv2.THRESH_TOZERO,
        )
        mode_lines = [
            "Current mode: ToZero",
            "Active parameters: threshold value. Max value is ignored by OpenCV for ToZero.",
        ]
    elif mode_index == 4:
        _, thresholded = cv2.threshold(
            processed_gray,
            threshold_value,
            max_value,
            cv2.THRESH_TOZERO_INV,
        )
        mode_lines = [
            "Current mode: ToZero Inv",
            "Active parameters: threshold value. Max value is ignored by OpenCV for ToZero Inv.",
        ]
    elif mode_index == 5:
        thresholded = cv2.adaptiveThreshold(
            processed_gray,
            max_value,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            block_size,
            c_value,
        )
        mode_lines = [
            "Current mode: Adaptive Mean",
            "Active parameters: max value, block size, and C. Threshold slider is ignored.",
        ]
    elif mode_index == 6:
        thresholded = cv2.adaptiveThreshold(
            processed_gray,
            max_value,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            c_value,
        )
        mode_lines = [
            "Current mode: Adaptive Gaussian",
            "Active parameters: max value, block size, and C. Threshold slider is ignored.",
        ]
    else:
        otsu_value, thresholded = cv2.threshold(
            processed_gray,
            0,
            max_value,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )
        mode_lines = [
            "Current mode: Otsu",
            "Active parameters: max value only. Threshold, block size, and C are ignored.",
            f"Computed Otsu threshold: {otsu_value:.1f}",
        ]

    if blur_kernel == 0:
        mode_lines.append("Pre-blur: disabled.")
    else:
        mode_lines.append(f"Pre-blur kernel: {blur_kernel} x {blur_kernel}")

    return processed_gray, thresholded, mode_lines


def render_frame(
    image: np.ndarray,
    mode_index: int,
    threshold_value: int,
    max_value: int,
    block_slider: int,
    c_slider: int,
    blur_slider: int,
) -> np.ndarray:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_gray, thresholded, mode_lines = apply_threshold(
        gray_image,
        mode_index,
        threshold_value,
        max_value,
        block_slider,
        c_slider,
        blur_slider,
    )

    block_size = odd_kernel_from_slider(block_slider, minimum=3)
    c_value = c_slider - 20
    status_lines = [
        "Mode slider: 0 Binary | 1 Binary Inv | 2 Trunc | 3 ToZero | 4 ToZero Inv | 5 Adaptive Mean | 6 Adaptive Gaussian | 7 Otsu",
        f"Threshold slider: {threshold_value}",
        f"Max value slider: {max_value}",
        f"Block size slider: {block_slider} -> {block_size}",
        f"C slider: {c_slider} -> {c_value}",
        f"Pre-blur slider: {blur_slider} -> {optional_blur_kernel_from_slider(blur_slider)}",
        *mode_lines,
        "Controls: drag sliders to update in real time, press q or Esc to quit.",
    ]
    return build_canvas(
        [
            ("Original", image),
            ("Threshold Input", ensure_color(processed_gray)),
            ("Threshold Result", thresholded),
        ],
        status_lines,
    )


def main() -> None:
    image = load_image_from_script_dir(__file__, "imgs/test.png")
    preview_image, _ = prepare_preview(image)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 1500, 900)
    cv2.createTrackbar("Mode", WINDOW_NAME, 0, len(THRESHOLD_MODE_NAMES) - 1, noop)
    cv2.createTrackbar("Threshold", WINDOW_NAME, 127, 255, noop)
    cv2.createTrackbar("Max Value", WINDOW_NAME, 255, 255, noop)
    cv2.createTrackbar("Block Size", WINDOW_NAME, 4, 20, noop)
    cv2.createTrackbar("C Offset", WINDOW_NAME, 20, 40, noop)
    cv2.createTrackbar("Pre-Blur", WINDOW_NAME, 0, 10, noop)

    last_state: Optional[Tuple[int, int, int, int, int, int]] = None

    while True:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

        state = (
            cv2.getTrackbarPos("Mode", WINDOW_NAME),
            cv2.getTrackbarPos("Threshold", WINDOW_NAME),
            cv2.getTrackbarPos("Max Value", WINDOW_NAME),
            cv2.getTrackbarPos("Block Size", WINDOW_NAME),
            cv2.getTrackbarPos("C Offset", WINDOW_NAME),
            cv2.getTrackbarPos("Pre-Blur", WINDOW_NAME),
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
