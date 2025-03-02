# Rock-Paper-Scissor-Game
Python | OpenCV | NumPy | TensorFlow | Matplotlib | Pygame | Tkinter


# 🪨📄✂️ Rock-Paper-Scissors Game

## 🎯 Project Overview
This project is an interactive **Rock-Paper-Scissors** game where a user plays against a computer using **hand gestures**! The game utilizes **image processing** to recognize user gestures and follows standard game rules to determine the winner.

## 🔑 Key Features
✅ **Hand Gesture Recognition**: Uses image processing to detect user gestures (Rock, Paper, Scissors).  
✅ **Voice Command Activation**: Captures gestures when the user says _"Rock, Paper, Scissor, Shoot!"_.  
✅ **Computer Opponent**: Randomly selects a move for the AI opponent.  
✅ **Image Processing Steps**: Includes **background removal**, **grayscale conversion**, **thresholding**, and **binarization**.  
✅ **Real-time Visualization**: Displays user and computer gestures side by side.  
✅ **Attractive UI**: Clean and professional interface with real-time updates.  
✅ **(Optional)**: Extended version with _Rock-Paper-Scissors-Lizard-Spock_.  

## 🛠️ Tech Stack
- **Python** 🐍
- **OpenCV** 👁️ (Image Processing)
- **MediaPipe** 🖐️ (Hand Tracking)
- **Tkinter / PyQt** 🎨 (GUI)
- **NumPy** 🔢 (Image Processing)
- **SpeechRecognition** 🎙️ (Voice Input)

## 🚀 How It Works
1️⃣ User positions their hand in front of the camera.  
2️⃣ Says _"Rock, Paper, Scissor, Shoot!"_ to capture the gesture.  
3️⃣ The system processes the image and identifies the gesture.  
4️⃣ The computer selects a random gesture.  
5️⃣ The winner is determined based on the classic game rules.  
6️⃣ The result is displayed on the screen.  

## 🖥️ Installation & Setup
1. **Clone the Repository** 📂  
   ```bash
   git clone https://github.com/SE-LAPS/Rock-Paper-Scissor-Game.git
   cd rock-paper-scissors-gesture
   ```

2. **Install Dependencies** 📦  
   ```bash
   pip install opencv-python mediapipe numpy speechrecognition tkinter
   ```

3. **Run the Game** ▶️  
   ```bash
   python main.py
   ```

## 📷 Example Screenshots
🖼️ _[Add screenshots of your game interface here]_  

## 🏆 Game Rules
- **Rock** 🪨 beats Scissors ✂️
- **Scissors** ✂️ beats Paper 📄
- **Paper** 📄 beats Rock 🪨
- (Optional) **Lizard** 🦎 and **Spock** 🖖 can be added for an advanced variant!

## 🛠️ Future Improvements
- ✨ Improve gesture recognition accuracy.
- 🎤 Enhance speech recognition for better user interaction.
- 🧠 Implement a Machine Learning model for gesture classification.

## 📜 License
This project is **open-source** and available under the **MIT License**.

🚀 Have fun playing! Let the best hand win! ✋🤖

