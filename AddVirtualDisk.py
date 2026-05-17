"""
ThisPC‑Namespace‑Linker - 在 Windows 资源管理器中添加自定义文件夹图标
支持此电脑 / 桌面 / 网络位置，支持排序和副标题
"""

import sys, os, uuid, winreg, ctypes

from typing import Optional, Dict, List, Any

# ============ 版本信息 ============
__version__ = "1.0.0"
VERSION = __version__


# ============ 路径常量 ============
KEY_CLSID     = r"Software\Classes\CLSID"
SHELLFOLDER_CLSID = "{0E5AAE11-A475-4c5b-AB00-C66DE400274E}"

# 可添加的位置
LOCATIONS: Dict[str, str] = {
    "此电脑": r"Software\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace",
    "桌面":   r"Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace",
    "网络":   r"Software\Microsoft\Windows\CurrentVersion\Explorer\Network\NameSpace",
}

def generate_guid() -> str:
    return "{" + str(uuid.uuid4()).upper() + "}"

def create_key(parent_path: str, sub_name: str):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, parent_path, 0, winreg.KEY_WRITE) as key:
        winreg.CreateKey(key, sub_name)

def ensure_key(full_path: str):
    """递归创建注册表键（确保路径存在）"""
    parts = full_path.split("\\")
    for i in range(1, len(parts) + 1):
        sub = "\\".join(parts[:i])
        parent = "\\".join(parts[:i-1]) if i > 1 else ""
        if parent:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, parent, 0, winreg.KEY_WRITE) as k:
                    winreg.CreateKey(k, parts[i-1])
            except:
                pass
        else:
            try:
                winreg.CreateKey(winreg.HKEY_CURRENT_USER, sub)
            except:
                pass


def set_sz(key_path: str, value_name: str, value: str):
    """设置 REG_SZ 字符串值"""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)

def set_expand_sz(key_path: str, value_name: str, value: str):
    """设置 REG_EXPAND_SZ 字符串值"""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_EXPAND_SZ, value)

def set_dword(key_path: str, value_name: str, value: int):
    """设置 REG_DWORD 值"""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)


def _delete_key_recursive(full_path: str):
    """递归删除注册表键"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, full_path, 0, winreg.KEY_WRITE)
        # 先递归删除所有子键
        while True:
            try:
                sub = winreg.EnumKey(key, 0)
                _delete_key_recursive(full_path + "\\" + sub)
            except OSError:
                break
        key.Close()
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, full_path)
    except FileNotFoundError:
        pass
    except PermissionError:
        raise


def add_virtual_folder(
    display_name: str,
    target_path: str,
    comment: str = "",
    icon_path: str = "",
    guid: Optional[str] = None,
    location: str = "此电脑",
    sort_order: int = 60,
    subtitle: str = "",
) -> str:
    """
    在指定位置中添加一个自定义文件夹图标。

    Parameters:
        display_name: 显示名称
        target_path: 目标文件夹路径
        comment: 鼠标悬停提示
        icon_path: 图标路径，留空用默认
        guid: 指定 GUID，留空自动生成
        location: 目标位置（此电脑/桌面/网络）
        sort_order: 排序索引，越小越靠前
        subtitle: 副标题（显示在名称下方的灰体字）
    """
    if not guid:
        guid = generate_guid()

    # 归一化路径：Qt 文件对话框返回 /，注册表需要 \
    target_path = target_path.replace("/", "\\")
    if icon_path:
        icon_path = icon_path.replace("/", "\\")

    # === 构建注册表路径 ===

    ns_path  = LOCATIONS.get(location, LOCATIONS["此电脑"])
    base     = f"{KEY_CLSID}\\{guid}"
    ip       = f"{base}\\Instance"
    ipb      = f"{ip}\\InitPropertyBag"
    di       = f"{base}\\DefaultIcon"
    ips      = f"{base}\\InProcServer32"
    soc      = f"{base}\\Shell\\Open\\Command"
    sf       = f"{base}\\ShellFolder"
    ns       = f"{ns_path}\\{guid}"


    # 1. CLSID 主键
    create_key(KEY_CLSID, guid)
    set_sz(base, "", display_name)

    # 2. 排序索引
    set_dword(base, "SortOrderIndex", sort_order)

    # 3. 副标题（灰体字）
    if subtitle:
        set_sz(base, "TileInfo", "prop:System.ItemAuthors")
        set_sz(base, "System.ItemAuthors", subtitle)
    else:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_WRITE) as k:
                try: winreg.DeleteValue(k, "TileInfo")
                except: pass
                try: winreg.DeleteValue(k, "System.ItemAuthors")
                except: pass
        except: pass

    # 4. InfoTip（鼠标悬停提示）
    if comment:
        set_sz(base, "InfoTip", comment)
    else:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_WRITE) as k:
                try: winreg.DeleteValue(k, "InfoTip")
                except: pass
        except: pass

    # 5. DefaultIcon
    create_key(base, "DefaultIcon")
    if icon_path:
        set_sz(di, "", icon_path)
    else:
        set_expand_sz(di, "", r"%systemroot%\system32\imageres.dll,-3")

    # 6. InProcServer32（使用 shdocvw.dll，跟百度网盘一致）
    create_key(base, "InProcServer32")
    set_expand_sz(ips, "", r"%systemroot%\system32\shdocvw.dll")
    set_sz(ips, "ThreadingModel", "Apartment")

    # 7. Instance（命名空间扩展 CLSID）
    create_key(base, "Instance")
    set_sz(ip, "", "")
    set_sz(ip, "CLSID", SHELLFOLDER_CLSID)

    # 8. InitPropertyBag
    create_key(ip, "InitPropertyBag")
    set_sz(ipb, "TargetFolderPath", target_path)
    set_dword(ipb, "Attributes", 0x00000011)

    # 9. Shell\Open\Command（双击执行 explorer.exe 打开目标目录）
    create_key(base, "Shell")
    create_key(f"{base}\\Shell", "Open")
    create_key(f"{base}\\Shell\\Open", "Command")

    set_expand_sz(soc, "", r'%SystemRoot%\explorer.exe /e,"' + target_path + r'"')



    # 10. ShellFolder
    create_key(base, "ShellFolder")
    set_dword(sf, "Attributes", 0xF080004D)

    # 11. 添加到指定位置的 NameSpace
    create_key(ns_path, guid)
    set_sz(ns, "", display_name)

    return guid



def remove_virtual_folder(guid: str) -> bool:
    """从所有位置中移除一个虚拟文件夹（包括 CLSID 注册）"""
    # 从所有 NameSpace 位置移除
    for ns_path in LOCATIONS.values():
        try:
            _delete_key_recursive(f"{ns_path}\\{guid}")
        except Exception:
            pass
    # 移除 CLSID 主键
    try:
        _delete_key_recursive(f"{KEY_CLSID}\\{guid}")
        return True
    except Exception:
        return False


def list_virtual_folders() -> List[Dict[str, Any]]:
    """列出所有位置中的自定义项"""
    folders = []
    seen_guids = set()

    # 扫描所有位置
    for location_name, ns_path in LOCATIONS.items():
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, ns_path, 0, winreg.KEY_READ) as ns_key:
                i = 0
                while True:
                    try:
                        guid = winreg.EnumKey(ns_key, i)
                        if guid not in seen_guids:
                            seen_guids.add(guid)
                            folders.append({
                                "guid": guid, "name": "", "target": "",
                                "comment": "", "icon": "", "location": location_name,
                                "sort_order": 60, "subtitle": "",
                            })
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass

    # 从 CLSID 读取详细信息
    for f in folders:
        base = f"{KEY_CLSID}\\{f['guid']}"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_READ) as k:
                try: f["name"] = winreg.QueryValueEx(k, "")[0] or ""
                except: pass
                try: f["comment"] = winreg.QueryValueEx(k, "InfoTip")[0] or ""
                except: pass
                try: f["subtitle"] = winreg.QueryValueEx(k, "System.ItemAuthors")[0] or ""
                except: pass
                try: f["sort_order"] = winreg.QueryValueEx(k, "SortOrderIndex")[0] or 60
                except: pass
        except: pass

        # 读目标路径
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                f"{base}\\Instance\\InitPropertyBag", 0, winreg.KEY_READ) as k:
                f["target"] = winreg.QueryValueEx(k, "TargetFolderPath")[0] or ""
        except: pass

        # 读图标
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                f"{base}\\DefaultIcon", 0, winreg.KEY_READ) as k:
                f["icon"] = winreg.QueryValueEx(k, "")[0] or ""
        except: pass

    return folders


def refresh_explorer():
    """通知 Windows 刷新外壳"""
    try:
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
    except Exception:
        pass


def main():
    """启动 PySide6 GUI"""
    from AddVirtualDisk_ui import main as gui_main
    gui_main()


if __name__ == "__main__":
    main()
