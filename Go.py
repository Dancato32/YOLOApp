from ultralytics import YOLO
import pyttsx3
from collections import Counter
import time
import cv2


print("Loading YOLO model...")
model = YOLO("yolov8n.pt")
print("Model loaded successfully!")


last_speech_time = 0
speech_interval = 3  

print("Starting webcam detection... Press 'q' to quit")
print("=" * 50)


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot open camera")
    exit()

def speak_message(message):
    """Function to handle speech with fresh engine each time"""
    try:
        print(f"🔊 Speaking: {message}")
        
        # Create fresh engine each time - this fixes the stuck issue!
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        
        engine.say(message)
        engine.runAndWait()
        
        # Clean up engine
        engine.stop()
        del engine
        
        print("✓ Speech completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Speech failed: {e}")
        return False

try:
    while True:
        # Read frame from camera
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame")
            break
        
        # Run YOLO detection on this frame
        results = model.predict(frame, conf=0.5, verbose=False)
        
        # Process detections
        labels = []
        annotated_frame = frame.copy()
        
        for result in results:
            if result.boxes is not None:
                # Draw annotations
                annotated_frame = result.plot()
                
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    label = model.names[cls_id]
                    
                    # Only include high-confidence detections
                    if confidence > 0.5:
                        labels.append(label)
        
        # Display the frame
        cv2.imshow('YOLO Detection', annotated_frame)
        
        # Speech logic
        current_time = time.time()
        
        if labels and (current_time - last_speech_time > speech_interval):
            # Count objects
            counts = Counter(labels)
            messages = []
            
            for label, count in counts.items():
                if count == 1:
                    messages.append(f"a {label}")
                else:
                    messages.append(f"{count} {label}s")
            
            if messages:
                full_message = "I see " + ", ".join(messages)
                
                # Use the new speak function that creates fresh engine
                if speak_message(full_message):
                    last_speech_time = current_time
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nStopping detection...")

except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("Program stopped successfully!")


# ========== BACKUP SOLUTION - If pyttsx3 still doesn't work ==========

def backup_version_with_system_tts():
    """Alternative version using system TTS commands"""
    print("\n=== BACKUP VERSION WITH SYSTEM TTS ===")
    
    import os
    import platform
    
    def system_speak(text):
        """Cross-platform system TTS"""
        system = platform.system().lower()
        
        try:
            if system == "windows":
                # Windows PowerShell TTS
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"'
                os.system(cmd)
                return True
            elif system == "darwin":  # macOS
                os.system(f'say "{text}"')
                return True
            elif system == "linux":
                # Try espeak first, then festival
                if os.system(f'espeak "{text}" 2>/dev/null') == 0:
                    return True
                elif os.system(f'festival --tts <<< "{text}" 2>/dev/null') == 0:
                    return True
            return False
        except:
            return False
    
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)
    last_time = 0
    
    print("Testing system TTS...")
    if system_speak("System TTS ready"):
        print("✓ System TTS working!")
    else:
        print("✗ System TTS failed")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if time.time() - last_time > 3:
            results = model.predict(frame, verbose=False)
            
            objects = []
            for r in results:
                if r.boxes is not None:
                    for box in r.boxes:
                        if float(box.conf[0]) > 0.5:
                            name = model.names[int(box.cls[0])]
                            objects.append(name)
            
            if objects:
                unique_objects = list(set(objects))
                text = f"I see {', '.join(unique_objects)}"
                print(f"🔊 Speaking: {text}")
                
                if system_speak(text):
                    last_time = time.time()
        
        cv2.imshow('Backup Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()