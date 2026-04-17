from __future__ import annotations

import os

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QLabel, QToolButton, QVBoxLayout, QWidget

ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")

TOOL_SEARCH = "search"
TOOL_HIGHLIGHT = "highlight"
TOOL_UNDERLINE = "underline"


def _icon(name: str) -> QIcon:
    path = os.path.join(ICON_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing rail icon: {name}")
    icon = QIcon(path)
    if icon.isNull():
        raise RuntimeError(f"Failed to load rail icon: {name}")
    return icon


class AppToolRail(QWidget):
    tool_selected = Signal(str)
    tool_deselected = Signal()
    fullscreen_requested = Signal()
    zoom_in_requested = Signal()
    zoom_out_requested = Signal()
    rotate_page_cw_requested = Signal()
    rotate_page_ccw_requested = Signal()
    rotate_doc_cw_requested = Signal()
    rotate_doc_ccw_requested = Signal()
    cancel_tool_requested = Signal()
    delete_annotation_requested = Signal()
    reset_annotations_requested = Signal()
    extract_pages_requested = Signal()
    split_requested = Signal()
    delete_pages_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._active_tool_name: str | None = None
        self.setObjectName("appToolRail")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(8)

        self.search_button = self._build_top_button(
            tool_name=TOOL_SEARCH,
            tooltip="Search (\u2318F)",
            icon=_icon("search_icon.png"),
        )
        self.highlight_button = self._build_top_button(
            tool_name=TOOL_HIGHLIGHT,
            tooltip="Highlight (H)",
            icon=_icon("highlighter_icon.png"),
        )
        self.underline_button = self._build_top_button(
            tool_name=TOOL_UNDERLINE,
            tooltip="Underline (U)",
            icon=_icon("underline_icon.png"),
        )
        self.top_buttons = {
            TOOL_SEARCH: self.search_button,
            TOOL_HIGHLIGHT: self.highlight_button,
            TOOL_UNDERLINE: self.underline_button,
        }
        for button in self.top_buttons.values():
            layout.addWidget(button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.top_divider = self._build_divider()
        layout.addWidget(self.top_divider)

        self.page_label = self._build_section_label("Page")
        layout.addWidget(self.page_label)
        self.rotate_page_cw_button = self._build_action_button(
            tooltip="Rotate Page 90\u00b0 CW",
            icon=_icon("icons8-rotate-right-48.png"),
        )
        self.rotate_page_ccw_button = self._build_action_button(
            tooltip="Rotate Page 90\u00b0 CCW",
            icon=_icon("icons8-rotate-left-48.png"),
        )
        self.rotate_page_cw_button.clicked.connect(self.rotate_page_cw_requested.emit)
        self.rotate_page_ccw_button.clicked.connect(self.rotate_page_ccw_requested.emit)
        layout.addWidget(self.rotate_page_cw_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.rotate_page_ccw_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.page_divider = self._build_divider()
        layout.addWidget(self.page_divider)

        self.doc_label = self._build_section_label("Doc")
        layout.addWidget(self.doc_label)
        self.rotate_doc_cw_button = self._build_action_button(
            tooltip="Rotate All Pages 90\u00b0 CW",
            icon=_icon("icons8-rotate-right-48.png"),
        )
        self.rotate_doc_ccw_button = self._build_action_button(
            tooltip="Rotate All Pages 90\u00b0 CCW",
            icon=_icon("icons8-rotate-left-48.png"),
        )
        self.rotate_doc_cw_button.clicked.connect(self.rotate_doc_cw_requested.emit)
        self.rotate_doc_ccw_button.clicked.connect(self.rotate_doc_ccw_requested.emit)
        layout.addWidget(self.rotate_doc_cw_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.rotate_doc_ccw_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.doc_divider = self._build_divider()
        layout.addWidget(self.doc_divider)

        self.editor_action_label = self._build_section_label("Edit")
        layout.addWidget(self.editor_action_label)
        self.extract_pages_button = self._build_action_button(
            tooltip="Extract Selected Pages",
            icon=_icon("icons8-extract-64.png"),
        )
        self.split_button = self._build_action_button(
            tooltip="Split by Page Range",
            icon=_icon("icons8-split-96.png"),
        )
        self.delete_pages_button = self._build_action_button(
            tooltip="Delete Selected Pages",
            icon=_icon("icons8-delete-96.png"),
        )
        self.extract_pages_button.clicked.connect(self.extract_pages_requested.emit)
        self.split_button.clicked.connect(self.split_requested.emit)
        self.delete_pages_button.clicked.connect(self.delete_pages_requested.emit)
        layout.addWidget(self.extract_pages_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.split_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.delete_pages_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.editor_action_divider = self._build_divider()
        layout.addWidget(self.editor_action_divider)

        self.cancel_tool_button = self._build_action_button(
            tooltip="Cancel Tool (Esc)",
            icon=_icon("icons8-cancel-96.png"),
        )
        self.delete_annotation_button = self._build_action_button(
            tooltip="Delete Selected Annotation",
            icon=_icon("icons8-delete-96.png"),
        )
        self.reset_annotations_button = self._build_action_button(
            tooltip="Reset Document Annotations",
            icon=_icon("icons8-reset-96.png"),
        )
        self.cancel_tool_button.clicked.connect(self.cancel_tool_requested.emit)
        self.delete_annotation_button.clicked.connect(self.delete_annotation_requested.emit)
        self.reset_annotations_button.clicked.connect(self.reset_annotations_requested.emit)
        layout.addWidget(self.cancel_tool_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.delete_annotation_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.reset_annotations_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.fullscreen_button = self._build_action_button(
            tooltip="Toggle Full Screen (F11)",
            icon=_icon("fullscreen_icon.png"),
        )
        self.fullscreen_button.clicked.connect(self.fullscreen_requested.emit)
        layout.addWidget(self.fullscreen_button, 0, Qt.AlignmentFlag.AlignHCenter)

        self.utility_divider = self._build_divider()
        layout.addWidget(self.utility_divider)

        self.zoom_in_button = self._build_action_button(
            tooltip="Zoom In (\u2318+)",
            icon=_icon("icons8-zoom-in-48.png"),
        )
        self.zoom_out_button = self._build_action_button(
            tooltip="Zoom Out (\u2318-)",
            icon=_icon("icons8-zoom-out-48.png"),
        )
        self.zoom_in_button.clicked.connect(self.zoom_in_requested.emit)
        self.zoom_out_button.clicked.connect(self.zoom_out_requested.emit)
        layout.addWidget(self.zoom_in_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.zoom_out_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)

        self.setFixedWidth(52)
        self.setStyleSheet(
            """
            QWidget#appToolRail {
                background-color: #3a3f46;
                border-left: 1px solid #4a5058;
            }
            QWidget#appToolRail QToolButton {
                border: 1px solid #444b54;
                border-radius: 10px;
                background-color: transparent;
                padding: 0px;
            }
            QWidget#appToolRail QToolButton:hover {
                background-color: #444b54;
                border-color: #454c53;
            }
            QWidget#appToolRail QToolButton:checked {
                background-color: #444b54;
                border-color: #7a8794;
            }
            """
        )

    def set_mode(self, mode: str) -> None:
        self.set_active_tool(None)

        is_viewer = mode == "viewer"
        is_editor = mode == "editor"
        is_home = mode == "home"

        self.search_button.setVisible(is_viewer)
        self.highlight_button.setVisible(is_viewer)
        self.underline_button.setVisible(is_viewer)

        shared_visible = is_viewer or is_editor
        self.page_label.setVisible(shared_visible)
        self.rotate_page_cw_button.setVisible(shared_visible)
        self.rotate_page_ccw_button.setVisible(shared_visible)
        self.doc_label.setVisible(shared_visible)
        self.rotate_doc_cw_button.setVisible(shared_visible)
        self.rotate_doc_ccw_button.setVisible(shared_visible)
        self.cancel_tool_button.setVisible(shared_visible)
        self.delete_annotation_button.setVisible(shared_visible)
        self.reset_annotations_button.setVisible(shared_visible)
        self.fullscreen_button.setVisible(shared_visible)
        self.zoom_in_button.setVisible(shared_visible)
        self.zoom_out_button.setVisible(shared_visible)

        self.top_divider.setVisible(not is_home)
        self.page_divider.setVisible(not is_home)
        self.doc_divider.setVisible(not is_home)
        self.editor_action_divider.setVisible(is_editor)
        self.utility_divider.setVisible(not is_home)

        if is_home:
            self.top_divider.setVisible(False)
            self.page_divider.setVisible(False)
            self.doc_divider.setVisible(False)
            self.editor_action_divider.setVisible(False)
            self.utility_divider.setVisible(False)

        self.editor_action_label.setVisible(is_editor)
        self.extract_pages_button.setVisible(is_editor)
        self.split_button.setVisible(is_editor)
        self.delete_pages_button.setVisible(is_editor)

        self.cancel_tool_button.setVisible(is_viewer)
        self.delete_annotation_button.setVisible(is_viewer)
        self.reset_annotations_button.setVisible(is_viewer)

    def set_active_tool(self, tool_name: str | None) -> None:
        self._active_tool_name = tool_name if tool_name in self.top_buttons else None
        for name, button in self.top_buttons.items():
            button.blockSignals(True)
            button.setChecked(name == self._active_tool_name)
            button.blockSignals(False)

    def active_tool(self) -> str | None:
        return self._active_tool_name

    def _build_top_button(self, tool_name: str, tooltip: str, icon: QIcon) -> QToolButton:
        button = self._build_action_button(tooltip=tooltip, icon=icon)
        button.setCheckable(True)
        button.clicked.connect(lambda checked, name=tool_name: self._handle_top_button_clicked(name, checked))
        return button

    @staticmethod
    def _build_action_button(tooltip: str, icon: QIcon) -> QToolButton:
        button = QToolButton()
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        button.setFixedSize(40, 40)
        button.setIcon(icon)
        button.setIconSize(QSize(24, 24))
        button.setToolTip(tooltip)
        return button

    @staticmethod
    def _build_section_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        label.setStyleSheet("color: #cfcfcf; font-size: 9pt; padding-top: 2px; padding-bottom: 2px;")
        return label

    @staticmethod
    def _build_divider() -> QFrame:
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Plain)
        divider.setStyleSheet("color: #3d4349;")
        return divider

    def _handle_top_button_clicked(self, tool_name: str, checked: bool) -> None:
        if checked:
            previous_tool = self._active_tool_name
            if previous_tool is not None and previous_tool != tool_name:
                self.tool_deselected.emit()
            self.set_active_tool(tool_name)
            self.tool_selected.emit(tool_name)
            return
        self.set_active_tool(None)
        self.tool_deselected.emit()
