# Sokoban - Classic Puzzle Game

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/pygame-2.0%2B-yellow.svg)](https://www.pygame.org/wiki/GettingStarted)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Levels](https://img.shields.io/badge/10%20Levels-brightgreen.svg)](https://github.com/username/sokoban-python)

A faithful **Sokoban** implementation in Python using **Pygame**. Push boxes onto targets without getting stuck! Features beautiful pixel-art graphics, smooth controls, undo system, level select menu, and 10 hand-crafted levels from tutorial to expert.

## ✨ Features
- **10 Challenging Levels**: Tutorial → Expert, including spiral, warehouse, and multi-room puzzles
- **Pixel-Art Graphics**: Custom-drawn walls, boxes, player, and glowing targets
- **Smooth Controls**: WASD/Arrow Keys, mouse buttons, auto-repeat movement
- **Game Features**:
  - Undo (Z key)
  - Reset level (R key)
  - Move/Push counters
  - Level completion tracking
  - Resizable window
- **Zero Dependencies** beyond Pygame (single `SokobanGame.py` file)
- **Professional Polish**: Menu system, win screens, hover effects

## 🎮 How to Play
```
Goal: Push all brown boxes (crates) onto red target spots.
Rules:
- You can push boxes, but cannot pull them
- Boxes cannot be pushed through walls or other boxes
- Get all boxes on targets to win!

Controls:
- ↑↓←→ / WASD: Move player
- Z: Undo last move
- R: Reset current level
- ESC: Main menu
- Mouse: Button hovers & clicks
```

## 🚀 Quick Start
```bash
# Install Pygame (one-time)
pip install pygame

# Run the game
python SokobanGame.py
```

## 📁 Screenshots
*(Add your own gameplay screenshots here after testing!)*

**Main Menu** | **Gameplay** | **Level Complete**
---|---|---
![Menu](screenshots\Menu.png) | ![Gameplay](screenshots\Gameplay.png) | ![Win](screenshots\Win.png)

## 🏆 Levels
| # | Name      | Difficulty | Boxes |
|---|-----------|------------|-------|
| 1 | Tutorial  | ⭐         | 1     |
| 2 | Simple    | ⭐         | 2     |
| 3 | Corner    | ⭐⭐        | 3     |
| 4 | Hallway   | ⭐⭐        | 3     |
| 5 | L-Shape   | ⭐⭐        | 2     |
| 6 | Cross     | ⭐⭐⭐       | 4     |
| 7 | Spiral    | ⭐⭐⭐       | 3     |
| 8 | Tricky    | ⭐⭐⭐       | 4     |
| 9 | Warehouse | ⭐⭐⭐⭐      | 6     |
|10 | Expert    | ⭐⭐⭐⭐⭐     | 5     |

## 🛠️ Development
- **Python 3.8+**
- **Pygame 2.0+**
- Single file: `SokobanGame.py` (~500 LOC)
- Window: Resizable, 900x680 default
- Tile size: Adaptive (16-48px)

### Customization
- Edit `LEVELS` list in code to add your own levels
- Each level is a simple 2D list using:
  - `#` = Wall
  - `@` = Player start
  - `$` = Box
  - `.` = Target
  - `!` = Player on target
  - `+` = Box on target
  - Space = Floor

## 🤝 Contributing
1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingNewFeature`)
3. Commit changes (`git commit -m 'Add some AmazingNewFeature'`)
4. Push (`git push origin feature/AmazingNewFeature`)
5. Open Pull Request

New levels welcome! 🎉

## 📄 License
MIT License - see [LICENSE](LICENSE) file or [here](https://choosealicense.com/licenses/mit/).

## 🙏 Acknowledgments
- Built with [Pygame](https://pygame.org)
- Level designs inspired by classic Sokoban
- Pixel art styled after retro puzzle games

---

⭐ Star this repo if you enjoy Sokoban!  
🐛 Found a bug? [Open an issue](https://github.com/username/sokoban-python/issues/new)


