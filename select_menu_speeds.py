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

def select_menu(screen):
    """
    Display mode selection menu and return the selected mode.
    Returns: 
        - "classic" for classic mode with fixed speed
        - "escalation" for mode where speed increases with score
    """
    pygame.font.init()
    font = pygame.font.SysFont(pygame.font.get_default_font(), constants.FONT_SIZE)
    selected_mode = None
    running = True

    while running:
        screen.fill(constants.BLACK)
        
        # Draw title
        title = font.render("SELECT MODE", True, constants.WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
        
        # Define button actions
        def select_classic():
            nonlocal selected_mode
            selected_mode = "classic"
            nonlocal running
            running = False
            
        def select_escalation():
            nonlocal selected_mode
            selected_mode = "escalation"
            nonlocal running
            running = False
        
        # Draw buttons with consistent styling
        draw_button(screen, "Classic", screen.get_width() // 2 - 100, 250, 200, 50, 
                   constants.GREEN, constants.BLUE, select_classic)
        draw_button(screen, "Escalation", screen.get_width() // 2 - 100, 320, 200, 50, 
                   constants.PURPLE, constants.RED, select_escalation)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
                
        pygame.time.delay(100)
    
    return selected_mode