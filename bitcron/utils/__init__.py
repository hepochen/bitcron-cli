#coding: utf8
import sys
import os
import time
import subprocess
import hashlib
import datetime


is_win = sys.platform == 'win32'
is_mac = sys.platform == 'darwin'


class UnicodeWithAttrs(unicode):
    pass


ENCODINGS = [
    "utf8",
    "gb18030",
    "big5",
    "latin1",
    "ascii"
]

def to_unicode(content):
    if not content:
        return u''
    if isinstance(content, unicode):
        return content
    try:
        return unicode(content)
    except:
        for encode in ENCODINGS:
            try:
                return unicode(content, encode)
            except:
                pass
        try:
            return unicode(content, 'utf8', 'ignore')
        except:
            return u""

def to_str(content):
    content = to_unicode(content)
    return content.encode('utf8')

smart_unicode = to_unicode

smart_str = to_str


unicode_class = getattr(__builtins__, 'unicode', None)
has_unicode = bool(unicode_class)
def is_char(content):
    if has_unicode:
        # py 2.7
        return isinstance(content, (str, unicode_class))
    else:
        return isinstance(content, str)


MARKDOWN_EXTS = ['.md', '.markdown', '.txt', '.mk']

def is_markdown(path):
    if os.path.splitext(path)[1].lower() in MARKDOWN_EXTS:
        return True
    else:
        return False



def get_folders(path):  # just folder name
    if not os.path.isdir(path): # 目录不存在
        return []
    filenames = os.listdir(path)
    folders = []
    for filename in filenames:
        if os.path.isdir(os.path.join(path, filename)) and not filename.startswith('.'):
            folders.append(filename)
    return folders


def md5(text):
    if isinstance(text, unicode):
        text = text.encode('utf8')
    text = str(text)
    return hashlib.md5(text).hexdigest()


def md5_for_file(file_path, block_size=2**20):
    if os.path.isdir(file_path):
        return 'folder'
    f = open(file_path)
    md5_obj = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5_obj.update(data)
    f.close()
    return md5_obj.hexdigest()


def chunks_list(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]



def run_commands(commands, sleep=0):
    for command in commands.split('\n'):
        command = command.strip()
        if command.startswith('#'): continue # just comment
        if not command: continue
        subprocess.call(command, shell=True)
        if sleep: time.sleep(sleep)


def get_now_str(fmt='%Y-%m-%d %H:%M:%S'):
    now = datetime.datetime.now()
    now_str = now.strftime(fmt)
    return now_str