from typing import Optional
from PySide6.QtWidgets import QWidget

from src.filters.color import ColorFilter
from src.widgets.base_section import BaseSection
from src.widgets.labeled_slider import LabeledSlider


class ColorSection(BaseSection):
    """Collapsible section housing White Balance (Temperature and Tint) controls."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(title="White Balance & Color", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        # Temperature Slider: Blue -> Amber gradient
        self.temp_slider = LabeledSlider(
            name="Temperature",
            min_val=-100.0,
            max_val=100.0,
            default_val=0.0,
            scale=1.0,
            formatter=lambda v: f"Temp: {v:+.0f}" if v != 0 else "Temp: 0",
            track_colors=("#2563eb", "#eab308"),
            parent=self
        )
        self.temp_slider.valueChanged.connect(lambda _: self.adjustmentsChanged.emit())
        self.add_widget(self.temp_slider)

        # Tint Slider: Green -> Magenta gradient
        self.tint_slider = LabeledSlider(
            name="Tint",
            min_val=-100.0,
            max_val=100.0,
            default_val=0.0,
            scale=1.0,
            formatter=lambda v: f"Tint: {v:+.0f}" if v != 0 else "Tint: 0",
            track_colors=("#16a34a", "#c026d3"),
            parent=self
        )
        self.tint_slider.valueChanged.connect(lambda _: self.adjustmentsChanged.emit())
        self.add_widget(self.tint_slider)

    def get_filter(self) -> Optional[ColorFilter]:
        if not self.has_modifications():
            return None
        return ColorFilter(
            temperature=self.temp_slider.value,
            tint=self.tint_slider.value
        )

    def has_modifications(self) -> bool:
        return (
            abs(self.temp_slider.value) > 0.01 
            or abs(self.tint_slider.value) > 0.01
        )

    def reset_adjustments(self) -> None:
        self.temp_slider.reset()
        self.tint_slider.reset()
        self.adjustmentsChanged.emit()

    def set_enabled(self, enabled: bool) -> None:
        self.set_reset_enabled(enabled)
        self.temp_slider.set_enabled(enabled)
        self.tint_slider.set_enabled(enabled)