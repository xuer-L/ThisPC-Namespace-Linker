"""
i18n - 多语言支持
ThisPC‑Namespace‑Linker 的中/英文语言包
"""

LANGUAGES = {
    "zh": {
        # ---- 应用 ----
        "app_name": "ThisPC‑Namespace‑Linker",
        "window_title": "ThisPC‑Namespace‑Linker - 资源管理器自定义文件夹管理",

        # ---- 按钮 ----
        "add": "＋ 添加",
        "edit": "✎ 编辑",
        "delete": "✕ 删除",
        "refresh": "↻ 刷新",
        "refresh_shell": "⟳ 刷新资源管理器",
        "about": "ℹ 关于",
        "confirm": "确定",
        "cancel": "取消",
        "browse": "浏览...",

        # ---- 添加/编辑对话框 ----
        "add_title": "添加自定义文件夹",
        "edit_title": "编辑自定义文件夹",
        "label_name": "显示名称 *:",
        "label_subtitle": "副标题:",
        "label_target": "目标路径 *:",
        "label_comment": "备注:",
        "label_icon": "图标路径:",
        "label_location": "目标位置:",
        "label_sort": "排序索引:",
        "placeholder_name": "例如: 我的工作文件夹",
        "placeholder_subtitle": "显示在名称下方的灰色说明文字",
        "placeholder_target": "例如: D:\\MyFolder",
        "placeholder_comment": "鼠标悬停时显示的提示信息",
        "placeholder_icon": "留空则使用默认文件夹图标",
        "tooltip_sort": "数值越小越靠前（系统盘符通常为 0-10，文件夹为 11-40）",
        "help_text": (
            "💡 图标路径可以是:\n"
            "  · .ico 文件路径，如 C:\\MyIcon.ico\n"
            "  · DLL/EXE 资源索引，如 C:\\Windows\\System32\\imageres.dll,-3\n"
            "  · 留空则用默认文件夹图标\n\n"
            "💡 排序索引越小越靠前，系统盘符通常为 0-10，文件夹为 11-40\n"
            "💡 副标题会显示在图标名称下方的灰色小字中"
        ),
        "warn_empty_name": "显示名称不能为空",
        "warn_empty_target": "目标路径不能为空",

        # ---- 表格表头 ----
        "col_name": "显示名称",
        "col_subtitle": "副标题",
        "col_guid": "GUID",
        "col_target": "目标路径",
        "col_location": "目标位置",
        "col_sort": "排序",
        "col_comment": "备注",

        # ---- 关于页 ----
        "about_title": "关于 ThisPC‑Namespace‑Linker",
        "motto": "好好学习，天天向上",
        "developer": "Developer: Xuer with Deepseek\n"
                     "©Xuer 2026 · Licensed under GPL-3.0\n"
                     "E-mail: public@xuer.space",
        "privacy": "您的所有数据保存在本地，Xuer不会利用您的数据",
        "blog": "Xuer`Space: LLT-生活/文学/技术",

        # ---- 状态栏 ----
        "status_ready": "就绪",
        "status_added": "✅ 已添加: {name}  [{location}]  GUID: {guid}",
        "status_updated": "✅ 已更新: {name}",
        "status_deleted": "🗑️ 已删除: {name}",
        "status_refreshed": "已刷新 (可能需要手动 F5)",
        "status_read_error": "读取失败: {e}",
        "status_count": "共 {total} 个自定义项  ({loc_str})",

        # ---- 其他 ----
        "select_hint": "请先选中一个项目",
        "delete_confirm": "删除「{name}」?",
        "op_failed": "操作失败",
        "delete_failed": "删除失败",
        "language": "语言 / Language:",

        # ---- 位置名称 ----
        "loc_this_pc": "此电脑",
        "loc_desktop": "桌面",

        # ---- 虚拟盘符 ----
        "drive_mapper": "\U0001f4bf 映射盘符",
    },

    "en": {
        # ---- App ----
        "app_name": "ThisPC‑Namespace‑Linker",
        "window_title": "ThisPC‑Namespace‑Linker - Custom Folder Manager",

        # ---- Buttons ----
        "add": "＋ Add",
        "edit": "✎ Edit",
        "delete": "✕ Delete",
        "refresh": "↻ Refresh",
        "refresh_shell": "⟳ Refresh Explorer",
        "about": "ℹ About",
        "confirm": "OK",
        "cancel": "Cancel",
        "browse": "Browse...",

        # ---- Add/Edit Dialog ----
        "add_title": "Add Custom Folder",
        "edit_title": "Edit Custom Folder",
        "label_name": "Display Name *:",
        "label_subtitle": "Subtitle:",
        "label_target": "Target Path *:",
        "label_comment": "Comment:",
        "label_icon": "Icon Path:",
        "label_location": "Location:",
        "label_sort": "Sort Order:",
        "placeholder_name": "e.g. My Work Folder",
        "placeholder_subtitle": "Gray text shown below the name",
        "placeholder_target": "e.g. D:\\MyFolder",
        "placeholder_comment": "Tooltip text on mouse hover",
        "placeholder_icon": "Leave empty for default folder icon",
        "tooltip_sort": "Lower values appear first (drives: 0-10, folders: 11-40)",
        "help_text": (
            "💡 Icon path can be:\n"
            "  · A .ico file, e.g. C:\\MyIcon.ico\n"
            "  · A DLL/EXE resource index, e.g. C:\\Windows\\System32\\imageres.dll,-3\n"
            "  · Leave empty for default folder icon\n\n"
            "💡 Lower sort order = appears first (drives: 0-10, folders: 11-40)\n"
            "💡 Subtitle is shown in gray below the folder name"
        ),
        "warn_empty_name": "Display name cannot be empty",
        "warn_empty_target": "Target path cannot be empty",

        # ---- Table Headers ----
        "col_name": "Name",
        "col_subtitle": "Subtitle",
        "col_guid": "GUID",
        "col_target": "Target Path",
        "col_location": "Location",
        "col_sort": "Sort",
        "col_comment": "Comment",

        # ---- About Dialog ----
        "about_title": "About ThisPC‑Namespace‑Linker",
        "motto": "Study hard and make progress every day",
        "developer": "Developer: Xuer with Deepseek\n"
                     "©Xuer 2026 · Licensed under GPL-3.0\n"
                     "E-mail: public@xuer.space",
        "privacy": "All your data stays local. Xuer does not collect your data.",
        "blog": "Xuer`Space: LLT-Life/Literature/Tech",

        # ---- Status Bar ----
        "status_ready": "Ready",
        "status_added": "✅ Added: {name}  [{location}]  GUID: {guid}",
        "status_updated": "✅ Updated: {name}",
        "status_deleted": "🗑️ Deleted: {name}",
        "status_refreshed": "Refreshed (may need F5)",
        "status_read_error": "Read failed: {e}",
        "status_count": "{total} items  ({loc_str})",

        # ---- Other ----
        "select_hint": "Please select an item first",
        "delete_confirm": "Delete「{name}」?",
        "op_failed": "Operation failed",
        "delete_failed": "Delete failed",
        "language": "语言 / Language:",

        # ---- Location Names ----
        "loc_this_pc": "This PC",
        "loc_desktop": "Desktop",

        # ---- Virtual Drive ----
        "drive_mapper": "\U0001f4bf Map as Drive",
    },
}


# 默认语言
DEFAULT_LANG = "zh"


def get_text(lang: str, key: str, **kwargs) -> str:
    """获取指定语言的文本，支持格式化参数"""
    lang_data = LANGUAGES.get(lang, LANGUAGES[DEFAULT_LANG])
    text = lang_data.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


def get_location_name(lang: str, location_key: str) -> str:
    """获取位置名称的翻译"""
    mapping = {
        "此电脑": "loc_this_pc",
        "桌面": "loc_desktop",
    }
    key = mapping.get(location_key, location_key)
    return get_text(lang, key)
