import os
from typing import List, Sequence, Tuple

import cv2
import numpy as np


MAX_PREVIEW_WIDTH = 1200
MAX_DISPLAY_WIDTH = 1600
MAX_DISPLAY_HEIGHT = 900
PANEL_GAP = 8
PANEL_BACKGROUND = (18, 18, 18)
STATUS_FONT_SCALE = 0.95
STATUS_TEXT_THICKNESS = 2
STATUS_LINE_HEIGHT = 40
STATUS_TEXT_PADDING_X = 20
STATUS_TEXT_PADDING_Y = 22


def noop(_: int) -> None:
    pass


def load_image_from_script_dir(
    script_file: str,
    relative_path: str,
    flags: int = cv2.IMREAD_COLOR,
) -> np.ndarray:
    base_dir = os.path.dirname(script_file)
    image_path = os.path.join(base_dir, relative_path)
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Source image not found: {image_path}")

    image = cv2.imread(image_path, flags)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    return image


def resize_by_scale(image: np.ndarray, scale: float) -> np.ndarray:
    if scale == 1.0:
        return image.copy()

    interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=interpolation,
    )


def prepare_preview(
    image: np.ndarray,
    max_width: int = MAX_PREVIEW_WIDTH,
) -> Tuple[np.ndarray, float]:
    height, width = image.shape[:2]
    if width <= max_width:
        return image.copy(), 1.0

    scale = max_width / float(width)
    return resize_by_scale(image, scale), scale


def fit_for_display(
    image: np.ndarray,
    max_width: int = MAX_DISPLAY_WIDTH,
    max_height: int = MAX_DISPLAY_HEIGHT,
) -> np.ndarray:
    height, width = image.shape[:2]
    scale = min(max_width / float(width), max_height / float(height), 1.0)
    return resize_by_scale(image, scale)


def ensure_color(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 1:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image.copy()


def normalize_to_uint8(image: np.ndarray) -> np.ndarray:
    if image.dtype == np.uint8:
        return image.copy()

    normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    return normalized.astype(np.uint8)


def draw_corner_label(image: np.ndarray, text: str) -> np.ndarray:
    labeled = ensure_color(image)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.95, min(labeled.shape[:2]) / 600.0)
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
        (0, 0, 0),
        thickness + 2,
        cv2.LINE_AA,
    )
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


def wrap_text_lines(
    lines: Sequence[str],
    max_width: int,
    font: int,
    font_scale: float,
    thickness: int,
) -> List[str]:
    wrapped_lines: List[str] = []

    for line in lines:
        words = line.split(" ")
        if not words:
            wrapped_lines.append("")
            continue

        current = words[0]
        for word in words[1:]:
            candidate = current + " " + word
            candidate_width, _ = cv2.getTextSize(candidate, font, font_scale, thickness)
            if candidate_width[0] <= max_width:
                current = candidate
            else:
                wrapped_lines.append(current)
                current = word
        wrapped_lines.append(current)

    return wrapped_lines


def build_status_panel(width: int, lines: Sequence[str]) -> np.ndarray:
    font = cv2.FONT_HERSHEY_SIMPLEX
    max_text_width = max(200, width - STATUS_TEXT_PADDING_X * 2)
    wrapped_lines = wrap_text_lines(
        lines,
        max_text_width,
        font,
        STATUS_FONT_SCALE,
        STATUS_TEXT_THICKNESS,
    )
    panel_height = STATUS_TEXT_PADDING_Y * 2 + len(wrapped_lines) * STATUS_LINE_HEIGHT
    panel = np.full((panel_height, width, 3), PANEL_BACKGROUND, dtype=np.uint8)

    for index, line in enumerate(wrapped_lines):
        y = STATUS_TEXT_PADDING_Y + 24 + index * STATUS_LINE_HEIGHT
        cv2.putText(
            panel,
            line,
            (STATUS_TEXT_PADDING_X, y),
            font,
            STATUS_FONT_SCALE,
            (0, 0, 0),
            STATUS_TEXT_THICKNESS + 2,
            cv2.LINE_AA,
        )
        cv2.putText(
            panel,
            line,
            (STATUS_TEXT_PADDING_X, y),
            font,
            STATUS_FONT_SCALE,
            (235, 235, 235),
            STATUS_TEXT_THICKNESS,
            cv2.LINE_AA,
        )

    return panel


def odd_kernel_from_slider(slider_value: int, minimum: int = 1) -> int:
    return max(minimum, slider_value * 2 + 1)


def optional_blur_kernel_from_slider(slider_value: int) -> int:
    if slider_value <= 0:
        return 0
    return slider_value * 2 + 1


def stack_panels(images: Sequence[np.ndarray]) -> np.ndarray:
    prepared = [ensure_color(image) for image in images]
    height = max(image.shape[0] for image in prepared)
    panels: List[np.ndarray] = []

    for index, image in enumerate(prepared):
        if image.shape[0] < height:
            padded = np.full((height, image.shape[1], 3), PANEL_BACKGROUND, dtype=np.uint8)
            padded[: image.shape[0], : image.shape[1]] = image
            panels.append(padded)
        else:
            panels.append(image)

        if index != len(prepared) - 1:
            gap = np.full((height, PANEL_GAP, 3), PANEL_BACKGROUND, dtype=np.uint8)
            panels.append(gap)

    return np.hstack(panels)


def build_canvas(
    labeled_panels: Sequence[Tuple[str, np.ndarray]],
    status_lines: Sequence[str],
) -> np.ndarray:
    panel_count = max(1, len(labeled_panels))
    target_panel_width = max(
        320,
        int((MAX_DISPLAY_WIDTH - PANEL_GAP * (panel_count - 1)) / float(panel_count)),
    )

    resized_panels = []
    for label, image in labeled_panels:
        display_image = ensure_color(image)
        width = display_image.shape[1]
        if width > target_panel_width:
            scale = target_panel_width / float(width)
            display_image = resize_by_scale(display_image, scale)
        resized_panels.append(draw_corner_label(display_image, label))

    comparison = stack_panels(resized_panels)
    panel = build_status_panel(comparison.shape[1], status_lines)
    return fit_for_display(np.vstack([comparison, panel]))
