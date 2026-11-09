import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color

GRID_SIZE = 14  # Controls image scaling (14x14 grid makes assets large and visible)


class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.direction = "UP"
        self.last_moved = "UP"  # Direction the snake actually moved last tick
        self.food = (3, 3)

        # Apple Image Pool
        self.apple_images = ['apple1.png', 'apple2.png', 'apple3.png']
        self.current_apple_img = random.choice(self.apple_images)

        # Moving Wall Configurations
        self.wall_segments = [(10, 10)]
        self.wall_direction = "LEFT"
        self.wall_move_counter = 0
        self.wall_grow_counter = 0

        self.game_over = False
        self.touch_start_x = 0
        self.touch_start_y = 0

        # Game Over textual overlay reference
        self.game_over_label = None

        self.bind(size=self.draw_game, pos=self.draw_game)
        Clock.schedule_interval(self.update, 0.2)

    def draw_game(self, *args):
        self.canvas.clear()

        cell_width = self.width / GRID_SIZE
        cell_height = self.height / GRID_SIZE

        with self.canvas:
            # Reset color to white so images are drawn without tint
            Color(1, 1, 1, 1)

            # 1. Draw Apple using randomized selector
            Rectangle(
                source=self.current_apple_img,
                pos=(self.x + self.food[0] * cell_width, self.y + self.food[1] * cell_height),
                size=(cell_width, cell_height)
            )

            # 2. Draw Moving Wall blocks
            for wx, wy in self.wall_segments:
                Rectangle(
                    source='Wall.png',
                    pos=(self.x + wx * cell_width, self.y + wy * cell_height),
                    size=(cell_width, cell_height)
                )

            # 3. Draw Snake Structure
            for index, (x, y) in enumerate(self.snake):
                if index == 0:
                    # Head uses custom single image layout
                    Color(1, 1, 1, 1)
                    Rectangle(
                        source='snake_head.png',
                        pos=(self.x + x * cell_width, self.y + y * cell_height),
                        size=(cell_width, cell_height)
                    )
                else:
                    # Body falls back to default geometric vector squares
                    Color(0.18, 0.80, 0.44, 1.0)
                    Rectangle(
                        pos=(self.x + x * cell_width + 1, self.y + y * cell_height + 1),
                        size=(cell_width - 2, cell_height - 2)
                    )

            # Reset color again so nothing drawn later is tinted green
            Color(1, 1, 1, 1)

    def show_game_over_screen(self):
        if not self.game_over_label:
            self.game_over_label = Label(
                text="GAME OVER\n[Tap to Restart]",
                font_size="40sp",
                color=(0.9, 0.1, 0.1, 1),
                halign="center",
                center=self.center
            )
            self.add_widget(self.game_over_label)

    def restart_game(self):
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.direction = "UP"
        self.last_moved = "UP"
        self.food = (3, 3)
        self.current_apple_img = random.choice(self.apple_images)
        self.wall_segments = [(10, 10)]
        self.wall_direction = "LEFT"
        self.wall_move_counter = 0
        self.wall_grow_counter = 0
        self.game_over = False

        if self.game_over_label:
            self.remove_widget(self.game_over_label)
            self.game_over_label = None

        self.draw_game()

    def update(self, dt):
        if self.game_over:
            return

        # 1. Moving Wall Step and Growth Cycle Logic
        self.wall_move_counter += 1
        if self.wall_move_counter >= 2:
            self.wall_move_counter = 0
            if random.random() < 0.2:
                self.wall_direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

            w_head_x, w_head_y = self.wall_segments[0]
            if self.wall_direction == "UP":
                w_head_y += 1
            elif self.wall_direction == "DOWN":
                w_head_y -= 1
            elif self.wall_direction == "LEFT":
                w_head_x -= 1
            elif self.wall_direction == "RIGHT":
                w_head_x += 1

            w_head_x %= GRID_SIZE
            w_head_y %= GRID_SIZE
            new_wall_head = (w_head_x, w_head_y)

            self.wall_segments.insert(0, new_wall_head)

            self.wall_grow_counter += 1
            if self.wall_grow_counter >= 15:
                self.wall_grow_counter = 0
            else:
                self.wall_segments.pop()

        # 2. Snake Step Logic
        head_x, head_y = self.snake[0]
        if self.direction == "UP":
            head_y += 1
        elif self.direction == "DOWN":
            head_y -= 1
        elif self.direction == "LEFT":
            head_x -= 1
        elif self.direction == "RIGHT":
            head_x += 1

        new_head = (head_x, head_y)

        # Collision & Death Validations (screen margins, self, and moving wall coordinates)
        if (head_x < 0 or head_x >= GRID_SIZE or
                head_y < 0 or head_y >= GRID_SIZE or
                new_head in self.snake or
                new_head in self.wall_segments):
            self.game_over = True
            self.show_game_over_screen()
            return

        self.snake.insert(0, new_head)
        self.last_moved = self.direction  # Remember the direction actually moved

        # Apple Consumed Assessment
        if new_head == self.food:
            while True:
                self.food = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
                if self.food not in self.snake and self.food not in self.wall_segments:
                    break
            self.current_apple_img = random.choice(self.apple_images)
        else:
            self.snake.pop()

        self.draw_game()

    def on_touch_down(self, touch):
        if self.game_over:
            self.restart_game()
            return True

        self.touch_start_x = touch.x
        self.touch_start_y = touch.y
        return True

    def on_touch_up(self, touch):
        if self.game_over:
            return True

        dx = touch.x - self.touch_start_x
        dy = touch.y - self.touch_start_y

        # Compare against last_moved so quick double swipes can't reverse the snake
        if abs(dx) > abs(dy):
            if dx > 50 and self.last_moved != "LEFT":
                self.direction = "RIGHT"
            elif dx < -50 and self.last_moved != "RIGHT":
                self.direction = "LEFT"
        else:
            if dy > 50 and self.last_moved != "DOWN":
                self.direction = "UP"
            elif dy < -50 and self.last_moved != "UP":
                self.direction = "DOWN"
        return True


class SnakeApp(App):
    def build(self):
        return SnakeGame()


if __name__ == '__main__':
    SnakeApp().run()
