import pygame
import json
import os
import constants

# File to store high scores
HIGH_SCORES_FILE = "high_scores.json"

def load_high_scores():
    """Load high scores from file, or create new if file doesn't exist."""
    if os.path.exists(HIGH_SCORES_FILE):
        with open(HIGH_SCORES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_high_score(score):
    """Save a new high score to the file."""
    scores = load_high_scores()
    scores.append(score)
    scores.sort(reverse=True)  # Sort in descending order
    scores = scores[:5]  # Keep only top 5 scores
    
    with open(HIGH_SCORES_FILE, 'w') as f:
        json.dump(scores, f)

def show_high_scores(screen):
    """Display the high scores screen."""
    running = True
    scores = load_high_scores()
    
    while running:
        screen.fill(constants.BLACK)
        
        # Draw title
        font = pygame.font.SysFont(pygame.font.get_default_font(), constants.FONT_SIZE)
        title = font.render("HIGH SCORES", True, constants.WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
        
        # Draw scores
        y_pos = 200
        if not scores:
            no_scores = font.render("No scores yet!", True, constants.WHITE)
            screen.blit(no_scores, (screen.get_width() // 2 - no_scores.get_width() // 2, y_pos))
        else:
            for i, score in enumerate(scores, 1):
                score_text = font.render(f"{i}. {score}", True, constants.WHITE)
                screen.blit(score_text, (screen.get_width() // 2 - score_text.get_width() // 2, y_pos))
                y_pos += 40
        
        # Draw back button
        button_width = 200
        button_height = 50
        button_x = screen.get_width() // 2 - button_width // 2
        button_y = screen.get_height() - 100
        
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        if button_x < mouse[0] < button_x + button_width and button_y < mouse[1] < button_y + button_height:
            pygame.draw.rect(screen, constants.ORANGE, (button_x, button_y, button_width, button_height))
            if click[0] == 1:
                running = False
        else:
            pygame.draw.rect(screen, constants.RED, (button_x, button_y, button_width, button_height))
        
        back_text = font.render("Back", True, constants.WHITE)
        screen.blit(back_text, (button_x + (button_width - back_text.get_width()) // 2, 
                               button_y + (button_height - back_text.get_height()) // 2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        pygame.time.delay(100) 