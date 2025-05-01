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
