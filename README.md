# 🎮 Rock-Paper-Scissors-Lizard-Spock Game 🎲

## 📖 Overview

This is an interactive gesture-recognition Rock-Paper-Scissors-Lizard-Spock game that uses your webcam to detect hand gestures! Inspired by the popular extension to the classic Rock-Paper-Scissors game as featured in "The Big Bang Theory," this application uses computer vision to recognize your hand gestures in real-time.

## 🔍 Features

- 📹 **Real-time gesture recognition**: Play using your webcam
- 🖐️ **Five gestures**: Rock, Paper, Scissors, Lizard, and Spock
- 📊 **Game statistics**: Track your wins, losses, and ties
- 📈 **Performance testing**: Evaluate the accuracy of gesture recognition
- 🎭 **Fallback to random mode**: In case your camera is not available
- 🌈 **Beautiful UI**: Modern interface with smooth animations
- 📱 **Responsive design**: Adapts to different screen sizes

## 🎯 Game Rules

As Sheldon explains:

- ✂️ Scissors cuts Paper
- 📄 Paper covers Rock
- 🪨 Rock crushes Lizard
- 🦎 Lizard poisons Spock
- 🖖 Spock smashes Scissors
- ✂️ Scissors decapitates Lizard
- 🦎 Lizard eats Paper
- 📄 Paper disproves Spock
- 🖖 Spock vaporizes Rock
- 🪨 Rock crushes Scissors

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

1. 🚀 Launch the application by running `python main.py`
2. 👆 Click the "Start" button to begin a round
3. 🤚 When the countdown reaches "Now!", show your gesture to the camera
4. 🔄 The computer will randomly choose its gesture
5. 🏆 The winner is displayed along with the rule that determined the outcome
6. 📊 Click "Show Results" to see detailed game statistics

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

## 👤 Authors

- Your Name - Initial work

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.


## 🙏 Acknowledgments

- The Big Bang Theory for popularizing Rock-Paper-Scissors-Lizard-Spock
- Sam Kass and Karen Bryla for inventing the expanded game
- OpenCV community for the computer vision tools
- PySide6/Qt team for the UI framework 
