# import pygame
# import constants

# def menu(screen, font):
#     """Displays the main menu and waits for player input."""
#     menu_active = True
#     while menu_active:
#         screen.fill(constants.BLACK)
#         title = font.render("TETRIS", True, constants.WHITE)
#         start_text = font.render("Press ENTER to Start", True, constants.WHITE)
#         quit_text = font.render("Press Q to Quit", True, constants.WHITE)
        
#         screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
#         screen.blit(start_text, (screen.get_width() // 2 - start_text.get_width() // 2, 200))
#         screen.blit(quit_text, (screen.get_width() // 2 - quit_text.get_width() // 2, 250))
        
#         pygame.display.flip()
        
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 exit()
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_RETURN:
#                     menu_active = False  # Start game
#                 if event.key == pygame.K_q:
#                     pygame.quit()
#                     exit()

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

# def draw_slider(screen, x, y, min_val, max_val, current_val):
#     """Draws a slider for selecting speed."""
#     bar_width = 300
#     handle_x = x + ((current_val - min_val) / (max_val - min_val)) * bar_width
#     pygame.draw.line(screen, constants.WHITE, (x, y), (x + bar_width, y), 5)  # Slider bar
#     pygame.draw.circle(screen, constants.RED, (int(handle_x), y), 10)  # Handle

def menu(screen):
    """Displays the main menu with Start, Store and Quit buttons."""
    running = True
    selected_mode = None

    while running:
        screen.fill(constants.BLACK)

        font = pygame.font.SysFont(pygame.font.get_default_font(), constants.FONT_SIZE)
        title = font.render("TETRIS", True, constants.WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
        
        def start_game():
            nonlocal running, selected_mode
            selected_mode = "single"
            running = False

        def start_multiplayer():
            nonlocal running, selected_mode
            selected_mode = "multi"
            running = False

        def quit_game():
            pygame.quit()
            exit()
            
        def show_store():
            from store import show_store_screen
            show_store_screen(screen)
            
        def show_high_scores():
            from high_score import show_high_scores
            show_high_scores(screen)
        
        # Draw buttons
        button_width = 200
        button_height = 50
        button_x = screen.get_width() // 2 - button_width // 2

        draw_button(screen, "Single Player", button_x, 200, button_width, button_height, 
                   constants.GREEN, constants.BLUE, start_game)
        draw_button(screen, "Multi Player", button_x, 270, button_width, button_height, 
                   constants.GREEN, constants.BLUE, start_multiplayer)
        draw_button(screen, "High Score", button_x, 340, button_width, button_height,
                   constants.GREEN, constants.BLUE, show_high_scores)
        draw_button(screen, "Store", button_x, 410, button_width, button_height,
                   constants.RED, constants.ORANGE, show_store)
        draw_button(screen, "Quit", button_x, 480, button_width, button_height, 
                   constants.RED, constants.ORANGE, quit_game)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        pygame.time.delay(100)
    return selected_mode