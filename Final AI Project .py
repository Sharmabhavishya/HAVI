"""
HAVI (Hand AI Voice Interface)
AI powered computer vision system that recognizes sign language gestures
and converts them into spoken words

Team: Bhavishya Sharma,  Aarjav Jain, Aaditya Garg
School: Bharatiya Vidya Bhavan Vidyashram
"""

import cv2
from cvzone.HandTrackingModule import HandDetector
from gtts import gTTS
import pygame
import time
import numpy as np
import os
import sys
import itertools

# ==========================
# CONFIGURATION CONSTANTS
# ==========================

class Config:
    CAMERA_INDEX = 3
    CAMERA_WIDTH = 1920
    CAMERA_HEIGHT = 1080
    
    FIRST_LETTER_DELAY = 2.5
    LETTER_DETECTION_DELAY = 1.5
    
    DETECTION_CONFIDENCE = 0.8
    MAX_HANDS = 2
    
    # Modern UI Colors
    COLOR_BG_DARK = (20, 20, 30)
    COLOR_BG_CARD = (35, 35, 50)
    COLOR_BG_LIGHT = (50, 50, 70)
    COLOR_TEXT = (255, 255, 255)
    COLOR_TEXT_DIM = (180, 180, 200)
    COLOR_PRIMARY = (100, 150, 255)
    COLOR_SUCCESS = (50, 200, 120)
    COLOR_WARNING = (255, 180, 50)
    COLOR_PROGRESS = (100, 150, 255)
    COLOR_PROGRESS_BG = (60, 60, 80)
    
    SCROLL_SPEED = 6
    SCROLL_LINE_HEIGHT = 60
    SCROLL_FPS = 30

# ==========================
# GESTURE PATTERNS
# ==========================

HAND_PATTERNS = {
    "00000": "A", "00001": "B", "00010": "C", "00011": "D", "00100": "E",
    "00101": "F", "00110": "G", "00111": "H", "01000": "I", "01001": "J",
    "01010": "K", "01011": "L", "01100": "M", "01101": "N", "01110": "O",
    "01111": "P",  "10001": "R", "10010": "S", "10011": "T",
    "10100": "U", "10101": "V", "10110": "W", "10111": "X", "11000": "Y",
    "11001": "Z", 
    
    "00000 11111": "HELLO",
    "11111 00000": "BYE",
    "01000 11000": "OK",
    "00000 00000": "Hi",
    "11111 11111": "How are you",
    "10000 10000": "HAVI AT YOUR SERVICE",
    "00001 00001": "LOVE",
    "01100 01100": "PEACE", 
    "01000 01000": "HELP",
    "11000 11000": "STOP",  
    "00100 00100": "THANK YOU"
}

# ==========================
# HELPER FUNCTIONS
# ==========================

def loading_animation(text="Initializing system", duration=3):
    """Display a loading animation in the console"""
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    start_time = time.time()
    sys.stdout.write(text + " ")
    sys.stdout.flush()
    while time.time() - start_time < duration:
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
    print("✅")

def play_intro():
    """Display introduction message"""
    intro_lines = [
        "Welcome to HAVI, your Hand AI Voice Interface",
        "Made by:",
        "  Bhavishya Sharma",
        "  Aaditya Garg",
        "  Priyanshi Mathur",
        "  Aarjav Jain"
    ]
pygame.mixer.init()
pygame.mixer.music.load("havi_intro.mp3")
pygame.mixer.music.play()

def initialize_camera(index=Config.CAMERA_INDEX):
    """Initialize camera with error handling"""
    try:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            print(f"[ERROR] Cannot open camera at index {index}")
            print("[INFO] Trying alternative camera indices...")
            for alt_index in range(5):
                cap = cv2.VideoCapture(alt_index)
                if cap.isOpened():
                    print(f"[SUCCESS] Camera opened at index {alt_index}")
                    break
            else:
                raise ValueError("No working camera found")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
        return cap
    except Exception as e:
        print(f"[ERROR] Camera initialization failed: {e}")
        raise

def get_letter_from_pattern(hands_data):
    """Extract letter from hand gesture pattern"""
    if len(hands_data) == 1:
        pattern = ''.join(map(str, hands_data[0]['fingers']))
        return HAND_PATTERNS.get(pattern, None)
    elif len(hands_data) == 2:
        hands_sorted = sorted(hands_data, key=lambda h: h['center'][0])
        left_pattern = ''.join(map(str, hands_sorted[0]['fingers']))
        right_pattern = ''.join(map(str, hands_sorted[1]['fingers']))
        combined_pattern = f"{left_pattern} {right_pattern}"
        return HAND_PATTERNS.get(combined_pattern, None)
    return None

def speak_detected_letters(detected_letters):
    """Speak all detected letters/words using gTTS"""
    if not detected_letters:
        print("[INFO] No letters to speak.")
        return
    
    text_to_speak = " ".join(detected_letters)
    print(f"[SPEAKING] {text_to_speak}")
    
    try:
        tts = gTTS(text=text_to_speak, lang='en')
        tts.save("speak_output.mp3")
        
        pygame.mixer.init()
        pygame.mixer.music.load("speak_output.mp3")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
        
        if os.path.exists("speak_output.mp3"):
            os.remove("speak_output.mp3")
        
        print("[SUCCESS] Speech output via gTTS")
    except Exception as e:
        print(f"[ERROR] Failed to speak (gTTS requires internet): {e}")

def draw_rounded_rect(img, pt1, pt2, color, thickness=-1, radius=15):
    """Draw a rounded rectangle"""
    x1, y1 = pt1
    x2, y2 = pt2
    
    if thickness == -1:
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        
        cv2.circle(img, (x1 + radius, y1 + radius), radius, color, -1)
        cv2.circle(img, (x2 - radius, y1 + radius), radius, color, -1)
        cv2.circle(img, (x1 + radius, y2 - radius), radius, color, -1)
        cv2.circle(img, (x2 - radius, y2 - radius), radius, color, -1)
    else:
        cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
        cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
        cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
        cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
        
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

def put_bold_text(img, text, org, font, font_scale, color, thickness=1, offset=1):
    """Render thicker/bold-looking text by layering strokes."""
    x, y = org
    for dx in range(-offset, offset + 1):
        for dy in range(-offset, offset + 1):
            if dx == 0 and dy == 0:
                continue
            cv2.putText(img, text, (x + dx, y + dy), font, font_scale, color, thickness)
    cv2.putText(img, text, org, font, font_scale, color, thickness + 1)

def draw_ui_overlay(frame, current_pattern, detected_letter, detected_sentence, is_first_detection, first_detection_progress):
    """Draw modern UI overlay on the frame"""
    h, w, _ = frame.shape
    
    overlay = frame.copy()
    
    # Top Header Bar
    draw_rounded_rect(overlay, (20, 20), (w - 20, 100), Config.COLOR_BG_CARD, -1, 20)
    cv2.putText(overlay, "HAVI", (40, 70),
                cv2.FONT_HERSHEY_DUPLEX, 1.5, Config.COLOR_PRIMARY, 3)
    cv2.putText(overlay, "Hand AI Voice Interface", (250, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, Config.COLOR_TEXT_DIM, 2)
    
    # Left Card - Pattern Display
    draw_rounded_rect(overlay, (20, 120), (420, 240), Config.COLOR_BG_CARD, -1, 15)
    cv2.putText(overlay, "PATTERN", (40, 155),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, Config.COLOR_TEXT_DIM, 2)
    cv2.putText(overlay, current_pattern, (40, 210),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, Config.COLOR_PRIMARY, 3)
    
    # Right Card - Detection Status
    detection_color = Config.COLOR_SUCCESS if detected_letter else Config.COLOR_BG_LIGHT
    draw_rounded_rect(overlay, (440, 120), (w - 20, 240), detection_color, -1, 15)
    cv2.putText(overlay, "DETECTED", (460, 155),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, Config.COLOR_TEXT_DIM, 2)
    
    detected_text = detected_letter if detected_letter else "None"
    text_color = Config.COLOR_TEXT if detected_letter else Config.COLOR_TEXT_DIM
    cv2.putText(overlay, detected_text, (460, 210),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, text_color, 3)
    
    # Progress Bar Section (only show during first detection)
    if is_first_detection and first_detection_progress > 0:
        draw_rounded_rect(overlay, (20, 260), (w - 20, 360), Config.COLOR_BG_CARD, -1, 15)
        
        cv2.putText(overlay, "HOLD GESTURE TO DETECT", (40, 295),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, Config.COLOR_TEXT_DIM, 2)
        
        progress_bar_x = 40
        progress_bar_y = 310
        progress_bar_width = w - 80
        progress_bar_height = 30
        
        draw_rounded_rect(overlay, 
                         (progress_bar_x, progress_bar_y), 
                         (progress_bar_x + progress_bar_width, progress_bar_y + progress_bar_height),
                         Config.COLOR_PROGRESS_BG, -1, 10)
        
        filled_width = int(progress_bar_width * first_detection_progress)
        if filled_width > 0:
            draw_rounded_rect(overlay, 
                             (progress_bar_x, progress_bar_y), 
                             (progress_bar_x + filled_width, progress_bar_y + progress_bar_height),
                             Config.COLOR_PROGRESS, -1, 10)
        
        percentage_text = f"{int(first_detection_progress * 100)}%"
        text_size = cv2.getTextSize(percentage_text, cv2.FONT_HERSHEY_DUPLEX, 0.7, 2)[0]
        text_x = progress_bar_x + (progress_bar_width - text_size[0]) // 2
        text_y = progress_bar_y + (progress_bar_height + text_size[1]) // 2
        cv2.putText(overlay, percentage_text, (text_x, text_y),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, Config.COLOR_TEXT, 2)
    
    # Sentence Display Section
    sentence_y = 380 if is_first_detection and first_detection_progress > 0 else 260
    draw_rounded_rect(overlay, (20, sentence_y), (w - 20, sentence_y + 100), Config.COLOR_BG_CARD, -1, 15)
    
    cv2.putText(overlay, "SENTENCE", (40, sentence_y + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, Config.COLOR_TEXT_DIM, 2)
    
    sentence_display = detected_sentence[-60:] if len(detected_sentence) > 60 else detected_sentence
    if not sentence_display.strip():
        sentence_display = "Start making gestures..."
        sentence_color = Config.COLOR_TEXT_DIM
    else:
        sentence_color = Config.COLOR_TEXT
    
    cv2.putText(overlay, sentence_display, (40, sentence_y + 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, sentence_color, 2)
    
    # Bottom Control Bar
    draw_rounded_rect(overlay, (0, h - 60), (w, h), Config.COLOR_BG_CARD, -1, 0)
    
    controls = [
        ("SPACE", "Add Space"),
        ("C", "Clear"),
        ("S", "Speak"),
        ("Q", "Quit")
    ]
    
    x_offset = 40
    for key, action in controls:
        cv2.rectangle(overlay, (x_offset, h - 45), (x_offset + 80, h - 20), Config.COLOR_PRIMARY, -1)
        put_bold_text(overlay, key, (x_offset + 10, h - 28),
                      cv2.FONT_HERSHEY_DUPLEX, 0.5, Config.COLOR_TEXT, 1, 1)
        put_bold_text(overlay, action, (x_offset + 95, h - 28),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, Config.COLOR_TEXT_DIM, 1, 1)
        x_offset += 280
    
    cv2.addWeighted(overlay, 0.95, frame, 0.05, 0, frame)
    
    return frame

def show_summary_screen():
    """Display scrolling project summary screen"""
    summary = np.zeros((900, 1200, 3), np.uint8)
    summary[:] = Config.COLOR_BG_DARK
    
    lines = [
        "",
        "",
        "PROJECT NAME:  HAVI (Hand AI Voice Interface)",
        "AI powered computer vision system that recognizes sign language gestures",
        "and converts them into spoken words",
        "",
        "SCHOOL NAME:  Bharatiya Vidya Bhavan Vidyashram",
        "YEAR / CLASS:  2025 / XII C",
        "TEACHER NAME:  Smt Arti Sharma",
        "TEACHER EMAIL:  artisharmabvbvkmj@gmail.com",
        "",
        "TEAM MEMBERS:",
        "  1. Bhavishya Sharma",
        "  2. Priyanshi Mathur",
        "  3. Aarjav Jain",
        "  4. Aaditya Garg",
        "",
        "ROLES SUMMARY:",
        "  Project Leader:  Bhavishya Sharma",
        "  Data Expert:  Priyanshi Mathur",
        "  Researcher:  Aaditya Garg",
        "  Designer:  Priyanshi Mathur",
        "  Prototype Builder:  Aaditya Garg",
        "  Tester:  Aarjav Jain",
        "  Marketing Leader:  Aarjav Jain",
        "  Video Producer:  Bhavishya Sharma",
        "",
        "",
        "Thank you for using HAVI!",
        "",
        "",
        "Press 'Q' to exit"
    ]
    
    scroll_y = 900
    
    while True:
        frame = summary.copy()
        y = scroll_y
        
        for i, line in enumerate(lines):
            if 0 <= y <= 900:
                if i == 2:
                    cv2.putText(frame, line, (60, y), cv2.FONT_HERSHEY_DUPLEX, 
                               1.0, Config.COLOR_PRIMARY, 2, cv2.LINE_AA)
                elif "TEAM MEMBERS:" in line or "ROLES SUMMARY:" in line:
                    cv2.putText(frame, line, (60, y), cv2.FONT_HERSHEY_DUPLEX, 
                               0.9, Config.COLOR_PRIMARY, 2, cv2.LINE_AA)
                else:
                    cv2.putText(frame, line, (60, y), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.8, Config.COLOR_TEXT, 2, cv2.LINE_AA)
            y += Config.SCROLL_LINE_HEIGHT
        
        cv2.imshow("HAVI Project Summary", frame)
        scroll_y -= Config.SCROLL_SPEED
        
        if scroll_y + len(lines) * Config.SCROLL_LINE_HEIGHT < 0:
            time.sleep(2)
            break
        
        if cv2.waitKey(Config.SCROLL_FPS) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

# ==========================
# MAIN APPLICATION
# ==========================

def main():
    """Main application loop"""
    print("\n" + "="*60)
    print("  HAVI - Hand AI Voice Interface")
    print("="*60 + "\n")
    
    loading_animation("Initializing system", 3)
    play_intro()
    
    try:
        cap = initialize_camera()
    except Exception as e:
        print(f"[FATAL] Cannot proceed without camera: {e}")
        return
    
    window_name = "HAVI (Hand AI Voice Interface)"
    try:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, Config.CAMERA_WIDTH, Config.CAMERA_HEIGHT)
    except Exception as e:
        print(f"[ERROR] Cannot create window: {e}")
        cap.release()
        return
    
    detector = HandDetector(detectionCon=Config.DETECTION_CONFIDENCE, maxHands=Config.MAX_HANDS)
    
    detected_sentence = ""
    detected_letters = []
    last_letter = ""
    last_letter_time = 0
    
    is_first_detection = True
    first_detection_start_time = None
    first_detection_letter = None
    
    print("\n[READY] System initialized. Starting gesture recognition...")
    print("[INFO] Show a gesture and hold for 2.5 seconds for first detection")
    print("[INFO] Subsequent detections require 1.5 seconds\n")
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
                print("[ERROR] Failed to read frame from camera")
                break
            
            frame = cv2.flip(frame, 1)
            hands, frame = detector.findHands(frame)
            
            detected_letter = None
            hands_data = []
            current_pattern = "-----"
            first_detection_progress = 0.0
            
            if hands:
                for hand in hands:
                    fingers = detector.fingersUp(hand)
                    center = hand['center']
                    hands_data.append({'fingers': fingers, 'center': center})
                
                if len(hands_data) == 1:
                    current_pattern = ''.join(map(str, hands_data[0]['fingers']))
                elif len(hands_data) == 2:
                    hands_sorted = sorted(hands_data, key=lambda h: h['center'][0])
                    left = ''.join(map(str, hands_sorted[0]['fingers']))
                    right = ''.join(map(str, hands_sorted[1]['fingers']))
                    current_pattern = f"{left} {right}"
                
                detected_letter = get_letter_from_pattern(hands_data)
                
                if detected_letter:
                    current_time = time.time()
                    
                    if is_first_detection:
                        if first_detection_letter != detected_letter:
                            first_detection_letter = detected_letter
                            first_detection_start_time = current_time
                        
                        if first_detection_start_time is not None:
                            time_held = current_time - first_detection_start_time
                            first_detection_progress = min(time_held / Config.FIRST_LETTER_DELAY, 1.0)
                        else:
                            time_held = 0
                            first_detection_progress = 0.0
                        
                        if time_held >= Config.FIRST_LETTER_DELAY:
                            detected_letters.append(detected_letter)
                            detected_sentence += detected_letter + " "
                            last_letter = detected_letter
                            last_letter_time = current_time
                            is_first_detection = False
                            first_detection_letter = None
                            print(f"[DETECTED] First letter: {detected_letter}")
                    else:
                        if current_time - last_letter_time >= Config.LETTER_DETECTION_DELAY:
                            detected_letters.append(detected_letter)
                            detected_sentence += detected_letter + " "
                            last_letter = detected_letter
                            last_letter_time = current_time
                            print(f"[DETECTED] {detected_letter}")
            else:
                first_detection_letter = None
                first_detection_start_time = None
            
            frame = draw_ui_overlay(frame, current_pattern, detected_letter, 
                                   detected_sentence, is_first_detection, first_detection_progress)
            
            cv2.imshow(window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n[INFO] Exiting application...")
                break
            elif key == ord(' '):
                detected_sentence += " "
                detected_letters.append(" ")
                print("[ACTION] Space added")
            elif key == ord('c'):
                detected_sentence = ""
                detected_letters.clear()
                is_first_detection = True
                first_detection_letter = None
                print("[ACTION] Sentence cleared")
            elif key == ord('s'):
                speak_detected_letters(detected_letters)
    
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"[ERROR] Unexpected error in main loop: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    pygame.mixer.init()
    pygame.mixer.music.load("havi_outro.mp3")
    pygame.mixer.music.play()

    show_summary_screen()
    
    print("\n[GOODBYE] Thank you for using HAVI!")


if __name__ == "__main__":
    main()
