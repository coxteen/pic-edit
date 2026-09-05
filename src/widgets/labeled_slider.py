from typing import Callable, Optional, Tuple, Union
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget


class LabeledSlider(QWidget):
    """
    Modular slider widget with value display, double-click reset,
    and optional custom track coloring (solid color or two-color linear gradient).
    """

    valueChanged = Signal(float)

    def __init__(
        self,
        name: str,
        min_val: float,
        max_val: float,
        default_val: float = 0.0,
        scale: float = 1.0,
        formatter: Optional[Callable[[float], str]] = None,
        track_colors: Optional[Union[str, Tuple[str, str]]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.default_val = float(default_val)
        self._default_float = float(default_val)  # Alias for general_section compatibility
        self.scale = scale
        self.formatter = formatter or (lambda v: f"{v:+.1f}" if v != 0 else "0.0")
        self.track_colors = track_colors

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(2)

        # Header Row: Label name and numeric readout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.label_name = QLabel(self.name, self)
        self.label_name.setStyleSheet("color: #cccccc; font-size: 11px;")

        self.label_value = QLabel(self.formatter(self.default_val), self)
        self.label_value.setStyleSheet("color: #999999; font-size: 11px;")

        header_layout.addWidget(self.label_name)
        header_layout.addStretch()
        header_layout.addWidget(self.label_value)
        layout.addLayout(header_layout)

        # Slider Setup
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(int(round(self.min_val * self.scale)), int(round(self.max_val * self.scale)))
        self.slider.setValue(int(round(self.default_val * self.scale)))
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)

        self._apply_style()

        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)

    def _apply_style(self) -> None:
        if isinstance(self.track_colors, tuple) and len(self.track_colors) == 2:
            c1, c2 = self.track_colors
            groove_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c1}, stop:1 {c2})"
        elif isinstance(self.track_colors, str):
            groove_bg = self.track_colors
        else:
            groove_bg = "#3a3a3a"

        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background: {groove_bg};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: #e0e0e0;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
                border: 1px solid #1a1a1a;
            }}
            QSlider::handle:horizontal:hover {{
                background: #ffffff;
                border: 1px solid #3b82f6;
            }}
            QSlider::handle:horizontal:disabled {{
                background: #555555;
            }}
        """)

    def _on_slider_changed(self, raw_value: int) -> None:
        float_value = raw_value / self.scale
        self.label_value.setText(self.formatter(float_value))
        self.valueChanged.emit(float_value)

    @property
    def value(self) -> float:
        return self.slider.value() / self.scale

    @value.setter
    def value(self, val: float) -> None:
        self.slider.setValue(int(round(val * self.scale)))

    def is_modified(self) -> bool:
        return abs(self.value - self.default_val) > (0.5 / self.scale)

    def reset(self) -> None:
        self.value = self.default_val

    def set_enabled(self, enabled: bool) -> None:
        self.slider.setEnabled(enabled)
        color = "#cccccc" if enabled else "#666666"
        self.label_name.setStyleSheet(f"color: {color}; font-size: 11px;")
        self.label_value.setStyleSheet(f"color: {color}; font-size: 11px;")

    def mouseDoubleClickEvent(self, event) -> None:
        self.reset()
        super().mouseDoubleClickEvent(event)