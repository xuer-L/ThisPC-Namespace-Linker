"""
AddVirtualDisk - 在"此电脑"中添加自定义文件夹图标
通过注册表 HKCU 操作实现
"""

import sys, os, uuid, winreg, ctypes
from typing import Optional, Dict, List

# ============ 路径常量 ============
KEY_CLSID     = r"Software\Classes\CLSID"
KEY_NAMESPACE = r"Software\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace"
SHELLFOLDER_CLSID = "{0E5AAE11-A475-4c5b-AB00-C66DE400274E}"

def generate_guid() -> str:
    return "{" + str(uuid.uuid4()).upper() + "}"

def create_key(parent_path: str, sub_name: str):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, parent_path, 0, winreg.KEY_WRITE) as key:
        winreg.CreateKey(key, sub_name)

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
    guid: Optional[str] = None
) -> str:
    """
    在"此电脑"中添加一个自定义文件夹图标。
    返回使用的 GUID。
    """
    if not guid:
        guid = generate_guid()

    # === 构建注册表路径 ===
    base  = f"{KEY_CLSID}\\{guid}"
    ip    = f"{base}\\Instance"
    ipb   = f"{ip}\\InitPropertyBag"
    di    = f"{base}\\DefaultIcon"
    ips   = f"{base}\\InProcServer32"
    sf    = f"{base}\\ShellFolder"
    ns    = f"{KEY_NAMESPACE}\\{guid}"

    # 1. CLSID 主键
    create_key(KEY_CLSID, guid)
    set_sz(base, "", display_name)
    set_sz(base, "DefaultValue", display_name)

    # 2. InfoTip（备注）
    if comment:
        set_sz(base, "InfoTip", comment)

    # 3. DefaultIcon
    create_key(base, "DefaultIcon")
    if icon_path:
        set_sz(di, "", icon_path)
    else:
        set_expand_sz(di, "", r"%systemroot%\system32\imageres.dll,-3")

    # 4. InProcServer32
    create_key(base, "InProcServer32")
    set_expand_sz(ips, "", r"%systemroot%\system32\shell32.dll")
    set_sz(ips, "ThreadingModel", "Both")

    # 5. Instance
    create_key(base, "Instance")
    set_sz(ip, "", "")
    set_sz(ip, "CLSID", SHELLFOLDER_CLSID)

    # 6. InitPropertyBag
    create_key(ip, "InitPropertyBag")
    set_sz(ipb, "TargetFolderPath", target_path)
    set_dword(ipb, "Attributes", 0x00000011)

    # 7. ShellFolder
    create_key(base, "ShellFolder")
    set_dword(sf, "Attributes", 0x00000011)
    set_dword(sf, "FolderValueFlags", 0x00000000)

    # 8. 添加到 NameSpace
    create_key(KEY_NAMESPACE, guid)
    set_sz(ns, "", display_name)

    return guid


def remove_virtual_folder(guid: str) -> bool:
    """从"此电脑"中移除一个虚拟文件夹"""
    try:
        _delete_key_recursive(f"{KEY_NAMESPACE}\\{guid}")
    except Exception:
        pass
    try:
        _delete_key_recursive(f"{KEY_CLSID}\\{guid}")
        return True
    except Exception:
        return False


def list_virtual_folders() -> List[Dict[str, str]]:
    """列出当前"此电脑"中的所有自定义项"""
    folders = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_NAMESPACE, 0, winreg.KEY_READ) as ns_key:
            i = 0
            while True:
                try:
                    guid = winreg.EnumKey(ns_key, i)
                    folders.append({"guid": guid, "name": "", "target": "", "comment": "", "icon": ""})
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass

    for f in folders:
        g, base = f["guid"], f"{KEY_CLSID}\\{f['guid']}"
        # 读名称
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base, 0, winreg.KEY_READ) as k:
                try: f["name"] = winreg.QueryValueEx(k, "")[0] or ""
                except: pass
                try: f["comment"] = winreg.QueryValueEx(k, "InfoTip")[0] or ""
                except: pass
        except: pass
        # 读目标路径
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"{base}\\Instance\\InitPropertyBag", 0, winreg.KEY_READ) as k:
                f["target"] = winreg.QueryValueEx(k, "TargetFolderPath")[0] or ""
        except: pass
        # 读图标
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"{base}\\DefaultIcon", 0, winreg.KEY_READ) as k:
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
