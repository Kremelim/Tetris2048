import lib.stddraw as stddraw  # used for drawing the tiles to display them
from lib.color import Color  # used for coloring the tiles

# A class for modeling numbered tiles as in 2048
# Format: {number: (background_color, foreground_color, box_color)}
COLOR_MAP = {
    2:    (Color(238, 228, 218), Color(119, 110, 101), Color(187, 173, 160)), # bg, fg, box
    4:    (Color(237, 224, 200), Color(119, 110, 101), Color(187, 173, 160)),
    8:    (Color(242, 177, 121), Color(249, 246, 242), Color(210, 155, 103)), # White text starts here
    16:   (Color(245, 149, 99),  Color(249, 246, 242), Color(215, 129, 80)),
    32:   (Color(246, 124, 95),  Color(249, 246, 242), Color(216, 105, 76)),
    64:   (Color(246, 94, 59),   Color(249, 246, 242), Color(216, 78, 41)),
    128:  (Color(237, 207, 114), Color(249, 246, 242), Color(220, 180, 80)),
    256:  (Color(237, 204, 97),  Color(249, 246, 242), Color(220, 177, 65)),
    512:  (Color(237, 200, 80),  Color(249, 246, 242), Color(220, 173, 48)),
    1024: (Color(237, 197, 63),  Color(249, 246, 242), Color(220, 170, 30)),
    2048: (Color(237, 194, 46),  Color(249, 246, 242), Color(220, 167, 15)),
    # Add more entries as needed (4096, 8192...)
    # A default for numbers not explicitly listed (e.g., > 2048)
    'default': (Color(60, 58, 50), Color(249, 246, 242), Color(30, 28, 20))
}
class Tile:
   # Class variables shared among all Tile objects
   # ---------------------------------------------------------------------------
   # the value of the boundary thickness (for the boxes around the tiles)
   boundary_thickness = 0.004
   # font family and font size used for displaying the tile number
   font_family, font_size = "Arial", 14

   # A constructor that creates a tile with 2 as the number on it
   def _init_(self, number= 2):
      # set the number on this tile
      self.number = number
      # set the colors of this tile
      self.background_color = None  # background (tile) color
      self.foreground_color = None  # foreground (number) color
      self.box_color = None # box (boundary) color
      self.update_colors()


   def update_colors(self):
      """Sets the tile's colors based on its current number using COLOR_MAP."""
      # Get the tuple of colors for the number, or use the default
      colors = COLOR_MAP.get(self.number, COLOR_MAP['default'])
      self.background_color = colors[0]  # First color is background
      self.foreground_color = colors[1]  # Second color is foreground (text)
      self.box_color = colors[2]  # Third color is box boundary

      # --- Optional: Adjust font size based on number magnitude ---
      if self.number >= 1024:
         self.current_font_size = 10  # Use an instance variable for font size
      elif self.number >= 128:
         self.current_font_size = 12
      else:
         self.current_font_size = 14


   def update_number_and_color(self, new_number):
      """Updates the tile's number and its corresponding colors."""
      self.number = new_number
      self.update_colors()  # Re-calculate colors and font size

   # A method for drawing this tile at a given position with a given length
   def draw(self, position, length=1):  # length defaults to 1
      # draw the tile as a filled square
      stddraw.setPenColor(self.background_color)
      stddraw.filledSquare(position.x, position.y, length / 2)
      # draw the bounding box around the tile as a square
      stddraw.setPenColor(self.box_color)
      stddraw.setPenRadius(Tile.boundary_thickness)
      stddraw.square(position.x, position.y, length / 2)
      stddraw.setPenRadius()  # reset the pen radius to its default value
      # draw the number on the tile
      stddraw.setPenColor(self.foreground_color)
      stddraw.setFontFamily(Tile.font_family)
      stddraw.setFontSize(Tile.font_size)
      stddraw.text(position.x, position.y, str(self.number))
