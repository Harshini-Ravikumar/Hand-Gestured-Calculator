# 🤟 Hand Gesture Calculator 🧠📷

A real-time calculator using hand gestures detected via webcam, built with Python, OpenCV, and MediaPipe. Perform arithmetic operations like `+`, `-`, `*`, `/`, `//`, and `=` using just your fingers!

## 🔧 Technologies Used

- ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
- ![OpenCV](https://img.shields.io/badge/-OpenCV-5C3EE8?logo=opencv&logoColor=white)
- ![MediaPipe](https://img.shields.io/badge/-MediaPipe-FF6F00?logo=google&logoColor=white)
- ![NumPy](https://img.shields.io/badge/-NumPy-013243?logo=numpy&logoColor=white)

## 📸 Features

- 🤚 Detects single and dual-hand gestures via webcam
- ➕ Supports mathematical operations: `+`, `-`, `*`, `/`, `//`
- 🔢 Finger counting from right hand for number input (0–10)
- ✅ Detects `=` to evaluate the expression
- 🧠 Smart gesture recognition using hand angles and finger positions
- 🧼 Clears expression after every evaluation

## 💡 How It Works

| Gesture                             | Operation               |
|-------------------------------------|------------------------ |
| ✌️ Horizontal + Vertical Hands      | `+` (Plus)             |
| ☝️ Left hand Horizontal             | `-` (Minus)            |
| ✖️ Crossed wrists                   | `*` (Multiply)         |
| 🤞 left hand slanted like '/'       | `/` (Division)         |
| 🤞 Two hands slanted like '/'       | `//` (Floor Division)  |
| 👍 Folded fingers with thumbs-up    | `=` (Evaluate)         |
| 🖐️ Open hand (Right)                | Number Input           |

> Uses angle detection between wrist and fingers to determine the gesture direction and meaning.

## 🖥️ Run It Locally

```bash
pip install opencv-python mediapipe numpy
python gesture_calculator.py

