# --- START OF FILE Tetris_2048.py ---

################################################################################
#                                                                              #
# The main program of Tetris 2048 Base Code                                    #
#                                                                              #
################################################################################

import lib.stddraw as stddraw  # for creating an animation with user interactions
from lib.picture import Picture  # used for displaying an image on the game menu
from lib.color import Color  # used for coloring the game menu
import os  # the os module is used for file and directory operations
from game_grid import GameGrid  # the class for modeling the game grid
from tetromino import Tetromino  # the class for modeling the tetrominoes
import random  # used for creating tetrominoes with random types (shapes)
import time  # For dynamic timing
import pygame.mixer

# --- Configuration ---
# Game grid dimensions
GRID_H, GRID_W = 20, 12
# Width for the next piece display area
PREVIEW_AREA_WIDTH = 6
# Target FPS
TARGET_FPS = 30
# Gravity interval (seconds)
INITIAL_GRAVITY_INTERVAL = 0.8
# Music file path (relative to this script)
MUSIC_FILE = os.path.join("sounds", "Tetris.mp3") # ADJUST FILENAME if needed
INITIAL_VOLUME = 0.2 # Volume from 0.0 (silent) to 1.0 (full)

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
        # Get the directory in which this python code file is placed
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # Compute the full path to the music file
        music_file_path = os.path.join(current_dir, MUSIC_FILE)

        if os.path.exists(music_file_path):
            pygame.mixer.music.load(music_file_path)
            pygame.mixer.music.set_volume(INITIAL_VOLUME)
            pygame.mixer.music.play(loops=-1)  # Loop indefinitely
            music_playing = True
            print(f"Playing background music: {music_file_path}")
        else:
            print(f"Warning: Background music file not found at {music_file_path}")
            print("Current directory:", current_dir)
            print("Looking for relative path:", MUSIC_FILE)
    except pygame.error as e:
        print(f"Warning: Could not initialize mixer or load/play music: {e}")
    # --- End Music Initialization --

    # set the game grid dimension values stored and used in the Tetromino class
    Tetromino.grid_height = grid_h
    Tetromino.grid_width = grid_w

    # display a simple menu before opening the game
    # by using the display_game_menu function defined below
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

    # Function to create the first tetromino and check for immediate game over
    def spawn_tetromino(grid):
        tetromino = create_tetromino()
        grid.current_tetromino = tetromino
        # Check if the spawn position is valid *immediately*
        if not tetromino.can_be_moved("down", grid, check_initial=True): # Need to adapt can_be_moved slightly
             return None # Indicate spawn failed
        return tetromino

    # Create first tetromino and handle potential immediate game over
    current_tetromino = spawn_tetromino(grid)
    if current_tetromino is None:
        grid.game_over = True # Set game over if spawn failed
    else:
         # create next tetromino that will follow only if spawn was successful
         next_tetromino = create_tetromino()
         grid.next_tetromino = next_tetromino  # assign it to the grid object

    # Game state variables
    paused = False
    # grid.game_over is already initialized

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
                # If pausing, record current time to adjust gravity timer on resume
                if paused:
                    pause_start_time = time.time()
                    if pygame.mixer.music.get_busy():  # Check if music is playing before pausing
                        pygame.mixer.music.pause()
                else:
                    # Adjust last gravity time by duration of pause
                    pause_duration = time.time() - pause_start_time
                    last_gravity_time += pause_duration
                    if not pygame.mixer.music.get_busy():  # Check if music is paused before unpausing
                        pygame.mixer.music.unpause()
                stddraw.clearKeysTyped() # Clear keys after handling 'p'
                # continue # Continue loop to redraw immediately with pause state

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
                    if moved: # Soft drop resets gravity timer
                         last_gravity_time = time.time()
                elif key_typed == "up":
                    rotated = current_tetromino.rotate(grid)
                elif key_typed == "space":
                    # Hard drop: move down until it stops
                    while current_tetromino.move("down", grid):
                        pass # Keep moving down
                    hard_dropped = True # Set flag to trigger landing logic immediately

            # Maybe clear keys here if they are still interfering? Usually needed *after* processing.
            # stddraw.clearKeysTyped() # Let's try without clearing here unless needed

        # --- Game Logic (only if not paused/over) ---
        if not paused and not grid.game_over and current_tetromino is not None:
            # Automatic downward movement (gravity)
            current_time = time.time()
            if not hard_dropped and current_time - last_gravity_time >= gravity_interval:
                success = current_tetromino.move("down", grid)
                last_gravity_time = current_time # Reset timer regardless of success
            else:
                # If hard dropped or gravity interval not reached, check if current move failed
                # (e.g. user tried to move down into something, or hard drop finished)
                success = hard_dropped or current_tetromino.can_be_moved("down", grid)

            # --- Landing Logic ---
            # If the piece couldn't move down naturally OR was hard dropped
            if not current_tetromino.can_be_moved("down", grid) or hard_dropped:
                # Lock the piece, check lines/merges, update score
                tiles, pos = current_tetromino.get_min_bounded_tile_matrix(True)
                grid.update_grid(tiles, pos) # update_grid now handles game_over internally based on overlap

                # Check win condition (after grid updates)
                if check_for_win(grid):
                    display_win_screen(grid_h, grid_w)
                    # Loop for restart/exit options after win
                    while True:
                         if stddraw.hasNextKeyTyped():
                              key = stddraw.nextKeyTyped()
                              if key == 'r': return True
                              if key == 'escape': return False
                         stddraw.show(50) # Small delay while waiting

                # Check Game Over state from grid update
                if grid.game_over:
                    # No need to spawn next piece if game is over
                    current_tetromino = None
                    # continue # Go to next loop iteration to display Game Over screen

                else:
                    # Spawn the next piece
                    current_tetromino = spawn_tetromino(grid) # Use the function that checks spawn validity
                    if current_tetromino is None:
                        # Failed to spawn the new piece - Game Over!
                        grid.game_over = True
                        next_tetromino = None # Clear next piece display as well
                    else:
                        # Successfully spawned, prepare the *next* next piece
                        next_tetromino = create_tetromino()
                        grid.next_tetromino = next_tetromino

                    last_gravity_time = time.time() # Reset gravity timer for new piece

        # --- Drawing ---
        display_game_state(grid, paused, grid.game_over) # Pass grid's game_over flag

        # --- Frame Rate Control ---
        end_time = time.time()
        elapsed_time = end_time - start_time
        pause_duration = frame_duration - elapsed_time
        if pause_duration < 0:
            pause_duration = 0 # Avoid negative pause

        # The only stddraw.show() call should be this one
        stddraw.show(pause_duration * 1000) # Convert seconds to milliseconds


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

    # REMOVED: stddraw.show(200) - Handled by the main loop's timing control


# Function to display pause overlay (adjusted for centering)
def display_pause_overlay(grid_w, grid_h):
    center_x = (grid_w - 1) / 2
    center_y = (grid_h - 1) / 2
    stddraw.setPenColor(Color(0, 0, 0)) # Semi-transparent black overlay
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
    center_x = (grid_w - 1) / 2
    center_y = (grid_h - 1) / 2
    stddraw.setPenColor(Color(0, 0, 0)) # Semi-transparent black overlay
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
    # clear the background
    stddraw.clear(Color(42, 69, 99))
    center_x = (grid_w - 1) / 2
    center_y = (grid_h - 1) / 2

    # Display win message
    stddraw.setPenColor(stddraw.WHITE)
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(40)
    stddraw.text(center_x, center_y + 2, "YOU WIN!")
    stddraw.setFontSize(20)
    stddraw.text(center_x, center_y, "You reached 2048!")
    stddraw.text(center_x, center_y - 2, "Press 'r' to play again")
    stddraw.text(center_x, center_y - 3, "Press 'escape' to exit")

    # Show the win screen initially
    stddraw.show(20) # Show briefly before entering wait loop


# Function to display controls at the bottom of the screen
def display_controls_info(grid_width):
    stddraw.setPenColor(stddraw.WHITE)
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(12)
    controls = "Controls: ← → Move  ↑ Rotate  ↓ Soft Drop  Space Hard Drop  P Pause  R Restart  Esc Exit"
    # Adjust position slightly to fit within the standard scale
    stddraw.text((grid_width -1) / 2, -0.3, controls)


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
    # the colors used for the menu
    background_color = Color(42, 69, 99)
    button_color = Color(25, 255, 228)
    text_color = Color(31, 160, 239)
    # clear the background drawing canvas to background_color
    stddraw.clear(background_color)
    # get the directory in which this python code file is placed
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # compute the path of the image file
    img_file = current_dir + "/images/menu_image.png"
    # Check if image exists, handle potential error
    if not os.path.exists(img_file):
        print(f"Warning: Menu image not found at {img_file}")
        img_center_x, img_center_y = (grid_width - 1) / 2, grid_height - 7 # Position even if image missing
    else:
        # the coordinates to display the image centered horizontally
        img_center_x, img_center_y = (grid_width - 1) / 2, grid_height - 7
        # the image is modeled by using the Picture class
        image_to_display = Picture(img_file)
        # add the image to the drawing canvas
        stddraw.picture(image_to_display, img_center_x, img_center_y)

    # Title for the game
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(35)
    stddraw.setPenColor(Color(255, 255, 255))
    # Use the calculated img_center_x for centering text as well
    stddraw.text(img_center_x, grid_height - 3, "TETRIS 2048")

    # the dimensions for the start game button
    button_w, button_h = grid_width - 1.5, 2
    # the coordinates of the bottom left corner for the start game button
    button_blc_x, button_blc_y = img_center_x - button_w / 2, 4
    # add the start game button as a filled rectangle
    stddraw.setPenColor(button_color)
    stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)
    # add the text on the start game button
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(25)
    stddraw.setPenColor(text_color)
    text_to_display = "Click Here to Start the Game"
    stddraw.text(img_center_x, 5, text_to_display)

    # Add controls information
    stddraw.setFontFamily("Arial")
    stddraw.setFontSize(15)
    stddraw.setPenColor(Color(200, 200, 200))
    stddraw.text(img_center_x, 2, "Controls: Arrow Keys to Move/Rotate, Space for Hard Drop")
    stddraw.text(img_center_x, 1, "P to Pause, R to Restart, Esc to Exit")

    # the user interaction loop for the simple menu
    while True:
        # display the menu and wait for a short time (50 ms)
        stddraw.show(50) # Keep show here for menu interaction
        # check if the mouse has been left-clicked on the start game button
        if stddraw.mousePressed():
            # get the coordinates of the most recent location at which the mouse
            # has been left-clicked
            mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
            # check if these coordinates are inside the button
            if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
                if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
                    break  # break the loop to end the method and start the game


# start() function is specified as the entry point (main function) from which
# the program starts execution
if __name__ == '__main__':
    start()

# --- END OF FILE Tetris_2048.py ---
