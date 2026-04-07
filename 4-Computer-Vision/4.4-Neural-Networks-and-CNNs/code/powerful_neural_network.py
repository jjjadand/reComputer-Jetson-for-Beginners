from __future__ import annotations

import copy
import json
import queue
import random
import shutil
import threading
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


TORCH_IMPORT_ERROR: Optional[Exception] = None

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset

    TORCH_AVAILABLE = True
except Exception as exc:  # pragma: no cover - environment dependent
    torch = None  # type: ignore[assignment]
    nn = type("DummyNN", (), {"Module": object})()  # type: ignore[assignment]
    optim = None  # type: ignore[assignment]
    DataLoader = None  # type: ignore[assignment]
    Dataset = object  # type: ignore[assignment]
    TORCH_AVAILABLE = False
    TORCH_IMPORT_ERROR = exc


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
PYTORCH_GUIDE = (
    REPO_ROOT / "3-Basic-Tools-and-Getting-Started" / "3.5-Pytorch" / "README.md"
)
APP_TITLE = "Digit Classification With A Fully Connected Neural Network"
OUTPUT_ROOT = SCRIPT_DIR / "outputs" / "digit_mlp_demo"
DEMO_ROOT = SCRIPT_DIR / "demo_datasets" / "digit_mlp_demo"
IMAGE_SIZE = 28
INPUT_DIM = IMAGE_SIZE * IMAGE_SIZE
HIDDEN_DIMS = [256, 128]
RANDOM_SEED = 42
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}
PIL_RESAMPLING = getattr(Image, "Resampling", Image)


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def timestamp_string() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def set_global_seed(seed: int = RANDOM_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    if TORCH_AVAILABLE:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)


def ensure_torch_available() -> None:
    if TORCH_AVAILABLE:
        return
    detail = f"{TORCH_IMPORT_ERROR}" if TORCH_IMPORT_ERROR else "Unknown import error."
    raise RuntimeError(
        "PyTorch is not available in this environment.\n"
        f"Import error: {detail}\n"
        f"Please configure the JetPack 6.2 PyTorch environment first:\n{PYTORCH_GUIDE}"
    )


def preferred_device() -> "torch.device":
    ensure_torch_available()
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_demo_font(size: int) -> ImageFont.ImageFont:
    for font_name in ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "Arial.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(font_name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_digit_image(
    digit: int,
    rng: random.Random,
    image_size: int = IMAGE_SIZE,
    training: bool = True,
) -> Image.Image:
    canvas_size = 64
    canvas = Image.new("L", (canvas_size, canvas_size), 0)
    drawer = ImageDraw.Draw(canvas)

    font_size = rng.randint(34, 50) if training else rng.randint(36, 44)
    font = load_demo_font(font_size)
    text = str(digit)
    text_bbox = drawer.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x_pos = (canvas_size - text_width) // 2 + rng.randint(-8, 8)
    y_pos = (canvas_size - text_height) // 2 + rng.randint(-8, 8)
    drawer.text((x_pos, y_pos), text, fill=rng.randint(215, 255), font=font)

    if training:
        for _ in range(rng.randint(0, 6)):
            px = rng.randint(0, canvas_size - 1)
            py = rng.randint(0, canvas_size - 1)
            canvas.putpixel((px, py), rng.randint(50, 180))

    angle = rng.uniform(-28.0, 28.0) if training else rng.uniform(-15.0, 15.0)
    canvas = canvas.rotate(angle, resample=PIL_RESAMPLING.BILINEAR, fillcolor=0)

    if training and rng.random() < 0.4:
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=rng.uniform(0.15, 0.55)))

    array = np.asarray(canvas, dtype=np.float32)
    if training:
        generator = np.random.default_rng(rng.randint(0, 10_000_000))
        array += generator.normal(0.0, 12.0, size=array.shape)

    array = np.clip(array, 0.0, 255.0).astype(np.uint8)
    image = Image.fromarray(array, mode="L")
    image = ImageOps.autocontrast(image)
    image = image.resize((image_size, image_size), PIL_RESAMPLING.BILINEAR)
    return image


def generate_demo_digit_dataset(
    base_dir: Optional[Path] = None,
    train_per_class: int = 120,
) -> Dict[str, Any]:
    target_dir = base_dir or DEMO_ROOT
    if target_dir.exists():
        shutil.rmtree(target_dir)

    train_root = ensure_directory(target_dir / "train")

    for digit in range(10):
        class_dir = ensure_directory(train_root / str(digit))
        rng = random.Random(RANDOM_SEED + digit * 97)

        for index in range(train_per_class):
            image = render_digit_image(digit, rng, training=True)
            image.save(class_dir / f"{digit}_{index:03d}.png")

    metadata = {
        "dataset_root": str(train_root),
        "train_per_class": train_per_class,
        "image_size": IMAGE_SIZE,
    }
    (target_dir / "dataset_info.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {
        "dataset_root": train_root,
    }


def scan_digit_dataset(dataset_root: Path) -> Tuple[List[str], Dict[str, List[Path]]]:
    if not dataset_root.exists():
        raise ValueError(f"Dataset directory does not exist: {dataset_root}")
    if not dataset_root.is_dir():
        raise ValueError(f"Dataset path is not a directory: {dataset_root}")

    class_dirs = sorted(path for path in dataset_root.iterdir() if path.is_dir())
    if len(class_dirs) < 2:
        raise ValueError("Dataset must contain at least two class folders.")

    samples_by_class: Dict[str, List[Path]] = {}
    for class_dir in class_dirs:
        files = sorted(
            path for path in class_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        )
        if len(files) < 4:
            raise ValueError(f"Class '{class_dir.name}' must contain at least four image files.")
        samples_by_class[class_dir.name] = files

    return list(samples_by_class.keys()), samples_by_class


def stratified_split(
    samples_by_class: Dict[str, List[Path]],
    validation_ratio: float = 0.2,
    seed: int = RANDOM_SEED,
) -> Tuple[List[Tuple[Path, int]], List[Tuple[Path, int]]]:
    rng = random.Random(seed)
    train_samples: List[Tuple[Path, int]] = []
    val_samples: List[Tuple[Path, int]] = []

    for label_index, class_name in enumerate(sorted(samples_by_class.keys(), key=int)):
        class_files = list(samples_by_class[class_name])
        rng.shuffle(class_files)
        val_count = max(1, int(round(len(class_files) * validation_ratio)))
        val_count = min(val_count, len(class_files) - 1)
        val_subset = class_files[:val_count]
        train_subset = class_files[val_count:]
        if not train_subset or not val_subset:
            raise ValueError(f"Class '{class_name}' could not be split into train and validation subsets.")
        train_samples.extend((path, label_index) for path in train_subset)
        val_samples.extend((path, label_index) for path in val_subset)

    return train_samples, val_samples


def preprocess_digit_image(path: Path, image_size: int = IMAGE_SIZE) -> np.ndarray:
    image = Image.open(path).convert("L")
    return preprocess_digit_pil(image, image_size=image_size)


def normalize_digit_pil(image: Image.Image, image_size: int = IMAGE_SIZE) -> Image.Image:
    image = image.convert("L")
    image = image.resize((image_size, image_size), PIL_RESAMPLING.BILINEAR)
    array = np.asarray(image, dtype=np.float32)
    if float(array.mean()) > 127.0:
        image = ImageOps.invert(image)
        array = np.asarray(image, dtype=np.float32)
    image = ImageOps.autocontrast(image)
    array = np.asarray(image, dtype=np.uint8)

    active_pixels = np.argwhere(array > 20)
    if active_pixels.size == 0:
        return image

    y_min, x_min = active_pixels.min(axis=0)
    y_max, x_max = active_pixels.max(axis=0)
    cropped = array[y_min : y_max + 1, x_min : x_max + 1]

    side = max(cropped.shape[0], cropped.shape[1])
    square = np.zeros((side, side), dtype=np.uint8)
    y_offset = (side - cropped.shape[0]) // 2
    x_offset = (side - cropped.shape[1]) // 2
    square[y_offset : y_offset + cropped.shape[0], x_offset : x_offset + cropped.shape[1]] = cropped

    target_side = max(1, int(round(image_size * 0.78)))
    resized = Image.fromarray(square, mode="L").resize((target_side, target_side), PIL_RESAMPLING.BILINEAR)
    normalized = Image.new("L", (image_size, image_size), 0)
    paste_x = (image_size - target_side) // 2
    paste_y = (image_size - target_side) // 2
    normalized.paste(resized, (paste_x, paste_y))
    return ImageOps.autocontrast(normalized)


def preprocess_digit_pil(image: Image.Image, image_size: int = IMAGE_SIZE) -> np.ndarray:
    image = normalize_digit_pil(image, image_size=image_size)
    array = np.asarray(image, dtype=np.float32) / 255.0
    return array.reshape(-1)


def preview_image(path: Path, size: Tuple[int, int] = (180, 180)) -> Image.Image:
    image = Image.open(path).convert("L")
    return preview_pil_image(image, size=size)


def preview_pil_image(image: Image.Image, size: Tuple[int, int] = (180, 180)) -> Image.Image:
    image = image.convert("L")
    image = image.resize(size, PIL_RESAMPLING.NEAREST)
    image = ImageOps.expand(image, border=8, fill=15)
    return image.convert("RGB")


class FlattenedDigitDataset(Dataset):
    def __init__(self, samples: Sequence[Tuple[Path, int]], image_size: int = IMAGE_SIZE) -> None:
        self.samples = list(samples)
        self.image_size = image_size

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Tuple["torch.Tensor", int]:
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required to build the dataset.")

        path, label = self.samples[index]
        flat = preprocess_digit_image(path, self.image_size)
        return torch.tensor(flat, dtype=torch.float32), label


class SimpleFullyConnectedNet(nn.Module):
    def __init__(self, input_dim: int = INPUT_DIM, num_classes: int = 10) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, HIDDEN_DIMS[0]),
            nn.ReLU(inplace=True),
            nn.Linear(HIDDEN_DIMS[0], HIDDEN_DIMS[1]),
            nn.ReLU(inplace=True),
            nn.Linear(HIDDEN_DIMS[1], num_classes),
        )

    def forward(self, inputs: "torch.Tensor") -> "torch.Tensor":
        return self.network(inputs)


@dataclass
class RuntimeSession:
    model: Any
    device: Any
    class_names: List[str]
    dataset_root: str
    bundle_path: str
    summary_path: str
    best_validation_accuracy: float
    epoch_metrics: List[Dict[str, Any]]
    loss_points: List[Dict[str, float]]


def evaluate_model(
    model: "nn.Module",
    loader: "DataLoader",
    device: "torch.device",
    criterion: "nn.Module",
) -> Tuple[float, float]:
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_examples = 0

    with torch.no_grad():
        for inputs, targets in loader:
            inputs = inputs.to(device)
            targets = targets.to(device)
            logits = model(inputs)
            loss = criterion(logits, targets)
            total_loss += float(loss.item()) * targets.size(0)
            predictions = torch.argmax(logits, dim=1)
            total_correct += int((predictions == targets).sum().item())
            total_examples += int(targets.size(0))

    if total_examples == 0:
        return 0.0, 0.0
    return total_loss / total_examples, total_correct / total_examples


def save_training_artifacts(
    model: "nn.Module",
    class_names: List[str],
    dataset_root: Path,
    best_validation_accuracy: float,
    epoch_metrics: List[Dict[str, Any]],
    loss_points: List[Dict[str, float]],
    hyperparameters: Dict[str, Any],
    device_name: str,
) -> Tuple[str, str]:
    ensure_torch_available()
    output_dir = ensure_directory(OUTPUT_ROOT / f"run_{timestamp_string()}")
    bundle_path = output_dir / "digit_mlp_bundle.pt"
    summary_path = output_dir / "training_summary.json"

    payload = {
        "state_dict": copy.deepcopy(model.state_dict()),
        "class_names": class_names,
        "dataset_root": str(dataset_root),
        "best_validation_accuracy": best_validation_accuracy,
        "epoch_metrics": epoch_metrics,
        "loss_points": loss_points,
        "hyperparameters": hyperparameters,
        "device": device_name,
        "input_dim": INPUT_DIM,
        "hidden_dims": HIDDEN_DIMS,
        "image_size": IMAGE_SIZE,
    }
    torch.save(payload, bundle_path)

    summary_payload = {
        "weights_file": bundle_path.name,
        "class_names": class_names,
        "dataset_root": str(dataset_root),
        "best_validation_accuracy": best_validation_accuracy,
        "epoch_metrics": epoch_metrics,
        "loss_points": loss_points,
        "hyperparameters": hyperparameters,
        "device": device_name,
        "input_dim": INPUT_DIM,
        "hidden_dims": list(HIDDEN_DIMS),
        "image_size": IMAGE_SIZE,
        "total_epochs": len(epoch_metrics),
        "final_epoch": epoch_metrics[-1] if epoch_metrics else None,
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    return str(bundle_path), str(summary_path)


def train_digit_network(
    dataset_root: Path,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    event_callback: Optional[Any] = None,
) -> RuntimeSession:
    ensure_torch_available()
    set_global_seed(RANDOM_SEED)

    def emit(event_type: str, payload: Any) -> None:
        if event_callback is not None:
            event_callback(event_type, payload)

    class_names, samples_by_class = scan_digit_dataset(dataset_root)
    train_samples, val_samples = stratified_split(samples_by_class)
    train_dataset = FlattenedDigitDataset(train_samples)
    val_dataset = FlattenedDigitDataset(val_samples)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    device = preferred_device()
    model = SimpleFullyConnectedNet(input_dim=INPUT_DIM, num_classes=len(class_names)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    emit("log", f"Loaded {len(train_samples) + len(val_samples)} images across {len(class_names)} classes.")
    emit("log", f"Training samples: {len(train_samples)} | Validation samples: {len(val_samples)}")
    emit("log", f"Network structure: {INPUT_DIM} -> {HIDDEN_DIMS[0]} -> {HIDDEN_DIMS[1]} -> {len(class_names)}")

    total_steps = max(1, len(train_loader) * epochs)
    global_step = 0
    best_validation_accuracy = -1.0
    best_state = copy.deepcopy(model.state_dict())
    epoch_metrics: List[Dict[str, Any]] = []
    loss_points: List[Dict[str, float]] = []

    for epoch_index in range(epochs):
        model.train()
        epoch_loss_sum = 0.0
        epoch_correct = 0
        epoch_examples = 0

        for batch_index, (inputs, targets) in enumerate(train_loader, start=1):
            inputs = inputs.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            logits = model(inputs)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()

            predictions = torch.argmax(logits, dim=1)
            epoch_correct += int((predictions == targets).sum().item())
            epoch_examples += int(targets.size(0))
            epoch_loss_sum += float(loss.item()) * targets.size(0)

            global_step += 1
            point = {"step": float(global_step), "loss": float(loss.item())}
            loss_points.append(point)
            emit(
                "batch_loss",
                {
                    "point": point,
                    "epoch": epoch_index + 1,
                    "epochs": epochs,
                    "batch": batch_index,
                    "batches_per_epoch": len(train_loader),
                    "total_steps": total_steps,
                },
            )

        train_loss = epoch_loss_sum / max(1, epoch_examples)
        train_accuracy = epoch_correct / max(1, epoch_examples)
        val_loss, val_accuracy = evaluate_model(model, val_loader, device, criterion)

        epoch_info = {
            "epoch": epoch_index + 1,
            "train_loss": round(train_loss, 6),
            "train_accuracy": round(train_accuracy, 6),
            "val_loss": round(val_loss, 6),
            "val_accuracy": round(val_accuracy, 6),
        }
        epoch_metrics.append(epoch_info)

        emit(
            "epoch_end",
            {
                "epoch": epoch_index + 1,
                "epochs": epochs,
                "epoch_metrics": list(epoch_metrics),
                "best_validation_accuracy": max(best_validation_accuracy, val_accuracy),
            },
        )
        emit(
            "log",
            f"Epoch {epoch_index + 1}/{epochs} | "
            f"train loss {train_loss:.4f}, train acc {train_accuracy:.3f} | "
            f"val loss {val_loss:.4f}, val acc {val_accuracy:.3f}"
        )

        if val_accuracy >= best_validation_accuracy:
            best_validation_accuracy = val_accuracy
            best_state = copy.deepcopy(model.state_dict())
            emit("log", f"New best validation accuracy: {best_validation_accuracy * 100.0:.2f}%")

    model.load_state_dict(best_state)
    hyperparameters = {
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
    }
    bundle_path, summary_path = save_training_artifacts(
        model=model,
        class_names=class_names,
        dataset_root=dataset_root,
        best_validation_accuracy=best_validation_accuracy,
        epoch_metrics=epoch_metrics,
        loss_points=loss_points,
        hyperparameters=hyperparameters,
        device_name=str(device),
    )
    emit("log", f"Saved weights to: {bundle_path}")
    emit("log", f"Saved summary to: {summary_path}")

    return RuntimeSession(
        model=model,
        device=device,
        class_names=class_names,
        dataset_root=str(dataset_root),
        bundle_path=bundle_path,
        summary_path=summary_path,
        best_validation_accuracy=best_validation_accuracy,
        epoch_metrics=epoch_metrics,
        loss_points=loss_points,
    )


def load_runtime_session(bundle_path: Path) -> RuntimeSession:
    ensure_torch_available()
    payload = torch.load(bundle_path, map_location=preferred_device())
    class_names = list(payload["class_names"])
    model = SimpleFullyConnectedNet(input_dim=int(payload.get("input_dim", INPUT_DIM)), num_classes=len(class_names))
    device = preferred_device()
    model.load_state_dict(payload["state_dict"])
    model = model.to(device)
    model.eval()
    return RuntimeSession(
        model=model,
        device=device,
        class_names=class_names,
        dataset_root=str(payload.get("dataset_root", "")),
        bundle_path=str(bundle_path),
        summary_path=str(bundle_path.with_name("training_summary.json")),
        best_validation_accuracy=float(payload.get("best_validation_accuracy", 0.0)),
        epoch_metrics=list(payload.get("epoch_metrics", [])),
        loss_points=list(payload.get("loss_points", [])),
    )


def predict_digit(session: RuntimeSession, image_path: Path) -> Dict[str, Any]:
    ensure_torch_available()
    image = Image.open(image_path).convert("L")
    return predict_digit_from_pil(session, image, preview=preview_image(image_path))


def predict_digit_from_pil(
    session: RuntimeSession,
    image: Image.Image,
    preview: Optional[Image.Image] = None,
) -> Dict[str, Any]:
    ensure_torch_available()
    normalized = normalize_digit_pil(image, IMAGE_SIZE)
    flat = np.asarray(normalized, dtype=np.float32).reshape(-1) / 255.0
    inputs = torch.tensor(flat, dtype=torch.float32).unsqueeze(0).to(session.device)

    session.model.eval()
    with torch.no_grad():
        logits = session.model(inputs)
        probabilities = torch.softmax(logits, dim=1)[0].detach().cpu().numpy()

    top_index = int(np.argmax(probabilities))
    top_items = [
        {"label": session.class_names[index], "confidence": float(probabilities[index])}
        for index in np.argsort(probabilities)[::-1][:3]
    ]
    return {
        "predicted_label": session.class_names[top_index],
        "confidence": float(probabilities[top_index]),
        "top_items": top_items,
        "preview_image": preview if preview is not None else preview_pil_image(normalized),
    }


class DigitTeachingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1220x900")
        self.minsize(1100, 780)

        self.event_queue: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self.training_thread: Optional[threading.Thread] = None
        self.current_session: Optional[RuntimeSession] = None
        self.preview_photo: Optional[ImageTk.PhotoImage] = None
        self.loss_points: List[Dict[str, float]] = []
        self.sketch_canvas_size = 460
        self.sketch_line_width = 18
        self.sketch_last_point: Optional[Tuple[int, int]] = None
        self.sketch_image = Image.new("L", (self.sketch_canvas_size, self.sketch_canvas_size), 0)
        self.sketch_draw = ImageDraw.Draw(self.sketch_image)

        self.dataset_path_var = tk.StringVar()
        self.epochs_var = tk.StringVar(value="8")
        self.batch_size_var = tk.StringVar(value="64")
        self.learning_rate_var = tk.StringVar(value="0.001")
        self.status_var = tk.StringVar(value="Ready. Generate a digit dataset or select one from disk.")
        self.bundle_path_var = tk.StringVar(value="No trained weights loaded yet.")
        self.progress_value_var = tk.DoubleVar(value=0.0)
        self.progress_text_var = tk.StringVar(value="Training progress: idle")

        self._build_ui()
        self._reset_panels()
        self._announce_environment()
        self.after(120, self._poll_queue)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        controls = ttk.LabelFrame(self, text="Training Controls", padding=12)
        controls.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(7, weight=1)

        ttk.Label(controls, text="Dataset Root").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(controls, textvariable=self.dataset_path_var).grid(row=0, column=1, columnspan=5, sticky="ew")
        ttk.Button(controls, text="Browse", command=self._browse_dataset).grid(row=0, column=6, padx=(8, 0))
        self.generate_button = ttk.Button(
            controls,
            text="Generate Demo Digit Dataset",
            command=self._generate_demo_dataset,
        )
        self.generate_button.grid(row=0, column=7, sticky="ew", padx=(8, 0))

        ttk.Label(controls, text="Epochs").grid(row=1, column=0, sticky="w", pady=(12, 0))
        ttk.Entry(controls, textvariable=self.epochs_var, width=10).grid(row=1, column=1, sticky="w", pady=(12, 0))
        ttk.Label(controls, text="Batch Size").grid(row=1, column=2, sticky="w", padx=(16, 0), pady=(12, 0))
        ttk.Entry(controls, textvariable=self.batch_size_var, width=10).grid(row=1, column=3, sticky="w", pady=(12, 0))
        ttk.Label(controls, text="Learning Rate").grid(row=1, column=4, sticky="w", padx=(16, 0), pady=(12, 0))
        ttk.Entry(controls, textvariable=self.learning_rate_var, width=12).grid(row=1, column=5, sticky="w", pady=(12, 0))

        button_row = ttk.Frame(controls)
        button_row.grid(row=1, column=6, columnspan=2, sticky="ew", padx=(8, 0), pady=(12, 0))
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)
        self.train_button = ttk.Button(button_row, text="Train", command=self._start_training)
        self.train_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.load_button = ttk.Button(button_row, text="Load Weights", command=self._load_weights)
        self.load_button.grid(row=0, column=1, sticky="ew")

        self.progress_bar = ttk.Progressbar(
            controls,
            variable=self.progress_value_var,
            maximum=100.0,
            mode="determinate",
        )
        self.progress_bar.grid(row=2, column=0, columnspan=8, sticky="ew", pady=(12, 0))
        ttk.Label(controls, textvariable=self.progress_text_var, foreground="#475569").grid(
            row=3,
            column=0,
            columnspan=8,
            sticky="w",
            pady=(6, 0),
        )
        ttk.Label(
            controls,
            textvariable=self.status_var,
            wraplength=1120,
            foreground="#1d4ed8",
        ).grid(row=4, column=0, columnspan=8, sticky="w", pady=(8, 0))

        curve_frame = ttk.LabelFrame(self, text="Real-Time Loss Curve", padding=10)
        curve_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)
        curve_frame.columnconfigure(0, weight=1)
        curve_frame.rowconfigure(0, weight=1)
        self.loss_canvas = tk.Canvas(
            curve_frame,
            height=240,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#cbd5e1",
        )
        self.loss_canvas.grid(row=0, column=0, sticky="nsew")
        self.loss_canvas.bind("<Configure>", lambda _event: self._draw_loss_curve())

        bottom = ttk.Frame(self)
        bottom.grid(row=2, column=0, rowspan=2, sticky="nsew", padx=12, pady=(6, 12))
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=3)
        bottom.rowconfigure(0, weight=1)

        left_column = ttk.Frame(bottom)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_column.columnconfigure(0, weight=1)
        left_column.rowconfigure(0, weight=1)
        left_column.rowconfigure(1, weight=2)

        summary_frame = ttk.LabelFrame(left_column, text="Training Summary", padding=10)
        summary_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.rowconfigure(0, weight=1)
        self.summary_text = tk.Text(summary_frame, height=9, wrap="word", state="disabled")
        self.summary_text.grid(row=0, column=0, sticky="nsew")

        log_frame = ttk.LabelFrame(left_column, text="Training Log", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=18, wrap="word", state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        predict_frame = ttk.LabelFrame(bottom, text="Prediction Lab", padding=10)
        predict_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        predict_frame.columnconfigure(0, weight=5)
        predict_frame.columnconfigure(1, weight=3)
        predict_frame.rowconfigure(1, weight=1)

        ttk.Label(
            predict_frame,
            textvariable=self.bundle_path_var,
            wraplength=620,
            foreground="#334155",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        sketch_frame = ttk.LabelFrame(predict_frame, text="Handwriting Pad", padding=8)
        sketch_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        sketch_frame.columnconfigure(0, weight=1)
        sketch_frame.rowconfigure(2, weight=1)
        ttk.Label(
            sketch_frame,
            text="Draw one digit with the mouse. Handwriting is the only prediction input.",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        sketch_buttons = ttk.Frame(sketch_frame)
        sketch_buttons.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        sketch_buttons.columnconfigure(0, weight=1)
        sketch_buttons.columnconfigure(1, weight=1)
        self.clear_sketch_button = ttk.Button(
            sketch_buttons,
            text="Clear Sketch",
            command=self._clear_sketch_canvas,
        )
        self.clear_sketch_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.predict_sketch_button = ttk.Button(
            sketch_buttons,
            text="Predict Handwriting",
            command=self._predict_sketch_image,
            state="normal",
        )
        self.predict_sketch_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.sketch_canvas = tk.Canvas(
            sketch_frame,
            width=self.sketch_canvas_size,
            height=self.sketch_canvas_size,
            bg="#000000",
            highlightthickness=1,
            highlightbackground="#94a3b8",
            cursor="crosshair",
        )
        self.sketch_canvas.grid(row=2, column=0, sticky="nsew")
        self.sketch_canvas.bind("<ButtonPress-1>", self._start_sketch_stroke)
        self.sketch_canvas.bind("<B1-Motion>", self._draw_sketch_stroke)
        self.sketch_canvas.bind("<ButtonRelease-1>", self._end_sketch_stroke)

        preview_frame = ttk.Frame(predict_frame)
        preview_frame.grid(row=1, column=1, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        preview_frame.rowconfigure(2, weight=2)
        ttk.Label(
            preview_frame,
            text="Processed Preview And Prediction",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.preview_label = ttk.Label(preview_frame, anchor="center")
        self.preview_label.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        self.prediction_text = tk.Text(preview_frame, height=9, wrap="word", state="disabled")
        self.prediction_text.grid(row=2, column=0, sticky="nsew")

    def _announce_environment(self) -> None:
        ensure_directory(OUTPUT_ROOT)
        ensure_directory(DEMO_ROOT.parent)
        self._append_log("Simple digit-classification teaching demo is ready.")
        self._append_log("Network architecture: 784 -> 256 -> 128 -> 10")
        self._append_log("Demo dataset generator creates 28x28 grayscale digits for classes 0-9.")
        if TORCH_AVAILABLE:
            self._append_log(f"PyTorch detected. Preferred device: {preferred_device()}")
        else:
            self.status_var.set("PyTorch is missing. Training and prediction are disabled until it is installed.")
            self.train_button.configure(state="disabled")
            self.load_button.configure(state="disabled")
            self.predict_sketch_button.configure(state="disabled")
            self._append_log(f"PyTorch is missing. Please configure the environment first: {PYTORCH_GUIDE}")
            self.after(
                400,
                lambda: messagebox.showwarning(
                    "PyTorch Required",
                    "PyTorch is not available, so training and prediction are disabled.\n\n"
                    f"Please configure the JetPack 6.2 environment first:\n{PYTORCH_GUIDE}",
                ),
            )

    def _append_log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_text_widget_content(self, widget: tk.Text, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def _set_preview_image(self, image: Optional[Image.Image]) -> None:
        if image is None:
            self.preview_label.configure(image="", text="Preview appears here")
            self.preview_photo = None
            return
        self.preview_photo = ImageTk.PhotoImage(image)
        self.preview_label.configure(image=self.preview_photo, text="")

    def _reset_panels(self) -> None:
        self.loss_points = []
        self._draw_loss_curve()
        self._set_preview_image(None)
        self._clear_sketch_canvas()
        self._set_text_widget_content(
            self.summary_text,
            "Training summary will appear here.\n\n"
            "The live loss curve above updates during training, and the best validation accuracy will be shown here.",
        )
        self._set_text_widget_content(
            self.prediction_text,
            "Draw a digit on the handwriting pad, then click Predict Handwriting.",
        )

    def _browse_dataset(self) -> None:
        path = filedialog.askdirectory(
            title="Select Digit Dataset Root",
            initialdir=str(DEMO_ROOT if DEMO_ROOT.exists() else SCRIPT_DIR),
        )
        if path:
            self.dataset_path_var.set(path)
            self.status_var.set(f"Dataset selected: {path}")

    def _generate_demo_dataset(self) -> None:
        info = generate_demo_digit_dataset()
        self.dataset_path_var.set(str(info["dataset_root"]))
        self.status_var.set("Demo digit dataset generated. You can train immediately.")
        self._append_log(f"Generated demo dataset at {info['dataset_root']}")

    def _clear_sketch_canvas(self) -> None:
        self.sketch_canvas.delete("all")
        self.sketch_canvas.configure(bg="#000000")
        self.sketch_image = Image.new("L", (self.sketch_canvas_size, self.sketch_canvas_size), 0)
        self.sketch_draw = ImageDraw.Draw(self.sketch_image)
        self.sketch_last_point = None

    def _start_sketch_stroke(self, event: tk.Event) -> None:
        x_pos = int(event.x)
        y_pos = int(event.y)
        self.sketch_last_point = (x_pos, y_pos)
        radius = self.sketch_line_width // 2
        self.sketch_canvas.create_oval(
            x_pos - radius,
            y_pos - radius,
            x_pos + radius,
            y_pos + radius,
            fill="#ffffff",
            outline="#ffffff",
        )
        self.sketch_draw.ellipse(
            [x_pos - radius, y_pos - radius, x_pos + radius, y_pos + radius],
            fill=255,
            outline=255,
        )

    def _draw_sketch_stroke(self, event: tk.Event) -> None:
        x_pos = int(event.x)
        y_pos = int(event.y)
        if self.sketch_last_point is None:
            self._start_sketch_stroke(event)
            return

        last_x, last_y = self.sketch_last_point
        self.sketch_canvas.create_line(
            last_x,
            last_y,
            x_pos,
            y_pos,
            fill="#ffffff",
            width=self.sketch_line_width,
            capstyle=tk.ROUND,
            smooth=True,
        )
        self.sketch_draw.line(
            [last_x, last_y, x_pos, y_pos],
            fill=255,
            width=self.sketch_line_width,
        )
        radius = self.sketch_line_width // 2
        self.sketch_draw.ellipse(
            [x_pos - radius, y_pos - radius, x_pos + radius, y_pos + radius],
            fill=255,
            outline=255,
        )
        self.sketch_last_point = (x_pos, y_pos)

    def _end_sketch_stroke(self, _event: tk.Event) -> None:
        self.sketch_last_point = None

    def _update_progress(self, current_step: int, total_steps: int, message: str) -> None:
        if total_steps <= 0:
            self.progress_value_var.set(0.0)
        else:
            self.progress_value_var.set(max(0.0, min(100.0, (current_step / total_steps) * 100.0)))
        self.progress_text_var.set(message)

    def _draw_loss_curve(self) -> None:
        self.loss_canvas.delete("all")
        width = max(420, self.loss_canvas.winfo_width())
        height = max(280, self.loss_canvas.winfo_height())
        self.loss_canvas.create_rectangle(0, 0, width, height, fill="#ffffff", outline="")

        if not self.loss_points:
            self.loss_canvas.create_text(
                width / 2,
                height / 2,
                text="Loss values will appear here after training starts.",
                fill="#64748b",
                font=("Segoe UI", 12),
            )
            return

        margin_left = 54
        margin_right = 20
        margin_top = 24
        margin_bottom = 36
        plot_left = margin_left
        plot_right = width - margin_right
        plot_top = margin_top
        plot_bottom = height - margin_bottom

        losses = [float(point["loss"]) for point in self.loss_points]
        min_loss = min(losses)
        max_loss = max(losses)
        if abs(max_loss - min_loss) < 1e-6:
            min_loss -= 0.5
            max_loss += 0.5
        padding = (max_loss - min_loss) * 0.1
        min_loss -= padding
        max_loss += padding

        self.loss_canvas.create_rectangle(plot_left, plot_top, plot_right, plot_bottom, outline="#cbd5e1", width=1)
        self.loss_canvas.create_text(
            plot_left,
            8,
            anchor="nw",
            text="Mini-batch training loss",
            fill="#0f172a",
            font=("Segoe UI", 10, "bold"),
        )

        for tick_ratio in [0.0, 0.5, 1.0]:
            y = plot_bottom - tick_ratio * (plot_bottom - plot_top)
            tick_value = min_loss + tick_ratio * (max_loss - min_loss)
            self.loss_canvas.create_line(plot_left, y, plot_right, y, fill="#e2e8f0", dash=(2, 4))
            self.loss_canvas.create_text(
                plot_left - 8,
                y,
                anchor="e",
                text=f"{tick_value:.3f}",
                fill="#64748b",
                font=("Segoe UI", 8),
            )

        point_count = len(self.loss_points)
        xy_points: List[float] = []
        for index, point in enumerate(self.loss_points):
            if point_count == 1:
                x = (plot_left + plot_right) / 2
            else:
                x = plot_left + (index / (point_count - 1)) * (plot_right - plot_left)
            loss = float(point["loss"])
            y = plot_bottom - ((loss - min_loss) / (max_loss - min_loss)) * (plot_bottom - plot_top)
            xy_points.extend([x, y])

        if len(xy_points) >= 4:
            self.loss_canvas.create_line(*xy_points, fill="#2563eb", width=2, smooth=True)
        latest_x, latest_y = xy_points[-2], xy_points[-1]
        self.loss_canvas.create_oval(
            latest_x - 4,
            latest_y - 4,
            latest_x + 4,
            latest_y + 4,
            fill="#ef4444",
            outline="#ef4444",
        )
        self.loss_canvas.create_text(
            plot_right,
            plot_bottom + 18,
            anchor="e",
            text=f"steps: {point_count}",
            fill="#64748b",
            font=("Segoe UI", 8),
        )
        self.loss_canvas.create_text(
            latest_x,
            latest_y - 12,
            anchor="s",
            text=f"{losses[-1]:.4f}",
            fill="#1d4ed8",
            font=("Segoe UI", 8, "bold"),
        )
        self.loss_canvas.update_idletasks()

    def _render_summary(
        self,
        epoch_metrics: Sequence[Dict[str, Any]],
        best_validation_accuracy: float,
        bundle_path: Optional[str] = None,
        summary_path: Optional[str] = None,
    ) -> None:
        lines = [
            "Teaching Goal: understand how a simple fully connected network learns digit images.",
            f"Network: {INPUT_DIM} -> {HIDDEN_DIMS[0]} -> {HIDDEN_DIMS[1]} -> 10",
            f"Best validation accuracy: {best_validation_accuracy * 100.0:.2f}%",
        ]
        if epoch_metrics:
            latest = epoch_metrics[-1]
            lines.extend(
                [
                    f"Epochs finished: {len(epoch_metrics)}",
                    f"Latest train loss: {float(latest['train_loss']):.4f}",
                    f"Latest val loss: {float(latest['val_loss']):.4f}",
                    f"Latest train acc: {float(latest['train_accuracy']) * 100.0:.2f}%",
                    f"Latest val acc: {float(latest['val_accuracy']) * 100.0:.2f}%",
                ]
            )
        if bundle_path:
            lines.append(f"Weights: {bundle_path}")
        if summary_path:
            lines.append(f"Summary JSON: {summary_path}")
        self._set_text_widget_content(self.summary_text, "\n".join(lines))

    def _set_controls_for_training(self, training: bool) -> None:
        if not TORCH_AVAILABLE:
            return
        state = "disabled" if training else "normal"
        self.train_button.configure(state=state)
        self.load_button.configure(state=state)
        self.generate_button.configure(state=state)
        predict_state = "disabled" if training else "normal"
        self.predict_sketch_button.configure(state=predict_state)
        self.clear_sketch_button.configure(state=state)

    def _start_training(self) -> None:
        if self.training_thread and self.training_thread.is_alive():
            messagebox.showinfo("Training In Progress", "Please wait for the current training job to finish.")
            return

        try:
            ensure_torch_available()
            dataset_root = Path(self.dataset_path_var.get()).expanduser().resolve()
            epochs = int(self.epochs_var.get())
            batch_size = int(self.batch_size_var.get())
            learning_rate = float(self.learning_rate_var.get())
        except Exception as exc:
            messagebox.showerror("Invalid Settings", str(exc))
            return

        if epochs <= 0 or batch_size <= 0 or learning_rate <= 0:
            messagebox.showerror("Invalid Settings", "Epochs, batch size, and learning rate must all be positive.")
            return

        self.current_session = None
        self.bundle_path_var.set("Training in progress...")
        self.loss_points = []
        self._draw_loss_curve()
        self._render_summary([], 0.0)
        self.status_var.set("Training started. Watch the loss curve update in real time.")
        self._update_progress(0, 1, "Training progress: preparing data and model...")
        self._append_log(
            f"Starting training | dataset={dataset_root} | epochs={epochs}, batch_size={batch_size}, lr={learning_rate}"
        )
        self._set_controls_for_training(True)

        def worker() -> None:
            try:
                session = train_digit_network(
                    dataset_root=dataset_root,
                    epochs=epochs,
                    batch_size=batch_size,
                    learning_rate=learning_rate,
                    event_callback=lambda event_type, payload: self.event_queue.put((event_type, payload)),
                )
                self.event_queue.put(("train_complete", session))
            except Exception:
                self.event_queue.put(("train_error", traceback.format_exc()))

        self.training_thread = threading.Thread(target=worker, daemon=True)
        self.training_thread.start()

    def _load_weights(self) -> None:
        if not TORCH_AVAILABLE:
            return
        path = filedialog.askopenfilename(
            title="Load Saved Weights",
            initialdir=str(OUTPUT_ROOT if OUTPUT_ROOT.exists() else SCRIPT_DIR),
            filetypes=[("PyTorch Bundle", "*.pt"), ("All Files", "*.*")],
        )
        if not path:
            return

        try:
            session = load_runtime_session(Path(path))
        except Exception as exc:
            messagebox.showerror("Load Failed", str(exc))
            return

        self.current_session = session
        self.bundle_path_var.set(f"Loaded weights: {session.bundle_path}")
        self.loss_points = list(session.loss_points)
        self._draw_loss_curve()
        self._render_summary(
            session.epoch_metrics,
            session.best_validation_accuracy,
            session.bundle_path,
            session.summary_path,
        )
        self.status_var.set("Saved weights loaded. Draw a digit on the handwriting pad and click Predict Handwriting.")
        self._append_log(f"Loaded saved weights from {session.bundle_path}")
        self.predict_sketch_button.configure(state="normal")

    def _predict_sketch_image(self) -> None:
        if self.current_session is None:
            messagebox.showinfo("No Model", "Train the model or load saved weights before predicting.")
            return

        sketch_array = np.asarray(self.sketch_image, dtype=np.float32)
        if float(sketch_array.max()) < 12.0:
            messagebox.showinfo("Empty Sketch", "Please draw a digit on the handwriting pad first.")
            return

        try:
            prediction = predict_digit_from_pil(
                self.current_session,
                self.sketch_image,
            )
        except Exception as exc:
            messagebox.showerror("Prediction Failed", str(exc))
            return

        self._set_preview_image(prediction["preview_image"])
        lines = [
            "Prediction source: handwriting pad",
            f"Predicted digit: {prediction['predicted_label']}",
            f"Confidence: {prediction['confidence'] * 100.0:.2f}%",
            "",
            "Top probabilities:",
        ]
        for item in prediction["top_items"]:
            lines.append(f"- {item['label']}: {item['confidence'] * 100.0:.2f}%")
        self._set_text_widget_content(self.prediction_text, "\n".join(lines))
        self.status_var.set(
            f"Sketch prediction complete. The network thinks your drawing is {prediction['predicted_label']}."
        )
        self._append_log(
            f"Predicted sketch -> {prediction['predicted_label']} "
            f"({prediction['confidence'] * 100.0:.2f}%)"
        )

    def _poll_queue(self) -> None:
        while True:
            try:
                event_type, payload = self.event_queue.get_nowait()
            except queue.Empty:
                break

            if event_type == "log":
                self._append_log(str(payload))
            elif event_type == "batch_loss":
                point = payload["point"]
                self.loss_points.append(point)
                step = int(point["step"])
                self._update_progress(
                    step,
                    int(payload["total_steps"]),
                    f"Epoch {payload['epoch']}/{payload['epochs']} | "
                    f"Batch {payload['batch']}/{payload['batches_per_epoch']} | "
                    f"Loss {point['loss']:.4f}",
                )
                self._draw_loss_curve()
            elif event_type == "epoch_end":
                self._render_summary(
                    payload["epoch_metrics"],
                    float(payload["best_validation_accuracy"]),
                )
            elif event_type == "train_complete":
                session = payload
                self.current_session = session
                self.bundle_path_var.set(f"Latest weights: {session.bundle_path}")
                self._update_progress(
                    len(self.loss_points),
                    max(1, len(self.loss_points)),
                    f"Training complete. Best validation accuracy: {session.best_validation_accuracy * 100.0:.2f}%",
                )
                self._render_summary(
                    session.epoch_metrics,
                    session.best_validation_accuracy,
                    session.bundle_path,
                    session.summary_path,
                )
                self.status_var.set("Training finished. You can now draw a digit and use handwriting prediction.")
                self._append_log("Training completed successfully.")
                self.predict_sketch_button.configure(state="normal")
                self._set_controls_for_training(False)
            elif event_type == "train_error":
                self.status_var.set("Training failed. See the log for details.")
                self._append_log(str(payload))
                self._set_controls_for_training(False)
                messagebox.showerror("Training Failed", str(payload))

        self.after(120, self._poll_queue)


def main() -> None:
    set_global_seed(RANDOM_SEED)
    ensure_directory(OUTPUT_ROOT)
    ensure_directory(DEMO_ROOT.parent)
    app = DigitTeachingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
