import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing
import copy as cp


# A class for modeling the game grid
class GameGrid:
    # A constructor for creating the game grid based on the given arguments
    def __init__(self, grid_h, grid_w):
        # set the dimensions of the game grid as the given arguments
        self.grid_height = grid_h
        self.grid_width = grid_w
        # create a tile matrix to store the tiles locked on the game grid
        # Ensure dtype=object to store None or Tile instances
        self.tile_matrix = np.full((grid_h, grid_w), None, dtype=object) # Kept from first version
        # create the tetromino that is currently being moved on the game grid
        self.current_tetromino = None
        # add storage for the next piece
        self.next_tetromino = None
        # the game_over flag shows whether the game is over or not
        self.game_over = False
        # set the color used for the empty grid cells
        self.empty_cell_color = Color(42, 69, 99)
        # set the colors used for the grid lines and the grid boundaries
        self.line_color = Color(0, 100, 200)
        self.boundary_color = Color(0, 100, 200)
        # thickness values used for the grid lines and the grid boundaries
        self.line_thickness = 0.002
        self.box_thickness = 10 * self.line_thickness
        # Initialize score
        self.score = 0

    # A method for displaying the game grid (Unchanged from first version)
    def display(self):
        # clear the background to empty_cell_color
        stddraw.clear(self.empty_cell_color)
        # draw the game grid
        self.draw_grid()
        # draw the current/active tetromino if it is not None
        if self.current_tetromino is not None:
            self.current_tetromino.draw()

        # Display the next tetromino in a preview box
        if self.next_tetromino is not None:
            preview_box_x = self.grid_width + 0.5
            preview_box_w = 5  # Width of the preview box
            preview_box_h = 4  # Height of the preview box
            # Position the preview box somewhat vertically centered or towards the top
            preview_box_y = self.grid_height - preview_box_h - 1.5

            # "NEXT" Label
            stddraw.setPenColor(Color(255, 255, 255))
            stddraw.setFontFamily("Arial")
            stddraw.setFontSize(18)
            stddraw.text(preview_box_x + preview_box_w / 2,
                         preview_box_y + preview_box_h + 0.5, "NEXT")

            # Border for preview box
            stddraw.setPenRadius(self.line_thickness)
            stddraw.setPenColor(self.line_color)
            stddraw.rectangle(preview_box_x, preview_box_y,
                              preview_box_w, preview_box_h)
            stddraw.setPenRadius() # Reset pen radius

            # Get the minimal representation of the next tetromino
            next_tiles = self.next_tetromino.get_min_bounded_tile_matrix()

            if next_tiles.size > 0: # Check if the matrix is not empty
                 n_rows, n_cols = next_tiles.shape

                 # Calculate offsets to center the piece within the preview box
                 offset_x = (preview_box_w - n_cols) / 2.0
                 offset_y = (preview_box_h - n_rows) / 2.0

                 # Draw each tile of the next tetromino relative to the preview box
                 for r in range(n_rows):
                     for c in range(n_cols):
                         if next_tiles[r][c] is not None:
                             # Calculate draw position for the tile's center
                             draw_x = preview_box_x + offset_x + c + 0.5
                             draw_y = preview_box_y + offset_y + (n_rows - 1 - r) + 0.5 # Center of tile at this row

                             # Draw the tile using its draw method at the calculated position
                             draw_point = Point(draw_x, draw_y)
                             tile_to_draw = next_tiles[r][c]
                             tile_to_draw.draw(draw_point) # Draw the tile

        # Display score
        stddraw.setPenColor(Color(255, 255, 255))
        stddraw.setFontFamily("Arial")
        stddraw.setFontSize(18)
        # Position score below the next piece preview
        score_x = preview_box_x + preview_box_w / 2 # Center under preview box
        score_y_label = preview_box_y - 1.5 # Adjust spacing as needed
        score_y_value = preview_box_y - 2.5
        stddraw.text(score_x, score_y_label, "SCORE")
        stddraw.text(score_x, score_y_value, str(self.score))

        # draw a box around the game grid
        self.draw_boundaries()
        # The stddraw.show() is called in the main game loop for animation control

    # A method for drawing the cells and the lines of the game grid (Unchanged from first version)
    def draw_grid(self):
        # for each cell of the game grid
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # if the current grid cell is occupied by a tile
                if self.tile_matrix[row][col] is not None:
                    # draw this tile at its grid position (center point)
                    draw_pos = Point(col + 0.5, row + 0.5)
                    self.tile_matrix[row][col].draw(draw_pos) # Pass the center point
        # draw the inner lines of the game grid
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        # x and y ranges for the game grid boundaries
        start_x, end_x = -0.5, self.grid_width - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
            stddraw.line(x, start_y, x, end_y)
        for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # A method for drawing the boundaries around the game grid (Unchanged from first version)
    def draw_boundaries(self):
        # draw a bounding box around the game grid as a rectangle
        stddraw.setPenColor(self.boundary_color)  # using boundary_color
        stddraw.setPenRadius(self.box_thickness)
        # the coordinates of the bottom left corner for the rectangle
        pos_x, pos_y = -0.5, -0.5
        stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # A method used checking whether the grid cell is occupied (Unchanged from first version)
    def is_occupied(self, row, col):
         # Convert row/col to integers if they aren't already
        row, col = int(round(row)), int(round(col)) # Use round for robustness

        if not self.is_inside(row, col):
            return False # Outside grid is not occupied by definition
        # Access the tile matrix to check if the cell is None or contains a Tile object
        return self.tile_matrix[row][col] is not None

    # A method for checking whether the cell is inside the game grid (Unchanged from first version)
    def is_inside(self, row, col):
         # Convert row/col to integers if they aren't already
        row, col = int(round(row)), int(round(col)) # Use round for robustness
        # Check row bounds
        if row < 0 or row >= self.grid_height:
            return False
        # Check col bounds
        if col < 0 or col >= self.grid_width:
            return False
        return True

    # --- NEW: find_connected_tiles using DFS (from second version) ---
    def find_connected_tiles(self):
        """
        Identify tiles that are connected to the bottom of the grid using DFS.
        (Logic from second version)
        Returns a boolean matrix where True indicates a connected tile.
        """
        connected = np.full((self.grid_height, self.grid_width), False, dtype=bool) # Ensure boolean dtype

        # Start DFS from all occupied tiles in the bottom row (row 0)
        for col in range(self.grid_width):
            if self.tile_matrix[0][col] is not None:
                # Use integer indices for grid access
                self._dfs_connect(0, col, connected)

        return connected

    # --- NEW: DFS helper method (from second version) ---
    def _dfs_connect(self, row, col, connected):
        """Helper method for DFS to mark connected tiles (Logic from second version)"""
        # Ensure indices are integers
        row, col = int(round(row)), int(round(col))

        # Check bounds, already visited, or empty cell
        if not self.is_inside(row, col) or \
           connected[row][col] or \
           self.tile_matrix[row][col] is None:
            return

        # Mark the current tile as connected
        connected[row][col] = True

        # Recursively check 4-connected neighbors (right, left, up, down)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            self._dfs_connect(row + dr, col + dc, connected)
    # --- NEW: handle_free_tiles using _move_tile_down (from second version) ---
    def handle_free_tiles(self):
        """
        Attempts to move tiles that are not connected to the bottom down ONE step.
        (Logic from second version - may require multiple calls for full drop)
        Returns True if any tile was moved down one step in this pass, False otherwise.
        """
        # Find connected tiles using the DFS method
        connected = self.find_connected_tiles()
        tile_moved_this_pass = False

        # Process tiles from bottom to top (row 1 upwards) to handle dependencies correctly
        for row in range(1, self.grid_height):
            for col in range(self.grid_width):
                # Check if it's a tile and it's floating
                if self.tile_matrix[row][col] is not None and not connected[row][col]:
                    # Attempt to move this tile down one step using the helper
                    if self._move_tile_down(row, col):
                        tile_moved_this_pass = True
                        # Note: After moving, the 'connected' status isn't updated here.
                        # The calling context (e.g., update_grid loop) needs to handle stability.

        return tile_moved_this_pass

    # --- NEW: Helper method for handle_free_tiles (from second version) ---
    def _move_tile_down(self, row, col):
        """
        Moves the tile at (row, col) down ONE grid cell if the cell below is empty.
        (Helper for handle_free_tiles, logic from second version)
        Returns True if the tile was moved, False otherwise.
        """
        # Ensure indices are integers
        row, col = int(round(row)), int(round(col))

        # Basic checks: tile exists, not already at bottom
        if row <= 0 or self.tile_matrix[row][col] is None:
            return False

        # Check if the cell directly below is inside the grid and is empty
        if self.is_inside(row - 1, col) and self.tile_matrix[row - 1][col] is None:
            # Move the tile down one step
            self.tile_matrix[row - 1][col] = self.tile_matrix[row][col]
            self.tile_matrix[row][col] = None
            return True # Tile moved

        return False # Tile could not be moved down one step


    # A method for check and clear lines (Unchanged from first version, but ensure return value)
    def check_and_clear_lines(self):
        """
      Checks for and clears completed lines from bottom to top.
      Shifts the rows above cleared lines down.
      Returns number of lines cleared in this step. Adds score for cleared tiles.
      (Logic unchanged from first version)
      """
        lines_cleared = 0
        # Create a temporary new matrix to hold the state after clearing/shifting
        new_tile_matrix = np.full((self.grid_height, self.grid_width), None, dtype=object)
        # Index for writing rows into the new matrix (starts from bottom)
        write_row = 0

        # Iterate through the original grid rows from bottom (0) to top
        for read_row in range(self.grid_height):
            is_row_full = True
            row_score = 0
            for col in range(self.grid_width):
                tile = self.tile_matrix[read_row][col]
                if tile is None:
                    is_row_full = False
                    # No need to check rest of row if looking for fullness
                    break
                else:
                    # Accumulate score potential only if row turns out full
                    row_score += tile.number

            if not is_row_full:
                # If row is not full, copy it to the next available spot in the new matrix
                if write_row < self.grid_height: # Bounds check
                    new_tile_matrix[write_row] = self.tile_matrix[read_row].copy() # Copy the row
                    write_row += 1 # Move write index up for the next non-full row
            else:
                # Row IS full. Increment cleared count and add score.
                # Do NOT copy this row to the new matrix.
                lines_cleared += 1
                self.score += row_score # Add score from the cleared line

        # After checking all rows, if lines were cleared, update the grid's matrix
        if lines_cleared > 0:
            self.tile_matrix = new_tile_matrix # Replace old matrix with the shifted one

        return lines_cleared # Return the number of lines cleared


    # --- NEW: check_and_merge_tiles (from second version) ---
    def check_and_merge_tiles(self):
        """
        Check for and merge adjacent tiles with the same number vertically.
        Merging happens downwards (upper tile merges into lower tile).
        Calls handle_free_tiles repeatedly after each merge until stable.
        Loops checking for merges until no merges occur in a full pass.
        (Logic from second version)
        Returns the total score gained from merges in this invocation.
        """
        total_merge_score_this_invocation = 0
        merge_occurred_in_cycle = True # Flag to control the outer loop

        # Continue checking for merges as long as a merge happened in the previous pass
        while merge_occurred_in_cycle:
            merge_occurred_in_cycle = False # Reset for this pass

            # Check columns left to right
            for col in range(self.grid_width):
                # Check rows from bottom up (index 1 to height - 1)
                # Compare tile at row with tile at row-1
                for row in range(1, self.grid_height):
                    tile_current = self.tile_matrix[row][col]     # Upper tile
                    tile_below = self.tile_matrix[row - 1][col] # Lower tile

                    # Check if both tiles exist and have the same number
                    if (tile_current is not None and tile_below is not None and
                        tile_current.number == tile_below.number):

                        # --- Perform Merge ---
                        new_value = tile_below.number * 2
                        # Update the lower tile's number and color
                        self.tile_matrix[row - 1][col].update_number_and_color(new_value)
                        # Remove the upper tile
                        self.tile_matrix[row][col] = None

                        # --- Score ---
                        merge_score = new_value
                        total_merge_score_this_invocation += merge_score
                        self.score += merge_score # Update total game score

                        # --- State Change ---
                        merge_occurred_in_cycle = True # Mark that a merge happened

                        # --- Handle Falling Tiles Immediately After Merge ---
                        # Call handle_free_tiles repeatedly until stable
                        while self.handle_free_tiles():
                            pass # Keep calling until no more single steps happen

                        # --- Restart Scan After Merge and Fall ---
                        # Break inner loop (rows) to re-scan this column from bottom after change
                        break # Crucial to re-evaluate from bottom after merge/fall

                # If the inner loop was broken (due to a merge in this column),
                # break the outer loop too to restart the whole 'while' cycle
                if merge_occurred_in_cycle:
                    break # Break from the column loop

        return total_merge_score_this_invocation


    # --- MODIFIED: update_grid sequence using new logic ---
    def update_grid(self, tiles_to_lock, blc_position):
        """
        Locks the tiles, checks for game over, then iteratively handles
        merges, line clears, and falling tiles until the grid stabilizes.
        Uses the handling logic/sequence derived from the second version.
        """
        # Lock the tiles onto the grid (Adapted from first version)
        self.current_tetromino = None
        n_rows, n_cols = tiles_to_lock.shape
        spawn_overlap_or_above = False

        for r in range(n_rows):
            for c in range(n_cols):
                if tiles_to_lock[r][c] is not None:
                    # Calculate grid coordinates relative to the bounded box's bottom-left position
                    grid_x = blc_position.x + c
                    grid_y = blc_position.y + (n_rows - 1 - r) # Map matrix row to grid row

                    grid_x_int = int(round(grid_x)) # Ensure integer indices
                    grid_y_int = int(round(grid_y))

                    if self.is_inside(grid_y_int, grid_x_int):
                        if self.tile_matrix[grid_y_int][grid_x_int] is not None:
                            spawn_overlap_or_above = True
                            break
                        # Deepcopy the tile (as in first version)
                        self.tile_matrix[grid_y_int][grid_x_int] = cp.deepcopy(tiles_to_lock[r][c])
                    else:
                        # Check if trying to lock above the grid
                        if grid_y_int >= self.grid_height:
                            spawn_overlap_or_above = True
                            break
                        # Ignore tiles locking outside other bounds
            if spawn_overlap_or_above: # Exit outer loop if overlap found
                 break

        # Check for immediate game over from locking phase
        if spawn_overlap_or_above:
            self.game_over = True
            # print("Game Over: Piece locked overlapping existing tile or above grid.") # Optional debug
            return self.game_over # Return True for game over

        # --- Post-Placement Processing Loop ---
        # Continuously process merges, line clears, and falling tiles until grid stabilizes
        while True:
            grid_changed_this_cycle = False

            # 1. Check for merges (includes internal falling after each merge)
            merge_score = self.check_and_merge_tiles()
            if merge_score > 0:
                grid_changed_this_cycle = True

            # 2. Check for line clears
            lines_cleared = self.check_and_clear_lines()
            if lines_cleared > 0:
                grid_changed_this_cycle = True

            # 3. Handle any remaining free tiles (e.g., created by line clears)
            # Call repeatedly until no more single-step moves occur in a pass
            fell_in_pass = False
            while self.handle_free_tiles():
                fell_in_pass = True

            if fell_in_pass:
                grid_changed_this_cycle = True

            # Exit loop if the grid is stable (no changes happened in this full cycle)
            if not grid_changed_this_cycle:
                break

        # Return the final game_over state
        return self.game_over
