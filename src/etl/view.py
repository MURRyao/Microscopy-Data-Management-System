import io
import logging
from pathlib import Path

from PIL import Image as PILImage
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

_PREVIEW_PX = 400
_GENETIC_LINES = ["C57BL/6", "BALB/c", "DBA/2", "FVB/N", "129/Sv"]
_PREVIEWABLE = {".tif", ".tiff", ".png", ".jpg", ".jpeg"}


# ---------------------------------------------------------------------------
# Thin wrappers so controller.py keeps its .get() / .set() interface
# ---------------------------------------------------------------------------

class _StrVar:
    def __init__(self, widget):
        self._w = widget

    def get(self) -> str:
        if hasattr(self._w, "currentText"):
            return self._w.currentText()
        return self._w.text()

    def set(self, value: str):
        if hasattr(self._w, "setText"):
            self._w.setText(value)


class _BoolVar:
    def __init__(self, checkbox: QCheckBox):
        self._cb = checkbox

    def get(self) -> bool:
        return self._cb.isChecked()


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class ETLView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Microscopy ETL Uploader")
        self.setMinimumSize(960, 680)
        self._build_ui()
        self._expose_accessors()

    # ------------------------------------------------------------------ build

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("Microscopy ETL Uploader")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        # Horizontal splitter: form left, preview right
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, stretch=1)

        splitter.addWidget(self._build_form())
        splitter.addWidget(self._build_preview_panel())
        splitter.setSizes([560, _PREVIEW_PX + 40])

        # Upload button
        upload_btn = QPushButton("Загрузить в систему")
        upload_btn.setFixedHeight(44)
        btn_font = QFont()
        btn_font.setPointSize(11)
        btn_font.setBold(True)
        upload_btn.setFont(btn_font)
        upload_btn.setStyleSheet(
            "QPushButton          { background-color: #4CAF50; color: white;"
            "                       border-radius: 6px; }"
            "QPushButton:hover    { background-color: #45a049; }"
            "QPushButton:disabled { background-color: #aaa; }"
        )
        upload_btn.clicked.connect(self.controller.run_etl)
        root.addWidget(upload_btn)
        self._upload_btn = upload_btn

    def _build_form(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # ── File selection ────────────────────────────────────────────────
        file_group = QGroupBox("Изображение")
        file_vbox = QVBoxLayout(file_group)
        file_row = QHBoxLayout()

        self._file_edit = QLineEdit()
        self._file_edit.setPlaceholderText("Путь к файлу...")
        self._file_edit.setReadOnly(True)

        choose_btn = QPushButton("Выбрать файл")
        choose_btn.setFixedWidth(130)
        choose_btn.clicked.connect(self._on_choose_file)

        file_row.addWidget(self._file_edit)
        file_row.addWidget(choose_btn)
        file_vbox.addLayout(file_row)
        layout.addWidget(file_group)

        # ── Metadata ──────────────────────────────────────────────────────
        meta_group = QGroupBox("Метаданные")
        meta_layout = QVBoxLayout(meta_group)

        meta_layout.addWidget(QLabel("Название эксперимента:"))
        self._name_edit = QLineEdit()
        meta_layout.addWidget(self._name_edit)

        meta_layout.addWidget(QLabel("Генетическая линия:"))
        self._genetic_combo = QComboBox()
        self._genetic_combo.addItems(_GENETIC_LINES)
        meta_layout.addWidget(self._genetic_combo)

        sex_age_row = QHBoxLayout()

        sex_col = QVBoxLayout()
        sex_col.addWidget(QLabel("Пол:"))
        self._sex_combo = QComboBox()
        self._sex_combo.addItems(["male", "female"])
        sex_col.addWidget(self._sex_combo)

        age_col = QVBoxLayout()
        age_col.addWidget(QLabel("Возраст (нед.):"))
        self._age_edit = QLineEdit()
        self._age_edit.setPlaceholderText("напр. 12")
        age_col.addWidget(self._age_edit)

        sex_age_row.addLayout(sex_col)
        sex_age_row.addLayout(age_col)
        meta_layout.addLayout(sex_age_row)
        layout.addWidget(meta_group)

        # ── Structures ────────────────────────────────────────────────────
        struct_group = QGroupBox("Структуры")
        struct_layout = QVBoxLayout(struct_group)

        top_row = QHBoxLayout()
        self._cb_meninges = QCheckBox("Оболочки (meninges)")
        self._cb_brain = QCheckBox("Головной мозг (brain)")
        top_row.addWidget(self._cb_meninges)
        top_row.addWidget(self._cb_brain)
        top_row.addStretch()
        struct_layout.addLayout(top_row)

        men_group = QGroupBox("Уточнение оболочек")
        men_row = QHBoxLayout(men_group)
        self._cb_sss = QCheckBox("Верхний сагиттальный синус (SSS)")
        self._cb_confluence = QCheckBox("Слияние синусов")
        self._cb_transverse = QCheckBox("Поперечный синус")
        for cb in (self._cb_sss, self._cb_confluence, self._cb_transverse):
            men_row.addWidget(cb)
        men_row.addStretch()
        struct_layout.addWidget(men_group)

        brain_group = QGroupBox("Уточнение мозга")
        brain_row = QHBoxLayout(brain_group)
        self._cb_cortex = QCheckBox("Кора (cortex)")
        self._cb_thalamus = QCheckBox("Таламус")
        self._cb_hypothalamus = QCheckBox("Гипоталамус")
        for cb in (self._cb_cortex, self._cb_thalamus, self._cb_hypothalamus):
            brain_row.addWidget(cb)
        brain_row.addStretch()
        struct_layout.addWidget(brain_group)

        layout.addWidget(struct_group)
        layout.addStretch()
        return widget

    def _build_preview_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel("Предпросмотр")
        header_font = QFont()
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self._preview_label = QLabel("Файл не выбран")
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setMinimumSize(_PREVIEW_PX, _PREVIEW_PX)
        self._preview_label.setFrameShape(QFrame.StyledPanel)
        self._preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._preview_label.setWordWrap(True)
        layout.addWidget(self._preview_label, stretch=1)

        # File info shown below the preview image
        self._info_label = QLabel()
        self._info_label.setAlignment(Qt.AlignCenter)
        self._info_label.setWordWrap(True)
        self._info_label.setStyleSheet("color: #555; font-size: 11px;")
        layout.addWidget(self._info_label)

        return widget

    # ------------------------------------------------------------------ slots

    def _on_choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "TIFF files (*.tif *.tiff);;"
            "Microscope files (*.nd2);;"
            "Images (*.png *.jpg *.jpeg);;"
            "All files (*.*)",
        )
        if path:
            self._file_edit.setText(path)
            self._update_preview(path)

    def _update_preview(self, path: str):
        suffix = Path(path).suffix.lower()

        if suffix not in _PREVIEWABLE:
            self._preview_label.setPixmap(QPixmap())
            self._preview_label.setText(
                f"Предпросмотр недоступен\nдля формата «{suffix}»"
            )
            self._info_label.setText(self._file_info(path))
            return

        try:
            img = PILImage.open(path)
            img.seek(0)  # first frame for multi-page TIFFs
            img = img.convert("RGB")

            w, h = img.size
            try:
                resample = PILImage.Resampling.LANCZOS
            except AttributeError:
                resample = PILImage.LANCZOS  # Pillow < 10

            img.thumbnail((_PREVIEW_PX, _PREVIEW_PX), resample)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buf.read())
            self._preview_label.setPixmap(
                pixmap.scaled(
                    self._preview_label.width(),
                    self._preview_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
            self._info_label.setText(
                f"{Path(path).name}  •  {w} × {h} px\n{self._file_info(path)}"
            )
        except Exception as exc:
            logger.warning("Preview failed for %s: %s", path, exc)
            self._preview_label.setPixmap(QPixmap())
            self._preview_label.setText(f"Ошибка предпросмотра:\n{exc}")
            self._info_label.setText("")

    @staticmethod
    def _file_info(path: str) -> str:
        try:
            size_kb = Path(path).stat().st_size / 1024
            return f"{size_kb:.1f} KB"
        except OSError:
            return ""

    # ------------------------------------------------------------------ public API

    def choose_file(self) -> str:
        """Return the currently selected file path (controller compatibility)."""
        return self._file_edit.text()

    def show_error(self, message: str):
        QMessageBox.critical(self, "Ошибка", message)

    def show_success(self, message: str):
        QMessageBox.information(self, "Успех", message)

    # ------------------------------------------------------------------ accessors

    def _expose_accessors(self):
        """Expose Tkinter-style .get()/.set() wrappers so controller.py is unchanged."""
        self.file_path_var = _StrVar(self._file_edit)
        self.name_var = _StrVar(self._name_edit)
        self.genetic_line = _StrVar(self._genetic_combo)
        self.sex = _StrVar(self._sex_combo)
        self.age_weeks = _StrVar(self._age_edit)
        self.flags = {
            "meninges":             _BoolVar(self._cb_meninges),
            "brain":                _BoolVar(self._cb_brain),
            "sss":                  _BoolVar(self._cb_sss),
            "confluence_of_sinuses": _BoolVar(self._cb_confluence),
            "transverse_sinus":     _BoolVar(self._cb_transverse),
            "cortex":               _BoolVar(self._cb_cortex),
            "thalamus":             _BoolVar(self._cb_thalamus),
            "hypothalamus":         _BoolVar(self._cb_hypothalamus),
        }
