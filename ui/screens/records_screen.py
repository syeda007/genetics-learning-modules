"""
UI Screen: Experimental Records Browser
Academic Genetics Research System (Postgraduate M.Sc. Genetics)
"""
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal

from data.experiment_store import ExperimentStore


class RecordsBrowserScreen(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, exp_store: ExperimentStore, parent=None):
        super().__init__(parent)
        self.exp_store = exp_store
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(8)

        # Header bar
        header_h = QHBoxLayout()
        btn_back = QPushButton("← BACK TO DASHBOARD", self)
        btn_back.clicked.connect(lambda: self.navigate_to.emit("dashboard"))
        header_h.addWidget(btn_back)
        
        title = QLabel("EXPERIMENTAL RECORDS & SCIENTIFIC REPRODUCIBILITY ARCHIVE", self)
        title.setStyleSheet("font-size: 13px; font-weight: 800; color: #0f172a;")
        header_h.addWidget(title)
        header_h.addStretch()

        btn_refresh = QPushButton("🔄 Refresh Index", self)
        btn_refresh.clicked.connect(self.reload_records)
        header_h.addWidget(btn_refresh)
        main_layout.addLayout(header_h)

        splitter = QSplitter(Qt.Horizontal, self)

        # Left Table of Records
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget(left_widget)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Timestamp", "Type", "Parents", "χ²", "Seed"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self._on_record_selected)
        left_layout.addWidget(self.table)
        splitter.addWidget(left_widget)

        # Right Inspector Panel
        right_frame = QFrame(self)
        right_frame.setObjectName("lab-card")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(4)
        
        insp_title = QLabel("RECORD INSPECTOR & REPRODUCIBILITY DATA (JSON)", right_frame)
        insp_title.setStyleSheet("color: #2563eb; font-weight: 700; font-size: 10px;")
        right_layout.addWidget(insp_title)

        self.inspector_text = QTextEdit(right_frame)
        self.inspector_text.setReadOnly(True)
        self.inspector_text.setStyleSheet("background-color: #ffffff; border: 1.5px solid #cbd5e1; color: #0f172a; font-family: monospace; font-size: 9px;")
        right_layout.addWidget(self.inspector_text)
        
        splitter.addWidget(right_frame)
        splitter.setSizes([450, 350])
        main_layout.addWidget(splitter)
        self.reload_records()

    def reload_records(self):
        records = self.exp_store.list_recent_experiments(limit=50)
        self.table.setRowCount(len(records))
        for r, rec in enumerate(records):
            self.table.setItem(r, 0, QTableWidgetItem(rec.get("experiment_id", "")))
            self.table.setItem(r, 1, QTableWidgetItem(rec.get("timestamp", "")[:19]))
            self.table.setItem(r, 2, QTableWidgetItem(rec.get("experiment_type", "")))
            self.table.setItem(r, 3, QTableWidgetItem(f"{rec.get('parent1','')} × {rec.get('parent2','')}"))
            self.table.setItem(r, 4, QTableWidgetItem(rec.get("chi2_stat", "N/A")))
            self.table.setItem(r, 5, QTableWidgetItem(rec.get("seed", "N/A")))

    def _on_record_selected(self):
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return
        row = self.table.currentRow()
        exp_id_item = self.table.item(row, 0)
        if not exp_id_item:
            return
        exp_id = exp_id_item.text()
        record_obj = self.exp_store.load_experiment(exp_id)
        if record_obj:
            from dataclasses import asdict
            self.inspector_text.setText(json.dumps(asdict(record_obj), indent=2))
        else:
            self.inspector_text.setText(f"Record {exp_id} not found on disk.")
