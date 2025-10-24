import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()
pygame.font.init()

# -------------------------- Game Configuration Constants --------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Natural style color palette (green and brown tones)
COLOR_BG = (240, 248, 230)       # Light grass green background
COLOR_WOOD = (139, 69, 19)       # Dark brown (borders / title)
COLOR_WOOD_LIGHT = (178, 102, 28)# Light brown (input box)
COLOR_TEXT = (50, 100, 30)       # Dark green text
COLOR_PROMPT_CORRECT = (34, 139, 34)# Correct guess prompt color (dark green)
COLOR_PROMPT_HIGH = (205, 92, 92) # Guess too high prompt color (light red)
COLOR_PROMPT_LOW = (70, 130, 180) # Guess too low prompt color (light blue)

# Font configuration (rounded font to match natural style)
FONT_TITLE = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
FONT_TEXT = pygame.font.SysFont("Comic Sans MS", 22)
FONT_INPUT = pygame.font.SysFont("Comic Sans MS", 28)

# Game parameters
TARGET_NUM = random.randint(1, 100)  # Target number
MAX_ATTEMPTS = 8                     # Maximum number of attempts
current_attempts = 0                 # Current number of attempts
input_text = ""                      # Input box text
prompt_text = ""                     # Prompt text
prompt_color = COLOR_TEXT            # Prompt text color
is_win = False                       # Whether guessed correctly
show_fireworks = False               # Whether to show fireworks
fireworks = []                       # Firework particles list
leaf_particles = []                  # Leaf particles list

# -------------------------- Game Window Initialization --------------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Natural Style Particle Guess the Number")
clock = pygame.time.Clock()

# -------------------------- Particle Classes --------------------------
class LeafParticle:
    """Leaf particle (natural falling effect)"""
    def __init__(self):
        self.size = random.randint(8, 15)  # Leaf size
        self.x = random.randint(-20, SCREEN_WIDTH + 20)
        self.y = random.randint(-50, -10)  # Generated from outside the top of the screen
        self.speed_y = random.uniform(0.5, 1.2)  # Falling speed
        self.speed_x = random.uniform(-0.3, 0.3)  # Left-right drifting
        self.rotation = random.randint(0, 360)    # Initial rotation angle
        self.rot_speed = random.uniform(-1, 1)    # Rotation speed
        # Leaf color (random light green tones)
        self.color = (
            random.randint(100, 160),
            random.randint(180, 220),
            random.randint(80, 140)
        )

    def update(self):
        # Update position (falling + left-right drifting)
        self.y += self.speed_y
        self.x += self.speed_x
        # Update rotation
        self.rotation = (self.rotation + self.rot_speed) % 360
        # Reset if beyond the bottom of the screen
        if self.y > SCREEN_HEIGHT + 20:
            self.x = random.randint(-20, SCREEN_WIDTH + 20)
            self.y = random.randint(-50, -10)

    def draw(self, surface):
        # Draw rotating leaf (simulate leaf shape with polygon)
        leaf_points = [
            (0, -self.size // 2),
            (self.size // 3, self.size // 2),
            (0, self.size // 4),
            (-self.size // 3, self.size // 2)
        ]
        # Rotation matrix calculation
        rad = math.radians(self.rotation)
        rotated_points = []
        for (x, y) in leaf_points:
            new_x = x * math.cos(rad) - y * math.sin(rad) + self.x
            new_y = x * math.sin(rad) + y * math.cos(rad) + self.y
            rotated_points.append((new_x, new_y))
        # Draw leaf (with border)
        pygame.draw.polygon(surface, self.color, rotated_points)
        pygame.draw.polygon(surface, (80, 140, 60), rotated_points, width=1)


class FireworkParticle:
    """Firework particle (explosion effect after guessing correctly)"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(3, 6)
        # Random color (bright colors)
        self.color = (
            random.randint(180, 255),
            random.randint(80, 255),
            random.randint(80, 255)
        )
        # Random movement direction (360 degrees)
        angle = random.randint(0, 360)
        self.speed_x = math.cos(math.radians(angle)) * random.uniform(2, 5)
        self.speed_y = math.sin(math.radians(angle)) * random.uniform(2, 5)
        self.gravity = 0.05  # Gravity effect (simulate falling)
        self.life = random.randint(60, 120)  # Particle lifespan (frames)
        self.alpha = 255     # Transparency (gradually disappears)

    def update(self):
        # Update position (with gravity)
        self.speed_y += self.gravity
        self.x += self.speed_x
        self.y += self.speed_y
        # Reduce lifespan and transparency
        self.life -= 1
        self.alpha = max(0, self.alpha - 2)  # Reduce transparency by 2 points per frame

    def draw(self, surface):
        # Draw semi-transparent firework
        if self.alpha > 0:
            # Create a temporary Surface to store semi-transparent circle
            temp_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*self.color, self.alpha), (self.size, self.size), self.size)
            surface.blit(temp_surf, (self.x - self.size, self.y - self.size))


# -------------------------- Utility Functions --------------------------
def create_fireworks(x, y):
    """Create a group of firework particles (centered at (x, y))"""
    global fireworks
    fireworks = []
    for _ in range(150):  # Generate 150 particles per explosion
        fireworks.append(FireworkParticle(x, y))


# -------------------------- Main Game Logic --------------------------
def main():
    global input_text, prompt_text, prompt_color, current_attempts, is_win, show_fireworks, TARGET_NUM, fireworks

    # Initialize leaf particles (generate 30 initially)
    for _ in range(30):
        leaf_particles.append(LeafParticle())

    while True:
        # -------------------------- Event Handling --------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle input when not won
            if not is_win:
                # Keyboard input (numbers, backspace, enter)
                if event.type == pygame.KEYDOWN:
                    # Enter to confirm guess
                    if event.key == pygame.K_RETURN and input_text.isdigit():
                        guess = int(input_text)
                        current_attempts += 1

                        # Judge the result
                        if guess == TARGET_NUM:
                            is_win = True
                            show_fireworks = True
                            # Generate fireworks at the center of the screen
                            create_fireworks(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                            prompt_text = f"Congratulations! {guess} is the correct answer! It took {current_attempts} attempts."
                            prompt_color = COLOR_PROMPT_CORRECT
                        elif guess > TARGET_NUM:
                            prompt_text = f"{guess} is too high! {MAX_ATTEMPTS - current_attempts} attempts left."
                            prompt_color = COLOR_PROMPT_HIGH
                        else:
                            prompt_text = f"{guess} is too low! {MAX_ATTEMPTS - current_attempts} attempts left."
                            prompt_color = COLOR_PROMPT_LOW

                        # Ran out of attempts without guessing correctly
                        if current_attempts >= MAX_ATTEMPTS and not is_win:
                            prompt_text = f"Out of attempts! The correct answer is {TARGET_NUM}."
                            prompt_color = COLOR_PROMPT_HIGH

                        input_text = ""  # Clear input box

                    # Backspace to delete
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]

                    # Input numbers (0-9)
                    elif event.unicode.isdigit() and len(input_text) < 3:  # Limit to max 3 digits (1-100)
                        input_text += event.unicode

            # Press Space to restart after guessing correctly
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Reset game state
                    TARGET_NUM = random.randint(1, 100)
                    current_attempts = 0
                    input_text = ""
                    prompt_text = ""
                    is_win = False
                    show_fireworks = False
                    fireworks = []

        # -------------------------- Particle Update --------------------------
        # Update leaf particles
        for leaf in leaf_particles:
            leaf.update()

        # Update firework particles (only when showing)
        if show_fireworks:
            for firework in fireworks[:]:  # Iterate over a copy to avoid errors when deleting
                firework.update()
                if firework.life <= 0:
                    fireworks.remove(firework)
            # Stop showing when all firework particles disappear
            if not fireworks:
                show_fireworks = False

        # -------------------------- Drawing --------------------------
        # 1. Draw background (light grass green)
        screen.fill(COLOR_BG)

        # 2. Draw leaf particles
        for leaf in leaf_particles:
            leaf.draw(screen)

        # 3. Draw title (natural style title)
        title_text = FONT_TITLE.render("Natural Style Guess the Number", True, COLOR_WOOD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)
        # Title underline (wood color)
        pygame.draw.line(screen, COLOR_WOOD, (title_rect.left - 20, title_rect.bottom + 5),
                         (title_rect.right + 20, title_rect.bottom + 5), 3)

        # 4. Draw game instructions
        info_text1 = FONT_TEXT.render(f"Guess a number between 1-100, {MAX_ATTEMPTS} attempts in total.", True, COLOR_TEXT)
        info_text2 = FONT_TEXT.render(f"Current attempts: {current_attempts}/{MAX_ATTEMPTS}", True, COLOR_TEXT)
        screen.blit(info_text1, (SCREEN_WIDTH // 2 - info_text1.get_width() // 2, 150))
        screen.blit(info_text2, (SCREEN_WIDTH // 2 - info_text2.get_width() // 2, 190))

        # 5. Draw input box (wood style)
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 250, 240, 60)
        # Input box background (light brown, with dark brown border)
        pygame.draw.rect(screen, COLOR_WOOD_LIGHT, input_rect)
        pygame.draw.rect(screen, COLOR_WOOD, input_rect, 4, border_radius=8)  # Rounded border
        # Input box text (centered)
        input_surf = FONT_INPUT.render(input_text, True, COLOR_TEXT)
        input_surf_rect = input_surf.get_rect(center=input_rect.center)
        screen.blit(input_surf, input_surf_rect)

        # 6. Draw prompt text (with fade effect)
        if prompt_text:
            prompt_surf = FONT_TEXT.render(prompt_text, True, prompt_color)
            prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, 350))
            # Prompt text background (semi-transparent light color to avoid overlapping with particles)
            prompt_bg_rect = pygame.Rect(
                prompt_rect.left - 15, prompt_rect.top - 5,
                prompt_rect.width + 30, prompt_rect.height + 10
            )
            pygame.draw.rect(screen, (*COLOR_BG, 200), prompt_bg_rect, border_radius=5)
            screen.blit(prompt_surf, prompt_rect)

        # 7. Draw firework particles (only when showing)
        if show_fireworks:
            for firework in fireworks:
                firework.draw(screen)

        # 8. Show restart prompt after guessing correctly
        if is_win and not show_fireworks:
            restart_surf = FONT_TEXT.render("Press Space to Restart", True, COLOR_PROMPT_CORRECT)
            restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, 420))
            screen.blit(restart_surf, restart_rect)

        # -------------------------- Refresh Screen --------------------------
        pygame.display.flip()
        clock.tick(FPS)


# -------------------------- Start Game --------------------------
if __name__ == "__main__":
    main()