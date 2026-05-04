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

def select_handicap(screen, font):
    """
    Display handicap selection menu.
    
    Parameters:
        - screen: pygame screen to draw on
        - font: pygame font object
    
    Returns:
        - selected handicap level (int)
    """
    selected_handicap = None
    running = True
    handicaps = [0, 3, 6, 9, 12]

    while running:
        screen.fill(constants.BLACK)
        
        # Draw title
        title = font.render("SELECT HANDICAP", True, constants.WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
        
        # Define button actions and positions
        button_width = 200
        button_height = 50
        button_spacing = 70
        start_y = 250

        # Create closure for button actions
        def create_handicap_action(handicap):
            def action():
                nonlocal selected_handicap, running
                selected_handicap = handicap
                running = False
            return action

        # Draw buttons for each handicap
        for i, handicap in enumerate(handicaps):
            button_x = screen.get_width() // 2 - button_width // 2
            button_y = start_y + i * button_spacing
            
            draw_button(
                screen,
                f"{handicap} Layers",
                button_x,
                button_y,
                button_width,
                button_height,
                constants.GREEN,  # default color
                constants.BLUE,   # hover color
                create_handicap_action(handicap)
            )
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
                
        pygame.time.delay(100)
    
    return selected_handicap