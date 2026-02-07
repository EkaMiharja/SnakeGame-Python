from tkinter import *
import random

# Game constants
GAME_WIDTH = 800
GAME_HEIGHT = 400
SPACE_SIZE = 30
BODY_PARTS = 3
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
SPECIAL_FOOD_COLOR = "#FF00FF"  # Purple color for special food
BACKGROUND_COLOR = "#000000"

# Difficulty levels with different speeds
DIFFICULTY_LEVELS = {
    "Easy": 150,  # Slow speed
    "Medium": 100,  # Normal speed
    "Hard": 70  # Fast speed
}

# Special food properties
SPECIAL_FOOD_POINTS = 5  # Extra points for special food
SPECIAL_FOOD_DURATION = 5  # Seconds before special food disappears
SPECIAL_FOOD_CHANCE = 0.3  # 30% chance to spawn special food


class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []

        # Initialize snake starting coordinates
        for i in range(0, BODY_PARTS):
            self.coordinates.append([0, 0])

        # Create snake visual representation on canvas
        for x, y in self.coordinates:
            square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)


class Food:
    def __init__(self, is_special=False):
        self.is_special = is_special

        # Generate random food position within game boundaries
        x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE

        self.coordinates = [x, y]

        # Create food visual on canvas
        if is_special:
            # Draw special food as a diamond shape
            points = [
                x + SPACE_SIZE // 2, y,  # Top
                x + SPACE_SIZE, y + SPACE_SIZE // 2,  # Right
                x + SPACE_SIZE // 2, y + SPACE_SIZE,  # Bottom
                x, y + SPACE_SIZE // 2  # Left
            ]
            canvas.create_polygon(points, fill=SPECIAL_FOOD_COLOR, outline="yellow",
                                  tag="special_food", width=2)
        else:
            # Draw normal food as oval
            canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOR, tag="food")


def next_turn(snake, food):
    global direction, game_active, current_speed, special_food, score, special_food_timer

    # Only run game if active
    if not game_active:
        return

    # Get snake head position
    x, y = snake.coordinates[0]

    # Update position based on direction
    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE

    # Add new position as snake head
    snake.coordinates.insert(0, (x, y))
    square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
    snake.squares.insert(0, square)

    # Check if snake eats normal food
    if x == food.coordinates[0] and y == food.coordinates[1]:
        score += 1
        update_score_label()
        canvas.delete("food")
        food = Food()  # Create new normal food

        # Random chance to spawn special food
        if random.random() < SPECIAL_FOOD_CHANCE and special_food is None:
            spawn_special_food()

    # Check if snake eats special food
    elif special_food and x == special_food.coordinates[0] and y == special_food.coordinates[1]:
        score += SPECIAL_FOOD_POINTS
        update_score_label()
        canvas.delete("special_food")
        special_food = None

        # Clear any pending timer for special food removal
        if special_food_timer:
            window.after_cancel(special_food_timer)
            special_food_timer = None

        # Show bonus message
        canvas.create_text(
            x + SPACE_SIZE // 2, y - 20,
            font="consolas 12 bold",
            text=f"+{SPECIAL_FOOD_POINTS}!",
            fill="yellow",
            tag="bonus_text"
        )
        window.after(500, lambda: canvas.delete("bonus_text"))
    else:
        # Remove snake tail if no food eaten
        del snake.coordinates[-1]
        canvas.delete(snake.squares[-1])
        del snake.squares[-1]

    # Check collisions
    if check_collisions(snake):
        game_over()
    else:
        # Continue to next turn with current speed
        window.after(current_speed, next_turn, snake, food)


def update_score_label():
    """Update the score label with current score"""
    label.config(text=f"Score: {score}")


def spawn_special_food():
    """Spawn a special food item with timer"""
    global special_food, special_food_timer

    # Create special food
    special_food = Food(is_special=True)

    # Set timer to remove special food after duration
    special_food_timer = window.after(SPECIAL_FOOD_DURATION * 1000, remove_special_food)

    # Show notification
    canvas.create_text(
        GAME_WIDTH // 2, 30,
        font="consolas 14 bold",
        text="SPECIAL FOOD APPEARED!",
        fill=SPECIAL_FOOD_COLOR,
        tag="special_notice"
    )
    window.after(1000, lambda: canvas.delete("special_notice"))


def remove_special_food():
    """Remove special food when timer expires"""
    global special_food, special_food_timer

    if special_food:
        canvas.delete("special_food")
        special_food = None
        special_food_timer = None


def change_direction(new_direction):
    global direction

    # Prevent snake from turning 180 degrees (instant death)
    if new_direction == "left" and direction != "right":
        direction = new_direction
    elif new_direction == "right" and direction != "left":
        direction = new_direction
    elif new_direction == "up" and direction != "down":
        direction = new_direction
    elif new_direction == "down" and direction != "up":
        direction = new_direction


def change_difficulty(level):
    """Change game difficulty level"""
    global current_speed, current_difficulty

    current_difficulty = level
    current_speed = DIFFICULTY_LEVELS[level]

    # Update difficulty label
    difficulty_value_label.config(text=level)


def check_collisions(snake):
    # Get head position
    x, y = snake.coordinates[0]

    # Check wall collisions
    if x < 0 or x >= GAME_WIDTH:
        return True
    elif y < 0 or y >= GAME_HEIGHT:
        return True

    # Check self collision
    for body_part in snake.coordinates[1:]:
        if x == body_part[0] and y == body_part[1]:
            return True

    return False


def game_over():
    global game_active, retry_button, menu_button, special_food_timer

    # Set game to inactive
    game_active = False

    # Cancel special food timer if exists
    if special_food_timer:
        window.after_cancel(special_food_timer)
        special_food_timer = None

    # Clear all canvas elements
    canvas.delete(ALL)

    # Display game over text
    canvas.create_text(
        canvas.winfo_width() / 2,
        canvas.winfo_height() / 2 - 80,
        font="consolas 40 bold",
        text="GAME OVER",
        fill="#FF3333",
        tag="gameover"
    )

    # Display final score
    canvas.create_text(
        canvas.winfo_width() / 2,
        canvas.winfo_height() / 2 - 20,
        font="consolas 20 bold",
        text=f"Final Score: {score}",
        fill="white",
        tag="score"
    )

    # Display difficulty
    canvas.create_text(
        canvas.winfo_width() / 2,
        canvas.winfo_height() / 2 + 20,
        font="consolas 16",
        text=f"Difficulty: {current_difficulty}",
        fill="#AAAAAA",
        tag="difficulty"
    )

    # Create buttons frame
    buttons_frame = Frame(window, bg=BACKGROUND_COLOR)

    # Create retry button
    retry_button = Button(
        buttons_frame,
        text="RETRY",
        font="consolas 14 bold",
        bg="#4CAF50",
        fg="white",
        activebackground="#45a049",
        activeforeground="white",
        bd=0,
        padx=25,
        pady=10,
        cursor="hand2",
        command=restart_game
    )
    retry_button.pack(side=LEFT, padx=10)

    # Create menu button
    menu_button = Button(
        buttons_frame,
        text="MAIN MENU",
        font="consolas 14 bold",
        bg="#2196F3",
        fg="white",
        activebackground="#1976D2",
        activeforeground="white",
        bd=0,
        padx=25,
        pady=10,
        cursor="hand2",
        command=back_to_menu
    )
    menu_button.pack(side=LEFT, padx=10)

    # Position buttons frame in center of canvas
    canvas.create_window(
        canvas.winfo_width() / 2,
        canvas.winfo_height() / 2 + 80,
        window=buttons_frame,
        tag="buttons_frame"
    )


def restart_game():
    global snake, food, score, direction, game_active, retry_button, menu_button, special_food, special_food_timer

    # Reset game variables
    score = 0
    direction = 'down'
    game_active = True
    special_food = None

    # Cancel any existing timer
    if special_food_timer:
        window.after_cancel(special_food_timer)
        special_food_timer = None

    # Update score label
    update_score_label()

    # Clear all elements from canvas
    canvas.delete("all")

    # Hide retry and menu buttons
    if retry_button:
        retry_button.destroy()
        retry_button = None
    if menu_button:
        menu_button.destroy()
        menu_button = None

    # Create new snake and food
    snake = Snake()
    food = Food()

    # Start new game
    next_turn(snake, food)


def back_to_menu():
    """Return to main menu from game over screen"""
    global game_active, retry_button, menu_button, special_food, special_food_timer

    # Set game to inactive
    game_active = False
    special_food = None

    # Cancel any existing timer
    if special_food_timer:
        window.after_cancel(special_food_timer)
        special_food_timer = None

    # Hide and destroy buttons
    if retry_button:
        retry_button.destroy()
        retry_button = None
    if menu_button:
        menu_button.destroy()
        menu_button = None

    # Hide game UI
    game_ui_frame.pack_forget()

    # Show start menu
    show_start_menu()


def show_start_menu():
    """Display the start menu with play button"""
    # Clear canvas
    canvas.delete("all")

    # Hide game UI
    game_ui_frame.pack_forget()

    # Game title
    canvas.create_text(
        GAME_WIDTH / 2,
        70,
        font="consolas 50 bold",
        text="SNAKE GAME",
        fill="#00FF00",
        tag="title"
    )

    # Subtitle
    canvas.create_text(
        GAME_WIDTH / 2,
        130,
        font="consolas 16",
        text="A Classic Arcade Experience",
        fill="#AAAAAA",
        tag="subtitle"
    )

    # Difficulty selection
    canvas.create_text(
        GAME_WIDTH / 2,
        170,
        font="consolas 14 bold",
        text="SELECT DIFFICULTY:",
        fill="white",
        tag="diff_title"
    )

    # Difficulty buttons frame
    difficulty_menu_frame = Frame(window, bg=BACKGROUND_COLOR)

    # Create difficulty buttons
    for i, level in enumerate(DIFFICULTY_LEVELS.keys()):
        color = "#4CAF50" if level == "Easy" else "#FF9800" if level == "Medium" else "#F44336"
        hover_color = "#45a049" if level == "Easy" else "#FB8C00" if level == "Medium" else "#E53935"

        btn = Button(difficulty_menu_frame, text=level, font="consolas 14 bold",
                     command=lambda lvl=level: select_difficulty_menu(lvl),
                     bg=color, fg="white", bd=0, padx=25, pady=10,
                     activebackground=hover_color, activeforeground="white",
                     cursor="hand2", width=10)
        btn.pack(side=LEFT, padx=8)

    canvas.create_window(
        GAME_WIDTH / 2,
        215,
        window=difficulty_menu_frame,
        tag="diff_buttons"
    )

    # Selected difficulty display
    canvas.create_text(
        GAME_WIDTH / 2,
        260,
        font="consolas 12 bold",
        text=f"Current: {current_difficulty}",
        fill="#FFA500",
        tag="current_diff"
    )

    # Instructions
    instructions_text = [
        "🎮 Use Arrow Keys to Control the Snake",
        "🍎 Eat Red Food = +1 Point",
        "💎 Eat Purple Diamond = +5 Points",
    ]

    y_pos = 290
    for instruction in instructions_text:
        canvas.create_text(
            GAME_WIDTH / 2,
            y_pos,
            font="consolas 10",
            text=instruction,
            fill="#CCCCCC",
            tag="instructions"
        )
        y_pos += 18

    # Play button
    play_button = Button(
        window,
        text="▶ PLAY GAME",
        font="consolas 18 bold",
        bg="#4CAF50",
        fg="white",
        activebackground="#45a049",
        activeforeground="white",
        bd=0,
        padx=12,
        pady=5,
        cursor="hand2",
        command=start_game_from_menu
    )

    canvas.create_window(
        GAME_WIDTH / 2,
        367,
        window=play_button,
        tag="play_btn"
    )


def select_difficulty_menu(level):
    """Change difficulty from menu and update display"""
    global current_speed, current_difficulty

    current_difficulty = level
    current_speed = DIFFICULTY_LEVELS[level]

    # Update the displayed current difficulty in menu
    canvas.itemconfig("current_diff", text=f"Current: {current_difficulty}")


def start_game_from_menu():
    """Start the game from the menu"""
    global snake, food, score, direction, game_active, special_food, special_food_timer

    # Reset game variables
    score = 0
    direction = 'down'
    game_active = True
    special_food = None
    special_food_timer = None

    # Update score label
    update_score_label()

    # Clear canvas
    canvas.delete("all")

    # Show game UI
    game_ui_frame.pack(side=TOP, fill=X, pady=10)

    # Create snake and food
    snake = Snake()
    food = Food()

    # Start game
    next_turn(snake, food)


# Initialize window
window = Tk()
window.title("Snake Game - Python Edition")
window.resizable(False, False)
window.configure(bg="#1a1a1a")

# Global variables
score = 0
direction = 'down'
game_active = True
retry_button = None
menu_button = None
special_food = None
special_food_timer = None

# Set default difficulty
current_difficulty = "Medium"
current_speed = DIFFICULTY_LEVELS[current_difficulty]

# Game UI Frame (hidden initially)
game_ui_frame = Frame(window, bg="#1a1a1a")

# Top stats container
stats_container = Frame(game_ui_frame, bg="#2d2d2d", pady=8)
stats_container.pack(side=TOP, fill=X)

# Score display
score_frame = Frame(stats_container, bg="#2d2d2d")
score_frame.pack(side=LEFT, padx=20)

Label(score_frame, text="SCORE", font="consolas 10",
      bg="#2d2d2d", fg="#888888").pack()
label = Label(score_frame, text=f"{score}", font="consolas 24 bold",
              bg="#2d2d2d", fg="#00FF00")
label.pack()

# Difficulty display
difficulty_display_frame = Frame(stats_container, bg="#2d2d2d")
difficulty_display_frame.pack(side=LEFT, padx=20)

Label(difficulty_display_frame, text="DIFFICULTY", font="consolas 10",
      bg="#2d2d2d", fg="#888888").pack()
difficulty_value_label = Label(difficulty_display_frame, text=current_difficulty,
                               font="consolas 16 bold",
                               bg="#2d2d2d", fg="#FFA500")
difficulty_value_label.pack()

# Difficulty controls
difficulty_frame = Frame(stats_container, bg="#2d2d2d")
difficulty_frame.pack(side=RIGHT, padx=20)

Label(difficulty_frame, text="CHANGE DIFFICULTY", font="consolas 10",
      bg="#2d2d2d", fg="#888888").pack()

difficulty_buttons_frame = Frame(difficulty_frame, bg="#2d2d2d")
difficulty_buttons_frame.pack(pady=5)

# Create difficulty buttons
for level in DIFFICULTY_LEVELS.keys():
    color = "#4CAF50" if level == "Easy" else "#FF9800" if level == "Medium" else "#F44336"
    hover_color = "#45a049" if level == "Easy" else "#FB8C00" if level == "Medium" else "#E53935"

    btn = Button(difficulty_buttons_frame, text=level, font="consolas 11 bold",
                 command=lambda lvl=level: change_difficulty(lvl),
                 bg=color, fg="white", bd=0, padx=12, pady=5,
                 activebackground=hover_color, activeforeground="white",
                 cursor="hand2")
    btn.pack(side=LEFT, padx=3)

# Special food info
info_frame = Frame(game_ui_frame, bg="#1a1a1a", pady=5)
info_frame.pack(side=TOP, fill=X)

Label(info_frame,
      text="💎 Special Food: Purple Diamond = +5 points (appears randomly, limited time!)",
      font="consolas 10", fg="#FF00FF", bg="#1a1a1a").pack()

# Game canvas
canvas = Canvas(window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH,
                highlightthickness=2, highlightbackground="#333333")
canvas.pack()

# Update window to get actual dimensions
window.update()

# Center window on screen
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Keyboard bindings for snake control
window.bind("<Left>", lambda event: change_direction("left"))
window.bind("<Right>", lambda event: change_direction("right"))
window.bind("<Up>", lambda event: change_direction("up"))
window.bind("<Down>", lambda event: change_direction("down"))

# Show start menu instead of starting game immediately
show_start_menu()

# Run main loop
window.mainloop()