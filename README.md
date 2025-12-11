# Flappy Bird Game (Kivy)

A fun Flappy Bird clone built with Python and Kivy framework.

## Installation

### Prerequisites
- Python 3.8+

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd flappy-modi
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add game assets** (Images & Audio)
   - Create a `recs/` folder in the project root
   - Add these files:
     - `recs/background.jpeg`
     - `recs/character.jpg`
     - `recs/pipes.jpeg`
     - `recs/audio.mp3`

5. **Run the game**
   ```bash
   python3 main.py
   ```

## Controls
- **Click/Tap** to flap and start the game
- **Click/Tap** again to restart after game over

## Game Features
- ✨ Background music with looping
- 🎮 Score tracking
- 🏆 Best score saving
- 🎨 Custom graphics

## File Structure
```
flappy-modi/
├── main.py              # Main game code
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── recs/               # Game assets (images & audio)
    ├── background.jpeg
    ├── character.jpg
    ├── pipes.jpeg
    └── audio.mp3
```