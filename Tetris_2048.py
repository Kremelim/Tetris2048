# --- START OF FILE Tetris_2048.py ---

# ... (imports and configuration remain the same) ...
import lib.stddraw as stddraw
from lib.picture import Picture
from lib.color import Color
import os
from game_grid import GameGrid
from tetromino import Tetromino
import random
import time
import pygame.mixer

# --- Configuration ---
GRID_H, GRID_W = 20, 12
PREVIEW_AREA_WIDTH = 6
TARGET_FPS = 30
INITIAL_GRAVITY_INTERVAL = 0.8
MUSIC_FILE = os.path.join("sounds", "Tetris.mp3")
INITIAL_VOLUME = 0.2

# The main function where this program starts execution
def start():
    # set the dimensions of the game grid
    grid_h, grid_w = 20, 12

    # add extra width for the next piece display area
    preview_area_width = 6

    # set the size of the drawing canvas (the displayed window)
    canvas_h, canvas_w = 40 * grid_h, 40 * (grid_w + preview_area_width)
    stddraw.setCanvasSize(canvas_w, canvas_h)
    # set the scale of the coordinate system for the drawing canvas
    stddraw.setXscale(-0.5, grid_w + preview_area_width - 0.5)
    stddraw.setYscale(-0.5, grid_h - 0.5)

    # --- Initialize Mixer and Load Music ---
    music_playing = False
    try:
        pygame.mixer.init()
        current_dir = os.path.dirname(os.path.realpath(_file_))
        music_file_path = os.path.join(current_dir, MUSIC_FILE)

        if os.path.exists(music_file_path):
            pygame.mixer.music.load(music_file_path)
            pygame.mixer.music.set_volume(INITIAL_VOLUME)
            pygame.mixer.music.play(loops=-1)
            music_playing = True
            print(f"Playing background music: {music_file_path}")
        else:
            print(f"Warning: Background music file not found at {music_file_path}")
    except pygame.error as e:
        print(f"Warning: Could not initialize mixer or load/play music: {e}")
    # --- End Music Initialization --

    # set the game grid dimension values stored and used in the Tetromino class
    Tetromino.grid_height = grid_h
    Tetromino.grid_width = grid_w

    # display a simple menu before opening the game
    display_game_menu(grid_h, grid_w)

    # start the game loop
    try:
        while True: # Allows restarting the game
            restart_game = play_game(grid_h, grid_w, preview_area_width)
            if not restart_game:
                break # Exit if play_game returns False (e.g., user pressed Escape)
    finally:
        # --- Stop Music on Exit ---
        if music_playing:
            pygame.mixer.music.stop()
            print("Music stopped.")
        # --- End Stop Music ---

    print("Game exited.") # Optional message

def play_game(grid_h, grid_w, preview_area_width):
    """Plays one instance of the game. Returns True if restart requested, False to exit."""
    # create the game grid
    grid = GameGrid(grid_h, grid_w)

    # Timing control
    target_fps = TARGET_FPS
    frame_duration = 1.0 / target_fps
    gravity_interval = INITIAL_GRAVITY_INTERVAL
    last_gravity_time = time.time()

    # --- Initial Piece Creation ---
    # Create the very first piece directly
    current_tetromino = create_tetromino()
    grid.current_tetromino = current_tetromino
    # Validate its initial spawn position
    if not current_tetromino.can_be_moved("down", grid, check_initial=True):
        print("Game Over: Cannot spawn initial piece.") # Debug message
        grid.game_over = True
        current_tetromino = None  # Ensure it's None if spawn failed
        grid.current_tetromino = None
        next_tetromino = None # No next piece either
        grid.next_tetromino = None
    else:
        # If the first piece spawns successfully, create the next piece for the preview
        next_tetromino = create_tetromino()
        grid.next_tetromino = next_tetromino  # assign it to the grid object

    # Game state variables
    paused = False
    # grid.game_over is already initialized based on initial spawn check

    # the main game loop
    while True:
        start_time = time.time() # Record frame start time

        # --- Input Handling ---
        hard_dropped = False # Reset hard drop flag each frame
        if stddraw.hasNextKeyTyped():
            key_typed = stddraw.nextKeyTyped()

            # Pause/resume with 'p' key
            if key_typed == "p":
                paused = not paused
                if paused:
                    pause_start_time = time.time()
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                else:
                    pause_duration = time.time() - pause_start_time
                    last_gravity_time += pause_duration
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.unpause()
                stddraw.clearKeysTyped()

            # Restart with 'r' key
            elif key_typed == "r":
                stddraw.clearKeysTyped()
                return True # Signal to restart

            # Exit with 'escape' key
            elif key_typed == "escape":
                stddraw.clearKeysTyped()
                return False # Signal to exit

            # --- Active Game Input (only if not paused/over) ---
            elif not paused and not grid.game_over and current_tetromino is not None:
                moved = False
                rotated = False
                if key_typed == "left":
                    moved = current_tetromino.move(key_typed, grid)
                elif key_typed == "right":
                    moved = current_tetromino.move(key_typed, grid)
                elif key_typed == "down":
                    moved = current_tetromino.move(key_typed, grid)
                    if moved:
                         last_gravity_time = time.time()
                elif key_typed == "up":
                    rotated = current_tetromino.rotate(grid)
                elif key_typed == "space":
                    while current_tetromino.move("down", grid):
                        pass
                    hard_dropped = True

        # --- Game Logic (only if not paused/over) ---
        if not paused and not grid.game_over and current_tetromino is not None:
            # Automatic downward movement (gravity)
            current_time = time.time()
            gravity_move_attempted = False
            if not hard_dropped and current_time - last_gravity_time >= gravity_interval:
                success_gravity = current_tetromino.move("down", grid)
                last_gravity_time = current_time # Reset timer regardless of success
                gravity_move_attempted = True # Flag that gravity tried to move

            # --- Landing Logic ---
            # Check if the piece cannot move down after potential gravity/user move this frame,
            # OR if it was hard dropped.
            # The can_be_moved check is crucial here.
            if hard_dropped or not current_tetromino.can_be_moved("down", grid):
                # Lock the piece, check lines/merges, update score
                tiles, pos = current_tetromino.get_min_bounded_tile_matrix(True)
                # update_grid handles locking & checking game over due to overlap
                grid.update_grid(tiles, pos)

                # Check win condition (after grid updates)
                if check_for_win(grid):
                    display_win_screen(grid_h, grid_w)
                    while True:
                         if stddraw.hasNextKeyTyped():
                              key = stddraw.nextKeyTyped()
                              if key == 'r': return True
                              if key == 'escape': return False
                         stddraw.show(50)

                # Check Game Over state from grid update OR inability to spawn next piece
                if grid.game_over:
                    current_tetromino = None # Clear current piece on game over
                    grid.current_tetromino = None
                    grid.next_tetromino = None # Also clear next piece display
                    # Go to next loop iteration to display Game Over screen

                else: # Game not over yet, proceed to spawn next piece cycle
                    # 1. The piece previously in 'next' becomes the 'current'
                    current_tetromino = grid.next_tetromino

                    # Safety check: If next_tetromino was somehow None, it's an error state
                    if current_tetromino is None:
                         print("Error: grid.next_tetromino was None unexpectedly during piece transition.")
                         grid.game_over = True
                         grid.current_tetromino = None
                         grid.next_tetromino = None
                         next_tetromino = None # Clear local var just in case
                    else:
                        # 2. Set the grid's current_tetromino reference
                        grid.current_tetromino = current_tetromino

                        # 3. Check if this newly assigned piece can actually spawn at its default location
                        if not current_tetromino.can_be_moved("down", grid, check_initial=True):
                            # Cannot spawn the piece that was in 'next' - Game Over!
                            print("Game Over: Cannot spawn the next piece.") # Debug message
                            grid.game_over = True
                            current_tetromino = None # Clear the invalid current piece
                            grid.current_tetromino = None
                            grid.next_tetromino = None # Clear next display too
                            next_tetromino = None # Clear local var
                        else:
                            # 4. Successfully spawned the current piece, now generate the next piece for the preview
                            next_tetromino = create_tetromino()
                            grid.next_tetromino = next_tetromino # Store it in the grid

                    # Reset gravity timer for the new piece (or for the game over state)
                    last_gravity_time = time.time()

        # --- Drawing ---
        # Pass grid's game_over flag to the display function
        display_game_state(grid, paused, grid.game_over)

        # --- Frame Rate Control ---
        end_time = time.time()
        elapsed_time = end_time - start_time
        pause_duration_ms = (frame_duration - elapsed_time) * 1000
        if pause_duration_ms < 0:
            pause_duration_ms = 0 # Avoid negative pause

        # The only stddraw.show() call should be this one
        stddraw.show(pause_duration_ms) # Use calculated pause duration

# ... (rest of the functions: check_for_win, display_game_state, display_pause_overlay, display_game_over_overlay, display_win_screen, display_controls_info, create_tetromino, display_game_menu remain the same)

# Helper function to check if any tile has reached 2048
def check_for_win(grid):
    for row in range(grid.grid_height):
        for col in range(grid.grid_width):
            if grid.tile_matrix[row][col] is not None and grid.tile_matrix[row][col].number >= 2048:
                return True
    return False

# Function to display the current state of the game
def display_game_state(grid, paused, game_over):
    # Display the basic game grid and pieces
    grid.display() # grid.display() NO LONGER CALLS stddraw.show()

    # Display overlays based on state
    if paused:
        display_pause_overlay(grid.grid_width, grid.grid_height) # Pass dimensions for centering
    elif game_over:
        display_game_over_overlay(grid.score, grid.grid_width, grid.grid_height) # Pass score & dimensions

    # Display controls info at the bottom
    display_controls_info(grid.grid_width)

# Function to display pause overlay (adjusted for centering)
def display_pause_overlay(grid_w, grid_h):
    center_x = (grid_w - 1) / 2.0 # Use float for potentially non-integer center
    center_y = (grid_h - 1) / 2.0
    # Use a semi-transparent color by adding an alpha channel (stddraw might not support alpha directly)
    # If stddraw doesn't support alpha, use a solid dark color
    # stddraw.setPenColor(Color(0, 0, 0, 150)) # Example with alpha (may not work)
    stddraw.setPenColor(Color(20, 20, 20)) # Dark solid color as fallback
    stddraw.filledRectangle(-0.5, -0.5, grid_w, grid_h) # Cover grid area

    stddraw.setPenColor(stddraw.WHITE)
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(30)
    stddraw.text(center_x, center_y + 1, "GAME PAUSED")
    stddraw.setFontSize(20)
    stddraw.text(center_x, center_y - 1, "Press 'p' to resume")
    stddraw.text(center_x, center_y - 2, "Press 'r' to restart")
    stddraw.text(center_x, center_y - 3, "Press 'escape' to exit")

# Function to display game over overlay (adjusted for centering)
def display_game_over_overlay(score, grid_w, grid_h):
    center_x = (grid_w - 1) / 2.0
    center_y = (grid_h - 1) / 2.0
    # stddraw.setPenColor(Color(0, 0, 0, 150)) # Example with alpha (may not work)
    stddraw.setPenColor(Color(20, 20, 20)) # Dark solid color as fallback
    stddraw.filledRectangle(-0.5, -0.5, grid_w, grid_h) # Cover grid area

    stddraw.setPenColor(stddraw.WHITE)
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(30)
    stddraw.text(center_x, center_y + 2, "GAME OVER")
    stddraw.setFontSize(20)
    stddraw.text(center_x, center_y + 0.5, f"Final Score: {score}")
    stddraw.text(center_x, center_y - 1, "Press 'r' to restart")
    stddraw.text(center_x, center_y - 2, "Press 'escape' to exit")


# Function to display winning screen
def display_win_screen(grid_h, grid_w):
    stddraw.clear(Color(42, 69, 99))
    center_x = (grid_w - 1) / 2.0
    center_y = (grid_h - 1) / 2.0

    stddraw.setPenColor(stddraw.WHITE)
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(40)
    stddraw.text(center_x, center_y + 2, "YOU WIN!")
    stddraw.setFontSize(20)
    stddraw.text(center_x, center_y, "You reached 2048!")
    stddraw.text(center_x, center_y - 2, "Press 'r' to play again")
    stddraw.text(center_x, center_y - 3, "Press 'escape' to exit")
    stddraw.show(20)


# Function to display controls at the bottom of the screen
def display_controls_info(grid_width):
    stddraw.setPenColor(stddraw.WHITE)
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(12)
    controls = "Controls: ← → Move  ↑ Rotate  ↓ Soft Drop  Space Hard Drop  P Pause  R Restart  Esc Exit"
    stddraw.text((grid_width -1) / 2.0, -0.3, controls)


# A function for creating random shaped tetrominoes to enter the game grid
def create_tetromino():
    # the type (shape) of the tetromino is determined randomly
    tetromino_types = ['I', 'O', 'Z', 'J', 'L', 'S', 'T']
    random_index = random.randint(0, len(tetromino_types) - 1)
    random_type = tetromino_types[random_index]
    # create and return the tetromino
    tetromino = Tetromino(random_type)
    return tetromino


# A function for displaying a simple menu before starting the game
def display_game_menu(grid_height, grid_width):
     # (Code for display_game_menu remains unchanged)
    background_color = Color(42, 69, 99)
    button_color = Color(25, 255, 228)
    text_color = Color(31, 160, 239)
    stddraw.clear(background_color)
    current_dir = os.path.dirname(os.path.realpath(_file_))
    img_file = os.path.join(current_dir, "images", "menu_image.png") # Use os.path.join
    img_center_x, img_center_y = (grid_width - 1) / 2.0, grid_height - 7
    if not os.path.exists(img_file):
        print(f"Warning: Menu image not found at {img_file}")
    else:
        image_to_display = Picture(img_file)
        stddraw.picture(image_to_display, img_center_x, img_center_y)

    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(35)
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.text(img_center_x, grid_height - 3, "TETRIS 2048")

    button_w, button_h = grid_width - 1.5, 2
    button_blc_x, button_blc_y = img_center_x - button_w / 2, 4
    stddraw.setPenColor(button_color)
    stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(25)
    stddraw.setPenColor(text_color)
    text_to_display = "Click Here to Start the Game"
    stddraw.text(img_center_x, 5, text_to_display)

    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(15)
    stddraw.setPenColor(Color(200, 200, 200))
    stddraw.text(img_center_x, 2, "Controls: Arrow Keys to Move/Rotate, Space for Hard Drop")
    stddraw.text(img_center_x, 1, "P to Pause, R to Restart, Esc to Exit")

    while True:
        stddraw.show(50)
        if stddraw.mousePressed():
            mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
            if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
                if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
                    break


if _name_ == '_main_':
    start()

# --- END OF FILE Tetris_2048.py ---
