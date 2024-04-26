import os
import re

from yt_dlp import YoutubeDL
from PyQt6.QtCore import QThread, pyqtSignal


def get_video_info(url):
    ydl_opts = {
        "quiet": True,  # 不打印输出到控制台
        "no_warnings": True,  # 不显示警告信息
        "simulate": True,  # 不下载视频，只获取信息
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get("title", None)
        formats = info_dict.get("formats", [])
        video_info = []
        for f in formats:
            format_id = f.get("format_id", None)
            ext = f.get("ext", None)
            if ext == "mhtml":
                continue
            resolution = f.get("height", None)
            video_info.append((format_id, ext, resolution))

        return title, video_info


def download_video(url, format_id, output_dir, progress_hook):
    ydl_opts = {
        "quiet": True,  # 不打印输出到控制台
        "no_warnings": True,  # 不显示警告信息
        "format": format_id,  # 指定视频格式
        "outtmpl": os.path.join(
            output_dir, "%(title)s.%(ext)s"
        ),  # 指定输出目录和文件名格式
        "progress_hooks": [progress_hook],  # 添加进度钩子
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


class DownloadThread(QThread):
    download_finished = pyqtSignal(bool, str, str)
    update_progress = pyqtSignal(int, int)

    def __init__(self, url, format_id, output_dir, index):
        super().__init__()
        self.url = url
        self.format_id = format_id
        self.output_dir = output_dir
        self.index = index

    def create_thread_progress_hook(self):
        def thread_progress_hook(d):
            if d["status"] == "downloading":
                percent_str = d["_percent_str"]
                percent_str = re.sub(
                    r"\x1b\[.*?m", "", percent_str
                )  # 去掉 ANSI escape code
                percent = float(percent_str.strip("%"))  # 去掉 "%"，转换为浮点数
                self.update_progress.emit(self.index, int(percent))  # 更新进度

        return thread_progress_hook

    def run(self):
        progress_hook = self.create_thread_progress_hook()
        ydl_opts = {
            "quiet": True,  # 不打印输出到控制台
            "no_warnings": True,  # 不显示警告信息
            "format": self.format_id,  # 指定视频格式
            "outtmpl": os.path.join(
                self.output_dir, "%(title)s.%(ext)s"
            ),  # 指定输出目录和文件名格式
            "progress_hooks": [progress_hook],  # 添加进度钩子
        }
        download_item_identifier = self.url + self.format_id
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
        except Exception as e:
            err_str = self.format_id + " 下载失败，错误信息：\n" + str(e)
            self.download_finished.emit(
                False, err_str, download_item_identifier
            )  # 发出 finished 信号
            return

        self.download_finished.emit(
            True, "下载完成", download_item_identifier
        )  # 发出 finished 信号


class GetVideoInfoThread(QThread):
    get_video_info_finished = pyqtSignal(bool, str, str, list, str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        ydl_opts = {
            "quiet": True,  # 不打印输出到控制台
            "no_warnings": True,  # 不显示警告信息
            "simulate": True,  # 不下载视频，只获取信息
        }

        video_info = []
        title = ""
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
                title = info_dict.get("title", None)
                formats = info_dict.get("formats", [])
                for f in formats:
                    format_id = f.get("format_id", None)
                    ext = f.get("ext", None)
                    if ext == "mhtml":
                        continue
                    resolution = f.get("height", None)
                    video_info.append((format_id, ext, resolution))
        except Exception as e:
            err_str = "获取视频信息失败，错误信息：\n" + str(e)
            self.get_video_info_finished.emit(False, err_str, "", [], self.url)
            return

        self.get_video_info_finished.emit(
            True, "success", title, video_info, self.url
        )


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=4lcCK0xyS78"
    title, video_info = get_video_info(url)
    print(title)
    print(video_info)
