from listener import receive_audio,SpeechDetection
from speaker import send_audio
import threading
import os
from daily_init import get_init
from constants import SAMPLE_RATE, NUM_CHANNELS, SPEECH_THRESHOLD, SPEECH_THRESHOLD_MS, SILENCE_THRESHOLD_MS, VAD_RESET_PERIOD_MS

client,app_error,app_quit,microphone_device,speaker_device,Daily = get_init()
vad = Daily.create_native_vad(
            reset_period_ms=VAD_RESET_PERIOD_MS,
            sample_rate=SAMPLE_RATE,
            channels=NUM_CHANNELS)
vad = SpeechDetection(sample_rate=SAMPLE_RATE,num_channels=NUM_CHANNELS,vad=vad)
thread1 = threading.Thread(target=receive_audio,args=(speaker_device,vad,app_quit,app_error,client),daemon=True)
thread2 = threading.Thread(target=send_audio, args=(microphone_device, app_quit, app_error,client), daemon=True)
os.system("rm -rf student/* bot/*")
try:
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
except:
    client.leave()
    client.release()