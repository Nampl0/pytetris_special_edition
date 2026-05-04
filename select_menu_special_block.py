import pygame
import constants
from store import load_store_data, save_store_data

def select_special_blocks(screen, font):
    """Menu to toggle which purchased special blocks are enabled for the next session."""
    data = load_store_data()
    purchased = data.get("purchased_blocks", {})
    selected = set(data.get("selected_blocks", []))
    special_blocks = [
        {"name": "Eraser Block", "color": constants.WHITE},
        {"name": "Builder Block", "color": constants.YELLOW},
        {"name": "Dynamite Block", "color": constants.RED},
    ]
    running = True
    while running:
        screen.fill(constants.BLACK)
        title = font.render("Select Special Blocks", True, constants.WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 50))
        y = 150
        button_w, button_h = 350, 60
        button_x = screen.get_width() // 2 - button_w // 2
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        for block in special_blocks:
            name = block["name"]
            count = purchased.get(name, 0)
            is_selected = name in selected
            color = block["color"] if is_selected else constants.GRAY
            border_color = constants.GREEN if is_selected else constants.WHITE
            rect = pygame.Rect(button_x, y, button_w, button_h)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, border_color, rect, 3)
            text = font.render(f"{name} (Owned: {count})", True, constants.BLACK if is_selected else constants.WHITE)
            screen.blit(text, (button_x + 20, y + button_h // 2 - text.get_height() // 2))
            if count > 0 and rect.collidepoint(mouse) and click[0]:
                pygame.time.wait(200)
                if is_selected:
                    selected.remove(name)
                else:
                    selected.add(name)
            if count == 0:
                lock_text = font.render("LOCKED", True, constants.RED)
                screen.blit(lock_text, (button_x + button_w - lock_text.get_width() - 20, y + button_h // 2 - lock_text.get_height() // 2))
            y += button_h + 20
        # Next button
        next_rect = pygame.Rect(button_x, y + 40, button_w, button_h)
        pygame.draw.rect(screen, constants.ORANGE, next_rect)
        next_text = font.render("Next", True, constants.WHITE)
        screen.blit(next_text, (button_x + button_w // 2 - next_text.get_width() // 2, y + 40 + button_h // 2 - next_text.get_height() // 2))
        if next_rect.collidepoint(mouse) and click[0]:
            data["selected_blocks"] = list(selected)
            save_store_data(data)
            pygame.time.wait(200)
            return list(selected)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                data["selected_blocks"] = list(selected)
                save_store_data(data)
                return list(selected)
        pygame.time.delay(50)