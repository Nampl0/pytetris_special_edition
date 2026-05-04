import pygame
import constants
import random

class TetrisAI:
    def __init__(self, game):
        self.game = game
        self.last_move_time = 0
        self.move_delay = 500  # milliseconds between moves

    def play_step(self):
        """Make a move for the AI player."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay:
            return

        # Simple AI: randomly choose between moving left, right, or rotating
        action = random.choice(['left', 'right', 'rotate', 'down'])
        
        if action == 'left':
            self.game.active_block.move(-constants.BWIDTH, 0)
        elif action == 'right':
            self.game.active_block.move(constants.BWIDTH, 0)
        elif action == 'rotate':
            if self.game.blockstyle == "rotate":
                self.game.active_block.rotate()
        elif action == 'down':
            if self.game.reverse_mode:
                self.game.active_block.move(0, -constants.BHEIGHT)
            else:
                self.game.active_block.move(0, constants.BHEIGHT)

        self.last_move_time = current_time

        # Advance the game logic (simulate a tick)
        self.game.get_block()
        self.game.game_logic()