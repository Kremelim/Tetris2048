import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing

# A class for modeling the game grid
class GameGrid:
   # A constructor for creating the game grid based on the given arguments
   def __init__(self, grid_h, grid_w):
      # set the dimensions of the game grid as the given arguments
      self.grid_height = grid_h
      self.grid_width = grid_w
      # create a tile matrix to store the tiles locked on the game grid
      self.tile_matrix = np.full((grid_h, grid_w), None)
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

   # A method for displaying the game grid
   def display(self):
      # clear the background to empty_cell_color
      stddraw.clear(self.empty_cell_color)
      # draw the game grid
      self.draw_grid()
      # draw the current/active tetromino if it is not None
      # (the case when the game grid is updated)
      if self.current_tetromino is not None:
         self.current_tetromino.draw()

      # next tetromino labels on game grid
      if self.next_tetromino is not None:
         preview_box_x = self.grid_width + 0.5
         preview_box_w = 5
         preview_box_h = 4
         preview_box_y = self.grid_height - preview_box_h - 1.5
         # NEXT label above the box
         stddraw.setPenColor(Color(255, 255, 255))
         stddraw.setFontFamily("Arial")
         stddraw.setFontSize(18)
         stddraw.text(preview_box_x + preview_box_w / 2,
                      preview_box_y + preview_box_h + 0.5,
                      "NEXT")
         # Border for preview box
         stddraw.setPenRadius(self.line_thickness)
         stddraw.setPenColor(self.line_color)
         stddraw.rectangle(preview_box_x, preview_box_y,
                           preview_box_w, preview_box_h)
         stddraw.setPenRadius()

         next_tiles = self.next_tetromino.get_min_bounded_tile_matrix()
         n_rows, n_cols = len(next_tiles), len(next_tiles[0])
         # center the piece within the preview box
         offset_x = (preview_box_w - n_cols) / 2.0
         offset_y = (preview_box_h - n_rows) / 2.0

         # Draw each tile of the next tetromino relative to the preview box
         for r in range(n_rows):
            for c in range(n_cols):
               if next_tiles[r][c] is not None:
                  draw_x = preview_box_x + offset_x + c
                  draw_y = preview_box_y + offset_y + (n_rows - 1 - r) + 0.5

                  tile_to_draw = cp.deepcopy(next_tiles[r][c])
                  tile_to_draw.draw(Point(draw_x, draw_y))
      # draw a box around the game grid
      self.draw_boundaries()
      # show the resulting drawing with a pause duration = 250 ms
      stddraw.show(250)

   # A method for drawing the cells and the lines of the game grid
   def draw_grid(self):
      # for each cell of the game grid
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            # if the current grid cell is occupied by a tile
            if self.tile_matrix[row][col] is not None:
               # draw this tile
               self.tile_matrix[row][col].draw(Point(col, row))
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

   # A method for drawing the boundaries around the game grid
   def draw_boundaries(self):
      # draw a bounding box around the game grid as a rectangle
      stddraw.setPenColor(self.boundary_color)  # using boundary_color
      # set the pen radius as box_thickness (half of this thickness is visible
      # for the bounding box as its lines lie on the boundaries of the canvas)
      stddraw.setPenRadius(self.box_thickness)
      # the coordinates of the bottom left corner of the game grid
      pos_x, pos_y = -0.5, -0.5
      stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
      stddraw.setPenRadius()  # reset the pen radius to its default value

   # A method used checking whether the grid cell with the given row and column
   # indexes is occupied by a tile or not (i.e., empty)
   def is_occupied(self, row, col):
      # considering the newly entered tetrominoes to the game grid that may
      # have tiles with position.y >= grid_height
      if not self.is_inside(row, col):
         return False  # the cell is not occupied as it is outside the grid
      # the cell is occupied by a tile if it is not None
      return self.tile_matrix[row][col] is not None

   # A method for checking whether the cell with the given row and col indexes
   # is inside the game grid or not
   def is_inside(self, row, col):
      if row < 0 or row >= self.grid_height:
         return False
      if col < 0 or col >= self.grid_width:
         return False
      return True

   # A method for check and clear lines if rows are full
   def check_and_clear_lines(self):
      """
      Checks for and clears completed lines from bottom to top
      Shifts the rows above cleared lines down
      Returns number of lines cleared in this step
      """
      lines_cleared = 0
      row = 0
      while row < self.grid_height:
         is_row_full = True

         for col in range(self.grid_width):
            if self.tile_matrix[row][col] is None:
               is_row_full = False
               break # found an empty cell

         if is_row_full:
            lines_cleared +=1
            # row is full, clear it and shift rows above down
            for r_shift in range(row, self.grid_height - 1):
               self.tile_matrix[r_shift] = self.tile_matrix[r_shift + 1].copy()
            # Clear the topmost row
            self.tile_matrix[self.grid_height - 1] = np.full(self.grid_width, None)

         else:
            # row wasn't full, move on the next row up for checking
            row += 1

      return lines_cleared

   # A method that locks the tiles of a landed tetromino on the grid checking
   # if the game is over due to having any tile above the topmost grid row.
   # (This method returns True when the game is over and False otherwise.)
   def update_grid(self, tiles_to_lock, blc_position):
      # necessary for the display method to stop displaying the tetromino
      self.current_tetromino = None
      # lock the tiles of the current tetromino (tiles_to_lock) on the grid
      n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
      for col in range(n_cols):
         for row in range(n_rows):
            # place each tile (occupied cell) onto the game grid
            if tiles_to_lock[row][col] is not None:
               # compute the position of the tile on the game grid
               pos = Point()
               pos.x = blc_position.x + col
               pos.y = blc_position.y + (n_rows - 1) - row
               if self.is_inside(pos.y, pos.x):
                  self.tile_matrix[pos.y][pos.x] = tiles_to_lock[row][col]
               # the game is over if any placed tile is above the game grid
               else:
                  self.game_over = True
      # return the value of the game_over flag
      return self.game_over
