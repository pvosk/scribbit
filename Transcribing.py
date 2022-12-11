# Import Libraries

import whisper
import os
from pytube import YouTube
from datetime import timedelta
import glob
from pydub import AudioSegment
import streamlit as st

st.set_page_config(layout="wide")

# File Path
destination = "tempDir"

st.subheader("*SCRIBBIT* \n Transcription Made *Easy*")
st.write("")



@st.cache
def load_whisper_model(size):
    model = whisper.load_model(size)
    # model = whisper.load_model("medium")
    return model


def clear_directory(directory):
    # Delete other files in temp folder
    for dirpath, dirnames, filenames in os.walk(directory):
        # Remove regular files, ignore directories
        for filename in filenames:
            os.unlink(os.path.join(dirpath, filename))


def get_yt_audio(url):

    # Delete previous files in temp folder
    clear_directory(destination)

    # Create youtube object with url, get audio only
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()

    # Download
    download = video.download(output_path=destination)

    # Save, Rename as .mp3
    base, ext = os.path.splitext(download)
    new_filename = base + '.mp3'
    os.rename(download, new_filename)

    # Export mp3
    new_file = AudioSegment.from_file(new_filename).export(new_filename, format="mp3")

    return new_file


def get_file_audio(upload_file):
    # Delete previous files in temp folder
    clear_directory(destination)

    # Define new filename
    upload_filename = os.path.splitext(os.path.basename(upload_file.name))[0] + ".mp3"

    # Open file upload, export to temp directory
    new_file = AudioSegment.from_file(upload_file).export(destination + "/" + upload_filename, format="mp3")

    return new_file


def preprocess_audio(load_audio):
    audio = whisper.load_audio(load_audio.name)
    audio = whisper.pad_or_trim(audio)
    return audio


def transcribe(load_audio):

    model = load_whisper_model("medium")

    # Transcribe
    result = model.transcribe(load_audio.name)

    return result


def yt_process():

    # Get url from user
    yt_url = st.text_input("Enter the YouTube URL of the video you want to transcribe!",
                           "https://www.youtube.com/watch?v=pqZqfTOxFhY")

    # Transcribe youtube url button functionality
    yt_button = st.button("Transcribe")

    if yt_button:
        load_audio = get_yt_audio(yt_url)

        result = transcribe(load_audio)

        return result


def file_process():
    upload = st.file_uploader("Choose an audio file", type=['.wav', '.mp3', '.flac', '.aac',
                                                            '.wave', '.mp4', '.mov', 'm4v'])

    if upload is not None:
        file_button = st.button("Transcribe")
        if file_button:

            load_audio = get_file_audio(upload)

            result = transcribe(load_audio)

            return result


def format_script(transcript):

    spaced_lines = str("")

    if transcript is not None:

        for i in range(len(transcript["segments"])):
            start = round(transcript["segments"][i]['start'])
            end = round(transcript["segments"][i]['end'])
            line = str(timedelta(seconds=start)) + "  -  " + str(timedelta(seconds=end)) + str(
                transcript["segments"][i]["text"])
            spaced_lines += line + "\n"
        return spaced_lines


selection = st.radio("Transcribe a YouTube URL or local file?", ["Youtube URL", "File Upload"])

script = None

try:
    if selection == "Youtube URL":
        script = yt_process()

    if selection == "File Upload":
        script = file_process()

    st.audio(glob.glob('tempDir/*')[0])

    page = format_script(script)

    txt = st.text_area("Timestamped Transcript", value=page, placeholder="Transcript will appear here",
                       disabled=True)
    st.download_button("Download", txt)

except RuntimeError:
    st.write("No Transcript")
