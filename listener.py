import threading
import time

from enum import Enum
from datetime import datetime
import wave
import os
from constants import SAMPLE_RATE, NUM_CHANNELS, SPEECH_THRESHOLD, SPEECH_THRESHOLD_MS, SILENCE_THRESHOLD_MS, VAD_RESET_PERIOD_MS


class SpeechStatus(Enum):
    SPEAKING = 1
    NOT_SPEAKING = 2

class SpeechDetection:
    def __init__(self, sample_rate, num_channels,vad):
        self.__speech_threshold = SPEECH_THRESHOLD
        self.__speech_threshold_ms = SPEECH_THRESHOLD_MS
        self.__silence_threshold_ms = SILENCE_THRESHOLD_MS

        self.__status = SpeechStatus.NOT_SPEAKING
        self.__started_speaking_time = 0
        self.__last_speaking_time = 0

        self.__vad = vad
        

    def analyze(self, buffer):
        confidence = self.__vad.analyze_frames(buffer)
        current_time_ms = time.time() * 1000
        #print("confidence: ", confidence)
        if confidence > self.__speech_threshold:
            #print(time.time())
            diff_ms = current_time_ms - self.__started_speaking_time

            if self.__status == SpeechStatus.NOT_SPEAKING:
                self.__started_speaking_time = current_time_ms

            if diff_ms > self.__speech_threshold_ms:
                self.__status = SpeechStatus.SPEAKING
                self.__last_speaking_time = current_time_ms
        else:
            diff_ms = current_time_ms - self.__last_speaking_time
            if diff_ms > self.__silence_threshold_ms:
                self.__status = SpeechStatus.NOT_SPEAKING

        return confidence, self.__status


def record_audio_to_file(file_path, frames):
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(NUM_CHANNELS)
        wf.setsampwidth(2)  # assuming 16-bit audio
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))


def receive_audio(speaker_device, vad, app_quit, app_error,client):
    try:
        if app_error:
            print(f"Unable to receive audio!")
            return

        frames = []
        recording = False
        recording_start_time = None

        while not app_quit:
            buffer = speaker_device.read_frames(int(SAMPLE_RATE / 100))
            if len(buffer) > 0:
                confidence, status = vad.analyze(buffer)
                # print(confidence)
                if status == SpeechStatus.SPEAKING and recording:
                    frames.append(buffer)
                    print(datetime.now(),confidence)

                if status == SpeechStatus.SPEAKING:
                    if not recording:
                        recording_start_time = time.time()
                        recording = True
                else:
                    if recording:
                        recording_duration = time.time() - recording_start_time
                        if recording_duration > 1:  # Minimum duration for a file
                            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
                            file_name = f"student/audio_{current_time}.wav"
                            record_audio_to_file(file_name, frames)
                            print(f"Saved audio to {file_name} and time is {datetime.now()}")
                        frames = []
                        recording = False
    except KeyboardInterrupt:
        client.leave()
        client.release()

                    







