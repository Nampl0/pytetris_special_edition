import pygame
import constants

def draw_button(screen, text, x, y, width, height, color, hover_color, action=None):
    """Draws a button on the screen and handles click events."""
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))

        if click[0] == 1 and action:
            action()
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))
    
    font = pygame.font.SysFont(pygame.font.get_default_font(), constants.FONT_SIZE)
    label = font.render(text, True, constants.WHITE)
    screen.blit(label, (x + (width - label.get_width()) // 2, y + (height - label.get_height()) // 2))

def game_over_menu(screen):
    """Displays the Game Over menu with Try Again and Quit buttons."""
    restart = False

    while True:
        screen.fill(constants.BLACK)

        font = pygame.font.SysFont(pygame.font.get_default_font(), constants.FONT_SIZE)
        title = font.render("Game Over", True, constants.WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
        
        def set_restart():
            nonlocal restart
            restart = True

        def quit_game():
            pygame.quit()
            exit()
        
        draw_button(screen, "Try Again", screen.get_width() // 2 - 100, 250, 200, 50, constants.GREEN, constants.BLUE, set_restart)
        draw_button(screen, "Quit", screen.get_width() // 2 - 100, 320, 200, 50, constants.RED, constants.ORANGE, quit_game)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
        
        if restart:
                return True  # Return True to indicate restart
        
        pygame.time.delay(100)