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

def select_boardstyle(screen, font):
    """
    Choose to reverse the board or not.
    
    Parameters:
        - screen: pygame screen to draw on
        - font: pygame font object
    
    Returns:
        - "normal" or "reverse" based on selection
    """
    selected_boardstyle = None
    running = True

    while running:
        screen.fill(constants.BLACK)
        
        # Draw title
        title = font.render("SELECT BLOCK SPAWN", True, constants.WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
        
        # Define button actions and positions
        button_width = 200
        button_height = 50
        button_spacing = 70
        start_y = 250

        # Create closure for button actions
        def create_style_action(style):
            def action():
                nonlocal selected_boardstyle, running
                selected_boardstyle = style
                running = False
            return action

        # Draw buttons for each style
        styles = [("Normal", "normal"), ("Reverse", "reverse")]
        for i, (text, style) in enumerate(styles):
            button_x = screen.get_width() // 2 - button_width // 2
            button_y = start_y + i * button_spacing
            
            draw_button(
                screen,
                text,
                button_x,
                button_y,
                button_width,
                button_height,
                constants.RED,  # default color
                constants.GOLD,   # hover color
                create_style_action(style)
            )
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "normal"  # default to normal if quit
                
        pygame.time.delay(100)
    
    return selected_boardstyle