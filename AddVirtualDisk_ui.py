"""
AddVirtualDisk - PySide6 GUI
在"此电脑"中添加自定义文件夹图标
"""

import sys, os
from typing import Optional, Dict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QMessageBox, QDialog, QLineEdit, QFileDialog,
    QStatusBar, QAbstractItemView, QStyleFactory,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon

from AddVirtualDisk import (
    add_virtual_folder, remove_virtual_folder,
    list_virtual_folders, refresh_explorer,
)


# ============================================================
# 添加/编辑对话框
# ============================================================

class AddEditDialog(QDialog):
    def __init__(self, parent=None, edit_data: Optional[Dict[str, str]] = None):
        super().__init__(parent)
        self.edit_data = edit_data
        self.is_edit = edit_data is not None
        self.setWindowTitle("编辑自定义文件夹" if self.is_edit else "添加自定义文件夹")
        self.setMinimumWidth(540)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 表单
        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如: 我的文档")
        self.name_edit.setText(self.edit_data.get("name", "") if self.is_edit else "")
        form.addRow("显示名称 *:", self.name_edit)

        # 目标路径 + 浏览按钮
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("例如: D:\\MyFolder")
        self.path_edit.setText(self.edit_data.get("target", "") if self.is_edit else "")
        browse_path_btn = QPushButton("浏览...")
        browse_path_btn.clicked.connect(lambda: self._browse_folder())
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_path_btn)
        form.addRow("目标路径 *:", path_widget)

        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("鼠标悬停时显示的提示信息")
        self.comment_edit.setText(self.edit_data.get("comment", "") if self.is_edit else "")
        form.addRow("备注:", self.comment_edit)

        # 图标路径 + 浏览按钮
        icon_widget = QWidget()
        icon_layout = QHBoxLayout(icon_widget)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("留空则使用默认文件夹图标")
        self.icon_edit.setText(self.edit_data.get("icon", "") if self.is_edit else "")
        browse_icon_btn = QPushButton("浏览...")
        browse_icon_btn.clicked.connect(lambda: self._browse_icon())
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(browse_icon_btn)
        form.addRow("图标路径:", icon_widget)

        layout.addLayout(form)

        # 帮助提示
        help_label = QLabel(
            "💡 图标路径可以是:\n"
            "  · .ico 文件路径，如 C:\\MyIcon.ico\n"
            "  · DLL/EXE 资源索引，如 C:\\Windows\\System32\\imageres.dll,-3\n"
            "  · 留空则用默认文件夹图标"
        )
        help_label.setStyleSheet("color: #888; font-size: 12px; padding: 8px;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        confirm_btn = QPushButton("确定")
        confirm_btn.setDefault(True)
        confirm_btn.clicked.connect(self._confirm)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
        if folder:
            self.path_edit.setText(folder)

    def _browse_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图标文件",
            "",
            "图标/程序 (*.ico *.dll *.exe);;所有文件 (*.*)"
        )
        if file_path:
            self.icon_edit.setText(file_path)

    def _confirm(self):
        name = self.name_edit.text().strip()
        target = self.path_edit.text().strip()
        comment = self.comment_edit.text().strip()
        icon = self.icon_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "错误", "显示名称不能为空")
            return
        if not target:
            QMessageBox.warning(self, "错误", "目标路径不能为空")
            return

        self.result_data = {
            "name": name,
            "target": target,
            "comment": comment,
            "icon": icon,
        }
        self.accept()


# ============================================================
# 主窗口
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AddVirtualDisk - 此电脑自定义文件夹管理")
        self.setMinimumSize(900, 620)
        self._build_ui()
        self.refresh_list()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 12, 16, 8)
        layout.setSpacing(10)

        # 标题
        title = QLabel("📁 \"此电脑\" - 自定义文件夹管理")
        title_font = QFont("Microsoft YaHei", 14, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # 按钮栏
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(6)

        add_btn = QPushButton("＋ 添加")
        add_btn.clicked.connect(self.show_add_dialog)
        btn_bar.addWidget(add_btn)

        edit_btn = QPushButton("✎ 编辑")
        edit_btn.clicked.connect(self.edit_selected)
        btn_bar.addWidget(edit_btn)

        delete_btn = QPushButton("✕ 删除")
        delete_btn.clicked.connect(self.delete_selected)
        btn_bar.addWidget(delete_btn)

        refresh_btn = QPushButton("↻ 刷新")
        refresh_btn.clicked.connect(self.refresh_list)
        btn_bar.addWidget(refresh_btn)

        btn_bar.addStretch()

        refresh_shell_btn = QPushButton("⟳ 刷新资源管理器")
        refresh_shell_btn.clicked.connect(self._refresh_shell)
        btn_bar.addWidget(refresh_shell_btn)

        layout.addLayout(btn_bar)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["显示名称", "GUID", "目标路径", "备注", "图标路径"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 200)
        self.table.doubleClicked.connect(self.edit_selected)

        layout.addWidget(self.table)

        # 状态栏
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("就绪")

    def refresh_list(self):
        self.table.setRowCount(0)
        try:
            folders = list_virtual_folders()
            self.table.setRowCount(len(folders))
            for row, f in enumerate(folders):
                self.table.setItem(row, 0, QTableWidgetItem(f["name"]))
                self.table.setItem(row, 1, QTableWidgetItem(f["guid"]))
                self.table.setItem(row, 2, QTableWidgetItem(f["target"]))
                self.table.setItem(row, 3, QTableWidgetItem(f["comment"]))
                self.table.setItem(row, 4, QTableWidgetItem(f["icon"]))
            self.status.showMessage(f"共 {len(folders)} 个自定义项")
        except Exception as e:
            self.status.showMessage(f"读取失败: {e}")

    def _refresh_shell(self):
        refresh_explorer()
        self.status.showMessage("已刷新 (可能需要手动 F5)")

    def _get_selected_row(self) -> int:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "提示", "请先选中一个项目")
            return -1
        return rows[0].row()

    def _get_row_data(self, row: int) -> Dict[str, str]:
        return {
            "name": self.table.item(row, 0).text() if self.table.item(row, 0) else "",
            "guid": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
            "target": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
            "comment": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
            "icon": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
        }

    # --- 操作 ---

    def show_add_dialog(self, edit_data: Dict[str, str] = None):
        dlg = AddEditDialog(self, edit_data)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.result_data
            try:
                is_edit = edit_data is not None
                if is_edit:
                    remove_virtual_folder(edit_data["guid"])
                    add_virtual_folder(data["name"], data["target"],
                                       data["comment"], data["icon"], edit_data["guid"])
                    self.status.showMessage(f"✅ 已更新: {data['name']}")
                else:
                    guid = add_virtual_folder(data["name"], data["target"],
                                              data["comment"], data["icon"])
                    self.status.showMessage(f"✅ 已添加: {data['name']}  GUID: {guid}")
                refresh_explorer()
                self.refresh_list()
            except Exception as e:
                QMessageBox.critical(self, "操作失败", str(e))

    def edit_selected(self):
        row = self._get_selected_row()
        if row < 0:
            return
        data = self._get_row_data(row)
        self.show_add_dialog(data)

    def delete_selected(self):
        row = self._get_selected_row()
        if row < 0:
            return
        data = self._get_row_data(row)
        reply = QMessageBox.question(
            self, "确认", f"删除「{data['name']}」?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            remove_virtual_folder(data["guid"])
            refresh_explorer()
            self.refresh_list()
            self.status.showMessage(f"🗑️ 已删除: {data['name']}")
        except Exception as e:
            QMessageBox.critical(self, "删除失败", str(e))


# ============================================================
# 入口
# ============================================================

def main():
    app = QApplication(sys.argv)
    # 使用 Fusion 风格，在现代 Windows 上更干净
    app.setStyle(QStyleFactory.create("Fusion"))

    # 全局样式表
    app.setStyleSheet("""
        QMainWindow {
            background: #f5f5f5;
        }
        QPushButton {
            padding: 6px 16px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #fafafa, stop:1 #e8e8e8);
            min-width: 80px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f0f0f0);
            border-color: #aaa;
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #e0e0e0, stop:1 #d0d0d0);
        }
        QTableWidget {
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            gridline-color: #eee;
            font-size: 13px;
        }
        QTableWidget::item {
            padding: 4px 8px;
        }
        QTableWidget::item:selected {
            background: #0078d4;
            color: white;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #fafafa, stop:1 #e8e8e8);
            border: none;
            border-bottom: 1px solid #ddd;
            border-right: 1px solid #ddd;
            padding: 6px 8px;
            font-weight: bold;
            font-size: 13px;
        }
        QLineEdit {
            padding: 5px 8px;
            border: 1px solid #ccc;
            border-radius: 3px;
            background: white;
        }
        QLineEdit:focus {
            border-color: #0078d4;
        }
        QStatusBar {
            background: #f0f0f0;
            border-top: 1px solid #ddd;
            font-size: 12px;
            padding: 2px 8px;
        }
        QLabel {
            font-size: 13px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
