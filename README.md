# 🎮 Rock-Paper-Scissors-Lizard-Spock Game 🎲

## 📖 Overview

This is an interactive gesture-recognition Rock-Paper-Scissors-Lizard-Spock game that uses your webcam to detect hand gestures! Inspired by the popular extension to the classic Rock-Paper-Scissors game as featured in "The Big Bang Theory," this application uses computer vision to recognize your hand gestures in real-time.

## 🔍 Features

- **Real-time gesture recognition**: Play using your webcam
- **Five gestures**: Rock, Paper, Scissors, Lizard, and Spock
- **Game statistics**: Track your wins, losses, and ties
- **Performance testing**: Evaluate the accuracy of gesture recognition
- **Fallback to random mode**: In case your camera is not available
- **Beautiful UI**: Modern interface with smooth animations
- **Responsive design**: Adapts to different screen sizes

## 🎯 Game Rules

As Sheldon explains:

- Scissors cuts Paper
- Paper covers Rock
- Rock crushes Lizard
- Lizard poisons Spock
- Spock smashes Scissors
- Scissors decapitates Lizard
- Lizard eats Paper
- Paper disproves Spock
- Spock vaporizes Rock
- Rock crushes Scissors

## 🚀 Getting Started

### 📋 Prerequisites

- Python 3.8+
- Webcam (built-in or external)
- Windows/Mac/Linux operating system

### 🔧 Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rock-paper-scissors-lizard-spock.git
   cd rock-paper-scissors-lizard-spock
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the game:
   ```
   python main.py
   ```

## 🕹️ How to Play

1. Launch the application by running `python main.py`
2. Click the "Start" button to begin a round
3. When the countdown reaches "Now!", show your gesture to the camera
4. The computer will randomly choose its gesture
5. The winner is displayed along with the rule that determined the outcome
6. Click "Show Results" to see detailed game statistics

### 🖐️ Gesture Guide

- **Rock** 👊: Make a fist
- **Paper** ✋: Open your hand with fingers extended
- **Scissors** ✌️: Extend index and middle fingers in a V shape
- **Lizard** 🤏: Form a "puppet mouth" shape with your hand
- **Spock** 🖖: Make the Vulcan salute

## 🛠️ Technical Details

This application uses:

- **PySide6**: For the UI components and application framework
- **OpenCV**: For computer vision and gesture recognition
- **NumPy**: For numerical calculations and array operations
- **Python**: For the application logic

### 🧠 Gesture Recognition

The gesture recognition system uses:

- Background subtraction to isolate the hand
- Contour detection to find the hand shape
- Convexity defects analysis to identify fingers
- Feature extraction to classify different gestures
- Stability tracking to reduce false positives

## 🧪 Testing

You can test the gesture recognition accuracy:

1. Click on "Actions" in the top right
2. Select "Test Recognition Accuracy"
3. Follow the on-screen instructions to test each gesture
4. Review your accuracy results

## 📝 Troubleshooting

- **Camera not working?**: Ensure no other application is using your webcam
- **Poor recognition?**: Adjust your lighting and ensure your hand is within the green rectangle
- **Game not starting?**: Check the console for error messages

## 👨‍💻 Collaborators 

| LAHIRU | THEVINDU | WASANA | PRASITHA |CHAMITH |
|---------|------------|-------------|-------------|-------------|
| ![1](https://github.com/user-attachments/assets/2d9422fb-b2a6-4851-b117-d40b3dc58bd1) | ![1](https://github.com/user-attachments/assets/2d9422fb-b2a6-4851-b117-d40b3dc58bd1) | ![1](https://github.com/user-attachments/assets/2d9422fb-b2a6-4851-b117-d40b3dc58bd1) | ![1](https://github.com/user-attachments/assets/2d9422fb-b2a6-4851-b117-d40b3dc58bd1) | ![1](https://github.com/user-attachments/assets/2d9422fb-b2a6-4851-b117-d40b3dc58bd1) |
| ![3](https://github.com/user-attachments/assets/93e43b9b-b5fa-44af-a0bd-46323ffb83df) | ![1](https://github.com/user-attachments/assets/f0a812fc-a6b0-40bf-8375-0bac9e73a00b) | ![1](https://github.com/user-attachments/assets/a19d6f80-deaa-4d54-b6b1-ac6c9c10820a) | ![1](https://github.com/user-attachments/assets/57448c2a-36ed-49e2-a94e-6d29e2c3f687) |![1](https://github.com/user-attachments/assets/c31cf1f1-86ba-4875-b708-efecbf0cdccb) |
| ![8](https://github.com/user-attachments/assets/fe4da7e0-931c-4465-ac35-0b6a6d0c4aee) | ![2](https://github.com/user-attachments/assets/9d703464-4c84-4b35-85dd-325e32f114da) | ![2](https://github.com/user-attachments/assets/ac377097-9c58-4dd4-bd32-c942d3f57ae5) | ![2](https://github.com/user-attachments/assets/c6c756df-15a1-463a-85fd-e5791800eca4) | ![2](https://github.com/user-attachments/assets/c4dae83c-5b1f-4b15-b8af-ab49c3455070) |
| ![6](https://github.com/user-attachments/assets/0c2b5411-044c-4e34-9349-35f2d624a966) | ![3](https://github.com/user-attachments/assets/8641188e-a3d5-4755-9c84-abe2c0cda655) | ![3](https://github.com/user-attachments/assets/1a20b175-8686-49ce-bc5a-db067c3a0835) | ![3](https://github.com/user-attachments/assets/e0d9211b-63bf-4b31-8318-92c2746fd5d8) | ![3](https://github.com/user-attachments/assets/7c81ed15-df44-4071-97d9-68573ebbcfd1) |
| ![11](https://github.com/user-attachments/assets/82981900-d89a-4fd9-89f4-b346ef27bfde) | ![4](https://github.com/user-attachments/assets/d73ddab4-60dd-4dfb-a9a2-41038267d033) | ![4](https://github.com/user-attachments/assets/93d55bf7-2a57-46e4-8830-148fa62f792e) | ![4](https://github.com/user-attachments/assets/af975e9b-e73c-460c-8369-e5ea2c199f33) | ![4](https://github.com/user-attachments/assets/87b5b4fa-0e28-4724-b8b7-4471bd5dc465) |




## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details. <br><br>
1️⃣YouTube Link 1 -> https://youtu.be/tJH4Owejj7Y?si=NF0Hd6oI_v7DF4aA <br>
2️⃣YouTube Link 2 -> <br>
3️⃣GitHub Link -> https://github.com/SE-LAPS/Rock-Paper-Scissor-Game 


## 🙏 Acknowledgments

- The Big Bang Theory for popularizing Rock-Paper-Scissors-Lizard-Spock
- Sam Kass and Karen Bryla for inventing the expanded game
- OpenCV community for the computer vision tools
- PySide6/Qt team for the UI framework 
