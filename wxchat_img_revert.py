# ==============================================================================
# Copyright (C) 2025 Evil0ctal
#
# This file is part of the WeChat-image-decryption project.
# Github: https://github.com/Evil0ctal/WeChat-image-decryption
#
# This project is licensed under the MIT license.
# ==============================================================================
#                                     ,
#              ,-.       _,---._ __  / \
#             /  )    .-'       `./ /   \
#            (  (   ,'            `/    /|
#             \  `-"             \'\   / |
#              `.              ,  \ \ /  |
#               /`.          ,'-`----Y   |
#              (            ;        |   '
#              |  ,-.    ,-'         |  /
#              |  | (   |  Evil0ctal | /
#              )  |  \  `.___________|/  Github - WeChat-image-decryption
#              `--'   `--'
# ==============================================================================

import concurrent.futures
import os
import queue
import subprocess
import threading
import tkinter as tk
import warnings
import webbrowser
from tkinter import scrolledtext, filedialog, ttk, messagebox

# 忽略libpng警告
warnings.filterwarnings("ignore", category=UserWarning)


class WxChatImgRevert:
    def __init__(self):
        # 文件类型标识映射（十六进制签名到文件扩展名）
        self.FILE_TYPE_MAP = {
            "ffd8ffe000104a464946": "jpg",
            "89504e470d0a1a0a0000": "png",
            "47494638396126026f01": "gif",
            "49492a00227105008037": "tif",
            "424d228c010000000000": "bmp",
            "424d8240090000000000": "bmp",
            "424d8e1b030000000000": "bmp",
            "41433130313500000000": "dwg",
            "3c21444f435459504520": "html",
            "3c21646f637479706520": "htm",
            "48544d4c207b0d0a0942": "css",
            "696b2e71623d696b2e71": "js",
            "7b5c727466315c616e73": "rtf",
            "38425053000100000000": "psd",
            "46726f6d3a203d3f6762": "eml",
            "d0cf11e0a1b11ae10000": "doc",
            "5374616E64617264204A": "mdb",
            "252150532D41646F6265": "ps",
            "255044462d312e360d25": "pdf",
            "2e524d46000000120001": "rmvb",
            "464c5601050000000900": "flv",
            "00000020667479706973": "mp4",
            "49443303000000000f76": "mp3",
            "000001ba210001000180": "mpg",
            "3026b2758e66cf11a6d9": "wmv",
            "524946464694c9015741": "wav",
            "52494646d07d60074156": "avi",
            "4d546864000000060001": "mid",
            "504b0304140000000800": "zip",
            "526172211a0700cf9073": "rar",
            "235468697320636f6e66": "ini",
            "504b03040a0000000000": "jar",
            "4d5a9000030000000400": "exe",
            "3c25402070616765206c": "jsp",
            "4d616e69666573742d56": "mf",
            "3c3f786d6c2076657273": "xml",
            "efbbbf2f2a0d0a53514c": "sql",
            "7061636b616765207765": "java",
            "406563686f206f66660d": "bat",
            "1f8b0800000000000000": "gz",
            "6c6f67346a2e726f6f74": "properties",
            "cafebabe0000002e0041": "class",
            "49545346030000006000": "chm",
            "04000000010000001300": "mxp",
            "504b0304140006000800": "docx",
            "6431303a637265617465": "torrent",
            "494d4b48010100000200": "264",
            "6D6F6F76": "mov",
            "FF575043": "wpd",
            "CFAD12FEC5FD746F": "dbx",
            "2142444E": "pst",
            "AC9EBD8F": "qdf",
            "E3828596": "pwl",
            "2E7261FD": "ram"
        }
        self.running = False
        self.message_queue = queue.Queue()
        self.processed_files = 0
        self.total_files = 0
        self.should_stop = False

    def convert(self, path, target_path, gui=None):
        """
        转换加密的微信图像为原始格式

        Args:
            path: 包含加密文件的源路径
            target_path: 保存解密文件的目标目录
            gui: 可选的GUI对象，用于显示进度和控制处理
        """
        self.should_stop = False
        self.processed_files = 0
        self.message_queue = queue.Queue()

        # 启动一个后台线程进行转换
        thread = threading.Thread(target=self._convert_thread, args=(path, target_path, gui))
        thread.daemon = True
        thread.start()

        # 更新GUI的消息处理
        if gui:
            self.running = True
            gui.root.after(100, lambda: self._process_messages(gui))

    def _convert_thread(self, path, target_path, gui):
        """在后台线程中处理转换逻辑"""
        try:
            source_file = os.path.abspath(path)

            # 检查源是否为单个文件
            if os.path.isfile(source_file):
                self.total_files = 1
                self._update_gui("正在处理单个文件...", gui)
                self.parse_file(source_file, target_path, 0, gui)
                self._update_gui("\n解密完成！", gui)
                return

            # 获取目录中的所有文件
            all_files = []
            self._scan_directory(path, all_files)

            if not all_files:
                self._update_gui("\n在目录中未发现文件。", gui)
                return

            self.total_files = len(all_files)
            self._update_gui(f"总共发现 {self.total_files} 个文件", gui)

            # 从第一个有效文件中找到XOR密钥
            xor_key = 0
            for file_path in all_files[:20]:  # 只检查前20个文件以提高速度
                if self.should_stop:
                    self._update_gui("\n操作已取消。", gui)
                    return

                if os.path.isfile(file_path):
                    xor_info = self.get_xor(file_path)
                    if xor_info and xor_info[1] is not None:
                        xor_key = xor_info[1]
                        self._update_gui(f"找到XOR密钥: {xor_key}", gui)
                        break

            # 创建目标目录（如果不存在）
            os.makedirs(target_path, exist_ok=True)

            # 使用线程池处理文件
            max_workers = min(os.cpu_count() or 4, 8)  # 限制最大工作线程数
            self._update_gui(f"使用 {max_workers} 个线程进行解密处理...", gui)

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {}

                # 提交所有任务
                for file_path in all_files:
                    if self.should_stop:
                        break
                    future = executor.submit(self.parse_file, file_path, target_path, xor_key, gui)
                    future_to_file[future] = file_path

                # 等待完成
                for future in concurrent.futures.as_completed(future_to_file):
                    if self.should_stop:
                        executor.shutdown(wait=False)
                        self._update_gui("\n操作已取消。", gui)
                        return
                    # 结果已在parse_file中处理

            if not self.should_stop:
                self._update_gui("\n解密完成！", gui)

                # 询问是否打开目标目录
                if gui:
                    gui.root.after(500, lambda: gui.ask_open_directory(target_path))

        except Exception as e:
            self._update_gui(f"\n处理时发生错误: {str(e)}", gui)
        finally:
            self.running = False

    def _scan_directory(self, directory, file_list):
        """递归扫描目录并收集所有文件"""
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    self._scan_directory(full_path, file_list)
                else:
                    file_list.append(full_path)
        except Exception as e:
            print(f"扫描目录时出错 {directory}: {str(e)}")

    def _update_gui(self, message, gui):
        """将消息添加到队列以更新GUI"""
        if gui:
            self.message_queue.put(message)
        else:
            print(message)

    def _process_messages(self, gui):
        """从队列处理消息并更新GUI"""
        try:
            # 处理队列中的所有消息
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                gui.log_area.insert(tk.END, f"\n{message}")
                gui.log_area.see(tk.END)  # 自动滚动到底部

                # 更新进度条
                if self.total_files > 0:
                    progress = self.processed_files / self.total_files
                    gui.progress_bar["value"] = progress * 100
                    gui.progress_label.config(text=f"进度: {self.processed_files}/{self.total_files} ({progress:.1%})")

            # 更新按钮状态
            if self.running:
                gui.convert_btn.config(text="取消解密", command=lambda: self._cancel_conversion(gui))
            else:
                gui.convert_btn.config(text="开始解密", command=lambda: self._start_conversion(gui))

            # 如果仍在运行，继续处理消息
            if self.running:
                gui.root.after(100, lambda: self._process_messages(gui))
        except Exception as e:
            print(f"处理消息时出错: {str(e)}")
            if self.running:
                gui.after(100, lambda: self._process_messages(gui))

    def _start_conversion(self, gui):
        """启动转换过程"""
        source_path = gui.source_entry.get()
        target_path = gui.target_entry.get()

        if not source_path or not target_path:
            self._update_gui("错误：请指定源路径和目标路径", gui)
            return

        gui.log_area.delete(1.0, tk.END)  # 清除日志区域
        gui.progress_bar["value"] = 0
        gui.progress_label.config(text="准备中...")

        self.convert(source_path, target_path, gui)

    def _cancel_conversion(self, gui):
        """取消正在进行的转换"""
        self.should_stop = True
        gui.convert_btn.config(text="取消中...", state=tk.DISABLED)
        self._update_gui("\n正在取消操作...", gui)

    def parse_file(self, file_path, target_path, xor_key, gui=None):
        """处理单个文件进行解密"""
        try:
            # 跳过目录文件
            if os.path.isdir(file_path):
                new_target_path = os.path.join(target_path, os.path.basename(file_path))
                os.makedirs(new_target_path, exist_ok=True)
                return

            # 获取XOR值和文件类型
            xor_info = self.get_xor(file_path)

            # 如果检测失败，则使用提供的XOR密钥
            if not xor_info[1]:
                xor_info[1] = xor_key

            # 获取不带扩展名的文件名
            file_name = os.path.basename(file_path).split('.')[0]

            # 添加检测到的扩展名（如果可用）
            if xor_info[0]:
                output_file = os.path.join(target_path, f"{file_name}.{xor_info[0]}")
            else:
                output_file = os.path.join(target_path, file_name)

            # 读取、解密并写入文件
            file_size_kb = os.path.getsize(file_path) / 1000.0

            if not xor_info[1]:  # 如果没有可用的XOR键，跳过此文件
                progress_msg = f"{os.path.basename(file_path)} (无法检测XOR值，已跳过)"
                self._update_gui(progress_msg, gui)
                return

            # 确保目标目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # 读取并解密文件
            with open(file_path, 'rb') as reader, open(output_file, 'wb') as writer:
                buffer_size = 102400  # 增加到100KB缓冲区以提高性能
                while True:
                    buffer = reader.read(buffer_size)
                    if not buffer:
                        break

                    # 对每个字节应用XOR操作
                    decrypted = bytes([b ^ xor_info[1] for b in buffer])
                    writer.write(decrypted)

            # 更新进度
            self.processed_files += 1
            progress_msg = f"{os.path.basename(file_path)} (大小: {file_size_kb:.2f}kb, XOR值: {xor_info[1]})"
            self._update_gui(progress_msg, gui)

        except Exception as e:
            error_msg = f"处理 {os.path.basename(file_path)} 时出错: {str(e)}"
            self._update_gui(error_msg, gui)
            self.processed_files += 1  # 即使出错也计数以保持进度准确

    def get_xor(self, file_path):
        """
        从文件头检测XOR密钥和文件类型

        返回:
            tuple: (file_extension, xor_key)
        """
        if not file_path or not os.path.exists(file_path):
            return [None, None]

        try:
            with open(file_path, 'rb') as f:
                header = f.read(10)  # 读取前10个字节以支持更长的签名

            return self.get_xor_from_bytes(header)
        except Exception as e:
            print(f"读取文件头时出错: {str(e)}")
            return [None, None]

    def get_xor_from_bytes(self, header_bytes):
        """
        从头部字节确定文件类型和XOR密钥

        Args:
            header_bytes: 文件的前几个字节

        Returns:
            tuple: (file_extension, xor_key)
        """
        result = [None, None]

        # 将字节转换为整数列表
        bytes_values = [b & 0xFF for b in header_bytes]

        # 尝试每个文件签名以找到匹配项
        for signature_hex, extension in self.FILE_TYPE_MAP.items():
            # 检查是否有足够的字节进行比较
            if len(signature_hex) < 6:
                continue

            # 将十六进制签名转换为字节（取前3-5个字节）
            hex_values = []
            signature_len = min(len(signature_hex), 10)  # 限制为最多10个字节

            for i in range(0, signature_len, 2):
                if i + 1 < len(signature_hex):
                    hex_values.append(int(signature_hex[i:i + 2], 16))

            # 检查是否有足够的头字节进行比较
            bytes_len = min(len(bytes_values), len(hex_values))
            if bytes_len < 3:
                continue

            # 计算潜在的XOR值
            xor_values = [0] * bytes_len
            match_count = 0

            for i in range(bytes_len):
                xor_values[i] = bytes_values[i] ^ hex_values[i]

            # 找到出现最多的XOR值
            if len(xor_values) >= 3 and xor_values[0] == xor_values[1] and xor_values[0] == xor_values[2]:
                result[0] = extension
                result[1] = xor_values[0]
                break

        return result


class WxChatDecryptGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("微信图片解密工具")
        self.root.geometry("700x500")
        self.converter = WxChatImgRevert()

        # 设置主题样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")

        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 路径框架
        path_frame = ttk.LabelFrame(main_frame, text="路径设置", padding="5")
        path_frame.pack(fill=tk.X, pady=5)

        # 源路径
        ttk.Label(path_frame, text="源路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.source_entry = ttk.Entry(path_frame, width=50)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(path_frame, text="浏览", command=lambda: self.browse_folder(self.source_entry)).grid(row=0, column=2,
                                                                                                        padx=5)

        # 目标路径
        ttk.Label(path_frame, text="目标路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.target_entry = ttk.Entry(path_frame, width=50)
        self.target_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(path_frame, text="浏览", command=lambda: self.browse_folder(self.target_entry)).grid(row=1, column=2,
                                                                                                        padx=5)

        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 日志区域
        self.log_area = scrolledtext.ScrolledText(log_frame, width=80, height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area.insert(tk.END, "欢迎使用微信图片解密工具。请选择源路径和目标路径，然后点击'开始解密'按钮。")

        # 进度框架
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)

        # 进度条
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 进度标签
        self.progress_label = ttk.Label(progress_frame, text="就绪")
        self.progress_label.pack(side=tk.RIGHT, padx=5)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        # 转换按钮
        self.convert_btn = ttk.Button(button_frame, text="开始解密", command=self._start_conversion)
        self.convert_btn.pack(side=tk.LEFT, padx=5)

        # 关于按钮
        ttk.Button(button_frame, text="关于", command=self.show_about).pack(side=tk.LEFT, padx=5)

        # 退出按钮
        ttk.Button(button_frame, text="退出", command=self.root.destroy).pack(side=tk.LEFT, padx=5)

    def browse_folder(self, entry_widget):
        """打开文件对话框选择文件夹"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder_path)

    def _start_conversion(self):
        """启动转换过程"""
        self.converter._start_conversion(self)

    def show_about(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.transient(self.root)  # 设置为主窗口的子窗口
        about_window.grab_set()  # 模态对话框

        # 创建内容框架
        content_frame = ttk.Frame(about_window, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(
            content_frame,
            text="微信图片解密工具",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 10))

        # 版本和作者信息
        ttk.Label(
            content_frame,
            text="作者: Evil0ctal",
            font=("Arial", 10)
        ).pack(pady=2)

        # 描述
        ttk.Label(
            content_frame,
            text="用于解密微信缓存的图片文件",
            font=("Arial", 10)
        ).pack(pady=2)

        # 开源声明
        ttk.Label(
            content_frame,
            text="本软件是免费开源的，请不要倒卖此软件",
            font=("Arial", 10),
            foreground="red"
        ).pack(pady=10)

        # GitHub链接
        github_frame = ttk.Frame(content_frame)
        github_frame.pack(pady=10)

        ttk.Label(
            github_frame,
            text="GitHub: ",
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        github_link = ttk.Label(
            github_frame,
            text="https://github.com/Evil0ctal/WeChat-image-decryption",
            font=("Arial", 10),
            foreground="blue",
            cursor="hand2"
        )
        github_link.pack(side=tk.LEFT)
        github_link.bind("<Button-1>",
                         lambda e: webbrowser.open_new("https://github.com/Evil0ctal/WeChat-image-decryption"))

        # 关闭按钮
        ttk.Button(
            content_frame,
            text="关闭",
            command=about_window.destroy
        ).pack(pady=20)

    def ask_open_directory(self, directory):
        """询问是否打开目标目录"""
        if messagebox.askyesno("解密完成", "所有文件已解密完成，是否打开目标目录查看文件？"):
            self.open_directory(directory)

    def open_directory(self, directory):
        """打开指定目录"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(directory)
            elif os.name == 'posix':  # macOS, Linux
                if os.path.exists('/usr/bin/open'):  # macOS
                    subprocess.call(['open', directory])
                else:  # Linux
                    subprocess.call(['xdg-open', directory])
            else:
                self.log_area.insert(tk.END, "\n无法自动打开目录，请手动打开: " + directory)
        except Exception as e:
            self.log_area.insert(tk.END, f"\n打开目录时发生错误: {str(e)}")
            messagebox.showerror("错误", f"无法打开目录: {str(e)}")


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='微信图片解密工具')
    parser.add_argument('--source', '-s', help='包含加密文件的源路径')
    parser.add_argument('--target', '-t', help='解密文件的目标目录')
    parser.add_argument('--gui', '-g', action='store_true', help='启动GUI模式')

    args = parser.parse_args()

    if args.gui or (not args.source and not args.target):
        root = tk.Tk()
        app = WxChatDecryptGUI(root)
        root.protocol("WM_DELETE_WINDOW", root.destroy)  # 确保窗口关闭时终止程序
        root.mainloop()
    elif args.source and args.target:
        converter = WxChatImgRevert()
        converter.convert(args.source, args.target)
    else:
        print("请同时指定源路径和目标路径，或使用--gui参数启动图形界面。")
        parser.print_help()


if __name__ == "__main__":
    main()
