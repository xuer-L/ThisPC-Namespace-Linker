"""
ThisPC‑Namespace‑Linker - PySide6 GUI
在 Windows 资源管理器中添加自定义文件夹图标
支持此电脑 / 桌面 / 网络位置，支持排序和副标题
支持中/英文语言切换
"""

import sys, os
from typing import Optional, Dict, Any

def _resource_path(relative_path: str) -> str:
    """获取资源文件路径，兼容开发环境和 PyInstaller 打包的 exe"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, relative_path)

from PySide6.QtWidgets import (

    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QMessageBox, QDialog, QLineEdit, QFileDialog,
    QStatusBar, QAbstractItemView, QStyleFactory, QComboBox, QSpinBox,
    QInputDialog,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QDesktopServices
from PySide6.QtCore import QUrl

from AddVirtualDisk import (
    add_virtual_folder, remove_virtual_folder,
    list_virtual_folders, refresh_explorer, LOCATIONS, VERSION,
    get_available_drive_letters, add_virtual_drive,
    remove_virtual_drive, list_virtual_drives,
)
from i18n import get_text, get_location_name, DEFAULT_LANG


# ============================================================
# 添加/编辑对话框
# ============================================================

class AddEditDialog(QDialog):
    def __init__(self, parent=None, edit_data: Optional[Dict[str, Any]] = None, lang: str = DEFAULT_LANG):
        super().__init__(parent)
        self.edit_data = edit_data
        self.is_edit = edit_data is not None
        self.lang = lang
        self.result_data: Optional[Dict[str, Any]] = None
        self.setWindowTitle(get_text(lang, "edit_title") if self.is_edit else get_text(lang, "add_title"))
        self.setMinimumWidth(580)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 表单
        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        T = lambda k, **kw: get_text(self.lang, k, **kw)

        # 显示名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(T("placeholder_name"))
        self.name_edit.setText(self.edit_data.get("name", "") if self.is_edit else "")
        form.addRow(T("label_name"), self.name_edit)

        # 副标题
        self.subtitle_edit = QLineEdit()
        self.subtitle_edit.setPlaceholderText(T("placeholder_subtitle"))
        self.subtitle_edit.setText(self.edit_data.get("subtitle", "") if self.is_edit else "")
        form.addRow(T("label_subtitle"), self.subtitle_edit)

        # 目标路径 + 浏览按钮
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(T("placeholder_target"))
        self.path_edit.setText(self.edit_data.get("target", "") if self.is_edit else "")
        browse_path_btn = QPushButton(T("browse"))
        browse_path_btn.clicked.connect(lambda: self._browse_folder())
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_path_btn)
        form.addRow(T("label_target"), path_widget)

        # 备注
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText(T("placeholder_comment"))
        self.comment_edit.setText(self.edit_data.get("comment", "") if self.is_edit else "")
        form.addRow(T("label_comment"), self.comment_edit)

        # 图标路径 + 浏览按钮
        icon_widget = QWidget()
        icon_layout = QHBoxLayout(icon_widget)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText(T("placeholder_icon"))
        self.icon_edit.setText(self.edit_data.get("icon", "") if self.is_edit else "")
        browse_icon_btn = QPushButton(T("browse"))
        browse_icon_btn.clicked.connect(lambda: self._browse_icon())
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(browse_icon_btn)
        form.addRow(T("label_icon"), icon_widget)

        # 目标位置
        self.location_combo = QComboBox()
        loc_names = list(LOCATIONS.keys())
        self.location_combo.addItems(loc_names)
        if self.is_edit:
            loc = self.edit_data.get("location", "此电脑")
            idx = self.location_combo.findText(loc)
            if idx >= 0:
                self.location_combo.setCurrentIndex(idx)
        form.addRow(T("label_location"), self.location_combo)

        # 排序索引
        self.sort_spin = QSpinBox()
        self.sort_spin.setRange(0, 999)
        self.sort_spin.setValue(self.edit_data.get("sort_order", 60) if self.is_edit else 60)
        self.sort_spin.setToolTip(T("tooltip_sort"))
        form.addRow(T("label_sort"), self.sort_spin)

        layout.addLayout(form)

        # 帮助提示
        help_label = QLabel(T("help_text"))
        help_label.setStyleSheet("color: #888; font-size: 12px; padding: 8px;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        confirm_btn = QPushButton(T("confirm"))
        confirm_btn.setDefault(True)
        confirm_btn.clicked.connect(self._confirm)
        cancel_btn = QPushButton(T("cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择目标文件夹" if self.lang == "zh" else "Select target folder")
        if folder:
            self.path_edit.setText(folder)

    def _browse_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图标文件" if self.lang == "zh" else "Select icon file",
            "",
            "Icon/Program (*.ico *.dll *.exe);;All Files (*.*)"
        )
        if file_path:
            self.icon_edit.setText(file_path)

    def _confirm(self):
        T = lambda k, **kw: get_text(self.lang, k, **kw)
        name = self.name_edit.text().strip()
        target = self.path_edit.text().strip()
        comment = self.comment_edit.text().strip()
        icon = self.icon_edit.text().strip()
        subtitle = self.subtitle_edit.text().strip()
        location = self.location_combo.currentText()
        sort_order = self.sort_spin.value()

        if not name:
            QMessageBox.warning(self, T("op_failed"), T("warn_empty_name"))
            return
        if not target:
            QMessageBox.warning(self, T("op_failed"), T("warn_empty_target"))
            return

        self.result_data = {
            "name": name,
            "target": target,
            "comment": comment,
            "icon": icon,
            "location": location,
            "sort_order": sort_order,
            "subtitle": subtitle,
        }
        self.accept()


# ============================================================
# 关于对话框
# ============================================================

class AboutDialog(QDialog):
    def __init__(self, parent=None, lang: str = DEFAULT_LANG):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(get_text(lang, "about_title"))
        self.setFixedSize(420, 380)
        self._build_ui()

    def _build_ui(self):
        T = lambda k, **kw: get_text(self.lang, k, **kw)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(24, 20, 24, 20)

        # Logo
        logo_path = _resource_path("logo.ico")

        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pix = QIcon(logo_path).pixmap(64, 64)
            logo_label.setPixmap(logo_pix)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        # 软件名称
        name_label = QLabel(T("app_name"))
        name_font = QFont("Microsoft YaHei", 18, QFont.Bold)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)


        # 版本号
        ver_label = QLabel(f"Version: {VERSION}")
        ver_label.setAlignment(Qt.AlignCenter)
        ver_label.setStyleSheet("color: #666; font-size: 13px;")
        layout.addWidget(ver_label)

        # 分隔
        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #ddd;")
        layout.addWidget(line)

        # 好好学习，天天向上
        motto = QLabel(T("motto"))
        motto.setAlignment(Qt.AlignCenter)
        motto_font = QFont("Microsoft YaHei", 12)
        motto.setFont(motto_font)
        motto.setStyleSheet("color: #555; padding: 6px;")
        layout.addWidget(motto)

        # 分隔
        line2 = QLabel()
        line2.setFixedHeight(1)
        line2.setStyleSheet("background: #ddd;")
        layout.addWidget(line2)

        # 开发者信息
        info = QLabel(T("developer"))
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #444; font-size: 12px; line-height: 1.6;")
        layout.addWidget(info)

        # 分隔
        line3 = QLabel()
        line3.setFixedHeight(1)
        line3.setStyleSheet("background: #ddd;")
        layout.addWidget(line3)

        # 隐私声明
        privacy = QLabel(T("privacy"))
        privacy.setAlignment(Qt.AlignCenter)
        privacy.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(privacy)

        # 博客超链接（独立行）
        blog_label = QLabel(
            '<a href="https://xuer.space" style="color: #0078d4; text-decoration: none;">'
            + T("blog") + "</a>"
        )
        blog_label.setAlignment(Qt.AlignCenter)
        blog_label.setTextFormat(Qt.RichText)
        blog_label.setOpenExternalLinks(True)
        blog_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(blog_label)


        layout.addStretch()

        # 确定按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton(T("confirm"))
        ok_btn.setFixedWidth(100)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)


# ============================================================
# 虚拟盘符对话框
# ============================================================

class DriveMapperDialog(QDialog):
    """管理 subst 虚拟盘符的对话框"""
    def __init__(self, parent=None, lang: str = DEFAULT_LANG):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(get_text(lang, "drive_mapper"))
        self.setMinimumSize(520, 380)
        self._build_ui()
        self._refresh_list()

    def T(self, key: str, **kwargs) -> str:
        return get_text(self.lang, key, **kwargs)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(
            ["盘符", "目标路径"] if self.lang == "zh" else ["Drive", "Target Path"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 80)
        layout.addWidget(self.table)

        # 按钮栏
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton(self.T("add"))
        self.add_btn.clicked.connect(self._add_drive)
        btn_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton(self.T("delete"))
        self.remove_btn.clicked.connect(self._remove_drive)
        btn_layout.addWidget(self.remove_btn)

        btn_layout.addStretch()

        self.close_btn = QPushButton(self.T("confirm"))
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

    def _refresh_list(self):
        self.table.setRowCount(0)
        drives = list_virtual_drives()
        self.table.setRowCount(len(drives))
        for row, d in enumerate(drives):
            self.table.setItem(row, 0, QTableWidgetItem(f"{d['letter']}:\\"))
            self.table.setItem(row, 1, QTableWidgetItem(d['target']))

    def _add_drive(self):
        letters = get_available_drive_letters()
        if not letters:
            QMessageBox.warning(
                self,
                "提示" if self.lang == "zh" else "Notice",
                "没有可用的盘符" if self.lang == "zh" else "No drive letters available",
            )
            return

        path = QFileDialog.getExistingDirectory(
            self,
            "选择目标文件夹" if self.lang == "zh" else "Select target folder",
        )
        if not path:
            return

        items = [f"{l}:\\" for l in letters]
        letter_item, ok = QInputDialog.getItem(
            self,
            "选择盘符" if self.lang == "zh" else "Select Drive Letter",
            "盘符:" if self.lang == "zh" else "Drive:",
            items, 0, False,
        )
        if not ok:
            return
        letter = letter_item.rstrip(":\\")

        try:
            add_virtual_drive(path, letter)
            self._refresh_list()
        except Exception as e:
            QMessageBox.critical(self, self.T("op_failed"), str(e))

    def _remove_drive(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, self.T("op_failed"), self.T("select_hint"))
            return
        letter = self.table.item(rows[0].row(), 0).text().rstrip(":\\")
        name = f"{letter}:\\"
        reply = QMessageBox.question(
            self, self.T("op_failed"),
            f"确定要取消映射 {name}?" if self.lang == "zh" else f"Remove mapping {name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            remove_virtual_drive(letter)
            self._refresh_list()
        except Exception as e:
            QMessageBox.critical(self, self.T("op_failed"), str(e))


# ============================================================
# 主窗口
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = DEFAULT_LANG  # 当前语言
        self.setWindowTitle(get_text(self.current_lang, "window_title"))
        self.setMinimumSize(1050, 680)
        self._build_ui()
        self.refresh_list()

    # ---- 语言工具 ----
    def T(self, key: str, **kwargs) -> str:
        return get_text(self.current_lang, key, **kwargs)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 12, 16, 8)
        layout.setSpacing(10)

        # 设置窗口图标
        logo_path = _resource_path("logo.ico")

        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # 标题
        self.title_label = QLabel("📁 " + self.T("window_title"))
        title_font = QFont("Microsoft YaHei", 14, QFont.Bold)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)


        # 按钮栏
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(6)

        self.add_btn = QPushButton(self.T("add"))
        self.add_btn.clicked.connect(lambda: self.show_add_dialog())
        btn_bar.addWidget(self.add_btn)


        self.edit_btn = QPushButton(self.T("edit"))
        self.edit_btn.clicked.connect(self.edit_selected)
        btn_bar.addWidget(self.edit_btn)

        self.delete_btn = QPushButton(self.T("delete"))
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_bar.addWidget(self.delete_btn)

        self.refresh_btn = QPushButton(self.T("refresh"))
        self.refresh_btn.clicked.connect(self.refresh_list)
        btn_bar.addWidget(self.refresh_btn)

        btn_bar.addStretch()

        self.refresh_shell_btn = QPushButton(self.T("refresh_shell"))
        self.refresh_shell_btn.clicked.connect(self._refresh_shell)
        btn_bar.addWidget(self.refresh_shell_btn)

        self.drive_btn = QPushButton(self.T("drive_mapper"))
        self.drive_btn.clicked.connect(self.show_drive_mapper)
        btn_bar.addWidget(self.drive_btn)

        self.about_btn = QPushButton(self.T("about"))
        self.about_btn.clicked.connect(self.show_about_dialog)
        btn_bar.addWidget(self.about_btn)

        # ---- 语言切换 ----
        btn_bar.addSpacing(12)
        self.lang_label = QLabel(self.T("language"))
        self.lang_label.setStyleSheet("font-size: 12px; color: #666;")
        btn_bar.addWidget(self.lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.setFixedWidth(80)
        self.lang_combo.addItem("中文", "zh")
        self.lang_combo.addItem("English", "en")
        idx = self.lang_combo.findData(self.current_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        btn_bar.addWidget(self.lang_combo)

        layout.addLayout(btn_bar)

        # 表格 - 7列
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self._set_table_headers()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(2, 260)  # GUID
        self.table.setColumnWidth(3, 200)  # 目标路径
        self.table.setColumnWidth(4, 70)   # 目标位置
        self.table.setColumnWidth(5, 50)   # 排序
        self.table.doubleClicked.connect(self.edit_selected)

        layout.addWidget(self.table)

        # 状态栏
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(self.T("status_ready"))

    def _set_table_headers(self):
        self.table.setHorizontalHeaderLabels([
            self.T("col_name"), self.T("col_subtitle"), self.T("col_guid"),
            self.T("col_target"), self.T("col_location"),
            self.T("col_sort"), self.T("col_comment"),
        ])

    def _on_lang_changed(self, index: int):
        self.current_lang = self.lang_combo.itemData(index)
        self._retranslate()

    def _retranslate(self):
        """切换语言时刷新所有文字"""
        # 记住当前选中的 GUID
        selected_guid = None
        sel_rows = self.table.selectionModel().selectedRows()
        if sel_rows:
            item = self.table.item(sel_rows[0].row(), 2)
            if item:
                selected_guid = item.text()

        self.setWindowTitle(self.T("window_title"))
        self.title_label.setText("📁 " + self.T("window_title"))
        self.add_btn.setText(self.T("add"))
        self.edit_btn.setText(self.T("edit"))
        self.delete_btn.setText(self.T("delete"))
        self.refresh_btn.setText(self.T("refresh"))
        self.refresh_shell_btn.setText(self.T("refresh_shell"))
        self.about_btn.setText(self.T("about"))
        self.drive_btn.setText(self.T("drive_mapper"))
        self.lang_label.setText(self.T("language"))
        self._set_table_headers()
        self.status.showMessage(self.T("status_ready"))
        self.refresh_list()

        # 恢复选中状态
        if selected_guid:
            for row in range(self.table.rowCount()):
                if self.table.item(row, 2) and self.table.item(row, 2).text() == selected_guid:
                    self.table.selectRow(row)
                    break

    # ---- 数据操作 ----

    def refresh_list(self):
        self.table.setRowCount(0)
        try:
            folders = list_virtual_folders()
            self.table.setRowCount(len(folders))
            for row, f in enumerate(folders):
                self.table.setItem(row, 0, QTableWidgetItem(f["name"]))
                self.table.setItem(row, 1, QTableWidgetItem(f["subtitle"]))
                self.table.setItem(row, 2, QTableWidgetItem(f["guid"]))
                self.table.setItem(row, 3, QTableWidgetItem(f["target"]))
                # 位置显示用当前语言翻译，UserRole 存原始值
                loc_name = get_location_name(self.current_lang, f["location"])
                loc_item = QTableWidgetItem(loc_name)
                loc_item.setData(Qt.UserRole, f["location"])  # 存原始中文名
                self.table.setItem(row, 4, loc_item)
                self.table.setItem(row, 5, QTableWidgetItem(str(f["sort_order"])))
                self.table.setItem(row, 6, QTableWidgetItem(f["comment"]))
                self.table.item(row, 0).setData(Qt.UserRole, f.get("icon", ""))

            total = len(folders)
            count_by_loc = {}
            for f in folders:
                loc = f["location"]
                count_by_loc[loc] = count_by_loc.get(loc, 0) + 1
            loc_str = " | ".join(
                f"{get_location_name(self.current_lang, k)}: {v}"
                for k, v in count_by_loc.items()
            )
            self.status.showMessage(self.T("status_count", total=total, loc_str=loc_str))
        except Exception as e:
            self.status.showMessage(self.T("status_read_error", e=str(e)))

    def _refresh_shell(self):
        refresh_explorer()
        self.status.showMessage(self.T("status_refreshed"))

    def show_about_dialog(self):
        dlg = AboutDialog(self, self.current_lang)
        dlg.exec()

    def show_drive_mapper(self):
        dlg = DriveMapperDialog(self, self.current_lang)
        dlg.exec()

    def _get_selected_row(self) -> int:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, self.T("op_failed"), self.T("select_hint"))
            return -1
        return rows[0].row()

    def _get_row_data(self, row: int) -> Dict[str, Any]:
        icon = ""
        item0 = self.table.item(row, 0)
        if item0:
            icon = item0.data(Qt.UserRole) or ""
        loc_item = self.table.item(row, 4)
        original_loc = loc_item.data(Qt.UserRole) if loc_item else "此电脑"
        return {
            "name": self.table.item(row, 0).text() if self.table.item(row, 0) else "",
            "subtitle": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
            "guid": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
            "target": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
            "location": original_loc or "此电脑",
            "sort_order": int(self.table.item(row, 5).text()) if self.table.item(row, 5) else 60,
            "comment": self.table.item(row, 6).text() if self.table.item(row, 6) else "",
            "icon": icon,
        }


    # --- 操作 ---

    def show_add_dialog(self, edit_data: Dict[str, Any] = None):
        dlg = AddEditDialog(self, edit_data, self.current_lang)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.result_data
            try:
                is_edit = edit_data is not None
                if is_edit:
                    old_guid = edit_data["guid"]
                    # 先移除旧的注册表条目
                    remove_virtual_folder(old_guid)
                    try:
                        add_virtual_folder(
                            data["name"], data["target"],
                            comment=data["comment"], icon_path=data["icon"],
                            guid=old_guid,
                            location=data["location"],
                            sort_order=data["sort_order"],
                            subtitle=data["subtitle"],
                        )
                    except Exception:
                        # re-add 失败 → 尝试恢复旧数据
                        try:
                            add_virtual_folder(
                                edit_data.get("name", ""),
                                edit_data.get("target", ""),
                                comment=edit_data.get("comment", ""),
                                icon_path=edit_data.get("icon", ""),
                                guid=old_guid,
                                location=edit_data.get("location", "此电脑"),
                                sort_order=edit_data.get("sort_order", 60),
                                subtitle=edit_data.get("subtitle", ""),
                            )
                        except Exception:
                            pass
                        raise
                    self.status.showMessage(self.T("status_updated", name=data["name"]))
                else:
                    guid = add_virtual_folder(
                        data["name"], data["target"],
                        comment=data["comment"], icon_path=data["icon"],
                        location=data["location"],
                        sort_order=data["sort_order"],
                        subtitle=data["subtitle"],
                    )
                    loc_display = get_location_name(self.current_lang, data["location"])
                    self.status.showMessage(self.T("status_added", name=data["name"], location=loc_display, guid=guid))
                refresh_explorer()
                self.refresh_list()
            except Exception as e:
                QMessageBox.critical(self, self.T("op_failed"), str(e))

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
            self, self.T("op_failed"),
            self.T("delete_confirm", name=data["name"]),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            remove_virtual_folder(data["guid"])
            refresh_explorer()
            self.refresh_list()
            self.status.showMessage(self.T("status_deleted", name=data["name"]))
        except Exception as e:
            QMessageBox.critical(self, self.T("delete_failed"), str(e))


# ============================================================
# 入口
# ============================================================

def main():
    app = QApplication(sys.argv)
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
        QComboBox {
            padding: 5px 8px;
            border: 1px solid #ccc;
            border-radius: 3px;
            background: white;
        }
        QComboBox:focus {
            border-color: #0078d4;
        }
        QSpinBox {
            padding: 5px 8px;
            border: 1px solid #ccc;
            border-radius: 3px;
            background: white;
        }
        QSpinBox:focus {
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
