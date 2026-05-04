import pygame
import json
import os
import constants

STORE_DATA_FILE = "store_data.json"

def load_store_data():
    if os.path.exists(STORE_DATA_FILE):
        with open(STORE_DATA_FILE, 'r') as f:
            return json.load(f)
    # Default: counts for each block
    return {
        "currency": 0,
        "purchased_blocks": {
            "Eraser Block": 0,
            "Builder Block": 0,
            "Dynamite Block": 0
        },
        "selected_blocks": []
    }

def save_store_data(data):
    with open(STORE_DATA_FILE, 'w') as f:
        json.dump(data, f)

def add_currency(score):
    data = load_store_data()
    data["currency"] += score
    save_store_data(data)

def buy_block(block_name, price):
    data = load_store_data()
    if data["currency"] >= price:
        data["currency"] -= price
        data["purchased_blocks"][block_name] = data["purchased_blocks"].get(block_name, 0) + 1
        save_store_data(data)
        return True
    return False

def show_store_screen(screen):
    running = True
    font = pygame.font.SysFont(pygame.font.get_default_font(), constants.FONT_SIZE)
    special_blocks = [
        {"name": "Eraser Block", "price": 1000, "description": "Deletes 1x1 on space, disappears on collision"},
        {"name": "Builder Block", "price": 1500, "description": "Creates 1x1 on space, disappears on collision"},
        {"name": "Dynamite Block", "price": 2000, "description": "Deletes 3x3 on collision, disappears"},
    ]
    while running:
        data = load_store_data()
        currency = data["currency"]
        purchased_blocks = data["purchased_blocks"]
        screen.fill(constants.BLACK)
        title = font.render("SPECIAL BLOCKS STORE", True, constants.WHITE)
        currency_text = font.render(f"${currency}", True, constants.GOLD)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 50))
        screen.blit(currency_text, (screen.get_width() - currency_text.get_width() - 20, 20))
        y_pos = 150
        button_width = 300
        button_height = 80
        button_x = screen.get_width() // 2 - button_width // 2
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        for block in special_blocks:
            count = purchased_blocks.get(block["name"], 0)
            can_afford = currency >= block["price"]
            color = constants.BLUE if can_afford else constants.GRAY
            rect = pygame.Rect(button_x, y_pos, button_width, button_height)
            pygame.draw.rect(screen, color, rect)
            name_text = font.render(block["name"], True, constants.WHITE)
            desc_text = font.render(block["description"], True, constants.WHITE)
            price_text = font.render(f"${block['price']}", True, constants.WHITE)
            count_text = font.render(f"Owned: {count}", True, constants.GREEN if count > 0 else constants.RED)
            screen.blit(name_text, (button_x + 10, y_pos + 10))
            screen.blit(desc_text, (button_x + 10, y_pos + 35))
            screen.blit(price_text, (button_x + button_width - price_text.get_width() - 10, y_pos + 10))
            screen.blit(count_text, (button_x + button_width - count_text.get_width() - 10, y_pos + 45))
            if rect.collidepoint(mouse) and click[0] and can_afford:
                pygame.time.wait(200)
                buy_block(block["name"], block["price"])
            y_pos += button_height + 20
        # Back button
        back_rect = pygame.Rect(button_x, y_pos + 40, button_width, button_height)
        pygame.draw.rect(screen, constants.ORANGE, back_rect)
        back_text = font.render("Back", True, constants.WHITE)
        screen.blit(back_text, (button_x + (button_width - back_text.get_width()) // 2,
                               y_pos + 40 + (button_height - back_text.get_height()) // 2))
        if back_rect.collidepoint(mouse) and click[0]:
            pygame.time.wait(200)
            running = False
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        pygame.time.delay(100)