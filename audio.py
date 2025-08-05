import speech_recognition as sr
from pynput import keyboard
import threading
import time

recognizer = sr.Recognizer()
microphone = sr.Microphone()
is_recording = False
audio_data = []
recording_thread = None



def start_recording():
    global is_recording, audio_data
    
    print("Recording...")
    audio_data.clear()
    
    try:
        with microphone as source:
            start_time = time.time()
            
            while is_recording:
                try:
                    chunk = recognizer.listen(source, timeout=0.1, phrase_time_limit=None)
                    audio_data.append(chunk)
                    if not is_recording:
                        break
                except sr.WaitTimeoutError:
                    print("vide for now")
                    continue
                except Exception as e:
                    if is_recording:
                        print(f"Error during recording: {e}")
                    break
            
            if time.time() - start_time < 0.5:
                print("Speak more")
                audio_data = None
                
    except Exception as e:
        print(f"Error occuring at start recording: {e}")


def combine_audio_chunks(chunks):
    if not chunks:
        return None
    
    if len(chunks) == 1:
        return chunks[0]
    
    sample_rate = chunks[0].sample_rate
    sample_width = chunks[0].sample_width
    
    combined_data = b''.join(chunk.frame_data for chunk in chunks)
    
    return sr.AudioData(combined_data, sample_rate, sample_width)


def process_audio():
    global audio_data
    
    combined_audio = combine_audio_chunks(audio_data)

    if combined_audio is None:
        print("No audio to process")
        return
    
    print("Processing...")
    
    try:
        text = recognizer.recognize_google(combined_audio, language='en-US')
        print(f"You said: {text}")
        
    except sr.UnknownValueError:
        print("I didn't understand")
    except sr.RequestError as e:
        print(f"Error service: {e}")
    except Exception as e:
        print(f"Errorr: {e}")

def on_key_press(key):
    global is_recording, recording_thread
    
    if key == keyboard.Key.space and not is_recording:
        is_recording = True
        
        recording_thread = threading.Thread(target=start_recording)
        recording_thread.daemon = True
        recording_thread.start()

def on_key_release(key):
    global is_recording, recording_thread
    
    if key == keyboard.Key.esc:
        print("All done")
        return False
    
    if key == keyboard.Key.space and is_recording:
        is_recording = False
        print("Stop Recording")
        
        if recording_thread and recording_thread.is_alive():
            recording_thread.join(timeout=2)
        
        processing_thread = threading.Thread(target=process_audio)
        processing_thread.daemon = True
        processing_thread.start()

def main():
    print("Hold SPACE to talk, ESC to Close")
    
    print("Eliminating noise...")
    
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=3)
    
    print("Ready")
    
    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()