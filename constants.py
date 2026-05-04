from pygame.locals import *

# Configuration of building shape block
# Width of the shape block
BWIDTH     = 20
# Height of the shape block
BHEIGHT    = 20
# Width of the line around the block
MESH_WIDTH = 1

# Configuration of the player board
# Board line height
BOARD_HEIGHT     = 9
# Margin of upper line (for score)
BOARD_UP_MARGIN  = 40
# Margins around all lines
BOARD_MARGIN     = 10
# Next block preview margin from the right side
NEXT_BLOCK_MARGIN = 5
# Spacing between the game board and the preview box
BOARD_PREVIEW_SPACING = 20
# Size of the next block preview box
PREVIEW_BOX_SIZE = 150
# Width of the game board (number of blocks in x * block width)
GAME_BOARD_WIDTH = 16 * BWIDTH  # Adjust 16 to match the number of blocks in the x direction

# Color declarations in the RGB notation
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
ORANGE = (255,69,0)
GOLD = (255,125,0)
PURPLE = (128,0,128)
CYAN = (0,255,255) 
BLACK = (0,0,0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Timing constraints
# Time for the generation of TIME_MOVE_EVENT (ms)
MOVE_TICK          = 1000
# Allocated number for the move dowon event
TIMER_MOVE_EVENT   = USEREVENT+1
# Time for players to move the block
LOCK_DELAY_MS = 1000
# Speed up ratio of the game (integer values)
GAME_SPEEDUP_RATIO = 1.5
# Score LEVEL - first threshold of the score
SCORE_LEVEL        = 2000
# Score level ratio
SCORE_LEVEL_RATIO  = 2 

# Configuration of score
# Number of points for one building block
POINT_VALUE       = 100
# Margin of the SCORE string
POINT_MARGIN      = 10

# Font size for all strings (score, pause, game over)
FONT_SIZE           = 25
