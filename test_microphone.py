import speech_recognition as sr
import pyaudio

print("=" * 50)
print("MICROPHONE DIAGNOSTIC TEST")
print("=" * 50)

# Test 1: Check available audio devices
print("\n1. Checking available microphones...")
try:
    p = pyaudio.PyAudio()
    print(f"Total audio devices: {p.get_device_count()}")

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"\nDevice {i}: {info['name']}")
        print(f"   Channels: {info['maxInputChannels']}")
        print(f"   Sample Rate: {info['defaultSampleRate']}")
        if info['maxInputChannels'] > 0:
            print(f"   ✓ This is an INPUT device")
    p.terminate()
except Exception as e:
    print(f"Error checking devices: {e}")

# Test 2: Try to access microphone with speech_recognition
print("\n" + "=" * 50)
print("2. Testing speech recognition with microphone...")
try:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("✓ Microphone accessed successfully!")
        print("Listening for 5 seconds...")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✓ Ambient noise detected and adjusted")

            audio = recognizer.listen(source, timeout=5)
            print(f"✓ Audio captured ({len(audio.frame_data)} bytes)")

            # Try to recognize
            text = recognizer.recognize_google(audio)
            print(f"✓ Recognized: {text}")
        except sr.UnknownValueError:
            print("⚠ Audio captured but couldn't understand it (try speaking louder)")
        except sr.RequestError as e:
            print(f"✗ API Error: {e}")
        except sr.Timeout:
            print("✗ No sound detected - microphone may not be picking up audio")
except Exception as e:
    print(f"✗ Cannot access microphone: {e}")
    print("\nTroubleshooting:")
    print("- Check if microphone is plugged in")
    print("- Check Windows Sound Settings")
    print("- Try running as Administrator")
    print("- Disable other audio apps using microphone")

print("\n" + "=" * 50)
