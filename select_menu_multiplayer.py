import pygame
import constants

def draw_button(screen, text, x, y, width, height, color, hover_color, action=None):
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

def select_menu_multiplayer(screen):
    """Displays the multiplayer mode selection menu and returns the selected mode."""
    running = True
    selected_mode = None

    def set_mode(mode):
        nonlocal running, selected_mode
        selected_mode = mode
        running = False

    while running:
        screen.fill(constants.BLACK)
        font = pygame.font.SysFont(pygame.font.get_default_font(), constants.FONT_SIZE)
        title = font.render("MULTIPLAYER", True, constants.WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))

        button_width = 250
        button_height = 50
        button_x = screen.get_width() // 2 - button_width // 2
        y_start = 200
        y_gap = 70

        draw_button(screen, "VS 2P", button_x, y_start, button_width, button_height,
                    constants.GREEN, constants.BLUE, lambda: set_mode("vs_2p"))
        draw_button(screen, "VS AI", button_x, y_start + y_gap, button_width, button_height,
                    constants.GREEN, constants.BLUE, lambda: set_mode("vs_ai"))
        draw_button(screen, "Co-op 2P", button_x, y_start + 2 * y_gap, button_width, button_height,
                    constants.GREEN, constants.BLUE, lambda: set_mode("coop_2p"))
        draw_button(screen, "Co-op AI", button_x, y_start + 3 * y_gap, button_width, button_height,
                    constants.GREEN, constants.BLUE, lambda: set_mode("coop_ai"))
        draw_button(screen, "Back", button_x, y_start + 4 * y_gap, button_width, button_height,
                    constants.RED, constants.ORANGE, lambda: set_mode("back"))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    set_mode("back")

        pygame.time.delay(100)

    return selected_mode