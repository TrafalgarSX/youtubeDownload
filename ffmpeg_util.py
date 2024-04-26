import ffmpeg
from PyQt6.QtCore import QThread, pyqtSignal


def extract_audio(video_path, audio_path):
    try:
        out, err = ffmpeg.input(video_path).output(audio_path).run_async()
    except ffmpeg.Error as e:
        raise e


def clip_video(video_path, output_path, start_time, end_time):
    # start_time_obj = datetime.datetime.strptime(start_time, "%H:%M:%S")
    # end_time_obj = datetime.datetime.strptime(end_time, "%H:%M:%S")
    print(start_time, end_time)
    duration_obj = end_time - start_time
    duration = str(duration_obj)
    (
        ffmpeg.input(video_path)
        .output(output_path, ss=start_time, t=duration)
        .run_async()
    )


class FfmpegThread(QThread):
    finished = pyqtSignal()

    def __init__(self, video_path, output_path, start_time, end_time):
        super().__init__()
        self.video_path = video_path
        self.output_path = output_path
        self.start_time = start_time
        self.end_time = end_time

    def run(self):
        duration_obj = self.end_time - self.start_time
        duration = str(duration_obj)
        process = (
            ffmpeg.input(self.video_path)
            .output(self.output_path, ss=self.start_time, t=duration)
            .run_async()
        )
        process.wait()  # 等待 ffmpeg 命令完成
        self.finished.emit()  # 发出 finished 信号


# thread = FfmpegThread("input.mp4", "output.mp4", start_time, end_time)
# thread.finished.connect(on_finished)  # on_finished 是当 ffmpeg 命令完成时要调用的函数
# thread.start()


def get_duration(file_path):
    metadata = ffmpeg.probe(file_path)
    duration = float(metadata["format"]["duration"])
    return int(duration)
