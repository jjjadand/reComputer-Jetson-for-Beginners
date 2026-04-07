import cv2
import numpy as np
from typing import List, Optional, Tuple

from interactive_cv_utils import (
    PANEL_BACKGROUND,
    PANEL_GAP,
    ensure_color,
    fit_for_display,
    load_image_from_script_dir,
    noop,
    prepare_preview,
    resize_by_scale,
)


WINDOW_NAME = "Interactive Feature Matching Demo"
DETECTOR_NAMES = [
    "ORB",
    "AKAZE",
    "SIFT",
]
TITLE_BAR_HEIGHT = 24
SUPPORT_PANEL_HEIGHT = 110
MATCH_PANEL_HEIGHT = 235
DISPLAY_MAX_WIDTH = 860
DISPLAY_MAX_HEIGHT = 470
DISPLAY_MIN_WIDTH = 760
STATUS_FONT_SCALE = 0.62
STATUS_TEXT_THICKNESS = 1
STATUS_LINE_HEIGHT = 24
STATUS_PADDING_X = 12
STATUS_PADDING_Y = 10


def create_detector(detector_index: int, max_features: int):
    if detector_index == 0:
        return "ORB", cv2.ORB_create(nfeatures=max_features), cv2.NORM_HAMMING
    if detector_index == 1:
        return "AKAZE", cv2.AKAZE_create(), cv2.NORM_HAMMING
    return "SIFT", cv2.SIFT_create(nfeatures=max_features), cv2.NORM_L2


def keep_strongest_keypoints(keypoints, descriptors, max_features: int):
    if descriptors is None or not keypoints:
        return [], None

    if len(keypoints) <= max_features:
        return list(keypoints), descriptors

    sorted_indices = sorted(
        range(len(keypoints)),
        key=lambda index: keypoints[index].response,
        reverse=True,
    )[:max_features]
    reduced_keypoints = [keypoints[index] for index in sorted_indices]
    reduced_descriptors = descriptors[sorted_indices]
    return reduced_keypoints, reduced_descriptors


def scale_keypoints(keypoints, scale: float):
    scaled_keypoints = []
    for keypoint in keypoints:
        scaled_keypoints.append(
            cv2.KeyPoint(
                keypoint.pt[0] * scale,
                keypoint.pt[1] * scale,
                keypoint.size * scale,
                keypoint.angle,
                keypoint.response,
                keypoint.octave,
                keypoint.class_id,
            )
        )
    return scaled_keypoints


def resize_to_height(image: np.ndarray, target_height: int) -> Tuple[np.ndarray, float]:
    scale = target_height / float(image.shape[0])
    return resize_by_scale(image, scale), scale


def dim_image(image: np.ndarray, alpha: float = 0.72) -> np.ndarray:
    canvas = ensure_color(image)
    return cv2.addWeighted(canvas, alpha, np.zeros_like(canvas), 1.0 - alpha, 0)


def draw_header_bar(width: int, title: str) -> np.ndarray:
    bar = np.full((TITLE_BAR_HEIGHT, width, 3), PANEL_BACKGROUND, dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.72
    text_thickness = 1

    while font_scale > 0.42:
        text_size, _ = cv2.getTextSize(title, font, font_scale, text_thickness)
        if text_size[0] <= width - 20:
            break
        font_scale -= 0.05

    cv2.putText(
        bar,
        title,
        (10, 18),
        font,
        font_scale,
        (0, 0, 0),
        text_thickness + 2,
        cv2.LINE_AA,
    )
    cv2.putText(
        bar,
        title,
        (10, 18),
        font,
        font_scale,
        (240, 240, 240),
        text_thickness,
        cv2.LINE_AA,
    )
    return bar


def build_compact_status_panel(width: int, lines: List[str]) -> np.ndarray:
    font = cv2.FONT_HERSHEY_SIMPLEX
    max_text_width = max(120, width - STATUS_PADDING_X * 2)
    wrapped_lines: List[str] = []

    for line in lines:
        words = line.split(" ")
        if not words:
            wrapped_lines.append("")
            continue

        current = words[0]
        for word in words[1:]:
            candidate = current + " " + word
            candidate_size, _ = cv2.getTextSize(
                candidate,
                font,
                STATUS_FONT_SCALE,
                STATUS_TEXT_THICKNESS,
            )
            if candidate_size[0] <= max_text_width:
                current = candidate
            else:
                wrapped_lines.append(current)
                current = word
        wrapped_lines.append(current)

    panel_height = STATUS_PADDING_Y * 2 + len(wrapped_lines) * STATUS_LINE_HEIGHT
    panel = np.full((panel_height, width, 3), PANEL_BACKGROUND, dtype=np.uint8)

    for index, line in enumerate(wrapped_lines):
        y = STATUS_PADDING_Y + 16 + index * STATUS_LINE_HEIGHT
        cv2.putText(
            panel,
            line,
            (STATUS_PADDING_X, y),
            font,
            STATUS_FONT_SCALE,
            (0, 0, 0),
            STATUS_TEXT_THICKNESS + 2,
            cv2.LINE_AA,
        )
        cv2.putText(
            panel,
            line,
            (STATUS_PADDING_X, y),
            font,
            STATUS_FONT_SCALE,
            (235, 235, 235),
            STATUS_TEXT_THICKNESS,
            cv2.LINE_AA,
        )

    return panel


def build_titled_panel(title: str, image: np.ndarray) -> np.ndarray:
    display_image = ensure_color(image)
    return np.vstack([draw_header_bar(display_image.shape[1], title), display_image])


def pad_to_width(image: np.ndarray, width: int) -> np.ndarray:
    if image.shape[1] >= width:
        return image

    padded = np.full((image.shape[0], width, 3), PANEL_BACKGROUND, dtype=np.uint8)
    start_x = (width - image.shape[1]) // 2
    padded[:, start_x : start_x + image.shape[1]] = image
    return padded


def stack_horizontal(images: List[np.ndarray]) -> np.ndarray:
    height = max(image.shape[0] for image in images)
    panels = []
    for index, image in enumerate(images):
        if image.shape[0] < height:
            padded = np.full((height, image.shape[1], 3), PANEL_BACKGROUND, dtype=np.uint8)
            padded[: image.shape[0], : image.shape[1]] = image
            panels.append(padded)
        else:
            panels.append(image)

        if index != len(images) - 1:
            gap = np.full((height, PANEL_GAP, 3), PANEL_BACKGROUND, dtype=np.uint8)
            panels.append(gap)

    return np.hstack(panels)


def draw_detected_region(scene_image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    canvas = scene_image.copy()
    cv2.polylines(canvas, [np.int32(corners)], True, (0, 255, 0), 4, cv2.LINE_AA)
    return canvas


def build_feature_views(
    query_image: np.ndarray,
    scene_image: np.ndarray,
    detector_index: int,
    max_features_slider: int,
    ratio_slider: int,
    drawn_matches_slider: int,
    ransac_slider: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
    max_features = max(50, max_features_slider)
    ratio_threshold = max(0.4, ratio_slider / 100.0)
    max_drawn_matches = max(10, drawn_matches_slider)
    ransac_threshold = max(1.0, ransac_slider / 10.0)

    detector_name, detector, matcher_norm = create_detector(detector_index, max_features)
    query_gray = cv2.cvtColor(query_image, cv2.COLOR_BGR2GRAY)
    scene_gray = cv2.cvtColor(scene_image, cv2.COLOR_BGR2GRAY)

    query_keypoints, query_descriptors = detector.detectAndCompute(query_gray, None)
    scene_keypoints, scene_descriptors = detector.detectAndCompute(scene_gray, None)
    query_keypoints, query_descriptors = keep_strongest_keypoints(
        query_keypoints,
        query_descriptors,
        max_features,
    )
    scene_keypoints, scene_descriptors = keep_strongest_keypoints(
        scene_keypoints,
        scene_descriptors,
        max_features,
    )

    query_view = cv2.drawKeypoints(
        query_image,
        query_keypoints,
        None,
        color=(0, 255, 0),
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
    )
    scene_view = scene_image.copy()
    matches_view = np.full((MATCH_PANEL_HEIGHT, 900, 3), 20, dtype=np.uint8)

    if query_descriptors is None or scene_descriptors is None:
        mode_lines = [
            f"Detector: {detector_name}",
            f"Query keypoints: {len(query_keypoints)}",
            f"Scene keypoints: {len(scene_keypoints)}",
            "Good matches: 0",
            "Inlier count: 0",
            "Homography: failed",
            "Displayed: 0 failed",
        ]
        return query_view, scene_view, matches_view, mode_lines

    matcher = cv2.BFMatcher(matcher_norm)
    knn_matches = matcher.knnMatch(query_descriptors, scene_descriptors, k=2)
    good_matches = []
    for pair in knn_matches:
        if len(pair) < 2:
            continue
        first, second = pair
        if first.distance < ratio_threshold * second.distance:
            good_matches.append(first)

    good_matches = sorted(good_matches, key=lambda match: match.distance)
    homography = None
    inlier_count = 0
    inlier_matches = []
    projected_corners = None

    if len(good_matches) >= 4:
        source_points = np.float32(
            [query_keypoints[match.queryIdx].pt for match in good_matches]
        ).reshape(-1, 1, 2)
        target_points = np.float32(
            [scene_keypoints[match.trainIdx].pt for match in good_matches]
        ).reshape(-1, 1, 2)
        homography, mask = cv2.findHomography(
            source_points,
            target_points,
            cv2.RANSAC,
            ransac_threshold,
        )
        if mask is not None:
            inlier_count = int(mask.ravel().sum())
            inlier_matches = [
                match for match, is_inlier in zip(good_matches, mask.ravel().tolist()) if is_inlier
            ]

    if homography is not None:
        height, width = query_image.shape[:2]
        corners = np.float32(
            [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]]
        ).reshape(-1, 1, 2)
        projected_corners = cv2.perspectiveTransform(corners, homography)
        scene_view = draw_detected_region(scene_view, projected_corners)

    displayed_matches = inlier_matches[:max_drawn_matches] if inlier_matches else good_matches[:max_drawn_matches]

    query_match_image, query_match_scale = resize_to_height(query_image, MATCH_PANEL_HEIGHT)
    scene_match_image, scene_match_scale = resize_to_height(scene_image, MATCH_PANEL_HEIGHT)
    query_match_keypoints = scale_keypoints(query_keypoints, query_match_scale)
    scene_match_keypoints = scale_keypoints(scene_keypoints, scene_match_scale)
    query_match_base = dim_image(query_match_image)
    scene_match_base = dim_image(scene_match_image)
    if projected_corners is not None:
        scene_match_corners = projected_corners * scene_match_scale
        scene_match_base = draw_detected_region(scene_match_base, scene_match_corners)

    matches_view = cv2.drawMatches(
        query_match_base,
        query_match_keypoints,
        scene_match_base,
        scene_match_keypoints,
        displayed_matches,
        None,
        matchesThickness=2,
        matchColor=(0, 255, 255),
        singlePointColor=(255, 120, 0),
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )
    mode_lines = [
        f"Detector: {detector_name}",
        f"Query keypoints: {len(query_keypoints)}",
        f"Scene keypoints: {len(scene_keypoints)}",
        f"Good matches: {len(good_matches)}",
        f"Inlier count: {inlier_count}",
        f"Homography: {'success' if homography is not None else 'failed'}",
        f"Displayed: {len(displayed_matches)} {'inliers' if inlier_matches else 'best'}",
    ]
    return query_view, scene_view, matches_view, mode_lines


def render_frame(
    query_image: np.ndarray,
    scene_image: np.ndarray,
    detector_index: int,
    max_features_slider: int,
    ratio_slider: int,
    drawn_matches_slider: int,
    ransac_slider: int,
) -> np.ndarray:
    query_view, scene_view, matches_view, mode_lines = build_feature_views(
        query_image,
        scene_image,
        detector_index,
        max_features_slider,
        ratio_slider,
        drawn_matches_slider,
        ransac_slider,
    )

    ratio_threshold = max(0.4, ratio_slider / 100.0)
    max_features = max(50, max_features_slider)
    max_drawn_matches = max(10, drawn_matches_slider)
    ransac_threshold = max(1.0, ransac_slider / 10.0)
    status_lines = [
        f"{mode_lines[0]} | {mode_lines[1]} | {mode_lines[2]}",
        f"{mode_lines[3]} | {mode_lines[4]} | {mode_lines[5]} | {mode_lines[6]}",
        f"Features: {max_features} | Ratio: {ratio_threshold:.2f} | RANSAC: {ransac_threshold:.1f} | Drag sliders above, q/Esc quit.",
    ]

    query_support_view, _ = resize_to_height(query_view, SUPPORT_PANEL_HEIGHT)
    scene_support_view, _ = resize_to_height(scene_view, SUPPORT_PANEL_HEIGHT)
    top_row = stack_horizontal(
        [
            build_titled_panel("Query", query_support_view),
            build_titled_panel("Scene", scene_support_view),
        ]
    )
    match_panel = build_titled_panel("Matches", matches_view)
    canvas_width = max(top_row.shape[1], match_panel.shape[1], DISPLAY_MIN_WIDTH)
    top_row = pad_to_width(top_row, canvas_width)
    match_panel = pad_to_width(match_panel, canvas_width)
    status_panel = build_compact_status_panel(canvas_width, status_lines)
    return fit_for_display(
        np.vstack(
            [
                top_row,
                np.full((PANEL_GAP, canvas_width, 3), PANEL_BACKGROUND, dtype=np.uint8),
                match_panel,
                status_panel,
            ]
        ),
        max_width=DISPLAY_MAX_WIDTH,
        max_height=DISPLAY_MAX_HEIGHT,
    )


def main() -> None:
    query_image = load_image_from_script_dir(__file__, "imgs/feature.png")
    scene_image = load_image_from_script_dir(__file__, "imgs/test.png")
    scene_preview, preview_scale = prepare_preview(scene_image, max_width=1200)
    query_preview = resize_by_scale(query_image, preview_scale)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("Detector", WINDOW_NAME, 1, len(DETECTOR_NAMES) - 1, noop)
    cv2.createTrackbar("Features", WINDOW_NAME, 500, 1500, noop)
    cv2.createTrackbar("Ratio x100", WINDOW_NAME, 75, 95, noop)
    cv2.createTrackbar("Drawn", WINDOW_NAME, 40, 100, noop)
    cv2.createTrackbar("RANSAC x10", WINDOW_NAME, 40, 100, noop)

    last_state: Optional[Tuple[int, int, int, int, int]] = None

    while True:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

        state = (
            cv2.getTrackbarPos("Detector", WINDOW_NAME),
            cv2.getTrackbarPos("Features", WINDOW_NAME),
            cv2.getTrackbarPos("Ratio x100", WINDOW_NAME),
            cv2.getTrackbarPos("Drawn", WINDOW_NAME),
            cv2.getTrackbarPos("RANSAC x10", WINDOW_NAME),
        )

        if state != last_state:
            frame = render_frame(query_preview, scene_preview, *state)
            cv2.imshow(WINDOW_NAME, frame)
            last_state = state

        key = cv2.waitKey(30) & 0xFF
        if key in (27, ord("q")):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
