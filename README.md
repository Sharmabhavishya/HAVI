HAVI – Hand AI Voice Interface
A computer-vision powered system that recognizes hand gestures and converts them into spoken words.

Overview
HAVI (Hand AI Voice Interface) is an assistive communication tool designed to translate hand gestures, including basic sign language patterns, into audible speech. It uses computer vision, hand‑tracking, gesture pattern mapping, and text‑to‑speech to create a real‑time gesture‑to‑voice interface.

The goal of the project is to support communication for individuals who rely on sign language or gesture-based expression.

Key Features
Real-time hand detection using OpenCV and CVZone

Finger‑pattern recognition for both single-hand and dual-hand gestures

Mapping of finger patterns to letters and predefined words

Progress‑based gesture confirmation (to reduce false detections)

Sentence building interface with keyboard controls

Text-to-speech output using Google Text-to-Speech (gTTS) and Pygame

Modern, layered UI overlay with rounded UI components

Summary screen with project credits and details

Technologies Used
Python

OpenCV for camera processing and UI drawing

CVZone HandTrackingModule for gesture and finger detection

gTTS (Google Text-to-Speech) for generating audio output

Pygame for playing audio files

NumPy for creating the summary screen visuals

Itertools, Time, OS, Sys for utilities and system interactions

Gesture System
HAVI identifies gestures by analyzing which fingers are up on each detected hand. Finger states are converted into numeric patterns (example: 01001), which are matched against a predefined dictionary.

The system supports:

Single-hand patterns mapped to letters A–Z

Two-hand patterns mapped to full words like HELLO, BYE, HELP, STOP, and others

This blend of alphabets and predefined phrases allows both spelling and direct expression.

User Interface
The application includes:

A header displaying the system name

A pattern card showing current finger pattern

A detection card showing the interpreted gesture

A progress bar for the first gesture hold duration

A live-updating sentence panel

A bottom control bar with available keyboard shortcuts

Keyboard controls:

Space: Add space to sentence

C: Clear current sentence

S: Speak out detected sentence

Q: Quit application

Detection Workflow
User shows a gesture to the camera.

The system identifies finger positions using CVZone.

A pattern string is generated and compared to known gesture patterns.

The gesture must be held for:

2.5 seconds for the first detection

1.5 seconds for all subsequent detections

Once confirmed, the letter or word is appended to the ongoing sentence.

The user can trigger text-to-speech output on command.

Project Summary Screen
Upon exiting, the program displays a scrollable summary window containing:

Project title

Description

School details

Teacher information

Team member list

Role assignments

Closing message

This serves as a structured and visually clean project conclusion.

Team
Bhavishya Sharma – Project Lead, Developer

Aarjav Jain – Tester, Marketing Lead

Aaditya Garg – Researcher, Prototype Builder

Priyanshi Mathur – Data Specialist, Designer
