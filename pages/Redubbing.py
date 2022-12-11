import torchaudio
import streamlit as st
import os
from speechbrain.pretrained import Tacotron2
from speechbrain.pretrained import HIFIGAN


st.subheader("Narrate a video *without* using your own voice *or* having to pay for voice talent")


# @st.cache
def initialize_model():
    # Intialize TTS (tacotron2) and Vocoder (HiFIGAN)
    tacotron2 = Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="tmpdir_tts")
    hifi_gan = HIFIGAN.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="tmpdir_vocoder")
    return tacotron2, hifi_gan

def clear_directory(directory):
    # Delete other files in temp folder
    for dirpath, dirnames, filenames in os.walk(directory):
        # Remove regular files, ignore directories
        for filename in filenames:
            os.unlink(os.path.join(dirpath, filename))


def encode_txt(input_text):
    clear_directory('tempDir_tts_audio')

    mel_output, mel_length, alignment = tacotron2.encode_text(input_text)

    # Running Vocoder (spectrogram-to-waveform)
    waveforms = hifi_gan.decode_batch(mel_output)

    # Save the waverform
    torchaudio.save('tempDir_tts_audio/synthesized.wav', waveforms.squeeze(1), 22050)


# Initialize

tacotron2, hifi_gan = initialize_model()


# Running the TTS
input_text = st.text_input("Enter what you want spoken")
try:
    st.button(" Synthesize Audio From Text", on_click=encode_txt(input_text))

    aud_down = st.audio('tempDir_tts_audio/synthesized.wav')
    st.download_button("Download", input_text)
except:
    st.write("")


# Integrate Custom MEL vocoders
