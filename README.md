## 🎈 BalloonSlayer

A fast-paced 2D arcade balloon-popping game developed in Unity!
Take aim with your crosshair, pop balloons, chase high scores, and enjoy two unique game modes: Classic and Zen.

## 📸 Screenshots

![Main Menu and Gameplay](Images/MainMenu.png)

## 🎮 Game Overview
### Classic Mode

A score-focused challenge with:

* ❤️ 3 lives

* ⏫ Increasing difficulty

* 🎈 Faster balloon speed over time

* 🎯 Faster spawn rate over time

### Zen Mode

A peaceful endless mode:

* ♾️ No lives

* 🚫 No difficulty progression

* 🎯 Consistent balloon speed & spawn rate

* 🌿 Relaxed gameplay

## 🎈 Balloon Types
![Balloon types](Images/BalloonTypes.png)


## 🧩 Core Gameplay Mechanics

* Crosshair-based aiming (mouse-controlled)

*  Hit detection via 2D colliders

* Audio feedback system (balloon pop, SFX, music)

* Lives system (Classic mode)

* Difficulty progression system

* Game loop: Main Menu → Gameplay → Pause → Game Over

## ⚙️ Technical Details
### 🛠 Built With

* Unity 6.1 (6000.1.4f1)

* C# scripting

* Unity Input System

* TextMeshPro

* AudioMixer

* ScriptableObjects

* 2D Physics (Colliders, Triggers)

## 🔧 Project Structure
### Start Menu Scene

* Camera

* Main Menu UI

* Settings panel

* Game Mode Manager (persistent)

* Audio Manager

### Main Game Scene

* Camera

* Background

* Crosshair control

* Game Manager

* UI Canvas elements:

  * Score

  * Lives

  * Pause panel

  * Game Over panel

## 🧠 Challenges & Solutions
1. Zig-zag balloons going off-screen

Problem: Zig-zag balloons sometimes moved outside the screen bounds.
Solution:

* Spawned slightly further from the edge

* Clamped their horizontal movement within screen boundaries

2. Pop sound triggering a life loss

Problem: Pop SFX played after leaving the screen triggered the lives system.
Solution:

* Adjusted the trigger line (raised to value 10)

* Ensured sound playback doesn’t interfere with life logic

## 📘 What We Learned

* Unity interface fundamentals

* Scene structure and UI design

* Prefab workflow

* ScriptableObjects & modular design

* Audio management

* Input System usage

* Debugging, iteration, and problem-solving

* Working collaboratively in a game development environment

## 🙏 Assets & Credits

### Assets Used

* Simple Button Set 01 – That Witch Design
https://assetstore.unity.com/packages/2d/gui/icons/simple-button-set-01-153979

* Dark Theme UI – Giniel Villacote
https://assetstore.unity.com/packages/2d/gui/dark-theme-ui-199010

* 8Bit Music 062022 – GWriter Studio
https://assetstore.unity.com/packages/p/8bit-music-062022-225623

* Crosshairs – OccaSoftware
https://assetstore.unity.com/packages/2d/gui/icons/crosshairs-216732

* Pixel Skies DEMO Background – Digital Moons
https://assetstore.unity.com/packages/p/pixel-skies-demo-background-pack-226622

* Free Balloons 2D Sprites – Qookie Games
https://assetstore.unity.com/packages/p/free-balloons-2d-sprites-300733

### Special Thanks
To every artist, creator, and company providing these high-quality free assets.
Your work made this project possible! 🙌

## 👥 Contributors

* Kerem Ataç

* Abdulalim Çiftçi

* Boran Cem Göksu

* Ulaş Uzun

Instructor: Prof. Dr. Muhittin Gökmen

Teaching Assistants: Mustafa Ersen (MSc), Fatih Said Duran (MSc)

## 📚 References

* Unity Tutorials (Ali Onur “gevendary” Geven):
https://www.youtube.com/playlist?list=PLbgnCnWZjdwbFZ0ypbyY5ZUfEtyUKUsZQ

* Unity Learn Tutorials: https://learn.unity.com/tutorials

* Unity Courses: https://learn.unity.com/courses

* Unity Manual: https://docs.unity3d.com/Manual/index.html

## 🚀 Enjoy the Game!

Thanks for checking out BalloonSlayer!
If you enjoyed it, consider ⭐ starring the repo!
