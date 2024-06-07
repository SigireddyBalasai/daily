import os
import wave
import threading
import time
import sys
from daily import Daily, CallClient
from constants import SAMPLE_RATE, NUM_CHANNELS

Daily.init()



client = CallClient()
client.update_subscription_profiles({
        "base": {
            "camera": "subscribed",
            "microphone": "subscribed",
            "speaker": "subscribed"
        }
})
speaker_device = Daily.create_speaker_device(
        "my-speaker", sample_rate=SAMPLE_RATE, channels=NUM_CHANNELS)
Daily.select_speaker_device("my-speaker")

microphone_device = Daily.create_microphone_device(
    "my-microphone",
    sample_rate=24000,
    channels=1
)

app_quit = False
app_error = None
def on_joined(data, error):
    if error:
        print(f"Unable to join meeting: {error}")
        app_error = error

client.join("https://balasai.daily.co/balasai", completion=on_joined,
client_settings={"inputs":{
        "camera": False,
        "microphone": {
            "isEnabled": True,
            "settings": {
                "deviceId" : "my-microphone"
        }
}}})
time.sleep(2)