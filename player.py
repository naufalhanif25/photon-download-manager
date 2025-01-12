# Importing necessary libraries
import sounddevice
import soundfile
import threading

# Function to play a sound from the given file path
def playsound(path):
    # Function to start sound playback
    def play(path):
        # Read audio data and sampling rate from the file
        data, rate = soundfile.read(path, dtype = "float32")  
        
        # Play the audio data with the specified sampling rate
        sounddevice.play(data, rate)
        sounddevice.wait()

    # Create a new thread to play the sound
    threading.Thread(target = play, args = (path,)).start()
