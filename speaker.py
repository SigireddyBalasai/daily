import wave
import threading
import time
import os
semaphore = threading.Semaphore(1)




def send_audio(microphone_device,app_quit,app_error,client):

    try:
        if app_error:
            print(f"Unable to receive audio!")
            return
            
        while not app_quit:
            with semaphore:
                output_files = os.listdir("bot/")
                output_files.remove('.gitkeep')
                output_files.sort()
                if len(output_files) != 0:
                    print("output_files: ", output_files)
                    i = 0
                    while i < len(output_files):
                        file = output_files[i]
                        file_path = "bot/"+file
                        print("file_path: ", file_path)
                        if not file_path.endswith(".wav"):
                            i += 1
                            continue
                        file_data = wave.open(file_path, 'rb')
                        total_frames = file_data.getnframes()
                        sample_rate = file_data.getframerate()
                        frames = file_data.readframes(total_frames)
                        for j in range(0, total_frames, int(sample_rate / 100)):
                            buffer = frames[j:j + int(sample_rate / 100)]
                        microphone_device.write_frames(frames)
                        duration = total_frames / sample_rate
                        print(f"Sent audio of duration {duration:.2f} seconds")
                        # time.sleep(duration)
                        file_data.close()
                        os.rename(file_path,"bot_temp/"+file)
                        i += 1
                else:
                    pass
    except KeyboardInterrupt:
                client.leave()
                client.release()




