#coding: utf8
import os, re, time, sys
from . import to_unicode, md5_for_file


is_win = sys.platform == 'win32'
is_mac = sys.platform == 'darwin'


def is_same_path(p1, p2):
    if not p1 or not p2:
        return False
    p1 = same_slash(p1).strip('/')
    p2 = same_slash(p2).strip('/')
    return p1==p2


def same_slash(path):
    if isinstance(path, (str, unicode)):
        if path.startswith('file://'):
            path = path[7:]
        if is_win:
            path = path.lstrip('/')
    if path:
        path = to_unicode(path.replace('\\', '/'))
        path = path.rstrip('/')
    return path




def make_sure_path(path, is_file=False, is_dir=False):
    # 保证path是有效的，特别是写入一个文件的时候，避免没有父目录，而写入失败
    # 如果返回False，表示有问题...
    # is_file 表示会新建一个文件，里面用当前的时间戳作为正文内容
    path = same_slash(path)
    if not is_dir: # 非 dir，只保证其父目录的存在
        folder, name = os.path.split(path)
    else:
        folder = path
    if not os.path.isdir(folder):
        try:
            os.makedirs(folder)
        except:
            return False
    if is_file: # like touch in linux
        try:
            with open(path, 'w') as f:
                f.write("%s" % time.time())
        except:
            pass
    return True


def is_real(path):
    # 主要是判断是否真实的文档，还是软链，或者软链下的目录内
    path = same_slash(path)
    if not os.path.exists(path):
        return False
    parts = path.split('/')
    for i in range(len(parts)):
        if i:
            _path = '/'.join(parts[:-i])
        else:
            _path = path
        if os.path.islink(_path):
            return False
    return True


def is_a_hidden_path(path):
    path = same_slash(path)
    if re.search('(^|/)(\.|~$)', path):
        return True
    elif re.search(r'~\.[^.]+$', path):
        return True
    elif path.endswith('~'):
        return True
    else:
        return False



_join = os.path.join

def join(*args, **kwargs):
    path = _join(*args, **kwargs)
    return same_slash(path)



def make_path_valid(path):
    if not path or not isinstance(path, (str, unicode)):
        return path
    path = re.sub(r'[*?:<>|"\']', ' ', path)
    if is_win: # windows 下的盘符保留
        path = re.sub(r'^([cdefghijk]) ', '\g<1>:', path, flags=re.I)
    return path





def is_same_file(path1, path2):
    """校验两个文件的md5是否一致来判定是否同一个文件"""
    if path1 and path1 == path2:
        return True
    if os.path.isfile(path1) and os.path.isfile(path2):
        return md5_for_file(path1)==md5_for_file(path2)
    return False



def get_relative_path(filepath, root, return_name_if_fail=True):
    # without '/' in head/foot
    filepath = same_slash(filepath)
    root = same_slash(root)
    if filepath and root and filepath.startswith(root+'/'):
        return filepath.replace(root, '').strip('/')
    elif filepath == root:
        return ''
    else:
        if return_name_if_fail:
            return os.path.split(filepath)[-1]
        else:
            return filepath



def get_home_path():
    home_path = ''
    if os.environ.has_key('HOME'):
        home_path = to_unicode(os.environ['HOME'])
        if not os.path.exists(home_path):
            home_path = ''
    if not home_path:
        home_path = ''
    home_path = same_slash(home_path)
    return  home_path



def is_sub_path(filepath, parent_path):
    if not parent_path: # ignore
        return False
    if not filepath:
        return False
    parent_path = same_slash(parent_path).lower()
    filepath = same_slash(filepath).lower()
    return filepath.startswith(parent_path+'/')



def get_parent_folders(folder):
    parents = []
    folder_path = same_slash(folder)
    parts = folder_path.split('/')
    for i in range(len(parts)):
        parent = '/'.join(parts[:i])
        if not parent or parent.endswith(':'):
            parent += '/'
        if parent not in parents:
            parents.append(parent)
    parents.reverse()
    return parents




