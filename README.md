# 微信图片解密工具 (WeChat Image Decryption Tool)

![GitHub stars](https://img.shields.io/github/stars/Evil0ctal/WeChat-image-decryption?style=social)
![GitHub forks](https://img.shields.io/github/forks/Evil0ctal/WeChat-image-decryption?style=social)
![GitHub issues](https://img.shields.io/github/issues/Evil0ctal/WeChat-image-decryption)
![GitHub license](https://img.shields.io/github/license/Evil0ctal/WeChat-image-decryption)

## 📝 简介

微信图片解密工具是一个用于解密微信缓存图片的开源软件，可以将微信在本地存储的`.dat`文件进行还原。微信为了优化存储和保护用户隐私，会对保存在本地的图片进行简单加密。本工具可以将这些加密的图片恢复为原始格式，方便用户查看和管理。

下面是软件截图

## 📷 截图

![软件截图1](https://raw.githubusercontent.com/Evil0ctal/WeChat-image-decryption/main/screenshot/screenshot1.png)

![软件截图2](https://raw.githubusercontent.com/Evil0ctal/WeChat-image-decryption/main/screenshot/screenshot2.png)


## 🔍 原理说明

### 微信图片加密原理

微信对本地缓存的图片使用一种简单的XOR（异或）加密算法：

1. **XOR加密**: 微信将图片的每个字节与一个特定的值（一般是恒定值）进行XOR运算
2. **文件类型隐藏**: 加密后的文件扩展名被更改或移除，使其无法被常规图片查看器打开
3. **文件头修改**: 原始图片文件头部(Magic Number)被加密，使系统无法识别文件类型

### 解密原理

本工具的解密过程如下：

1. **检测文件类型**: 通过分析加密文件的头部字节，与已知文件类型签名对比
2. **确定XOR密钥**: 计算头部字节与标准文件签名的XOR值来确定加密密钥
3. **应用XOR解密**: 对整个文件的每个字节应用相同的XOR操作
4. **还原文件类型**: 根据检测到的文件类型，添加正确的文件扩展名

例如，如果检测到文件被XOR密钥`0xE7`加密，且原始类型为JPEG，工具会将每个字节与`0xE7`进行XOR运算，并将还原后的文件保存为`.jpg`格式。

## 🚀 功能特点

- 支持**批量解密**微信图片缓存（.dat文件）
- **自动检测**文件类型（JPG、PNG、GIF等）
- **多线程处理**，高效解密大量文件
- **直观的进度显示**，清晰了解解密状态
- **用户友好的界面**，操作简单直观
- **跨平台支持**，可在Windows、macOS和Linux上运行
- **保持目录结构**，解密后的文件与原始路径对应

## 📋 支持的文件类型

本工具可以检测和解密以下文件类型：

- 图片格式：JPG, PNG, GIF, BMP, TIF
- 文档格式：PDF, DOC, DOCX, HTML, XML, CSS, JS
- 媒体格式：MP4, MP3, WAV, AVI, RMVB, FLV, MOV
- 压缩格式：ZIP, RAR, GZ
- 其他格式：EXE, JAR, CLASS, SQL, JAVA等

## 📁 微信文件存储位置

微信在本地存储的加密图片通常位于以下路径：

### Windows系统
```
C:\Users\<用户名>\Documents\WeChat Files\<微信ID>\FileStorage\Image\<年份-月份>
```

例如：
```
C:\Users\Evil0ctal\Documents\WeChat Files\wxid_vhqo51hxlpa612\FileStorage\Image\2022-07
```

### macOS系统
```
~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/<微信版本>/<微信ID>/FileStorage/Image/<年份-月份>
```

### 文件特征

- 微信缓存的加密图片通常以`.dat`为扩展名
- 文件夹按年份和月份组织（例如：`2022-07`表示2022年7月）
- 每个用户的微信ID文件夹下存储着该账号相关的所有文件

缓存目录中也可能包含其他类型的媒体文件，如视频(Video目录)、语音(Voice目录)等，本工具也可用于解密这些文件。

## 💻 使用方法

### 图形界面使用

1. 启动程序（双击执行文件或使用命令`python wxchat_img_revert.py --gui`）
2. 在"源路径"中选择包含加密微信图片的文件夹
3. 在"目标路径"中选择解密后文件的保存位置
4. 点击"开始解密"按钮
5. 等待解密完成，程序会询问是否打开目标文件夹

### 命令行使用

```bash
python wxchat_img_revert.py --source <源路径> --target <目标路径>
```

示例：
```bash
python wxchat_img_revert.py --source C:\WeChatFiles\Encrypted --target C:\WeChatFiles\Decrypted
```

## 🔧 安装说明

### 环境要求
- Python 3.6 或更高版本
- 无需额外依赖库（仅使用Python标准库）

### 安装步骤

1. 克隆或下载仓库:
```bash
git clone https://github.com/Evil0ctal/WeChat-image-decryption.git
```

2. 进入项目目录:
```bash
cd WeChat-image-decryption
```

3. 运行程序:
```bash
python wxchat_img_revert.py
```

## 📝 常见问题

1. **Q: 程序无法检测到正确的文件类型怎么办？**  
   A: 少数情况下，文件头部可能被严重损坏或使用了未收录的格式。可以尝试手动指定XOR密钥，或重新从微信获取文件。

2. **Q: .dat文件是什么？为什么微信使用这种格式？**  
   A: `.dat`是微信用于存储加密文件的通用扩展名，实际上这些文件是通过XOR加密后的各种媒体文件（图片、视频等）。微信使用这种方式来隐藏文件实际类型并提供基本的隐私保护。

2. **Q: 解密后的图片无法打开怎么办？**  
   A: 可能是XOR密钥检测错误。尝试使用十六进制编辑器查看文件头部，确认正确的密钥。

3. **Q: 是否支持微信视频解密？**  
   A: 是的，本工具可以解密大部分微信缓存的多媒体文件，包括视频文件。

4. **Q: 解密过程卡住或程序无响应怎么办？**  
   A: 可以点击"取消解密"按钮终止当前操作，然后尝试减少处理的文件数量或重启程序。

## 🛡️ 免责声明

本工具仅供技术研究和个人合法使用，请勿用于未授权访问他人数据或任何非法用途。使用本工具时请遵守当地法律法规，尊重个人隐私。

本软件是免费开源的，请勿用于商业销售。

## 🌟 贡献与反馈

欢迎提出问题、功能请求或提交Pull Request来帮助改进此项目。
您可以通过以下方式联系我们:

- 在GitHub上提交[Issue](https://github.com/Evil0ctal/WeChat-image-decryption/issues)
- 提交[Pull Request](https://github.com/Evil0ctal/WeChat-image-decryption/pulls)

## 📜 许可证

本项目使用[MIT许可证](LICENSE)。