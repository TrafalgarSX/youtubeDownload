from pytube import YouTube
from pytube.cli import on_progress
import traceback
import ffmpeg
import os

proxy = {"http": "socks5h://127.0.0.1:7890", "https": "socks5h://127.0.0.1:7890"}


def OnProgress(stream=None, chunk=None, bytesRemaining=None):
    """Callback function"""
    total_size = stream.filesize
    bytesDownloaded = total_size - bytesRemaining
    pctCompleted = bytesDownloaded / total_size * 100
    print(f"Status:{round(pctCompleted, 2)}%")


def OnComplete(stream, filepath):
    print("filepath", filepath)
    print(f"Download successful at location:{filepath}")
    pass


def Download(link):
    outputPath = os.getcwd()  # "D:/音乐/"
    video_only = False

    # video_only = True

    youtubeObject = YouTube(
        link,
        on_progress_callback=on_progress,
        on_complete_callback=OnComplete,
        proxies=proxy,
        use_oauth=False,
        allow_oauth_cache=True,
    )
    video = youtubeObject.streams.order_by("resolution").desc()

    video = (
        youtubeObject.streams.filter(
            only_video=video_only,
            mime_type="video/mp4",
            adaptive=video_only,
            progressive=~video_only,
        )
        .order_by("resolution")
        .desc()
        .first()
    )
    print(youtubeObject.title)
    try:
        video.download(outputPath)
    except Exception as e:
        traceback.print_exc()
        print("There has been an error in downloading your youtube video")
    print("This video download has completed! Yahooooo!")

    if video_only:
        audio = (
            youtubeObject.streams.filter(only_audio=True, adaptive=True)
            .order_by("abr")
            .desc()
            .first()
        )

        try:
            audio.download(outputPath)
        except:
            print("There has been an error in downloading your youtube audio")
        print("This autio download has completed! Yahooooo!")

    return video.default_filename, audio.default_filename


def merge(videoPath, audioPath):
    videoPath = os.getcwd() + "/" + videoPath
    audioPath = os.getcwd() + "/" + audioPath
    inputVideo = ffmpeg.input(videoPath)
    inputAudio = ffmpeg.input(audioPath)
    # todo delete orginal mp4 file, create new a new mp4 file with video and audio
    ffmpeg.concat(inputVideo, inputAudio, v=1, a=1).output(
        os.getcwd() + "/" + "finishedVideo.mp4"
    ).run()


link = input("PUt your youtube link here!!! URL:")

videoPath, audioPath = Download(link)
# merge(videoPath, audioPath)
