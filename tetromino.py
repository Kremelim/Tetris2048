from tile import Tile  # used for modeling each tile on the tetrominoes
from point import Point  # used for tile positions
import copy as cp  # the copy module is used for copying tiles and positions
import random  # the random module is used for generating random values
import numpy as np  # the fundamental Python module for scientific computing

# A class for modeling tetrominoes with 7 different types
class Tetromino:
   # the dimensions of the game grid (defined as class variables)
   grid_height, grid_width = None, None

   # A constructor for creating a tetromino with a given shape (type)
   def __init__(self, shape):
      self.type = shape  # set the type of this tetromino
      # determine the occupied (non-empty) cells in the tile matrix based on
      # the shape of this tetromino (see the documentation given with this code)
      occupied_cells = []
      if self.type == 'I':
         n = 4  # n = number of rows = number of columns in the tile matrix
         # shape of the tetromino I in its initial rotation state
         occupied_cells.append((1, 0)) # (col, row) from top-left
         occupied_cells.append((1, 1))
         occupied_cells.append((1, 2))
         occupied_cells.append((1, 3))
      elif self.type == 'O':
         n = 2 # O is 2x2
         # shape of the tetromino O in its initial rotation state
         occupied_cells.append((0, 0))
         occupied_cells.append((1, 0))
         occupied_cells.append((0, 1))
         occupied_cells.append((1, 1))
      elif self.type == 'Z':
         n = 3
         # shape of the tetromino Z in its initial rotation state
         occupied_cells.append((0, 0)) # Adjusted Z shape slightly based on common Tetris
         occupied_cells.append((1, 0))
         occupied_cells.append((1, 1))
         occupied_cells.append((2, 1))
      elif self.type == 'J':
         n = 3
         # shape of the tetromino J in its initial rotation state
         occupied_cells.append((0, 0)) # Adjusted J shape
         occupied_cells.append((1, 0))
         occupied_cells.append((2, 0))
         occupied_cells.append((2, 1))
      elif self.type == 'L':
         n = 3
         # shape of the tetromino L in its initial rotation state
         occupied_cells.append((0, 0)) # Adjusted L shape
         occupied_cells.append((1, 0))
         occupied_cells.append((2, 0))
         occupied_cells.append((0, 1))
      elif self.type == 'S':
         n = 3
         # shape of the tetromino S in its initial rotation state
         occupied_cells.append((1, 0)) # Adjusted S shape
         occupied_cells.append((2, 0))
         occupied_cells.append((0, 1))
         occupied_cells.append((1, 1))
      elif self.type == 'T':
         n = 3
         # shape of the tetromino T in its initial rotation state
         occupied_cells.append((0, 0)) # Adjusted T shape
         occupied_cells.append((1, 0))
         occupied_cells.append((2, 0))
         occupied_cells.append((1, 1))
      # create a matrix of numbered tiles based on the shape of this tetromino
      self.tile_matrix = np.full((n, n), None)
      # Rotation center (relative to matrix indices) - adjust per shape if needed
      # Defaulting to roughly center, may need fine-tuning per piece shape/size
      self.rotation_center = ( (n - 1) / 2, (n - 1) / 2)


      # create the four tiles (minos) of this tetromino and place these tiles
      # into the tile matrix
      for i in range(len(occupied_cells)):
         col_index, row_index = occupied_cells[i][0], occupied_cells[i][1]

         # --- Modification Start: Assign Random Number ---
         # Choose 2 or 4 with 90% probability for 2 and 10% for 4
         # random.choices returns a list, so get the first element [0]
         tile_number = random.choices([2, 4], weights=[0.9, 0.1], k=1)[0]

         # create a tile for each occupied cell of this tetromino
         self.tile_matrix[row_index][col_index] = Tile(tile_number)
      # initialize the position of this tetromino (as the bottom left cell in
      # the tile matrix) with a random horizontal position near the top
      # Ensure the piece spawns high enough, adjust y based on n
      # Spawn centered horizontally, adjust for piece width (n)
      self.bottom_left_cell = Point()
      # Start Y high enough so the bottom row of the matrix is just below grid_height
      self.bottom_left_cell.y = Tetromino.grid_height - n
      initial_x = Tetromino.grid_width // 2 - n // 2 # Center horizontally
      self.bottom_left_cell.x = max(0, min(initial_x, Tetromino.grid_width - n)) # Clamp within bounds


   # A method that computes and returns the position of the cell in the tile
   # matrix specified by the given row and column indexes on the game grid
   def get_cell_position(self, row, col):
      n = len(self.tile_matrix)  # n = number of rows = number of columns
      position = Point()
      # Grid X coordinate = bottom_left_x + column index in matrix
      position.x = self.bottom_left_cell.x + col
      # Grid Y coordinate = bottom_left_y + distance from bottom row in matrix
      # Distance from bottom row = (n - 1) - row index
      position.y = self.bottom_left_cell.y + (n - 1) - row
      return position

   # A method to return a copy of the tile matrix without any empty row/column,
   # and the position of the bottom left cell when return_position is set
   def get_min_bounded_tile_matrix(self, return_position=False):
        n = len(self.tile_matrix)
        min_row, max_row, min_col, max_col = -1, -1, -1, -1

        # Find the bounds of the actual tiles
        for r in range(n):
            for c in range(n):
                if self.tile_matrix[r][c] is not None:
                    if min_row == -1: # First tile found
                        min_row, max_row, min_col, max_col = r, r, c, c
                    else:
                        min_row = min(min_row, r)
                        max_row = max(max_row, r)
                        min_col = min(min_col, c)
                        max_col = max(max_col, c)

        # Handle case where tetromino is empty (shouldn't happen)
        if min_row == -1:
             if return_position:
                 return np.array([[]]), cp.copy(self.bottom_left_cell)
             else:
                 return np.array([[]])

        # Create the bounded copy
        bounded_height = max_row - min_row + 1
        bounded_width = max_col - min_col + 1
        copy = np.full((bounded_height, bounded_width), None, dtype=object) # Specify dtype=object

        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                if self.tile_matrix[r][c] is not None:
                    copy[r - min_row][c - min_col] = cp.deepcopy(self.tile_matrix[r][c])

        if not return_position:
            return copy
        else:
            # Calculate the grid position of the bottom-left cell of the bounded matrix
            # BLC corresponds to matrix cell (max_row, min_col)
            blc_position = self.get_cell_position(max_row, min_col)
            # # The old calculation might have been slightly off depending on interpretation.
            # # Let's recalculate blc based on the min/max found relative to the original bottom_left_cell
            # blc_position = cp.copy(self.bottom_left_cell)
            # # Translate horizontally by min_col
            # blc_position.translate(min_col, 0)
            # # Translate vertically. The original y corresponds to row n-1.
            # # The new bottom row is max_row. The difference in rows is (n-1) - max_row.
            # # Translate y by this amount.
            # blc_position.translate(0, (n - 1) - max_row) # This seems correct
            return copy, blc_position


   # A method for drawing the tetromino on the game grid
   def draw(self):
      n = len(self.tile_matrix)  # n = number of rows = number of columns
      for row in range(n):
         for col in range(n):
            # draw each occupied cell as a tile on the game grid
            if self.tile_matrix[row][col] is not None:
               # get the position of the tile
               position = self.get_cell_position(row, col)
               # draw only the tiles that are inside the game grid (visually)
               # Allow drawing slightly above the grid if piece is spawning/moving there
               if position.y < Tetromino.grid_height + n: # Allow buffer for spawning anim
                  self.tile_matrix[row][col].draw(position)

   # A method for moving this tetromino in a given direction by 1 on the grid
   def move(self, direction, game_grid):
      # check if this tetromino can be moved in the given direction by using
      # the can_be_moved method defined below
      if not (self.can_be_moved(direction, game_grid)):
         return False  # the tetromino cannot be moved in the given direction
      # move this tetromino by updating the position of its bottom left cell
      if direction == "left":
         self.bottom_left_cell.x -= 1
      elif direction == "right":
         self.bottom_left_cell.x += 1
      else:  # direction == "down"
         self.bottom_left_cell.y -= 1
      return True  # a successful move in the given direction

   # A method for checking if this tetromino can be moved in a given direction
   # Added check_initial flag for spawn validation
   def can_be_moved(self, direction, game_grid, check_initial=False):
        n = len(self.tile_matrix)
        # Iterate through each tile of the tetromino
        for row in range(n):
            for col in range(n):
                if self.tile_matrix[row][col] is not None:
                    # Calculate the current grid position of the tile
                    current_pos = self.get_cell_position(row, col)
                    # Calculate the potential next grid position
                    next_pos_x, next_pos_y = current_pos.x, current_pos.y

                    if direction == "left":
                        next_pos_x -= 1
                    elif direction == "right":
                        next_pos_x += 1
                    elif direction == "down":
                        next_pos_y -= 1
                    # Add check for "up" or other directions if needed

                    # If check_initial is True, we only check the current position
                    if check_initial:
                        if not game_grid.is_inside(current_pos.y, current_pos.x):
                            # If any part is initially outside (should mainly check above grid height)
                            if current_pos.y >= Tetromino.grid_height:
                                return False # Cannot spawn if initially outside top
                            # Allow spawning if slightly left/right outside if it can correct? No, enforce inside.
                            if current_pos.x < 0 or current_pos.x >= Tetromino.grid_width:
                                 return False
                        # Check if the initial position is occupied
                        if game_grid.is_occupied(current_pos.y, current_pos.x):
                            return False
                        # If checking initial spawn, skip movement checks below for this tile
                        continue

                    # --- Standard Movement Checks ---
                    # 1. Check boundary conditions for the next position
                    if direction == "left" and next_pos_x < 0:
                        return False
                    if direction == "right" and next_pos_x >= Tetromino.grid_width:
                        return False
                    if direction == "down" and next_pos_y < 0:
                        return False

                    # 2. Check grid occupation for the next position (only if inside grid)
                    if game_grid.is_inside(next_pos_y, next_pos_x):
                         if game_grid.is_occupied(next_pos_y, next_pos_x):
                              # If moving down and hitting occupied, specific logic might apply (landing)
                              # For now, any occupied next spot means cannot move there.
                              return False
                    # If moving down and the next position is below the grid (y < 0),
                    # it's also an invalid move (handled by boundary check above).

        # If we checked all tiles and none caused a conflict for the given direction (or initial placement)
        return True


   # Method for rotating the tetromino 90-degree clockwise
   def rotate(self, game_grid):
        """
        Rotates the tetromino 90 degrees clockwise. Checks for validity before applying.
        """
        n = len(self.tile_matrix)
        if self.type == 'O': # O doesn't rotate
            return True

        # Create a temporary matrix for the rotated state
        rotated_matrix = np.full((n, n), None, dtype=object)

        # Perform rotation math (clockwise)
        # New row = old col
        # New col = n - 1 - old row
        for r in range(n):
            for c in range(n):
                if self.tile_matrix[r][c] is not None:
                    new_r = c
                    new_c = n - 1 - r
                    if 0 <= new_r < n and 0 <= new_c < n:
                        rotated_matrix[new_r][new_c] = self.tile_matrix[r][c] # Shallow copy tile reference

        # Check if the rotated position is valid (within bounds and not occupied)
        for r_rot in range(n):
            for c_rot in range(n):
                if rotated_matrix[r_rot][c_rot] is not None:
                    # Calculate the potential grid position of this rotated tile
                    # Use the same logic as get_cell_position relative to bottom_left_cell
                    grid_x = self.bottom_left_cell.x + c_rot
                    grid_y = self.bottom_left_cell.y + (n - 1) - r_rot

                    # Check boundaries
                    if not game_grid.is_inside(grid_y, grid_x):
                        # Try wall kicks later if needed, for now, just fail rotation
                        return False
                    # Check occupation
                    if game_grid.is_occupied(grid_y, grid_x):
                        return False

        # If all checks pass, apply the rotation
        self.tile_matrix = rotated_matrix
        return True
