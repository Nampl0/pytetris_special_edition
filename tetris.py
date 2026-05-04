import pygame
import pdb

import random
import math
import block
import constants
import menu
import game_over_menu
import select_menu_speeds
import select_menu_speed_classic
import select_menu_handicap
import select_menu_blockstyle
import select_menu_boardstyle
import high_score
import store
from select_menu_special_block import select_special_blocks
import select_menu_multiplayer
import multiplayer

class Tetris(object):
    """The class with implementation of tetris game logic."""
    def __init__(self,bx,by,mode="classic"):
        """
        Initialize the tetris object.

        Parameters:
            - bx - number of blocks in x
            - by - number of blocks in y
            - mode - game mode
        """
        # Initialize pygame and font if not already initialized
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        self.myfont = pygame.font.SysFont(pygame.font.get_default_font(), constants.FONT_SIZE)
        
        self.blockstyle = "rotate"  # Default blockstyle for all modes
        # Initialize mode-related attributes
        self.mode = mode
        self.spawn_style = "normal"  # Default spawn style
        self.reverse_mode = False    # Explicit initialization
        self.handicap = 0           # Default handicap level
        self.lock_start_time = None # Delay blocks
        self.LOCK_DELAY_MS = constants.LOCK_DELAY_MS  # Delay for block movement
        # Compute the resolution of the play board based on the required number of blocks.
        self.resx = bx * constants.BWIDTH + 2 * constants.BOARD_HEIGHT + constants.BOARD_MARGIN
        self.resy = by * constants.BHEIGHT + 2 * constants.BOARD_HEIGHT + constants.BOARD_MARGIN
        # Add space for the preview box to the total screen width
        self.screen_width = self.resx + constants.PREVIEW_BOX_SIZE + constants.BOARD_PREVIEW_SPACING
        # Store the selected mode
        self.mode = mode
        # Set reverse mode default (must come early!)
        self.reverse_mode = False
        # Prepare the pygame board objects (white lines)
        self.board_up = pygame.Rect(constants.BOARD_MARGIN, constants.BOARD_UP_MARGIN, self.resx - 2 * constants.BOARD_MARGIN, constants.BOARD_HEIGHT)
        self.board_down = pygame.Rect(constants.BOARD_MARGIN, self.resy - constants.BOARD_HEIGHT, self.resx - 2 * constants.BOARD_MARGIN, constants.BOARD_HEIGHT)
        self.board_left = pygame.Rect(3, constants.BOARD_UP_MARGIN, constants.BOARD_MARGIN, self.resy - constants.BOARD_UP_MARGIN)
        self.board_right = pygame.Rect(self.resx - constants.BOARD_MARGIN - 3, constants.BOARD_UP_MARGIN, constants.BOARD_MARGIN, self.resy - constants.BOARD_UP_MARGIN)
        # List of used blocks
        self.blk_list    = []
        # Compute start indexes for tetris blocks
        self.start_x = math.ceil(self.resx/2.0)
        self.start_y = constants.BOARD_UP_MARGIN + constants.BOARD_HEIGHT + constants.BOARD_MARGIN
        # Fix spawn for reverse mode
        if self.reverse_mode:
            self.start_y = self.resy - constants.BOARD_HEIGHT - constants.BOARD_MARGIN
        # After spawn is finalized, initialize handicap
        self.initialize_handicap(self.handicap)
        # Blocka data (shapes and colors). The shape is encoded in the list of [X,Y] points. Each point
        # represents the relative position. The true/false value is used for the configuration of rotation where
        # False means no rotate and True allows the rotation.
        store_data = store.load_store_data()
        selected_blocks = set(store_data.get("selected_blocks", []))
        purchased_blocks = store_data.get("purchased_blocks", {})
        # Only allow blocks with count > 0 for this session
        self.session_special_blocks = [b for b in selected_blocks if purchased_blocks.get(b, 0) > 0]
        # Normal blocks
        self.block_data = [
            ([[0,0],[1,0],[2,0],[3,0]],constants.RED,True),     # I block 
            ([[0,0],[1,0],[0,1],[-1,1]],constants.GREEN,True),  # S block 
            ([[0,0],[1,0],[2,0],[2,1]],constants.BLUE,True),    # J block
            ([[0,0],[0,1],[1,0],[1,1]],constants.ORANGE,False), # O block
            ([[-1,0],[0,0],[0,1],[1,1]],constants.GOLD,True),   # S block
            ([[0,0],[1,0],[2,0],[1,1]],constants.PURPLE,True),  # T block
            ([[0,0],[1,0],[2,0],[0,1]],constants.CYAN,True),    # J block
        ]
        # Special blocks
        if "Eraser Block" in selected_blocks:
            self.block_data.append(([[0,0],[0,1]], constants.WHITE, False))
        if "Builder Block" in selected_blocks:
            self.block_data.append(([[0,0],[0,1]], constants.YELLOW, False))
        if "Dynamite Block" in selected_blocks:
            self.block_data.append(([[-1,2],[2,2],[0,0],[1,0],[0,1],[1,1]], constants.RED, False))
        # Compute the number of blocks. When the number of blocks is even, we can use it directly but 
        # we have to decrese the number of blocks in line by one when the number is odd (because of the used margin).
        self.blocks_in_line = bx if bx%2 == 0 else bx-1
        self.blocks_in_pile = by
        # Initialize the next block with a random block from block_data
        tmp = random.randint(0, len(self.block_data) - 1)
        self.next_block = self.block_data[tmp]
        # Score settings
        self.score = 0
        # Remember the current speed 
        self.speed = 1
        # The score level threshold
        self.score_level = constants.SCORE_LEVEL 


    def apply_action(self):
        """Get the event from the event queue and run the appropriate action."""       
        # Take the event from the event queue.
        for ev in pygame.event.get():
            # Check if the close button was fired.
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_q):
                self.done = True
                self.game_over = True
                return  # Exit immediately to prevent showing game over screen
            # Detect the key evevents for game control.
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_DOWN:
                    if self.reverse_mode:
                        self.active_block.move(0, -constants.BHEIGHT)
                    else:
                        self.active_block.move(0, constants.BHEIGHT)
                if ev.key == pygame.K_LEFT:
                    self.active_block.move(-constants.BWIDTH, 0)
                if ev.key == pygame.K_RIGHT:
                    self.active_block.move(constants.BWIDTH, 0)
                if ev.key == pygame.K_SPACE:
                    special = self.get_special_type(self.active_block)
                    if special == 'eraser':
                        # Create a collision area around the eraser block
                        eraser_area = pygame.Rect(self.active_block.shape[0].x - constants.BWIDTH // 2, self.active_block.shape[0].y - constants.BHEIGHT // 2, constants.BWIDTH * 2, constants.BHEIGHT * 2)
                        # Find all blocks colliding with the eraser area
                        candidates = []
                        for blk in self.blk_list:
                            if blk is self.active_block:
                                continue
                        for rect in blk.shape:
                            if eraser_area.colliderect(rect):
                                candidates.append((rect, blk))
                        
                        # Find the closest block in the shooting direction
                        if candidates:
                            if not self.reverse_mode:
                                target = min(candidates, key=lambda t: abs(t[0].y - eraser_area.y))
                            else:
                                target = min(candidates, key=lambda t: abs(t[0].y - eraser_area.y))
                            if target:
                                rect, blk = target
                                blk.shape.remove(rect)
                                if not blk.has_blocks():
                                    self.blk_list.remove(blk)
                            
                    elif special == 'dynamite':
                        # Get the dynamite block's center position
                        center = self.active_block.shape[3].center  # middle block
                        area = pygame.Rect(
                            center[0] - constants.BWIDTH,
                            center[1] - constants.BHEIGHT,
                            constants.BWIDTH * 3,
                            constants.BHEIGHT * 3
                        )
                        
                        # Find and remove blocks in explosion area
                        blocks_to_remove = []
                        for blk in self.blk_list[:]:
                            if blk is self.active_block:
                                continue
                            for rect in blk.shape[:]:
                                if area.colliderect(rect):
                                    blk.shape.remove(rect)
                            if not blk.has_blocks():
                                blocks_to_remove.append(blk)
                        
                        # Remove empty blocks
                        for blk in blocks_to_remove:
                            self.blk_list.remove(blk)
                        
                        # Remove the dynamite block after use
                        if self.active_block in self.blk_list:
                            self.blk_list.remove(self.active_block)
                        self.new_block = True
                        
                    elif special == 'builder':
                        builder_rect = self.active_block.shape[0]
                        builder_x = builder_rect.x
                        builder_y = builder_rect.y
                        # Find all blocks in the same column (colliding horizontally)
                        candidates = []
                        for blk in self.blk_list:
                            if blk is self.active_block:
                                continue
                            for rect in blk.shape:
                                if rect.colliderect(builder_rect):
                                    candidates.append(rect)
                        # Find the first empty spot in the shooting direction
                        target_y = None
                        if not self.reverse_mode:
                            # Normal mode: find the lowest y above the builder
                            # Get all y's >= builder_y (below or at builder)
                            below = [rect.y for rect in candidates if rect.y > builder_y]
                            if below:
                                # Place new block just above the lowest block below builder
                                target_y = min(below) - constants.BHEIGHT
                            else:
                                # No block below, place at bottom
                                target_y = self.resy - constants.BOARD_HEIGHT - constants.BHEIGHT
                        else:
                            # Reverse mode: find the highest y below the builder
                            above = [rect.y for rect in candidates if rect.y < builder_y]
                            if above:
                                # Place new block just below the highest block above builder
                                target_y = max(above) + constants.BHEIGHT
                            else:
                                # No block above, place at top
                                target_y = self.board_up.bottom
                        # Only place if within board limits and not overlapping another block
                        if target_y is not None:
                            new_rect = pygame.Rect(builder_x, target_y, constants.BWIDTH, constants.BHEIGHT)
                            # Check for line completion after placing the new block
                            self.detect_line()
                            # Check if space is empty
                            overlap = False
                            for blk in self.blk_list:
                                if blk is self.active_block:
                                    continue
                                for rect in blk.shape:
                                    if rect.colliderect(new_rect):
                                        overlap = True
                                        break
                                if overlap:
                                    break
                            if not overlap:
                                from block import Block
                                new_block = Block([[0, 0]], new_rect.x, new_rect.y, self.screen, constants.GRAY, False)
                                self.blk_list.append(new_block)
                    else:
                        # Handle spacebar for normal blocks (rotate or swap)
                        if self.get_special_type(self.active_block) is None:
                            if self.blockstyle == "rotate":
                                self.active_block.rotate()
                            elif self.blockstyle == "swap":
                                self.swap_next_block()
                if ev.key == pygame.K_p:
                    self.pause()
            # Detect if the movement event was fired by the timer.
            if ev.type == constants.TIMER_MOVE_EVENT:
                direction = -constants.BHEIGHT if self.reverse_mode else constants.BHEIGHT
                self.active_block.move(0, direction)
       
    def pause(self):
        """Pause the game and draw the string. This function also calls the flip function which draws the string on the screen."""       
        # Draw the string to the center of the screen.
        self.print_center(["PAUSE","Press \"p\" to continue"])
        pygame.display.flip()
        paused = True
        while paused:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.done = True
                    self.game_over = True
                    return
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_p:
                        paused = False
                        return
                    elif ev.key == pygame.K_q:
                        self.done = True
                        self.game_over = True
                        return
       
    def set_move_timer(self):
        """Setup the move timer."""         
        if self.mode == "classic":
            # Fixed speed for classic mode
            speed = math.floor(constants.MOVE_TICK / self.speed)
        elif self.mode == "escalation":
            # Speed increases with score for escalation mode
            speed = math.floor(constants.MOVE_TICK / self.speed)
        speed = max(1, speed)  # Setup the time to fire the move event. Minimal allowed value is 1
        pygame.time.set_timer(constants.TIMER_MOVE_EVENT, speed)
        # Scale lock delay with speed (higher speed = lower delay)
        self.LOCK_DELAY_MS = max(250, int(constants.LOCK_DELAY_MS / self.speed))
 
    def run(self):
        """Run the main game."""
        # Initialize pygame and screen
        if not hasattr(self, 'screen'):
            self.screen = pygame.display.set_mode((self.screen_width, self.resy))
            pygame.display.set_caption("Tetris")
            
        mode = menu.menu(self.screen)
        if mode == "multi":
            multiplayer_mode = select_menu_multiplayer.select_menu_multiplayer(self.screen)
            if multiplayer_mode == "vs_2p":
                multiplayer.run_vs_2p()
                return
            elif multiplayer_mode == "vs_ai":
                multiplayer.run_vs_ai()
                return
            elif multiplayer_mode == "coop_2p":
                multiplayer.run_coop_2p()
                return
            elif multiplayer_mode == "coop_ai":
                multiplayer.run_coop_ai()
                return
            elif multiplayer_mode == "back":
                return
        elif mode == "single":
            # Define font for menus
            font = pygame.font.SysFont(pygame.font.get_default_font(), constants.FONT_SIZE)
            # Select Speed
            selected_mode = select_menu_speeds.select_menu(self.screen)
            if selected_mode == "classic":
                selected_speed = select_menu_speed_classic.select_speed_classic(self.screen, font)
                self.speed = selected_speed
            elif selected_mode == "escalation":
                self.speed = 1
            # Select Special Blocks
            select_special_blocks(self.screen, self.myfont)
            # Select Space Bar Action (Block Style)
            selected_blockstyle = select_menu_blockstyle.select_blockstyle(self.screen, font)
            self.blockstyle = selected_blockstyle
            # Select Block Spawn
            selected_boardstyle = select_menu_boardstyle.select_boardstyle(self.screen, font)
            self.spawn_style = selected_boardstyle
            if self.spawn_style == "normal":
                # Normal spawn mode
                self.reverse_mode = False
                self.start_x = math.ceil(self.resx / 2.0)
                self.start_y = constants.BOARD_UP_MARGIN + constants.BOARD_HEIGHT + constants.BOARD_MARGIN
            elif self.spawn_style == "reverse":
                # Reverse spawn mode
                self.reverse_mode = True
                self.start_x = math.ceil(self.resx / 2.0)
                # Start above any handicap blocks
                self.start_y = self.resy - constants.BOARD_HEIGHT - constants.BOARD_MARGIN
            # Select Handicap
            selected_handicap = select_menu_handicap.select_handicap(self.screen, font)
            self.handicap = selected_handicap
            self.blk_list = []
            self.initialize_handicap(self.handicap)
            # Final setup
            self.set_move_timer()
            self.done = False
            self.game_over = False
            self.new_block = True
            self.print_status_line()
            # Main game loop
            while not self.done and not self.game_over:
                self.get_block()
                self.game_logic()
                self.draw_game()
            # Handle game over
            if self.game_over:
                # Save score to high scores
                high_score.save_high_score(self.score)
                # Add score to store currency
                store.add_currency(self.score)
                # Optionally show high scores screen
                high_score.show_high_scores(self.screen)
            if game_over_menu.game_over_menu(self.screen):
                self.__init__(16, 30)
                self.run()
        pygame.font.quit()
        pygame.display.quit()
   
    def print_status_line(self):
        """Print the current state line."""
        string = ["SCORE: {0}   SPEED: {1}x".format(self.score,self.speed)]
        self.print_text(string,constants.POINT_MARGIN,constants.POINT_MARGIN)        

    def print_text(self,str_lst,x,y):
        """
        Print the text on the X,Y coordinates. 

        Parameters:
            - str_lst - list of strings to print. Each string is printed on new line.
            - x - X coordinate of the first string
            - y - Y coordinate of the first string
        """
        prev_y = 0
        for string in str_lst:
            size_x,size_y = self.myfont.size(string)
            txt_surf = self.myfont.render(string,False,(255,255,255))
            self.screen.blit(txt_surf,(x,y+prev_y))
            prev_y += size_y 

    def print_center(self,str_list):
        """
        Print the string in the center of the screen.
        
        Parameters:
            - str_lst - list of strings to print. Each string is printed on new line.
        """
        max_xsize = max([tmp[0] for tmp in map(self.myfont.size,str_list)])
        self.print_text(str_list,self.resx/2-max_xsize/2,self.resy/2)

    def block_colides(self):
        """Check if the block colides with any other block. The function returns True if the collision is detected."""         
        for blk in self.blk_list:
            # Check if the block is not the same
            if blk == self.active_block:
                continue 
            # Detect situations
            if(blk.check_collision(self.active_block.shape)):
                return True
        # Check border collisions
        for shape_block in self.active_block.shape:
            if not self.reverse_mode:
                # Normal mode - check bottom border
                if shape_block.y >= self.resy - constants.BOARD_HEIGHT:
                    return True
            else:
                # Reverse mode - check top border
                if shape_block.y < self.board_up.bottom:
                    return True
            # Check side borders
            if (shape_block.x <= constants.BOARD_MARGIN or 
                shape_block.x >= self.resx - constants.BOARD_MARGIN - constants.BWIDTH):
                return True
        return False       

    def game_logic(self):
        """Implementation of the main game logic. This function detects collisions and insertion of new Tetris blocks."""
        # Remember the current configuration and try to apply the action
        self.active_block.backup()
        self.apply_action()
        # Border logic, check if we colide with down border or any other border. This check also includes the detection with other tetris blocks.
        if self.reverse_mode:
            down_board  = self.active_block.check_collision([self.board_up])
        else:
            down_board  = self.active_block.check_collision([self.board_down])
        any_border  = self.active_block.check_collision([self.board_left,self.board_up,self.board_right])
        block_any   = self.block_colides()
        # Restore the configuration if any collision was detected
        if down_board or any_border or block_any:
            self.active_block.restore()
            # Special block collision handling
            special = self.get_special_type(self.active_block)
            if special in ['eraser', 'builder', 'dynamite']:
                if block_any or down_board:
                    if self.active_block in self.blk_list:
                        self.blk_list.remove(self.active_block)
                    self.new_block = True
                    return
        # So far so good, sample the previous state and try to move down (to detect the colision with other block). After that, detect the the insertion of new block. The block new block is inserted if we reached the border or we cannot move down. 
        self.active_block.backup()
        if self.reverse_mode:
            self.active_block.move(0,-constants.BHEIGHT)
        else:
            self.active_block.move(0,constants.BHEIGHT)
        can_move_down = not self.block_colides()  
        self.active_block.restore()
        # Lock delay
        if not can_move_down or down_board:
            if self.lock_start_time is None:
                self.lock_start_time = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.lock_start_time >= self.LOCK_DELAY_MS:
                # We end the game if we are on the respawn and we cannot move --> bang!
                if not can_move_down:
                    if self.reverse_mode:
                        game_over_due_to_spawn = all(
                            shape_block.y >= self.start_y or self.block_colides()
                            for shape_block in self.active_block.shape
                        )
                        if game_over_due_to_spawn:
                            self.game_over = True
                            self.lock_start_time = None
                            return
                    else:
                        if self.start_x == self.active_block.x and self.start_y == self.active_block.y:
                            self.game_over = True
                            self.lock_start_time = None
                            return
                # The new block is inserted if we reached down board or we cannot move down.
                self.new_block = True
                self.detect_line()
                self.lock_start_time = None  # Reset lock timer for next block
        else:
            self.lock_start_time = None  # Reset lock timer if block can move down again
 
    def detect_line(self):
        """Detect if the line is filled. If yes, remove the line and move with remaining building blocks to new positions."""
        lines_cleared = 0
        # Get all possible y coordinates from all blocks
        all_y_coords = set()
        for blk in self.blk_list:
            for shape_block in blk.shape:
                all_y_coords.add(shape_block.y)
        
        # Check each line that has blocks
        for y in sorted(all_y_coords):
            # Count blocks in this line
            blocks_in_line = 0
            for blk in self.blk_list:
                for shape_block in blk.shape:
                    if shape_block.y == y:
                        blocks_in_line += 1
            
            # If line is complete, remove it
            if blocks_in_line >= self.blocks_in_line:
                self.remove_line(y)
                lines_cleared += 1
        
        if lines_cleared > 0:
            self.score += lines_cleared * self.blocks_in_line * constants.POINT_VALUE
            # Escalation logic: speed up if score passes threshold
            if self.mode == "escalation" and self.score > self.score_level:
                self.score_level *= constants.SCORE_LEVEL_RATIO
                self.speed *= constants.GAME_SPEEDUP_RATIO
                self.set_move_timer()

    def remove_line(self,y):
        """Remove the line with given Y coordinates. Blocks below the filled line are untouched. The rest of blocks (yi > y) are moved one level done.      

        Parameters:
            - y - Y coordinate to remove.
        """ 
        # Iterate over all blocks in the list and remove blocks with the Y coordinate.
        for block in self.blk_list:
            block.remove_blocks(y)
        # Setup new block list (not needed blocks are removed)
        self.blk_list = [blk for blk in self.blk_list if blk.has_blocks()]
        #Shift remaining blocks
        for block in self.blk_list:
            new_shape = []
            for shape_block in block.shape:
                if self.reverse_mode:
                    if shape_block.y >= y:
                        shape_block.y -= constants.BHEIGHT  # shift up
                else:
                    if shape_block.y < y:
                        shape_block.y += constants.BHEIGHT  # shift down
                new_shape.append(shape_block)
            block.shape = new_shape

    def get_blocks_in_line(self,y):
        """
        Get the number of shape blocks on the Y coordinate.

        Parameters:
            - y - Y coordinate to scan.
        """
        # Iteraveovel all block's shape list and increment the counter
        # if the shape block equals to the Y coordinate.
        tmp_cnt = 0
        for block in self.blk_list:
            for shape_block in block.shape:
                tmp_cnt += (1 if y == shape_block.y else 0)            
        return tmp_cnt

    def draw_board(self):
        """Draw the white board."""
        pygame.draw.rect(self.screen,constants.WHITE,self.board_up)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_down)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_left)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_right)
        # Update the score         
        self.print_status_line()

    def get_block(self):
        """Generate new block into the game if is required.""" 
        if self.new_block:
            # Filter block_data for available special blocks
            available_blocks = []
            for block_data in self.block_data:
                # Check if this is a special block
                special_type = None
                if block_data[1] == constants.WHITE and not block_data[2] and "Eraser Block" in self.session_special_blocks:
                    special_type = "Eraser Block"
                elif block_data[1] == constants.YELLOW and not block_data[2] and "Builder Block" in self.session_special_blocks:
                    special_type = "Builder Block"
                elif block_data[1] == constants.RED and not block_data[2] and len(block_data[0]) == 6 and "Dynamite Block" in self.session_special_blocks:
                    special_type = "Dynamite Block"
                if special_type:
                    available_blocks.append(block_data)
                elif special_type is None and not (block_data[1] in [constants.WHITE, constants.YELLOW, constants.RED] and not block_data[2]):
                    # It's a normal block, always available
                    available_blocks.append(block_data)
            if not available_blocks:
                # Fallback: only normal blocks
                available_blocks = [b for b in self.block_data if not (b[1] in [constants.WHITE, constants.YELLOW, constants.RED] and not b[2])]
            # Use the current next_block as the active block
            data = self.next_block
            spawn_y = self.start_y
            if self.reverse_mode:
                spawn_y -= constants.BHEIGHT
            self.active_block = block.Block(data[0], self.start_x, spawn_y, self.screen, data[1], data[2])
            # Validate the spawn position
            if self.block_colides():
                self.game_over = True
                return
            self.blk_list.append(self.active_block)
            # Generate a new next block for the preview
            # Only pick from available blocks
            tmp = random.randint(0, len(available_blocks) - 1)
            self.next_block = available_blocks[tmp]
            # If the new active block is a special block, decrement its count
            special = self.get_special_type(self.active_block)
            if special == 'eraser':
                self.use_special_block("Eraser Block")
            elif special == 'builder':
                self.use_special_block("Builder Block")
            elif special == 'dynamite':
                self.use_special_block("Dynamite Block")
            self.new_block = False

    def draw_next_block(self):
        """Draw the next block in the preview box."""
        if self.next_block:
            # Calculate the position to center the block in the preview box
            preview_x = self.resx + constants.BOARD_PREVIEW_SPACING + constants.PREVIEW_BOX_SIZE // 2
            preview_y = constants.BOARD_UP_MARGIN + constants.PREVIEW_BOX_SIZE // 2

            # Adjust offsets for specific blocks (e.g., I and J blocks)
            shape = self.next_block[0]
            if shape == [[0, 0], [1, 0], [2, 0], [3, 0]]:  # I block
                offset_x = -constants.BWIDTH * 1.5  # Shift left to center
                offset_y = -constants.BHEIGHT # Slight vertical adjustment
            elif shape == [[0, 0], [1, 0], [2, 0], [2, 1]]:  # J block
                offset_x = -constants.BWIDTH # Slight horizontal adjustment
                offset_y = -constants.BHEIGHT // 2 # Slight vertical adjustment
            else:
                offset_x = 0
                offset_y = 0

            # Draw each shape block of the next block
            for point in self.next_block[0]:
                block_x = preview_x + point[0] * constants.BWIDTH - constants.BWIDTH // 2
                block_y = preview_y + point[1] * constants.BHEIGHT - constants.BHEIGHT // 2
                # Draw the block
                pygame.draw.rect(self.screen, self.next_block[1], pygame.Rect(block_x, block_y, constants.BWIDTH, constants.BHEIGHT))
                # Draw the mesh around the block
                pygame.draw.rect(self.screen, constants.WHITE, pygame.Rect(block_x, block_y, constants.BWIDTH, constants.BHEIGHT), constants.MESH_WIDTH)

    def initialize_handicap(self, lvl):
        """Initialize the game board with pre-filled rows based on the handicap level."""
        safe_rows = 6  
        if self.reverse_mode:
            max_rows = self.blocks_in_pile - safe_rows
            lvl = min(lvl, max_rows)
        if lvl <= 0:
            return
        # Calculate starting position aligned with game grid
        left_x = self.board_left.right + 1
        for row in range(lvl):
            for col in range(self.blocks_in_line):
                if random.choice([True, False]):
                    continue
                block_x = left_x + col * constants.BWIDTH
                if self.reverse_mode:
                    # Top border is at self.board_up.bottom
                    block_y = self.board_up.bottom + row * constants.BHEIGHT
                else:
                    # Bottom border is at self.resy - constants.BOARD_HEIGHT
                    block_y = self.resy - constants.BOARD_HEIGHT - (row + 1) * constants.BHEIGHT
                new_block = block.Block([[0, 0]], block_x, block_y, self.screen, constants.GRAY, False)
                self.blk_list.append(new_block)
    
    def swap_next_block(self):
        """Swaps the current falling block with the next one in the queue."""
        # Remove the current active block from the block list
        if self.active_block in self.blk_list:
            self.blk_list.remove(self.active_block)
        # Save the current active block to be used as next
        current_x = self.active_block.x
        current_y = self.active_block.y
        # Swap the next block with the active block
        random_block_data = random.choice(self.block_data)
        self.active_block = block.Block(random_block_data[0], current_x, current_y, self.screen, random_block_data[1], random_block_data[2])
        # Add the new active block to the block list
        self.blk_list.append(self.active_block)

    def select_block_spawn(self):
        """Select where the block would spawn."""
        # Call the select_menu_boardstyle to choose the spawn location
        selected_spawn = select_menu_boardstyle.select_boardstyle(self.screen, self.myfont)
        self.spawn_style = selected_spawn
        if self.spawn_style == "normal":
        # Spawn from the top
            self.reverse_mode = False
            self.start_x = math.ceil(self.resx / 2.0)
            self.start_y = constants.BOARD_UP_MARGIN + constants.BOARD_HEIGHT + constants.BOARD_MARGIN
        elif self.spawn_style == "reverse":
        # Spawn from the bottom
            self.reverse_mode = True
            self.start_x = math.ceil(self.resx / 2.0)
            # Start above any handicap blocks
            self.start_y = (constants.BOARD_UP_MARGIN + constants.BOARD_HEIGHT + (self.handicap * constants.BHEIGHT) + constants.BOARD_MARGIN)
        # Re-initialize handicap blocks with correct mode
        self.initialize_handicap(self.handicap)

    def get_special_type(self, blk):
        """Return 'eraser', 'builder', 'dynamite', or None for a block."""
        # Eraser: white, 2 blocks, no rotate
        if blk.color == constants.WHITE and not blk.rotate_en and len(blk.shape) == 2:
            return 'eraser'
        # Builder: yellow, 2 blocks, no rotate
        if blk.color == constants.YELLOW and not blk.rotate_en and len(blk.shape) == 2:
            return 'builder'
        # Dynamite: red, 6 blocks, no rotate
        if (blk.color == constants.RED and not blk.rotate_en and len(blk.shape) == 6 and sorted([tuple(p) for p in blk.shape]) == sorted([(-1,0),(0,0),(1,0),(2,0),(0,1),(1,1)])):
            return 'dynamite'
        return None
    
    def use_special_block(self, block_name):
        # Remove from session list and decrement in store
        if block_name in self.session_special_blocks:
            self.session_special_blocks.remove(block_name)
            data = store.load_store_data()
            if data["purchased_blocks"].get(block_name, 0) > 0:
                data["purchased_blocks"][block_name] -= 1
                store.save_store_data(data)

    def end_session(self):
        data = store.load_store_data()
        for block_name in self.session_special_blocks:
            if data["purchased_blocks"].get(block_name, 0) > 0:
                data["purchased_blocks"][block_name] -= 1
        store.save_store_data(data)
        self.session_special_blocks = []

    def draw_game(self):
        """Draw the game screen."""              
        # Clean the screen, draw the board and draw
        # all tetris blocks
        self.screen.fill(constants.BLACK)
        self.draw_board()
        for blk in self.blk_list:
            blk.draw()
            
        # Draw the preview box (placeholder)
        preview_box_rect = pygame.Rect(self.resx + constants.BOARD_PREVIEW_SPACING,
                                     constants.BOARD_UP_MARGIN,
                                     constants.PREVIEW_BOX_SIZE,
                                     constants.PREVIEW_BOX_SIZE)     
        pygame.draw.rect(self.screen, constants.WHITE, preview_box_rect, 2)
        next_text_x = self.resx + constants.BOARD_PREVIEW_SPACING + constants.PREVIEW_BOX_SIZE // 2
        next_text_y = constants.BOARD_UP_MARGIN + constants.PREVIEW_BOX_SIZE // 5 - self.myfont.size("NEXT")[1] // 2
        self.print_text(["NEXT"], next_text_x - self.myfont.size("NEXT")[0] // 2, next_text_y)
        # Draw the next block inside the preview box
        self.draw_next_block()
        # Draw the screen buffer
        pygame.display.flip()

if __name__ == "__main__":
    Tetris(16,30).run()
    pygame.quit()