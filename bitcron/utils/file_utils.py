#coding: utf8
import os
import sys
import time
import ctypes
import subprocess
import shutil
try:
    import send2trash
except:
    send2trash = None
from . import run_commands
from .path import same_slash as _
try:
    import win32file, win32con
except:
    win32file = None
    win32con = None

is_win = sys.platform == 'win32'
is_mac = sys.platform == 'darwin'
is_linux = 'linux' in sys.platform.lower()


MARKDOWN_EXTS = ['.txt', '.md', '.markdown', '.mk']

IMAGE_EXTS = ['.gif', '.png', '.jpg', '.jpeg', '.bmp', '.webp']


def is_a_markdown_file(path):
    if not path:
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in MARKDOWN_EXTS




def create_file(filepath, content):
    # 会确保父目录的存在
    if os.path.isdir(filepath):
        return
    parent = os.path.split(filepath)[0]
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    if isinstance(content, unicode):
        content = content.encode('utf8')
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as old_f:
            old_content = old_f.read()
        if content == old_content:
            return # 内容没有变化，ignore
    try:
        with open(filepath, 'wb') as f:
            f.write(content)
    except IOError:
        time.sleep(1) # 先重试，不行再report错误
        with open(filepath, 'wb') as f:
            f.write(content)



def delete_file(file_path, to_trash=True):
    if not os.path.exists(file_path):
        return # ignore
    if os.path.isdir(file_path): # 对目录的处理
        if to_trash: # 文件夹整体移入回收站
            try:
                send2trash.send2trash(file_path)
            except:
                pass
        try:
            shutil.rmtree(file_path)
        except:
            pass
    else:
        if to_trash:
            try:
                send2trash.send2trash(file_path)
            except:
                pass
        if os.path.isfile(file_path): # 放入回收站失败，继续删除
            try:
                os.remove(file_path)
            except:
                pass


def hide_a_path(path):
    # 仅仅对win下有效
    path = _(path)
    if not os.path.exists(path):
        return
    if is_win:
        try:
            ctypes.windll.kernel32.SetFileAttributesW(path, 2)
        except:
            pass
    elif is_mac:
        run_commands("chflags hidden '%s'"%path)





def get_creation_time_for_mac(filepath):
    p = subprocess.Popen(['stat', '-f%B', filepath],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise OSError(p.stderr.read().rstrip())
    else:
        return int(p.stdout.read())


def get_file_create_time(filepath):
    state = os.stat(filepath)
    if hasattr(state, 'st_birthtime'):
        return int(state.st_birthtime)
    else:
        # mac 下直接得到getctime，不是创建时间
        # on some systems (like Unix) is the time of the last metadata change  -> https://docs.python.org/2/library/os.path.html
        if is_mac:
            try:
                return get_creation_time_for_mac(filepath)
            except:
                pass
        return int(os.path.getctime(filepath))

