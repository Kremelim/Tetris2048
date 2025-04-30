# --- START OF FILE game_grid.py ---

import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
from point import Point  # used for tile positions
import copy as cp  # the copy module is used for copying tiles and positions
import numpy as np  # fundamental Python module for scientific computing
from collections import deque # For BFS in handle_free_tiles

# A class for modeling the game grid
class GameGrid:
   # A constructor for creating the game grid based on the given arguments
   def _init_(self, grid_h, grid_w):
      # set the dimensions of the game grid as the given arguments
      self.grid_height = grid_h
      self.grid_width = grid_w
      # create a tile matrix to store the tiles locked on the game grid
      # Use dtype=object for numpy array to store None or Tile objects
      self.tile_matrix = np.full((grid_h, grid_w), None, dtype=object)
      # create the tetromino that is currently being moved on the game grid
      self.current_tetromino = None
      # add storage for the next piece
      self.next_tetromino = None
      # the game_over flag shows whether the game is over or not
      self.game_over = False
      # --- Add score attribute ---
      self.score = 0
      # --- Add win condition flag (optional for now, useful later) ---
      # self.game_won = False
      # set the color used for the empty grid cells
      self.empty_cell_color = Color(42, 69, 99)
      # set the colors used for the grid lines and the grid boundaries
      self.line_color = Color(0, 100, 200)
      self.boundary_color = Color(0, 100, 200)
      # thickness values used for the grid lines and the grid boundaries
      self.line_thickness = 0.002
      self.box_thickness = 4 * self.line_thickness

   # --- Method: apply_gravity_to_column (No changes needed) ---
   def apply_gravity_to_column(self, col_index):
      """Shifts tiles down in a specific column to fill empty spaces below them."""
      write_pointer = 0
      for read_pointer in range(self.grid_height):
         if self.tile_matrix[read_pointer, col_index] is not None:
            if read_pointer != write_pointer:
               # Move the tile object
               self.tile_matrix[write_pointer, col_index] = self.tile_matrix[read_pointer, col_index]
               # Update the tile's internal position if it stores it (assuming Tile doesn't store grid position)
               # tile = self.tile_matrix[write_pointer, col_index]
               # if hasattr(tile, 'position'): # Check if tile has position attribute
               #    tile.position.y = write_pointer # Update y coordinate

               self.tile_matrix[read_pointer, col_index] = None  # Clear the original spot
            write_pointer += 1

   # --- Method: apply_gravity (No changes needed) ---
   def apply_gravity(self):
      """Applies gravity to all columns."""
      for col in range(self.grid_width):
         self.apply_gravity_to_column(col)

   # --- Method: handle_merges (No changes needed) ---
   def handle_merges(self):
      """Checks for and performs merges column by column, bottom-up.
         Returns the score gained from merges in this pass and if any merge occurred."""
      score_from_merges = 0
      merge_occurred = False
      for col in range(self.grid_width):
         # Iterate bottom-up (from row 0 up to grid_height - 2)
         # Check tile at 'row' with tile at 'row + 1'
         row = 0
         while row < self.grid_height - 1:
            tile_current = self.tile_matrix[row, col]
            tile_above = self.tile_matrix[row + 1, col]

            # Check if merge is possible (both tiles exist and have same number)
            if tile_current is not None and tile_above is not None and \
                     tile_current.number == tile_above.number:
               # Perform merge: Update current tile's number and color, remove upper tile
               new_number = tile_current.number * 2
               tile_current.update_number_and_color(new_number)  # Use the method from tile.py
               self.tile_matrix[row + 1, col] = None  # Remove the upper tile

               # Update score and flag
               score_from_merges += new_number
               merge_occurred = True

               # Optional: Check for win condition here if you add self.game_won flag
               # if new_number == 2048:
               #    self.game_won = True

               # After a merge in this column, gravity needs to re-apply to potentially
               # cause further merges below the newly formed tile in the same pass.
               # Instead of full gravity, just shift down within this column above the merge point.
               # This is complex. The current loop structure only checks adjacent tiles once per pass.
               # A full re-application of gravity and re-check within the main loop is simpler.
               # The current logic handles one merge per adjacent pair per pass.
               # Chain merges like 2-2 becoming 4, then meeting another 4 requires the outer loop in update_grid.
               # For now, just move to the next row potential merge above the one just performed.
               row += 1 # Skip the row where the merged tile now sits
            row += 1


      # Apply gravity after all potential column merges are checked in this pass
      # This ensures tiles fall before the next merge check cycle.
      if merge_occurred:
          self.apply_gravity() # Apply gravity grid-wide if any merge happened

      return score_from_merges, merge_occurred
   # --- End Method: handle_merges ---

   # A method for displaying the game grid
   def display(self):
      # clear the background to empty_cell_color
      stddraw.clear(self.empty_cell_color)
      # draw the game grid
      self.draw_grid()
      # draw the current/active tetromino if it is not None
      if self.current_tetromino is not None:
         self.current_tetromino.draw()

      # Draw Score
      stddraw.setPenColor(Color(255, 255, 255))  # White text color
      stddraw.setFontFamily("Arial")
      stddraw.setFontSize(20)
      # Position score display (adjust x,y as needed for your layout)
      score_text_x = self.grid_width + 3 # Example: Center in the preview area
      score_text_y = self.grid_height - 1 # Example: Top of the preview area
      stddraw.text(score_text_x, score_text_y, "SCORE")
      stddraw.text(score_text_x, score_text_y - 1.2, str(self.score)) # Display score value below label

      # Draw Next Tetromino Preview Box and Label
      if self.next_tetromino is not None:
         preview_box_x = self.grid_width + 0.5 # Start x slightly right of grid
         preview_box_w = 5                   # Width of preview box
         preview_box_h = 4                   # Height of preview box
         preview_box_y = self.grid_height - preview_box_h - 4.5 # Position below score (adjust as needed)

         # "NEXT" Label
         stddraw.setPenColor(Color(255, 255, 255))
         stddraw.setFontFamily("Arial")
         stddraw.setFontSize(18)
         stddraw.text(preview_box_x + preview_box_w / 2,
                      preview_box_y + preview_box_h + 0.5, # Position label above the box
                      "NEXT")

         # Preview Box Border
         stddraw.setPenRadius(self.line_thickness)
         stddraw.setPenColor(self.line_color)
         stddraw.rectangle(preview_box_x, preview_box_y,
                           preview_box_w, preview_box_h)
         stddraw.setPenRadius() # Reset pen radius

         # Draw the next tetromino inside the box
         # Use get_min_bounded_tile_matrix to get the smallest representation
         next_tiles = self.next_tetromino.get_min_bounded_tile_matrix()
         n_rows, n_cols = next_tiles.shape # Use shape for numpy arrays

         # Calculate offsets to center the piece
         offset_x = (preview_box_w - n_cols) / 2.0
         offset_y = (preview_box_h - n_rows) / 2.0

         # Draw each tile relative to the preview box's bottom-left corner
         for r in range(n_rows):
            for c in range(n_cols):
               tile_data = next_tiles[r][c]
               if tile_data is not None:
                  # Calculate drawing coordinates for the center of the tile
                  # Adjust y calculation for numpy array indexing (0 is top row)
                  draw_x = preview_box_x + offset_x + c + 0.5 # center of tile x
                  draw_y = preview_box_y + offset_y + (n_rows - 1 - r) + 0.5 # center of tile y

                  # Create a temporary copy to draw (or just draw directly if Tile.draw uses position)
                  # Need to instantiate a Point object for the draw method
                  draw_position = Point(draw_x, draw_y)
                  tile_data.draw(draw_position) # Assuming Tile.draw takes a Point

      # draw a box around the game grid
      self.draw_boundaries()
      # show the resulting drawing (remove pause later if main loop controls it)
      # stddraw.show(150) # Keep this pause or adjust as needed for visual flow

   # A method for drawing the cells and the lines of the game grid
   def draw_grid(self):
      # for each cell of the game grid
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            # if the current grid cell is occupied by a tile
            tile = self.tile_matrix[row, col]
            if tile is not None:
               # draw this tile using its draw method
               # The tile's draw method needs the center point of the grid cell
               cell_center_pos = Point(col + 0.5, row + 0.5) # Calculate center based on grid indices
               # Adjust if your Point and draw methods expect bottom-left:
               # cell_bottom_left_pos = Point(col, row)
               # tile.draw(cell_bottom_left_pos)
               # --- Assuming draw uses center: ---
               tile.draw(Point(col, row)) # Keep original if it works
               # --- If tiles need absolute screen coords, that's handled in Tile.draw ---

      # draw the inner lines of the game grid
      stddraw.setPenColor(self.line_color)
      stddraw.setPenRadius(self.line_thickness)
      # x and y ranges for the game grid
      start_x, end_x = -0.5, self.grid_width - 0.5
      start_y, end_y = -0.5, self.grid_height - 0.5
      for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
         stddraw.line(x, start_y, x, end_y)
      for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
         stddraw.line(start_x, y, end_x, y)
      stddraw.setPenRadius()  # reset the pen radius to its default value

   # A method for drawing the boundaries around the game grid (No changes needed)
   def draw_boundaries(self):
      stddraw.setPenColor(self.boundary_color)
      stddraw.setPenRadius(self.box_thickness)
      pos_x, pos_y = -0.5, -0.5
      stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
      stddraw.setPenRadius()

   # Method for checking if a cell is occupied (No changes needed)
   def is_occupied(self, row, col):
      if not self.is_inside(row, col):
         return False
      # Ensure row/col are integers for indexing
      row, col = int(round(row)), int(round(col))
      return self.tile_matrix[row, col] is not None

   # Method for checking if a cell is inside the grid (No changes needed)
   def is_inside(self, row, col):
       # Convert row/col to potential integers before checking bounds
       # This handles cases where float values might be passed (e.g., from position calculations)
       try:
           row_int, col_int = int(round(row)), int(round(col))
       except ValueError:
           return False # Cannot convert to int, definitely not inside

       if row_int < 0 or row_int >= self.grid_height:
           return False
       if col_int < 0 or col_int >= self.grid_width:
           return False
       return True


   # --- METHOD MODIFICATION: check_and_clear_lines ---
   def check_and_clear_lines(self):
      """
      Checks for and clears completed lines from bottom to top.
      Shifts the rows above cleared lines down.
      Returns number of lines cleared and the total score gained from cleared lines.
      """
      lines_cleared_count = 0
      score_from_clearing = 0
      row = 0
      while row < self.grid_height: # Check up to current height being processed
         is_row_full = True
         current_row_score = 0 # Score for this specific row if cleared
         for col in range(self.grid_width):
            tile = self.tile_matrix[row, col]
            if tile is None:
               is_row_full = False
               break  # Found an empty cell in this row
            else:
               current_row_score += tile.number # Add tile's number to potential row score

         if is_row_full:
            lines_cleared_count += 1
            score_from_clearing += current_row_score # Add this row's score to total

            # Row is full, clear it by shifting rows above down
            # Shift from the current row 'row' up to the second to top row
            for r_shift in range(row, self.grid_height - 1):
               # Copy the entire row from above down
               self.tile_matrix[r_shift, :] = self.tile_matrix[r_shift + 1, :].copy()

            # Clear the topmost row (which is now empty or garbage)
            self.tile_matrix[self.grid_height - 1, :] = np.full(self.grid_width, None, dtype=object)

            # Important: Do NOT increment row here. The row index 'row'
            # now contains the content of the row that was previously above.
            # We need to re-check this same row index in the next iteration
            # in case the shifted-down row is also full.
         else:
            # Row wasn't full, move check to the next row up
            row += 1

      return lines_cleared_count, score_from_clearing
   # --- End METHOD MODIFICATION: check_and_clear_lines ---


   # --- NEW METHOD: handle_free_tiles ---
   def handle_free_tiles(self):
        """
        Identifies tiles not connected (4-directionally) to the bottom row (row 0),
        deletes them, adds their number to the score, and returns the score gained
        and a boolean indicating if any free tiles were found.
        Uses Breadth-First Search (BFS).
        """
        score_from_free_tiles = 0
        free_tile_found = False

        connected_to_bottom = np.full((self.grid_height, self.grid_width), False)
        queue = deque()

        # 1. Initialize BFS: Add all tiles in the bottom row to the queue
        for col in range(self.grid_width):
            if self.tile_matrix[0, col] is not None:
                queue.append((0, col))
                connected_to_bottom[0, col] = True

        # 2. Perform BFS to find all connected tiles
        while queue:
            row, col = queue.popleft()

            # Check 4 neighbors (up, down, left, right)
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = row + dr, col + dc

                # Check if neighbor is valid: inside grid, has a tile, and not visited yet
                if self.is_inside(nr, nc):
                   # Use integer indices after is_inside confirms bounds
                   nr_int, nc_int = int(round(nr)), int(round(nc))
                   if not connected_to_bottom[nr_int, nc_int] and self.tile_matrix[nr_int, nc_int] is not None:
                        connected_to_bottom[nr_int, nc_int] = True
                        queue.append((nr_int, nc_int))

        # 3. Identify, score, and remove unconnected tiles
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                if self.tile_matrix[r, c] is not None and not connected_to_bottom[r, c]:
                    free_tile_found = True
                    score_from_free_tiles += self.tile_matrix[r, c].number
                    self.tile_matrix[r, c] = None # Delete the free tile

        return score_from_free_tiles, free_tile_found
   # --- End NEW METHOD: handle_free_tiles ---


   # --- METHOD MODIFICATION: update_grid ---
   # This method orchestrates locking, merging, gravity, line clearing, and free tiles.
   def update_grid(self, tiles_to_lock, blc_position):
      # Lock the incoming tetromino tiles onto the grid
      self.current_tetromino = None  # Stop drawing the active tetromino
      n_rows, n_cols = tiles_to_lock.shape
      landed_coords = [] # Keep track of where tiles landed

      # Check for immediate game over condition before locking
      # A tile landing above the grid means game over.
      for r in range(n_rows):
          for c in range(n_cols):
              tile = tiles_to_lock[r, c]
              if tile is not None:
                  pos_y = blc_position.y + (n_rows - 1) - r # Calculate grid row index
                  pos_x = blc_position.x + c               # Calculate grid col index
                  if not self.is_inside(pos_y, pos_x):
                       # Check if it's specifically above the grid
                       if pos_y >= self.grid_height:
                           self.game_over = True
                           # Optional: Lock the tiles partially for visual feedback before game over screen
                           for r_lock in range(n_rows):
                               for c_lock in range(n_cols):
                                   tile_lock = tiles_to_lock[r_lock, c_lock]
                                   if tile_lock is not None:
                                       pos_y_lock = blc_position.y + (n_rows - 1) - r_lock
                                       pos_x_lock = blc_position.x + c_lock
                                       if self.is_inside(pos_y_lock, pos_x_lock):
                                           row_idx, col_idx = int(round(pos_y_lock)), int(round(pos_x_lock))
                                           self.tile_matrix[row_idx, col_idx] = tile_lock
                           # --- Force redraw to show final state ---
                           self.display()
                           stddraw.show(500) # Show final state briefly
                           # --- End Force redraw ---
                           return True # Game Over


      # Lock the tiles if no game over condition was met yet
      for r in range(n_rows):
          for c in range(n_cols):
              tile = tiles_to_lock[r, c]
              if tile is not None:
                  # Calculate the grid position for the tile
                  # The reference point 'blc_position' is the bottom-left of the
                  # bounding box returned by get_min_bounded_tile_matrix.
                  # Row index in tiles_to_lock increases downwards.
                  # Row index in grid increases upwards.
                  pos_y = blc_position.y + (n_rows - 1) - r # Calculate grid row index
                  pos_x = blc_position.x + c               # Calculate grid col index

                  # Lock the tile if it's inside the grid boundaries
                  if self.is_inside(pos_y, pos_x):
                      row_idx = int(round(pos_y))
                      col_idx = int(round(pos_x))
                      self.tile_matrix[row_idx, col_idx] = tile
                      landed_coords.append((row_idx, col_idx))
                  # else:
                      # Tiles outside the grid (e.g., during rotation near edge) are just ignored


      # --- Force a redraw showing the locked piece BEFORE merging/clearing ---
      # This gives visual feedback of the piece landing in place.
      self.display()
      stddraw.show(50) # Short pause to see the locked piece

      # --- Post-Landing Sequence ---
      total_merge_score = 0
      # 1. Repeatedly Apply Gravity & Handle Merges until stable
      while True:
         # Gravity first ensures tiles are adjacent before merge check
         self.apply_gravity()
         # Optional redraw after gravity if desired:
         # self.display(); stddraw.show(50)

         score_this_pass, merged_this_pass = self.handle_merges()
         total_merge_score += score_this_pass

         # Optional redraw after merges if desired:
         # if merged_this_pass: self.display(); stddraw.show(50)

         # If no merges occurred in this pass, the merging phase is stable
         if not merged_this_pass:
            break # Exit the merge/gravity loop

      self.score += total_merge_score # Update main score with merge points

      # 2. Check and Clear Full Lines (happens after merges stabilize)
      lines_cleared, score_from_lines = self.check_and_clear_lines()
      self.score += score_from_lines # Update main score

      # 3. Apply Gravity if lines were cleared
      if lines_cleared > 0:
          # Redraw to show cleared lines effect before gravity
          self.display()
          stddraw.show(100) # Pause to see cleared lines effect

          self.apply_gravity()
          # Redraw after gravity fills gaps from clearing
          self.display()
          stddraw.show(100) # Pause to see gravity effect

          # --- Optional: Re-run merge check after line clear gravity ---
          # This handles cases like:
          # 4 4
          # 2 2 <-- Cleared line
          # 4 4
          # After clearing and gravity:
          # 4 4
          # 4 4
          # These should now merge. Add another merge loop pass if needed.
          # For simplicity adhering to basic requirements, we might skip this complex re-merge.
          # Let's add one more merge/gravity cycle check just in case:
          additional_merge_score = 0
          while True:
              self.apply_gravity() # Apply gravity first in this inner loop too
              score_add_pass, merged_add_pass = self.handle_merges()
              additional_merge_score += score_add_pass
              if not merged_add_pass:
                  break
          self.score += additional_merge_score
          if additional_merge_score > 0: # Redraw if merges happened after line clear
              self.display()
              stddraw.show(100)


      # 4. Handle Free Tiles (Bonus Feature - happens after line clearing/gravity)
      score_from_free, free_found = self.handle_free_tiles()
      self.score += score_from_free # Update main score

      # 5. Apply Gravity if free tiles were removed
      if free_found:
          # Redraw to show state after free tiles removed, before gravity
          self.display()
          stddraw.show(100) # Pause to see free tiles removed

          self.apply_gravity()
          # Redraw after final gravity application
          self.display()
          stddraw.show(100) # Pause to see final gravity


      # The game state is now fully updated after a piece landing.
      # The main game loop will handle creating the next piece.
      return self.game_over # Return final game over status
# --- End METHOD MODIFICATION: update_grid ---
