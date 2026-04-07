import os
from typing import List, Optional, Tuple

import cv2
import numpy as np


WINDOW_NAME = "Interactive Filtering Demo"
FILTER_NAMES = [
    "Original",
    "Mean Blur",
    "Gaussian Blur",
    "Median Blur",
    "Bilateral Filter",
    "Sharpen",
]
MAX_PREVIEW_WIDTH = 1200
MAX_DISPLAY_WIDTH = 1600
MAX_DISPLAY_HEIGHT = 900


def noop(_: int) -> None:
    pass


def prepare_preview(image: np.ndarray, max_width: int = MAX_PREVIEW_WIDTH) -> np.ndarray:
    height, width = image.shape[:2]
    if width <= max_width:
        return image.copy()

    scale = max_width / float(width)
    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_AREA,
    )


def fit_for_display(
    image: np.ndarray,
    max_width: int = MAX_DISPLAY_WIDTH,
    max_height: int = MAX_DISPLAY_HEIGHT,
) -> np.ndarray:
    height, width = image.shape[:2]
    scale = min(max_width / float(width), max_height / float(height), 1.0)
    if scale == 1.0:
        return image

    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_AREA,
    )


def draw_corner_label(image: np.ndarray, text: str) -> np.ndarray:
    labeled = image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.8, min(labeled.shape[:2]) / 700.0)
    thickness = max(2, int(round(font_scale * 2)))
    padding = 14

    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    box_width = text_width + padding * 2
    box_height = text_height + baseline + padding * 2

    overlay = labeled.copy()
    cv2.rectangle(overlay, (12, 12), (12 + box_width, 12 + box_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, labeled, 0.45, 0, labeled)
    cv2.putText(
        labeled,
        text,
        (12 + padding, 12 + padding + text_height),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )
    return labeled


def build_status_panel(width: int, lines: List[str]) -> np.ndarray:
    panel_height = 24 + len(lines) * 34
    panel = np.full((panel_height, width, 3), (24, 24, 24), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX

    for index, line in enumerate(lines):
        y = 34 + index * 34
        cv2.putText(
            panel,
            line,
            (18, y),
            font,
            0.8,
            (235, 235, 235),
            2,
            cv2.LINE_AA,
        )

    return panel


def build_kernel_size(slider_value: int) -> int:
    return max(1, slider_value * 2 + 1)


def apply_selected_filter(
    image: np.ndarray,
    filter_index: int,
    kernel_slider: int,
    sigma_slider: int,
    strength_slider: int,
) -> Tuple[np.ndarray, List[str]]:
    kernel_size = build_kernel_size(kernel_slider)
    sigma_value = sigma_slider / 10.0
    strength_value = strength_slider / 10.0

    if filter_index == 0:
        return image.copy(), [
            "Current mode: Original",
            "No filtering is applied.",
        ]

    if filter_index == 1:
        filtered = cv2.blur(image, (kernel_size, kernel_size))
        return filtered, [
            "Current mode: Mean Blur",
            f"Kernel size: {kernel_size} x {kernel_size}",
        ]

    if filter_index == 2:
        filtered = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma_value)
        return filtered, [
            "Current mode: Gaussian Blur",
            f"Kernel size: {kernel_size} x {kernel_size}",
            f"Sigma: {sigma_value:.1f} (0.0 lets OpenCV infer it)",
        ]

    if filter_index == 3:
        filtered = cv2.medianBlur(image, kernel_size)
        return filtered, [
            "Current mode: Median Blur",
            f"Kernel size: {kernel_size} x {kernel_size}",
        ]

    if filter_index == 4:
        diameter = max(1, kernel_size)
        sigma_color = max(1.0, sigma_slider * 2.0)
        sigma_space = max(1.0, strength_slider * 2.0)
        filtered = cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)
        return filtered, [
            "Current mode: Bilateral Filter",
            f"Diameter: {diameter}",
            f"Sigma color: {sigma_color:.1f}",
            f"Sigma space: {sigma_space:.1f}",
        ]

    blur_sigma = sigma_value if sigma_value > 0 else kernel_size / 6.0
    amount = strength_value
    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), blur_sigma)
    filtered = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
    return filtered, [
        "Current mode: Sharpen",
        f"Blur kernel: {kernel_size} x {kernel_size}",
        f"Blur sigma: {blur_sigma:.1f}",
        f"Strength: {amount:.1f}",
    ]


def render_frame(
    source_image: np.ndarray,
    filter_index: int,
    kernel_slider: int,
    sigma_slider: int,
    strength_slider: int,
) -> np.ndarray:
    filtered_image, parameter_lines = apply_selected_filter(
        source_image,
        filter_index,
        kernel_slider,
        sigma_slider,
        strength_slider,
    )

    comparison = np.hstack(
        [
            draw_corner_label(source_image, "Original"),
            draw_corner_label(filtered_image, FILTER_NAMES[filter_index]),
        ]
    )

    status_lines = [
        "Mode slider: 0 Original | 1 Mean | 2 Gaussian | 3 Median | 4 Bilateral | 5 Sharpen",
        f"Kernel slider value: {kernel_slider} -> {build_kernel_size(kernel_slider)} x {build_kernel_size(kernel_slider)}",
        f"Sigma slider value: {sigma_slider} -> {sigma_slider / 10.0:.1f}",
        f"Strength slider value: {strength_slider} -> {strength_slider / 10.0:.1f}",
        *parameter_lines,
        "Controls: drag sliders to update in real time, press q or Esc to quit.",
    ]
    panel = build_status_panel(comparison.shape[1], status_lines)
    canvas = np.vstack([comparison, panel])
    return fit_for_display(canvas)


def main() -> None:
    base_dir = os.path.dirname(__file__)
    src_path = os.path.join(base_dir, "imgs", "test.png")
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source image not found: {src_path}")

    image = cv2.imread(src_path)
    if image is None:
        raise ValueError(f"Failed to load image: {src_path}")

    preview_image = prepare_preview(image)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 1400, 900)
    cv2.createTrackbar("Mode", WINDOW_NAME, 1, len(FILTER_NAMES) - 1, noop)
    cv2.createTrackbar("Kernel", WINDOW_NAME, 4, 15, noop)
    cv2.createTrackbar("Sigma x10", WINDOW_NAME, 20, 100, noop)
    cv2.createTrackbar("Strength x10", WINDOW_NAME, 15, 100, noop)

    last_state: Optional[Tuple[int, int, int, int]] = None

    while True:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

        state = (
            cv2.getTrackbarPos("Mode", WINDOW_NAME),
            cv2.getTrackbarPos("Kernel", WINDOW_NAME),
            cv2.getTrackbarPos("Sigma x10", WINDOW_NAME),
            cv2.getTrackbarPos("Strength x10", WINDOW_NAME),
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
