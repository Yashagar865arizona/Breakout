import pygame
import random
import math
from pygame import gfxdraw

"""
By Yash Agarwal

Still needs to be polished and many more things to be implemented
"""

# Set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = pygame.Color(255, 255, 255)
DARK_GRAY = pygame.Color(50, 50, 50)
LIGHT_GRAY = pygame.Color(200, 200, 200)


class BreakoutGame:
    def __init__(self, width, height):
        pygame.init()

        self.window_width = width
        self.window_height = height
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Breakout Game")

        self.clock = pygame.time.Clock()
        self.is_running = False

        self.paddle = Paddle((self.window_width - 100) // 2, self.window_height - 50, 100, 20, self.window_width,
                             self.window_height)
        self.ball = Ball(self.window_width // 2, self.window_height // 2, 10, 8, self.window_width,
                         self.window_height)
        self.wall = Wall(5, 10, 70, 20, 5, 10, 70, 20, 10)

        self.q_table = {}
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.2  # Discount factor
        self.epsilon = 0.6  # Exploration rate
        self.score = 0
        self.font = pygame.font.Font(None, 36)

    def start(self):
        self.is_running = True
        self.run_game()

    def run_game(self):
        while self.is_running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.render()

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

    def render_score(self, window):
        score_text = self.font.render("Score: " + str(self.score), True, WHITE)
        window.blit(score_text, (10, 10))

    def update(self):
        state = self.get_state()
        action = self.choose_action(state)
        self.paddle.update(self.window_width, self.ball.rect.centerx)

        self.ball.update(self.window_width)

        if self.ball.rect.colliderect(self.paddle.rect):
            self.ball.bounce_off_paddle(self.paddle)

        brick_hit = False

        for brick in self.wall.bricks:
            if self.ball.rect.colliderect(brick.rect):
                self.ball.bounce_off_brick(brick)
                self.wall.bricks.remove(brick)
                brick_hit = True
                break

        if brick_hit:
            self.score += 10

        if self.ball.rect.left <= 0 or self.ball.rect.right >= self.window_width:
            self.ball.bounce_off_walls(self.window_width, self.window_height)

        if self.ball.rect.top <= 0:
            self.ball.bounce_off_ceiling(self.window_height)

        if self.ball.rect.top >= self.window_height:
            self.is_running = False

        if len(self.wall.bricks) == 0:
            self.is_running = False

        next_state = self.get_state()
        reward = self.get_reward()
        self.update_q_table(state, action, reward, next_state)

        if not self.is_running:
            print("Game over. Score:", self.score)  # Print the score when the game is over

    def render(self):
        self.window.fill(BLACK)
        self.paddle.render(self.window)
        self.ball.render(self.window)
        self.wall.render(self.window)
        self.render_score(self.window)

        pygame.display.flip()

    def get_state(self):
        # Get the current state representation
        # For example, you can use the positions of the paddle, ball, and bricks
        paddle_x = self.paddle.rect.x
        ball_x = self.ball.rect.x
        brick_count = len(self.wall.bricks)
        state = (paddle_x, ball_x, brick_count)
        return state

    def choose_action(self, state):
        # Choose action based on epsilon-greedy policy
        if random.random() < self.epsilon:
            return random.choice([-1, 1])  # Random action
        else:
            state_q_values = self.q_table.get(state, {})
            if state_q_values:
                return max(state_q_values, key=state_q_values.get)
            else:
                return random.choice([-1, 1])  # Random action when no Q-values are available

    def get_reward(self):
        # Calculate and return the reward based on the current game state and score
        if len(self.wall.bricks) == 0:
            return self.score  # Reward based on the score
        elif self.ball.rect.top >= self.window_height:
            return -1  # Lose
        else:
            return 0  # No reward

    def update_q_table(self, state, action, reward, next_state):
        # Update the Q-values in the Q-table based on the Q-learning algorithm
        current_q_value = self.q_table.get(state, {}).get(action, 0)
        next_state_q_values = self.q_table.get(next_state, {})
        max_next_q_value = max(next_state_q_values.values()) if next_state_q_values else 0
        new_q_value = current_q_value + self.alpha * (reward + self.gamma * max_next_q_value - current_q_value)
        self.q_table.setdefault(state, {})[action] = new_q_value



class Paddle:
    def __init__(self, x, y, width, height, window_width, window_height):
        self.rect = pygame.Rect(x, y, width, height)
        self.window_width = window_width
        self.window_height = window_height
        self.gradient_colors = self.generate_gradient_colors()

    def generate_gradient_colors(self):
        gradient_colors = []
        for i in range(10):
            r = max(WHITE.r - i * 10, DARK_GRAY.r)
            g = max(WHITE.g - i * 10, DARK_GRAY.g)
            b = max(WHITE.b - i * 10, DARK_GRAY.b)
            gradient_colors.append(pygame.Color(r, g, b))
        return gradient_colors

    def update(self, window_width, ball_x):
        # Calculate the distance between the paddle's center and the ball's x-coordinate
        distance = ball_x - (self.rect.x + self.rect.width / 2)

        # Adjust the paddle's position based on the distance from the ball
        if distance < 0:
            self.rect.x -= abs(distance)
        elif distance > 0:
            self.rect.x += abs(distance)

        # Ensure the paddle stays within the window bounds
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > window_width - self.rect.width:
            self.rect.x = window_width - self.rect.width

    def render(self, window):
        pygame.draw.rect(window, WHITE, self.rect)

        gradient_width = self.rect.width // len(self.gradient_colors)
        for i, color in enumerate(self.gradient_colors):
            paddle_rect = pygame.Rect(
                self.rect.x + i * gradient_width,
                self.rect.y,
                gradient_width,
                self.rect.height
            )
            pygame.draw.rect(window, color, paddle_rect)

        self.render_3d_effect(window)

    def render_3d_effect(self, window):
        # Draw top and left shades
        pygame.gfxdraw.box(window, self.rect, DARK_GRAY)

        # Draw bottom and right shades
        shaded_rect = pygame.Rect(self.rect.x + 1, self.rect.y + 1, self.rect.width - 2, self.rect.height - 2)
        pygame.gfxdraw.box(window, shaded_rect, LIGHT_GRAY)



class Ball:
    def __init__(self, x, y, radius, speed, window_width, window_height):
        self.rect = pygame.Rect(x, y, radius, radius)
        self.speed = speed
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]
        self.window_width = window_width
        self.window_height = window_height
    def update(self,window_width):
        self.rect.x += self.speed * self.direction[0]
        self.rect.y += self.speed * self.direction[1]

        if self.rect.x <= 0 or self.rect.x >= window_width - self.rect.width:
            self.reverse_direction_x()
        if self.rect.y <= 0:
            self.reverse_direction_y()

    def reverse_direction_x(self):
        angle = math.atan2(self.direction[1], self.direction[0])
        angle += random.uniform(-math.pi / 4, math.pi / 4)  # Random angle variation
        self.direction = [math.cos(angle), math.sin(angle)]

    def reverse_direction_y(self):
        angle = math.atan2(self.direction[1], self.direction[0])
        angle += random.uniform(-math.pi / 4, math.pi / 4)  # Random angle variation
        self.direction = [math.cos(angle), math.sin(angle)]

    def render(self, window):
        pygame.draw.circle(window, WHITE, self.rect.center, self.rect.width // 2)

    def bounce_off_ceiling(self, window_height):
        if self.rect.top <= 0:
            self.rect.top = 0
            self.reverse_direction_y()

    def bounce_off_brick(self, brick):
        if self.rect.colliderect(brick.rect):
            # Calculate the center points of the ball and brick
            ball_center = self.rect.center
            brick_center = brick.rect.center

            # Calculate the distance vector between the centers
            dx = ball_center[0] - brick_center[0]
            dy = ball_center[1] - brick_center[1]

            # Calculate the reflection angle based on the distance vector
            angle = math.atan2(dy, dx)

            # Calculate the new direction based on the reflection angle
            new_direction = [math.cos(angle), math.sin(angle)]

            # Update the ball's direction
            self.direction = new_direction
    def bounce_off_walls(self, window_width, window_height):
        if self.rect.left <= 0:
            self.rect.left = 0
            self.reverse_direction_x()
        elif self.rect.right >= window_width:
            self.rect.right = window_width - 1
            self.reverse_direction_x()

        if self.rect.top <= 0 or self.rect.bottom >= window_height:
            self.reverse_direction_y()



    def bounce_off_paddle(self, paddle):
        # Calculate the collision position on the paddle
        collision_pos = self.rect.centerx - paddle.rect.centerx

        # Calculate the angle based on the collision position
        angle = (collision_pos / (paddle.rect.width / 2)) * (math.pi / 3)

        # Reverse the y-direction and adjust the x-direction based on the angle
        self.direction = [-math.sin(angle), -math.cos(angle)]

class Brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color(*color)  # Convert color to pygame.Color object
        self.gradient_colors = self.generate_gradient_colors()
        self.light_shade = self.generate_light_shade()
        self.dark_shade = self.generate_dark_shade()

    def generate_gradient_colors(self):
        gradient_colors = []
        r, g, b, _ = self.color
        for i in range(10):
            r -= 5
            g -= 5
            b -= 5
            gradient_colors.append(pygame.Color(max(r, 0), max(g, 0), max(b, 0)))
        return gradient_colors

    def generate_light_shade(self):
        r = min(self.color.r + 50, 255)
        g = min(self.color.g + 50, 255)
        b = min(self.color.b + 50, 255)
        return pygame.Color(r, g, b)

    def generate_dark_shade(self):
        r = max(self.color.r - 50, 0)
        g = max(self.color.g - 50, 0)
        b = max(self.color.b - 50, 0)
        return pygame.Color(r, g, b)

    def render(self, window):
        pygame.draw.rect(window, self.color, self.rect)

        gradient_height = self.rect.height // len(self.gradient_colors)
        for i, color in enumerate(self.gradient_colors):
            brick_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + i * gradient_height,
                self.rect.width,
                gradient_height
            )
            pygame.draw.rect(window, color, brick_rect)

        self.render_3d_effect(window)

    def render_3d_effect(self, window):
        # Draw top and left shades
        pygame.gfxdraw.box(window, self.rect, self.dark_shade)

        # Draw bottom and right shades
        shaded_rect = pygame.Rect(self.rect.x + 1, self.rect.y + 1, self.rect.width - 2, self.rect.height - 2)
        pygame.gfxdraw.box(window, shaded_rect, self.light_shade)




class Wall:
    def __init__(self, x, y, width, height, rows, cols, brick_width, brick_height, brick_gap):
        self.bricks = []
        for row in range(rows):
            for col in range(cols):
                brick_x = x + (brick_width + brick_gap) * col
                brick_y = y + (brick_height + brick_gap) * row
                brick_color = random.choice([RED, BLUE, GREEN, YELLOW])
                brick = Brick(brick_x, brick_y, brick_width, brick_height, brick_color)
                self.bricks.append(brick)

    def render(self, window):
        for brick in self.bricks:
            brick.render(window)


# Create and start the game
game = BreakoutGame(800, 600)
game.start()