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


WINDOW_NAME = "Interactive Contours Demo"
THRESHOLD_SOURCE_NAMES = [
    "Binary",
    "Binary Inv",
    "Adaptive Mean",
    "Adaptive Gaussian",
    "Otsu",
]
CONTOUR_VIEW_NAMES = [
    "Contours",
    "Bounding Boxes",
    "Approx Polygons",
]


def build_binary_mask(
    gray_image: np.ndarray,
    threshold_mode: int,
    threshold_value: int,
    block_slider: int,
    c_slider: int,
) -> Tuple[np.ndarray, List[str]]:
    block_size = odd_kernel_from_slider(block_slider, minimum=3)
    c_value = c_slider - 20

    if threshold_mode == 0:
        _, mask = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)
        lines = [
            "Threshold source: Binary",
            "Active parameters: threshold value. Block size and C are ignored.",
        ]
    elif threshold_mode == 1:
        _, mask = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY_INV)
        lines = [
            "Threshold source: Binary Inv",
            "Active parameters: threshold value. Block size and C are ignored.",
        ]
    elif threshold_mode == 2:
        mask = cv2.adaptiveThreshold(
            gray_image,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            block_size,
            c_value,
        )
        lines = [
            "Threshold source: Adaptive Mean",
            "Active parameters: block size and C. Threshold slider is ignored.",
        ]
    elif threshold_mode == 3:
        mask = cv2.adaptiveThreshold(
            gray_image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            block_size,
            c_value,
        )
        lines = [
            "Threshold source: Adaptive Gaussian",
            "Active parameters: block size and C. Threshold slider is ignored.",
        ]
    else:
        otsu_value, mask = cv2.threshold(
            gray_image,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )
        lines = [
            "Threshold source: Otsu",
            "Active parameters: automatic threshold only. Threshold slider, block size, and C are ignored.",
            f"Computed Otsu threshold: {otsu_value:.1f}",
        ]

    return mask, lines


def build_contour_view(
    image: np.ndarray,
    threshold_mode: int,
    contour_mode: int,
    threshold_value: int,
    block_slider: int,
    c_slider: int,
    area_slider: int,
    epsilon_slider: int,
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    mask, threshold_lines = build_binary_mask(
        gray_image,
        threshold_mode,
        threshold_value,
        block_slider,
        c_slider,
    )

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    minimum_area = area_slider * 10.0
    epsilon_ratio = max(0.001, epsilon_slider / 1000.0)
    filtered_contours = [
        contour for contour in contours if cv2.contourArea(contour) >= minimum_area
    ]

    view = image.copy()
    if contour_mode == 0:
        cv2.drawContours(view, filtered_contours, -1, (0, 255, 0), 2)
        view_lines = [
            "Contour view: Contours",
            "Drawing the contour outline for each filtered object.",
        ]
    elif contour_mode == 1:
        for contour in filtered_contours:
            x, y, width, height = cv2.boundingRect(contour)
            cv2.rectangle(view, (x, y), (x + width, y + height), (0, 255, 255), 2)
        view_lines = [
            "Contour view: Bounding Boxes",
            "Drawing an axis-aligned rectangle around each filtered contour.",
        ]
    else:
        for contour in filtered_contours:
            perimeter = cv2.arcLength(contour, True)
            approximation = cv2.approxPolyDP(contour, epsilon_ratio * perimeter, True)
            cv2.polylines(view, [approximation], True, (255, 200, 0), 2)
        view_lines = [
            "Contour view: Approx Polygons",
            f"Polygon epsilon ratio: {epsilon_ratio:.3f}",
        ]

    summary_lines = [
        f"Contours found: {len(contours)}",
        f"Contours after min-area filter: {len(filtered_contours)}",
        f"Minimum contour area: {minimum_area:.1f}",
    ]
    return mask, view, threshold_lines + view_lines + summary_lines


def render_frame(
    image: np.ndarray,
    threshold_mode: int,
    contour_mode: int,
    threshold_value: int,
    block_slider: int,
    c_slider: int,
    area_slider: int,
    epsilon_slider: int,
) -> np.ndarray:
    mask, contour_view, mode_lines = build_contour_view(
        image,
        threshold_mode,
        contour_mode,
        threshold_value,
        block_slider,
        c_slider,
        area_slider,
        epsilon_slider,
    )

    block_size = odd_kernel_from_slider(block_slider, minimum=3)
    c_value = c_slider - 20
    epsilon_ratio = max(0.001, epsilon_slider / 1000.0)
    status_lines = [
        "Threshold mode slider: 0 Binary | 1 Binary Inv | 2 Adaptive Mean | 3 Adaptive Gaussian | 4 Otsu",
        "Contour view slider: 0 Contours | 1 Bounding Boxes | 2 Approx Polygons",
        f"Threshold slider: {threshold_value}",
        f"Block size slider: {block_slider} -> {block_size}",
        f"C slider: {c_slider} -> {c_value}",
        f"Min area slider: {area_slider} -> {area_slider * 10.0:.1f}",
        f"Epsilon slider: {epsilon_slider} -> {epsilon_ratio:.3f}",
        *mode_lines,
        "Controls: drag sliders to update in real time, press q or Esc to quit.",
    ]
    return build_canvas(
        [
            ("Original", image),
            ("Binary Mask", mask),
            (CONTOUR_VIEW_NAMES[contour_mode], contour_view),
        ],
        status_lines,
    )


def main() -> None:
    image = load_image_from_script_dir(__file__, "imgs/test.png")
    preview_image, _ = prepare_preview(image)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 1500, 900)
    cv2.createTrackbar("Threshold Mode", WINDOW_NAME, 4, len(THRESHOLD_SOURCE_NAMES) - 1, noop)
    cv2.createTrackbar("Contour View", WINDOW_NAME, 0, len(CONTOUR_VIEW_NAMES) - 1, noop)
    cv2.createTrackbar("Threshold", WINDOW_NAME, 150, 255, noop)
    cv2.createTrackbar("Block Size", WINDOW_NAME, 4, 20, noop)
    cv2.createTrackbar("C Offset", WINDOW_NAME, 20, 40, noop)
    cv2.createTrackbar("Min Area x10", WINDOW_NAME, 20, 500, noop)
    cv2.createTrackbar("Poly Eps x1000", WINDOW_NAME, 20, 100, noop)

    last_state: Optional[Tuple[int, int, int, int, int, int, int]] = None

    while True:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

        state = (
            cv2.getTrackbarPos("Threshold Mode", WINDOW_NAME),
            cv2.getTrackbarPos("Contour View", WINDOW_NAME),
            cv2.getTrackbarPos("Threshold", WINDOW_NAME),
            cv2.getTrackbarPos("Block Size", WINDOW_NAME),
            cv2.getTrackbarPos("C Offset", WINDOW_NAME),
            cv2.getTrackbarPos("Min Area x10", WINDOW_NAME),
            cv2.getTrackbarPos("Poly Eps x1000", WINDOW_NAME),
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
