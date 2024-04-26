import os
import platform
import subprocess
import sys
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QMessageBox,
    QWidget,
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QGroupBox,
    QFileDialog,
)
from PyQt6.QtCore import pyqtSlot
from dowload_links_widget import DownloadLinksWidget
from video_widget import VideoWidget

import yt_dlp_util as yp_util
import ffmpeg_util as ff_util

audio_ext = ["mp3", "m4a", "wav", "flac", "aac", "ogg", "opus"]

video_ext = ["mp4", "mkv", "webm", "avi", "mov", "wmv", "flv", "3gp", "m4v"]


class YoutubeDLWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        # add action
        self.settings_action = self.file_menu.addAction("Settings")
        self.settings_action.triggered.connect(self.on_settings_clicked)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.url_input())
        main_layout.addWidget(self.download_links_widget())
        main_layout.addWidget(self.video_distract())

        central_widget = QWidget()  # 创建一个新的QWidget
        central_widget.setLayout(main_layout)  # 将布局设置到新的QWidget上
        self.download_links_threads = {}

        self.setCentralWidget(central_widget)  # 将新的QWidget设置为中心窗口
        self.setWindowTitle("视频下载工具")
        self.resize(800, 600)

    @pyqtSlot()
    def on_settings_clicked(self):
        pass

    def url_input(self):
        url_input_layout = QGridLayout()

        self.url_label = QLabel("URL:")
        self.url_edit = QLineEdit()
        self.download_links = QPushButton("show download links")

        self.download_links.clicked.connect(self.update_list_widget)

        url_input_layout.addWidget(self.url_label, 0, 0)
        url_input_layout.addWidget(self.url_edit, 0, 1)
        url_input_layout.addWidget(self.download_links, 0, 2)

        fixed_height = 35
        self.url_label.setFixedHeight(fixed_height)
        self.download_links.setFixedHeight(fixed_height)
        self.url_edit.setFixedHeight(fixed_height)

        self.url_edit.setPlaceholderText("input url here")
        url_input_widgtet = QWidget()

        url_input_widgtet.setStyleSheet(
            """
            QLabel, QPushButton, QLineEdit{
                border: 1px solid gray;
                border-radius: 10px;
                padding: 0 8px;
            }
            """
        )
        url_input_widgtet.setObjectName("input_widget")
        url_input_widgtet.setLayout(url_input_layout)
        return url_input_widgtet

    def download_links_widget(self):
        self.links_widget = DownloadLinksWidget()
        self.links_widget.show_download_result.connect(self.showMessageBox)
        return self.links_widget

    @pyqtSlot()
    def update_list_widget(self):
        self.links_widget.clear_model()
        url = self.url_edit.text()
        if url == "":
            self.showMessageBox(
                QMessageBox.Icon.Warning,
                "请输入URL",
                QMessageBox.StandardButton.Ok,
            )
        else:
            self.links_widget.set_url(url)
            download_links_thread = yp_util.GetVideoInfoThread(url)
            self.download_links_threads[url] = download_links_thread
            download_links_thread.get_video_info_finished.connect(
                self.on_get_video_info_finished
            )
            download_links_thread.start()

    @pyqtSlot(bool, str, str, list, str)
    def on_get_video_info_finished(
        self, success, err_str, title, video_info, url
    ):
        # close thread
        self.download_links_threads[url].deleteLater()
        self.download_links_threads.pop(url)
        if success:
            for info in video_info:
                self.addTableItem(title, info)
        else:
            self.showMessageBox(
                QMessageBox.Icon.Warning,
                err_str,
                QMessageBox.StandardButton.Ok,
            )

    def video_distract(self):
        distract_layout = QGridLayout()
        fixed_height = 35

        self.select_file_btn = QPushButton("select file")
        self.file_path_edit = QLineEdit()
        self.distract_btn = QPushButton("distract")
        self.video_widget = VideoWidget(1, fixed_height)
        self.trim_btn = QPushButton("trim")
        # 自定义输出路径  distract or trim
        output_layout = QHBoxLayout()
        self.output_filedir = QLineEdit()
        self.output_dir_btn = QPushButton("output dir")
        self.output_filename = QLineEdit()
        self.output_ext_combox = QComboBox()
        self.open_audio_btn = QPushButton("open audio")
        self.delete_audio_btn = QPushButton("delete audio")
        output_layout.addWidget(self.output_filedir)
        output_layout.addWidget(self.output_dir_btn)
        output_layout.addWidget(self.output_filename)
        output_layout.addWidget(self.output_ext_combox)
        output_layout.addWidget(self.open_audio_btn)
        output_layout.addWidget(self.delete_audio_btn)
        for ext in audio_ext:
            self.output_ext_combox.addItem(ext)

        for ext in video_ext:
            self.output_ext_combox.addItem(ext)

        self.file_path_edit.setPlaceholderText("select file")
        self.output_filedir.setPlaceholderText("自定义输出文件目录  distract or trim")
        self.output_filename.setPlaceholderText("自定义输出文件名  distract or trim")

        self.select_file_btn.clicked.connect(self.select_file)
        self.distract_btn.clicked.connect(self.distract_selected_file)
        self.trim_btn.clicked.connect(self.trim_video)
        self.output_dir_btn.clicked.connect(self.select_output_filedir)
        self.open_audio_btn.clicked.connect(self.open_audio_file)
        self.delete_audio_btn.clicked.connect(self.delete_audio_file)

        self.select_file_btn.setFixedHeight(fixed_height)
        self.file_path_edit.setFixedHeight(fixed_height)
        self.distract_btn.setFixedHeight(fixed_height)
        self.trim_btn.setFixedHeight(fixed_height)

        self.output_filedir.setFixedHeight(fixed_height)
        self.output_dir_btn.setFixedHeight(fixed_height)
        self.output_filename.setFixedHeight(fixed_height)
        self.output_ext_combox.setFixedHeight(fixed_height)
        self.open_audio_btn.setFixedHeight(fixed_height)
        self.delete_audio_btn.setFixedHeight(fixed_height)

        distract_layout.addWidget(self.file_path_edit, 0, 0)
        distract_layout.addWidget(self.select_file_btn, 0, 1)
        distract_layout.addWidget(self.distract_btn, 0, 2)
        distract_layout.addWidget(self.video_widget, 1, 0, 1, 2)
        distract_layout.addWidget(self.trim_btn, 1, 2, 1, 1)

        # distract_layout.addWidget(output_layout, 2, 0, 1, 3)
        distract_layout.addLayout(output_layout, 2, 0, 1, 3)

        distract_group_box = QGroupBox("Distract")
        distract_group_box.setStyleSheet(
            """
            QLabel, QPushButton, QLineEdit{
                border: 1px solid gray;
                border-radius: 10px;
                padding: 0 8px;
            }
            """
        )
        distract_group_box.setLayout(distract_layout)
        return distract_group_box

    def addTableItem(self, title, video_info):
        self.links_widget.add_data_to_model(title, video_info)

    @pyqtSlot()
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "select file", "")
        if file_path != "":
            self.file_path_edit.setText(file_path)
            dirname = os.path.dirname(file_path)
            filename_with_ext = os.path.basename(file_path)
            filename = filename_with_ext.split(".")[0]
            ext = filename_with_ext.split(".")[1]
            self.output_filedir.setText(dirname)
            self.output_filename.setText(filename)
            self.output_ext_combox.setCurrentText(ext)
            if ext in audio_ext:
                self.distract_btn.setEnabled(False)
            else:
                self.distract_btn.setEnabled(True)
            end_time = ff_util.get_duration(file_path)
            self.video_widget.set_slider_value(0, end_time)
            self.video_widget.set_end_time(end_time)
            self.video_widget.set_max_time(end_time)

    # TODO trim 时，如果文件已经存在，提示是否覆盖
    @pyqtSlot()
    def trim_video(self):
        # call ffmpeg
        file_path = self.file_path_edit.text()
        start_time = self.video_widget.get_start_time()
        end_time = self.video_widget.get_end_time()
        output_path = self.get_output_file_path()
        ff_util.clip_video(file_path, output_path, start_time, end_time)

    # TODO 提取音频时，如果文件已经存在，提示是否覆盖
    @pyqtSlot()
    def distract_selected_file(self):
        file_path = self.file_path_edit.text()
        output_path = self.get_output_file_path()
        try:
            ff_util.extract_audio(file_path, output_path)
        except Exception as e:
            print(e)
            self.showMessageBox(
                QMessageBox.Icon.Warning,
                "提取音频失败",
                QMessageBox.StandardButton.Ok,
            )

    @pyqtSlot()
    def select_output_filedir(self):
        # select output dir
        output_dir = QFileDialog.getExistingDirectory(self, "select output dir")
        if output_dir:
            self.output_filedir.setText(output_dir)

    def get_output_file_path(self):
        return (
            self.output_filedir.text()
            + "/"
            + self.output_filename.text()
            + "."
            + self.output_ext_combox.currentText()
        )

    @pyqtSlot()
    def open_audio_file(self):
        audio_file_path = self.get_output_file_path()
        # 使用 默认的程序打开文件
        if audio_file_path != "" and os.path.exists(audio_file_path):
            if platform.system() == "Windows":
                os.startfile(audio_file_path)
            else:
                opener = "open" if platform.system() == "Darwin" else "xdg-open"
                subprocess.call([opener, audio_file_path])

    @pyqtSlot()
    def delete_audio_file(self):
        audio_file_path = self.get_output_file_path()
        # 删除文件
        if (audio_file_path != "") and os.path.exists(audio_file_path):
            # 提示是否删除 show message
            result = self.showMessageBox(
                QMessageBox.Icon.Information,
                "是否删除文件",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result == QMessageBox.StandardButton.Yes:
                os.remove(audio_file_path)

    @pyqtSlot(QMessageBox.Icon, str, QMessageBox.StandardButton)
    def showMessageBox(self, icon, message, msg_btn):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("提示")
        msgBox.setText(message)
        msgBox.setIcon(icon)
        result = msgBox.setStandardButtons(msg_btn)
        msgBox.exec()
        return result


def main():
    # 这个就是要开发的app
    app = QApplication(sys.argv)
    # 创建一个QMainWindow, 用来装载你需要的各种组件、空间
    # ui是创建的ui类的实例化对象
    ui = YoutubeDLWindow()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
