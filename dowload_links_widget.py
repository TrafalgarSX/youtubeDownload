import re
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableView,
    QProgressBar,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor

import yt_dlp_util as yp_util

from colorful_progressbar import ColourfulProgress


class DownloadLinksWidget(QWidget):
    show_download_result = pyqtSignal(
        QMessageBox.Icon, str, QMessageBox.StandardButton
    )

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.table_view = QTableView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(
            ["标题", "format_id", "文件类型", "清晰度", "进度", "操作"]
        )

        self.table_view.setModel(self.model)

        self.layout.addWidget(self.table_view)
        self.progress_bars = {}
        self.default_save_dir_path = "./"
        self.download_threads = {}

        self.setLayout(self.layout)

        self.resize(800, 600)

    def resizeEvent(self, event):
        single_width = 80
        total_width = self.table_view.width() - 6 * single_width
        self.table_view.setColumnWidth(0, int(total_width))
        self.table_view.setColumnWidth(1, int(single_width))
        self.table_view.setColumnWidth(2, int(single_width))
        self.table_view.setColumnWidth(3, int(single_width))
        self.table_view.setColumnWidth(4, int(single_width))
        self.table_view.setColumnWidth(5, int(single_width))

    def add_data_to_model(self, title, video_info):
        format_id, ext, resolution = video_info
        if resolution is None:
            resolution = "audio"
        else:
            resolution = f"{resolution}p"
        items = [
            QStandardItem(title),
            QStandardItem(format_id),
            QStandardItem(ext),
            QStandardItem(resolution),
            QStandardItem(),  # 进度条
            QStandardItem(),  # 操作按钮
        ]

        self.model.appendRow(items)

        # progress_bar = QProgressBar()
        progress_bar = ColourfulProgress(color=QColor("#85c440"))
        # progress_bar = ColourfulProgress(color=QColor("#f2b63c"))

        progress_bar.setValue(0)  # 设置进度条的值
        self.table_view.setIndexWidget(items[4].index(), progress_bar)
        current_index = self.model.indexFromItem(items[4]).row()
        self.progress_bars[current_index] = progress_bar  # 将进度条存储到字典中

        button = QPushButton("操作")
        button.clicked.connect(
            lambda checked=False, index=current_index: self.download(index)
        )
        self.table_view.setIndexWidget(items[5].index(), button)

    def clear_model(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(
            ["标题", "format_id", "文件类型", "清晰度", "进度", "操作"]
        )
        self.progress_bars.clear()

    # TODO 下载时检测是否存在相同的文件，如果存在则提示是否覆盖
    @pyqtSlot(int)
    def download(self, index):
        file_path = QFileDialog.getExistingDirectory(
            self, "选择文件保存路径", self.default_save_dir_path
        )
        if file_path == "":
            return

        format_id = self.model.item(index, 1).text()

        download_thread = yp_util.DownloadThread(
            self.url, format_id, file_path, index
        )
        download_links_identifier = self.url + format_id
        self.download_threads[download_links_identifier] = download_thread
        download_thread.download_finished.connect(self.download_finished)
        download_thread.update_progress.connect(self.update_progress)
        download_thread.start()

    @pyqtSlot(bool, str, str)
    def download_finished(self, success, msg, download_item_identifier):
        if not success:
            self.show_download_result.emit(
                QMessageBox.Icon.Warning, msg, QMessageBox.StandardButton.Ok
            )
        else:
            self.show_download_result.emit(
                QMessageBox.Icon.Information, msg, QMessageBox.StandardButton.Ok
            )
        # close thread
        self.download_threads[download_item_identifier].deleteLater()
        self.download_threads.pop(download_item_identifier)

    def create_progress_hook(self, index):
        def progress_hook(d):
            if d["status"] == "downloading":
                percent_str = d["_percent_str"]
                percent_str = re.sub(
                    r"\x1b\[.*?m", "", percent_str
                )  # 去掉 ANSI escape code
                percent = float(percent_str.strip("%"))  # 去掉 "%"，转换为浮点数
                self.update_progress(index, int(percent))  # 更新进度

        return progress_hook

    def set_url(self, url):
        self.url = url

    @pyqtSlot(int, int)
    def update_progress(self, index, value):
        # 从字典中获取对应的进度条，并更新其值
        progress_bar = self.progress_bars.get(index)
        if progress_bar is not None:
            progress_bar.setValue(value)

    def set_default_save_path(self, path):
        self.default_save_dir_path = path
