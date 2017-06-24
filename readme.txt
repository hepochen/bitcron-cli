
## 安装
### 基本逻辑
1， 安装 python  (2.7.x版本)
2， 安装 pip (python 的包管理)
### Linux (以Ubuntu为例)
```
apt-get install python-pip -q
pip install bitcron -U
```

### MacOS
```
sudo easy_install pip
sudo pip install bitcron -U
```

### Windows
我们接触比较少，并不太清楚，但基本的逻辑是一样。
但是，在 Windows 直接使用命令行操作，似乎并不是很方便的事情……

## 基本使用方法
> 以 MacOS 为例，如果使用 Linux 的，本说明也是非常容易理解的。

1,  cd  某个目录路径
2,  运行 `bitcron TOKEN` 绑定网站 (**注意，TOKEN 类似 PDtXpyskj53GK7zjPXLXMJ ，在登录 Bitcron.com 自己的网站列表中可见**)
3,  运行 `bitcron` 后，就会将当前目录的内容同步到自己的 Bitcron 网站中

## 其它命令说明
- 从服务器中同步:  **bitcron sync**
- 解除网站绑定: **bitcron logout**
- 重置同步并解除绑定: **bitcron reset**
- 在浏览器中打开当前网站: **bitcron open** (视不同操作系统对应不同)
- 显示当前网站目录的信息: **bitcron info**
- 指定同步的节点(默认是账户的主节点): **bitcron  xx.bitcron.com**,  比如 hk.bitcron.com

<small>注意: 以上命令中，bitcron 换为 farbox，效果是一样的。 </small>


