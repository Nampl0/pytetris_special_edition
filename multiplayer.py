import pygame
import constants
from tetris import Tetris
from tetris_ai import TetrisAI
import block
import random
import math

def run_vs_2p():
    """VS 2P: Two human players, side by side."""
    _run_dual_boards(human1=True, human2=True)

def run_vs_ai():
    """VS AI: Player 1 (human) vs Player 2 (AI)."""
    _run_dual_boards(human1=True, human2=False)

def run_coop_2p():
    """Co-op 2P: Two humans play in the same large board."""
    _run_shared_board(human1=True, human2=True)

def run_coop_ai():
    """Co-op AI: Player 1 (human) and Player 2 (AI), both play together in a large board."""
    _run_shared_board(human1=True, human2=False)

def _run_shared_board(human1=True, human2=True):
    """Run co-op mode with a single large shared board."""
    pygame.init()
    pygame.font.init()
    
    # Create a larger board for co-op
    board_width = 24  # Wider board for two players
    board_height = 30
    
    # Calculate screen dimensions
    screen_width = board_width * constants.BWIDTH + 2 * constants.BOARD_HEIGHT + constants.BOARD_MARGIN + constants.PREVIEW_BOX_SIZE + constants.BOARD_PREVIEW_SPACING
    screen_height = board_height * constants.BHEIGHT + 2 * constants.BOARD_HEIGHT + constants.BOARD_MARGIN
    
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tetris Co-op")
    
    # Create a single Tetris instance for the shared board
    shared_tetris = Tetris(board_width, board_height)
    shared_tetris.screen = screen
    
    # Initialize the shared game
    shared_tetris.new_block = True
    shared_tetris.done = False
    shared_tetris.game_over = False
    shared_tetris.handicap = 0
    shared_tetris.score = 0
    shared_tetris.speed = 1
    shared_tetris.blk_list = []
    shared_tetris.initialize_handicap(0)
    shared_tetris.set_move_timer()
    
    # Create two active blocks (one for each player)
    shared_tetris.active_block1 = None
    shared_tetris.active_block2 = None
    shared_tetris.new_block1 = True
    shared_tetris.new_block2 = True
    
    # Controls
    controls1 = {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "down": pygame.K_s,
        "pause": pygame.K_e,
        "action": pygame.K_w,      # rotate/swap/special
    }
    controls2 = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "down": pygame.K_DOWN,
        "pause": pygame.K_p,
        "action": pygame.K_SPACE,  # rotate/swap/special
    }
    
    # Spawn positions for each player (left and right sides of the board)
    spawn_x1 = math.ceil(shared_tetris.resx / 4.0)  # Left side
    spawn_x2 = math.ceil(3 * shared_tetris.resx / 4.0)  # Right side
    spawn_y = shared_tetris.start_y
    
    # If AI, create AI instance for player 2
    ai2 = TetrisAI(shared_tetris) if not human2 else None
    
    # Get initial blocks
    _get_player_block(shared_tetris, 1, spawn_x1, spawn_y)
    _get_player_block(shared_tetris, 2, spawn_x2, spawn_y)
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            if event.type == pygame.KEYDOWN:
                # Player 1 controls
                if human1 and not shared_tetris.game_over and shared_tetris.active_block1:
                    if event.key == controls1["left"]:
                        shared_tetris.active_block1.move(-constants.BWIDTH, 0)
                    elif event.key == controls1["right"]:
                        shared_tetris.active_block1.move(constants.BWIDTH, 0)
                    elif event.key == controls1["down"]:
                        if shared_tetris.reverse_mode:
                            shared_tetris.active_block1.move(0, -constants.BHEIGHT)
                        else:
                            shared_tetris.active_block1.move(0, constants.BHEIGHT)
                    elif event.key == controls1["pause"]:
                        shared_tetris.pause()
                    elif event.key == controls1["action"]:
                        _handle_player_action(shared_tetris, shared_tetris.active_block1)
                
                # Player 2 controls
                if human2 and not shared_tetris.game_over and shared_tetris.active_block2:
                    if event.key == controls2["left"]:
                        shared_tetris.active_block2.move(-constants.BWIDTH, 0)
                    elif event.key == controls2["right"]:
                        shared_tetris.active_block2.move(constants.BWIDTH, 0)
                    elif event.key == controls2["down"]:
                        if shared_tetris.reverse_mode:
                            shared_tetris.active_block2.move(0, -constants.BHEIGHT)
                        else:
                            shared_tetris.active_block2.move(0, constants.BHEIGHT)
                    elif event.key == controls2["pause"]:
                        shared_tetris.pause()
                    elif event.key == controls2["action"]:
                        _handle_player_action(shared_tetris, shared_tetris.active_block2)
        
        # Handle timer events for both players
        if not shared_tetris.game_over:
            for ev in pygame.event.get():
                if ev.type == constants.TIMER_MOVE_EVENT:
                    direction = -constants.BHEIGHT if shared_tetris.reverse_mode else constants.BHEIGHT
                    if shared_tetris.active_block1:
                        shared_tetris.active_block1.move(0, direction)
                    if shared_tetris.active_block2:
                        shared_tetris.active_block2.move(0, direction)
        
        # Game logic for both players
        if not shared_tetris.game_over:
            # Get new blocks if needed
            if shared_tetris.new_block1:
                _get_player_block(shared_tetris, 1, spawn_x1, spawn_y)
            if shared_tetris.new_block2:
                _get_player_block(shared_tetris, 2, spawn_x2, spawn_y)
            
            # Game logic for both active blocks
            _game_logic_shared(shared_tetris)
            
            # AI move for player 2 if applicable
            if not human2 and shared_tetris.active_block2:
                ai2.play_step()
        
        # Draw the shared board
        _draw_shared_game(shared_tetris)
        
        # Check for game over
        if shared_tetris.game_over:
            running = False
        
        clock.tick(30)
    
    pygame.quit()

def _get_player_block(tetris, player_num, spawn_x, spawn_y):
    """Get a new block for a specific player."""
    # Filter block_data for available special blocks
    available_blocks = []
    for block_data in tetris.block_data:
        # Check if this is a special block
        special_type = None
        if block_data[1] == constants.WHITE and not block_data[2] and "Eraser Block" in tetris.session_special_blocks:
            special_type = "Eraser Block"
        elif block_data[1] == constants.YELLOW and not block_data[2] and "Builder Block" in tetris.session_special_blocks:
            special_type = "Builder Block"
        elif block_data[1] == constants.RED and not block_data[2] and len(block_data[0]) == 6 and "Dynamite Block" in tetris.session_special_blocks:
            special_type = "Dynamite Block"
        if special_type:
            available_blocks.append(block_data)
        elif special_type is None and not (block_data[1] in [constants.WHITE, constants.YELLOW, constants.RED] and not block_data[2]):
            # It's a normal block, always available
            available_blocks.append(block_data)
    
    if not available_blocks:
        # Fallback: only normal blocks
        available_blocks = [b for b in tetris.block_data if not (b[1] in [constants.WHITE, constants.YELLOW, constants.RED] and not b[2])]
    
    # Use a random block
    data = random.choice(available_blocks)
    spawn_y_adjusted = spawn_y
    if tetris.reverse_mode:
        spawn_y_adjusted -= constants.BHEIGHT
    
    new_block = block.Block(data[0], spawn_x, spawn_y_adjusted, tetris.screen, data[1], data[2])
    
    # Validate spawn position
    if _block_collides_shared(tetris, new_block):
        tetris.game_over = True
        return
    
    tetris.blk_list.append(new_block)
    
    # Assign to the appropriate player
    if player_num == 1:
        tetris.active_block1 = new_block
        tetris.new_block1 = False
    else:
        tetris.active_block2 = new_block
        tetris.new_block2 = False
    
    # Handle special block usage
    special = tetris.get_special_type(new_block)
    if special == 'eraser':
        tetris.use_special_block("Eraser Block")
    elif special == 'builder':
        tetris.use_special_block("Builder Block")
    elif special == 'dynamite':
        tetris.use_special_block("Dynamite Block")

def _handle_player_action(tetris, active_block):
    """Handle player action (rotate/swap/special) for a specific block."""
    special = tetris.get_special_type(active_block)
    if special == 'eraser':
        # Eraser logic
        eraser_rect = active_block.shape[0]
        eraser_y = eraser_rect.y
        candidates = []
        for blk in tetris.blk_list:
            if blk is active_block:
                continue
            for rect in blk.shape:
                if rect.colliderect(eraser_rect):
                    candidates.append((rect, blk))
        target = None
        if not tetris.reverse_mode:
            above = [(rect, blk) for rect, blk in candidates if rect.y < eraser_y]
            if above:
                target = max(above, key=lambda t: t[0].y)
        else:
            below = [(rect, blk) for rect, blk in candidates if rect.y > eraser_y]
            if below:
                target = min(below, key=lambda t: t[0].y)
        if target:
            rect, blk = target
            blk.shape.remove(rect)
            if not blk.has_blocks():
                tetris.blk_list.remove(blk)
    elif special == 'builder':
        # Builder logic
        builder_rect = active_block.shape[0]
        builder_x = builder_rect.x
        builder_y = builder_rect.y
        candidates = []
        for blk in tetris.blk_list:
            if blk is active_block:
                continue
            for rect in blk.shape:
                if rect.colliderect(builder_rect):
                    candidates.append(rect)
        target_y = None
        if not tetris.reverse_mode:
            below = [rect.y for rect in candidates if rect.y > builder_y]
            if below:
                target_y = min(below) - constants.BHEIGHT
            else:
                target_y = tetris.resy - constants.BOARD_HEIGHT - constants.BHEIGHT
        else:
            above = [rect.y for rect in candidates if rect.y < builder_y]
            if above:
                target_y = max(above) + constants.BHEIGHT
            else:
                target_y = tetris.board_up.bottom
        if target_y is not None:
            new_rect = pygame.Rect(builder_x, target_y, constants.BWIDTH, constants.BHEIGHT)
            overlap = False
            for blk in tetris.blk_list:
                if blk is active_block:
                    continue
                for rect in blk.shape:
                    if rect.colliderect(new_rect):
                        overlap = True
                        break
                if overlap:
                    break
            if not overlap:
                tetris.blk_list.append(block.Block([[0, 0]], new_rect.x, new_rect.y, tetris.screen, constants.GRAY, False))
                tetris.detect_line()
    elif special == 'dynamite':
        # Dynamite logic
        center = active_block.shape[3].center
        area = pygame.Rect(
            center[0] - constants.BWIDTH,
            center[1] - constants.BHEIGHT,
            constants.BWIDTH * 3,
            constants.BHEIGHT * 3
        )
        blocks_to_remove = []
        for blk in tetris.blk_list[:]:
            if blk is active_block:
                continue
            for rect in blk.shape[:]:
                if area.colliderect(rect):
                    blk.shape.remove(rect)
            if not blk.has_blocks():
                blocks_to_remove.append(blk)
        for blk in blocks_to_remove:
            tetris.blk_list.remove(blk)
        if active_block in tetris.blk_list:
            tetris.blk_list.remove(active_block)
        if active_block == tetris.active_block1:
            tetris.new_block1 = True
        else:
            tetris.new_block2 = True
    else:
        # Normal block action
        if tetris.blockstyle == "rotate":
            active_block.rotate()
        elif tetris.blockstyle == "swap":
            _swap_next_block_shared(tetris, active_block)

def _block_collides_shared(tetris, block):
    """Check if a block collides with any other block or borders."""
    for blk in tetris.blk_list:
        if blk == block:
            continue
        if blk.check_collision(block.shape):
            return True
    
    # Check border collisions
    for shape_block in block.shape:
        if not tetris.reverse_mode:
            if shape_block.y >= tetris.resy - constants.BOARD_HEIGHT:
                return True
        else:
            if shape_block.y < tetris.board_up.bottom:
                return True
        if (shape_block.x <= constants.BOARD_MARGIN or 
            shape_block.x >= tetris.resx - constants.BOARD_MARGIN - constants.BWIDTH):
            return True
    return False

def _game_logic_shared(tetris):
    """Game logic for the shared board with two active blocks."""
    # Handle both active blocks
    for active_block in [tetris.active_block1, tetris.active_block2]:
        if not active_block:
            continue
            
        # Remember current configuration
        active_block.backup()
        
        # Border logic
        if tetris.reverse_mode:
            down_board = active_block.check_collision([tetris.board_up])
        else:
            down_board = active_block.check_collision([tetris.board_down])
        any_border = active_block.check_collision([tetris.board_left, tetris.board_up, tetris.board_right])
        block_any = _block_collides_shared(tetris, active_block)
        
        # Restore if collision detected
        if down_board or any_border or block_any:
            active_block.restore()
            special = tetris.get_special_type(active_block)
            if special in ['eraser', 'builder', 'dynamite']:
                if block_any or down_board:
                    if active_block in tetris.blk_list:
                        tetris.blk_list.remove(active_block)
                    if active_block == tetris.active_block1:
                        tetris.new_block1 = True
                    else:
                        tetris.new_block2 = True
                    continue
        
        # Try to move down
        active_block.backup()
        if tetris.reverse_mode:
            active_block.move(0, -constants.BHEIGHT)
        else:
            active_block.move(0, constants.BHEIGHT)
        can_move_down = not _block_collides_shared(tetris, active_block)
        active_block.restore()
        
        # Lock delay logic
        if not can_move_down or down_board:
            if tetris.lock_start_time is None:
                tetris.lock_start_time = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - tetris.lock_start_time >= tetris.LOCK_DELAY_MS:
                # Check for game over
                if not can_move_down:
                    if tetris.reverse_mode:
                        game_over_due_to_spawn = all(
                            shape_block.y >= tetris.start_y or _block_collides_shared(tetris, active_block)
                            for shape_block in active_block.shape
                        )
                        if game_over_due_to_spawn:
                            tetris.game_over = True
                            tetris.lock_start_time = None
                            return
                    else:
                        if (tetris.start_x == active_block.x and tetris.start_y == active_block.y):
                            tetris.game_over = True
                            tetris.lock_start_time = None
                            return
                
                # Request new block
                if active_block == tetris.active_block1:
                    tetris.new_block1 = True
                else:
                    tetris.new_block2 = True
                tetris.detect_line()
                tetris.lock_start_time = None
        else:
            tetris.lock_start_time = None

def _swap_next_block_shared(tetris, active_block):
    """Swap the current falling block with a new random one."""
    if active_block in tetris.blk_list:
        tetris.blk_list.remove(active_block)
    
    current_x = active_block.x
    current_y = active_block.y
    
    # Get a random block
    random_block_data = random.choice(tetris.block_data)
    new_block = block.Block(random_block_data[0], current_x, current_y, tetris.screen, random_block_data[1], random_block_data[2])
    
    tetris.blk_list.append(new_block)
    
    # Update the appropriate active block reference
    if active_block == tetris.active_block1:
        tetris.active_block1 = new_block
    else:
        tetris.active_block2 = new_block

def _draw_shared_game(tetris):
    """Draw the shared game board."""
    # Clean the screen
    tetris.screen.fill(constants.BLACK)
    
    # Draw the board
    tetris.draw_board()
    
    # Draw all blocks
    for blk in tetris.blk_list:
        blk.draw()
    
    # Draw the preview box
    preview_box_rect = pygame.Rect(tetris.resx + constants.BOARD_PREVIEW_SPACING,
                                 constants.BOARD_UP_MARGIN,
                                 constants.PREVIEW_BOX_SIZE,
                                 constants.PREVIEW_BOX_SIZE)
    pygame.draw.rect(tetris.screen, constants.WHITE, preview_box_rect, 2)
    
    # Draw "NEXT" text
    next_text_x = tetris.resx + constants.BOARD_PREVIEW_SPACING + constants.PREVIEW_BOX_SIZE // 2
    next_text_y = constants.BOARD_UP_MARGIN + constants.PREVIEW_BOX_SIZE // 5 - tetris.myfont.size("NEXT")[1] // 2
    tetris.print_text(["NEXT"], next_text_x - tetris.myfont.size("NEXT")[0] // 2, next_text_y)
    
    # Draw the next block (placeholder - could be improved to show both players' next blocks)
    tetris.draw_next_block()
    
    # Draw player indicators
    if tetris.active_block1:
        # Draw player 1 indicator (left side)
        tetris.print_text(["P1"], 10, 10)
    if tetris.active_block2:
        # Draw player 2 indicator (right side)
        tetris.print_text(["P2"], tetris.resx - 30, 10)
    
    pygame.display.flip()

def _run_dual_boards(human1=True, human2=True, coop=False, shared_board=False):
    pygame.init()
    pygame.font.init()
    board_width = 16
    board_height = 30

    single_resx = board_width * constants.BWIDTH + 2 * constants.BOARD_HEIGHT + constants.BOARD_MARGIN + constants.PREVIEW_BOX_SIZE + constants.BOARD_PREVIEW_SPACING
    single_resy = board_height * constants.BHEIGHT + 2 * constants.BOARD_HEIGHT + constants.BOARD_MARGIN
    screen_width = single_resx * 2 + 40  # 40px gap between boards
    screen_height = single_resy

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tetris Multiplayer")

    # Create two Tetris instances
    tetris1 = Tetris(board_width, board_height)
    tetris2 = Tetris(board_width, board_height)

    tetris1.screen = screen.subsurface((0, 0, single_resx, single_resy))
    tetris2.screen = screen.subsurface((single_resx + 40, 0, single_resx, single_resy))

    # Properly initialize both games (fixes AttributeError: 'Tetris' object has no attribute 'new_block')
    for t in (tetris1, tetris2):
        t.new_block = True
        t.done = False
        t.game_over = False
        t.handicap = 0
        t.score = 0
        t.speed = 1
        t.blk_list = []
        t.initialize_handicap(0)
        t.set_move_timer()

    # Controls
    controls1 = {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "down": pygame.K_s,
        "pause": pygame.K_e,
        "action": pygame.K_w,      # rotate/swap/special
    }
    controls2 = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "down": pygame.K_DOWN,
        "pause": pygame.K_p,
        "action": pygame.K_SPACE,  # rotate/swap/special
    }

    # If AI, create AI instance for player 2
    ai2 = TetrisAI(tetris2) if not human2 else None
    tetris1.get_block()
    tetris2.get_block()

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                # Player 1 controls
                if human1 and not tetris1.game_over:
                    if event.key == controls1["left"]:
                        tetris1.active_block.move(-constants.BWIDTH, 0)
                    elif event.key == controls1["right"]:
                        tetris1.active_block.move(constants.BWIDTH, 0)
                    elif event.key == controls1["down"]:
                        if tetris1.reverse_mode:
                            tetris1.active_block.move(0, -constants.BHEIGHT)
                        else:
                            tetris1.active_block.move(0, constants.BHEIGHT)
                    elif event.key == controls1["pause"]:
                        tetris1.pause()
                    elif event.key == controls1["action"]:
                        special = tetris1.get_special_type(tetris1.active_block)
                        if special == 'eraser':
                            eraser_rect = tetris1.active_block.shape[0]
                            eraser_y = eraser_rect.y
                            candidates = []
                            for blk in tetris1.blk_list:
                                if blk is tetris1.active_block:
                                    continue
                                for rect in blk.shape:
                                    if rect.colliderect(eraser_rect):
                                        candidates.append((rect, blk))
                            target = None
                            if not tetris1.reverse_mode:
                                above = [(rect, blk) for rect, blk in candidates if rect.y < eraser_y]
                                if above:
                                    target = max(above, key=lambda t: t[0].y)
                            else:
                                below = [(rect, blk) for rect, blk in candidates if rect.y > eraser_y]
                                if below:
                                    target = min(below, key=lambda t: t[0].y)
                            if target:
                                rect, blk = target
                                blk.shape.remove(rect)
                                if not blk.has_blocks():
                                    tetris1.blk_list.remove(blk)
                        elif special == 'builder':
                            builder_rect = tetris1.active_block.shape[0]
                            builder_x = builder_rect.x
                            builder_y = builder_rect.y
                            candidates = []
                            for blk in tetris1.blk_list:
                                if blk is tetris1.active_block:
                                    continue
                                for rect in blk.shape:
                                    if rect.colliderect(builder_rect):
                                        candidates.append(rect)
                            target_y = None
                            if not tetris1.reverse_mode:
                                below = [rect.y for rect in candidates if rect.y > builder_y]
                                if below:
                                    target_y = min(below) - constants.BHEIGHT
                                else:
                                    target_y = tetris1.resy - constants.BOARD_HEIGHT - constants.BHEIGHT
                            else:
                                above = [rect.y for rect in candidates if rect.y < builder_y]
                                if above:
                                    target_y = max(above) + constants.BHEIGHT
                                else:
                                    target_y = tetris1.board_up.bottom
                            if target_y is not None:
                                new_rect = pygame.Rect(
                                    builder_x,
                                    target_y,
                                    constants.BWIDTH,
                                    constants.BHEIGHT
                                )
                                overlap = False
                                for blk in tetris1.blk_list:
                                    if blk is tetris1.active_block:
                                        continue
                                    for rect in blk.shape:
                                        if rect.colliderect(new_rect):
                                            overlap = True
                                            break
                                    if overlap:
                                        break
                                if not overlap:
                                    from block import Block
                                    tetris1.blk_list.append(Block([[0, 0]], new_rect.x, new_rect.y, tetris1.screen, constants.GRAY, False))
                        elif special == 'dynamite':
                            pass
                        else:
                            if tetris1.blockstyle == "rotate":
                                tetris1.active_block.rotate()
                            elif tetris1.blockstyle == "swap":
                                tetris1.swap_next_block()

                # Player 2 controls
                if human2 and not tetris2.game_over:
                    if event.key == controls2["left"]:
                        tetris2.active_block.move(-constants.BWIDTH, 0)
                    elif event.key == controls2["right"]:
                        tetris2.active_block.move(constants.BWIDTH, 0)
                    elif event.key == controls2["down"]:
                        if tetris2.reverse_mode:
                            tetris2.active_block.move(0, -constants.BHEIGHT)
                        else:
                            tetris2.active_block.move(0, constants.BHEIGHT)
                    elif event.key == controls2["pause"]:
                        tetris2.pause()
                    elif event.key == controls2["action"]:
                        special = tetris2.get_special_type(tetris2.active_block)
                        if special == 'eraser':
                            eraser_rect = tetris2.active_block.shape[0]
                            eraser_y = eraser_rect.y
                            candidates = []
                            for blk in tetris2.blk_list:
                                if blk is tetris2.active_block:
                                    continue
                                for rect in blk.shape:
                                    if rect.colliderect(eraser_rect):
                                        candidates.append((rect, blk))
                            target = None
                            if not tetris2.reverse_mode:
                                above = [(rect, blk) for rect, blk in candidates if rect.y < eraser_y]
                                if above:
                                    target = max(above, key=lambda t: t[0].y)
                            else:
                                below = [(rect, blk) for rect, blk in candidates if rect.y > eraser_y]
                                if below:
                                    target = min(below, key=lambda t: t[0].y)
                            if target:
                                rect, blk = target
                                blk.shape.remove(rect)
                                if not blk.has_blocks():
                                    tetris2.blk_list.remove(blk)
                        elif special == 'builder':
                            builder_rect = tetris2.active_block.shape[0]
                            builder_x = builder_rect.x
                            builder_y = builder_rect.y
                            candidates = []
                            for blk in tetris2.blk_list:
                                if blk is tetris2.active_block:
                                    continue
                                for rect in blk.shape:
                                    if rect.colliderect(builder_rect):
                                        candidates.append(rect)
                            target_y = None
                            if not tetris2.reverse_mode:
                                below = [rect.y for rect in candidates if rect.y > builder_y]
                                if below:
                                    target_y = min(below) - constants.BHEIGHT
                                else:
                                    target_y = tetris2.resy - constants.BOARD_HEIGHT - constants.BHEIGHT
                            else:
                                above = [rect.y for rect in candidates if rect.y < builder_y]
                                if above:
                                    target_y = max(above) + constants.BHEIGHT
                                else:
                                    target_y = tetris2.board_up.bottom
                            if target_y is not None:
                                new_rect = pygame.Rect(
                                    builder_x,
                                    target_y,
                                    constants.BWIDTH,
                                    constants.BHEIGHT
                                )
                                overlap = False
                                for blk in tetris2.blk_list:
                                    if blk is tetris2.active_block:
                                        continue
                                    for rect in blk.shape:
                                        if rect.colliderect(new_rect):
                                            overlap = True
                                            break
                                    if overlap:
                                        break
                                if not overlap:
                                    from block import Block
                                    tetris2.blk_list.append(Block([[0, 0]], new_rect.x, new_rect.y, tetris2.screen, constants.GRAY, False))
                        elif special == 'dynamite':
                            pass
                        else:
                            if tetris2.blockstyle == "rotate":
                                tetris2.active_block.rotate()
                            elif tetris2.blockstyle == "swap":
                                tetris2.swap_next_block()

        # Process apply_action for both boards to handle TIMER_MOVE_EVENT
        if not tetris1.game_over:
            tetris1.apply_action()
        if human2 and not tetris2.game_over:
            tetris2.apply_action()

        # Advance game logic for both players
        if not tetris1.game_over:
            tetris1.get_block()
            tetris1.game_logic()
        if human2 and not tetris2.game_over:
            tetris2.get_block()
            tetris2.game_logic()
        elif not human2:
            ai2.play_step()  # AI makes a move

        # Draw both boards
        tetris1.draw_game()
        tetris2.draw_game()

        # End game if both are done (or in co-op, if either is done)
        if coop:
            if tetris1.game_over or tetris2.game_over:
                running = False
        else:
            if tetris1.game_over and tetris2.game_over:
                running = False

        clock.tick(30)

    pygame.quit()