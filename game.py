import pygame
from pygame.locals import *
import random

# Screen dimensions
size = width, height = (1500, 1700)
roadWidth = int(width / 1.6)
roadMarkWidth = int(roadWidth / 30)
roadMarkHeight = int(height / 20)

# Dashed line parameters
dash_length = 200
space_between_dashes = 150
middle_line_width = roadMarkWidth
dashOffset = 0

# Tree positions
treesPositions = []

# Info board variables
board_timer = 0
board_interval = [30, 20, 10, 30, 5, 40]
current_interval_index = 0
board_side = random.choice([-1, 1])
board_y = 0
board_speed = 5
city_names = ["Belval", "Kirchberg", "Schieren", "Ettelbruck", "Wiltz"]
current_city = random.choice(city_names)

# Speeds
player_base_speed = 0.25  # Base speed for lateral movement
player_min_speed = 0  # Minimum forward speed
player_max_speed = 62  # Maximum forward speed
player_acceleration = 0.5  # How quickly player accelerates
player_deceleration = 0.3  # How quickly player decelerates

# All other cars keep constant speed
left_lane_car_speed = 10
right_lane_car_speed = 10  # Base speed for cars in the right lane
tree_speed = 5

# Current player speed (will change with acceleration/deceleration)
current_player_speed = player_min_speed


# Define column offsets
column_offset = 100  # Horizontal spacing between columns

# Left lane column positions
lane_x_left_col1 = width / 2 - roadWidth / 4 - column_offset
lane_x_left_col2 = width / 2 - roadWidth / 4 + column_offset

# Right lane column positions
lane_x_right_col1 = width / 2 + roadWidth / 4 - column_offset
lane_x_right_col2 = width / 2 + roadWidth / 4 + column_offset


# Variables for scroll speed
start_time = pygame.time.get_ticks()
scroll_speed_multiplier = 1
scroll_speed_increase_time = 30000  # 30 seconds before speed increases

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Car Game")

# Colors
grassColor = (60, 220, 0)
roadColor = (50, 50, 50)
lineColor = (255, 255, 255)

enemy_cars = []


def is_overlapping(new_rect, existing_cars, min_vertical_spacing=500):
    """Check if the new car overlaps with existing cars."""
    # Create a larger buffer zone around the new car
    buffer_zone = pygame.Rect(
        new_rect.x - 20,  # Horizontal buffer
        new_rect.y - min_vertical_spacing // 2,  # Vertical buffer
        new_rect.width + 40,  # Wider buffer
        new_rect.height + min_vertical_spacing,  # Taller buffer
    )

    # Check against all existing cars
    for _, car in existing_cars:
        if car.colliderect(buffer_zone):
            return True
    return False


def update_oppositCar(
    enemy_cars,
    car_speed,
    height,
    width,
    roadWidth,
    scroll_speed_multiplier,
    current_player_speed,
):
    # Create a list to store cars to keep
    cars_to_keep = []

    for car_image, car in enemy_cars[:]:
        # Determine direction based on lane position
        is_left_lane = car.centerx < width / 2

        # Left lane cars move down at constant speed
        if is_left_lane:
            # car.y += right_lane_car_speed
            # 1) When Porsche is stopped or moving very slowly
            if current_player_speed <= 0.5 * left_lane_car_speed:
                car.y += left_lane_car_speed  # Cars move downward at base speed

            # 2) When Porsche is accelerating but still slower than left-lane cars
            elif current_player_speed < left_lane_car_speed:
                relative_speed = left_lane_car_speed - current_player_speed
                car.y += relative_speed  # Cars move downward more quickly

            # 3) When Porsche is faster than left-lane cars
            else:
                relative_speed = current_player_speed - left_lane_car_speed
                car.y += relative_speed  # Cars appear to move upward (being overtaken)

            # When car goes off screen, replace it
            if car.y > height:
                new_car_image = pygame.transform.rotate(
                    random.choice(oppositCar_images), 180
                )
                new_y = -car.height  # Respawn at top for left lane
                lane_x = width / 2 - roadWidth / 4
                new_car_rect = new_car_image.get_rect(center=(lane_x, new_y))

                # Only add the car if it doesn't overlap with existing cars
                if not is_overlapping(new_car_rect, enemy_cars, 400):
                    cars_to_keep.append((new_car_image, new_car_rect))
                # If there's overlap, don't add this car back
            else:
                # Keep this car as is
                cars_to_keep.append((car_image, car))
        else:
            # RIGHT LANE CARS - Their movement depends on player's speed

            # 1) When Porsche is stopped or moving very slowly
            if current_player_speed <= 0.5 * right_lane_car_speed:
                car.y -= car_speed  # Cars move upward
                # Respawn from below when they exit the top
                if car.y < -car.height:
                    replace_car = True
                    new_car_image = random.choice(oppositCar_images)
                    new_y = height + random.randint(100, 400)
                    lane_x = width / 2 + roadWidth / 4
                    new_car_rect = new_car_image.get_rect(center=(lane_x, new_y))

                    if not is_overlapping(new_car_rect, enemy_cars, 400):
                        cars_to_keep.append((new_car_image, new_car_rect))
                    # If there's overlap, don't add this car back
                else:
                    cars_to_keep.append((car_image, car))

            # 2) When Porsche is accelerating but still slower than other cars
            elif current_player_speed < right_lane_car_speed:
                # Cars still move up but more slowly (relative speed difference)
                relative_speed = right_lane_car_speed - current_player_speed
                car.y -= relative_speed

                # Respawn from below when they exit the top
                if car.y < -car.height:
                    replace_car = True
                    new_car_image = random.choice(oppositCar_images)
                    new_y = height + random.randint(100, 400)
                    lane_x = width / 2 + roadWidth / 4
                    new_car_rect = new_car_image.get_rect(center=(lane_x, new_y))

                    if not is_overlapping(new_car_rect, enemy_cars, 400):
                        cars_to_keep.append((new_car_image, new_car_rect))
                    # If there's overlap, don't add this car back
                else:
                    # Keep this car as is
                    cars_to_keep.append((car_image, car))

            # 3) When Porsche is faster than the other cars
            else:
                # Cars move down (being passed by player)
                relative_speed = current_player_speed - right_lane_car_speed
                car.y += relative_speed

                # Respawn from top when they exit the bottom
                if car.y > height:
                    replace_car = True
                    new_car_image = random.choice(oppositCar_images)
                    new_y = -car.height - random.randint(100, 400)
                    lane_x = width / 2 + roadWidth / 4
                    new_car_rect = new_car_image.get_rect(center=(lane_x, new_y))

                    if not is_overlapping(new_car_rect, enemy_cars, 400):
                        cars_to_keep.append((new_car_image, new_car_rect))
                    # If there's overlap, don't add this car back
                else:
                    # Keep this car as is
                    cars_to_keep.append((car_image, car))

    # Replace the entire enemy_cars list with our new list
    enemy_cars.clear()
    enemy_cars.extend(cars_to_keep)


def draw_oppositCar(enemy_cars, screen):
    for car_image, car in enemy_cars:
        screen.blit(car_image, (car.x, car.y))


def generate_tree_positions():
    for _ in range(30):
        side = random.choice([-1, 1])
        if side == -1:
            x = random.randint(1, int(width / 2 - roadWidth / 2 - 180))
        else:
            x = random.randint(int(width / 2 + roadWidth / 2 + 50), width - 150)
        y = random.randint(-height, height)
        tree_type = random.choice(["tree1", "tree2"])
        treesPositions.append([x, y, tree_type])


def draw_trees(tree_images):
    for position in treesPositions:
        tree_type = position[2]
        screen.blit(tree_images[tree_type], (position[0], position[1]))


def load_board_image():
    try:
        return pygame.image.load("info_board.png")
    except FileNotFoundError:
        print("Missing 'info_board.png'")
        exit()
    

def draw_board(board_image, font, player_speed=0):
    global current_city

    board_x = width - board_image.get_width() - 200  # Keep original right-side behavior

    # Draw the board image
    screen.blit(board_image, (board_x, board_y))

    # Render and center the city text
    city_text = font.render(current_city, True, (0, 0, 0))
    text_x = board_x + (board_image.get_width() - city_text.get_width()) // 2
    text_y = board_y + (board_image.get_height() - (city_text.get_height()) - 60) // 2

    screen.blit(city_text, (text_x, text_y))

def move_trees(speed):
    for tree in treesPositions:
        tree[1] += speed
        if tree[1] > height:
            side = random.choice([-1, 1])
            if side == -1:
                tree[0] = random.randint(50, int(width / 2 - roadWidth / 2 - 50))
            else:
                tree[0] = random.randint(
                    int(width / 2 + roadWidth / 2 + 50), width - 50
                )
            tree[1] = -30




def draw_timer():
    """Draws a timer at the top middle of the screen."""
    # Calculate elapsed time in seconds
    current_time = pygame.time.get_ticks()
    elapsed_time_ms = current_time - start_time  # Use stored start_time
    elapsed_time_seconds = elapsed_time_ms // 1000  # Convert milliseconds to seconds

    # Format the timer text
    timer_text = f"Time: {elapsed_time_seconds} s"

    # Render the timer text
    font = pygame.font.SysFont('impact, fantasy', 60, True, True)
    text_surface = font.render(timer_text, True, (255,165,0))

    # Draw the timer on the screen
    screen.blit(text_surface, ((width // 2 - text_surface.get_width() // 2), 20))
    
    
    
def draw_road():
    screen.fill(grassColor)
    pygame.draw.rect(
        screen, roadColor, (width / 2 - roadWidth / 2, 0, roadWidth, height)
    )
    pygame.draw.rect(
        screen,
        lineColor,
        (width / 2 - roadWidth / 2 + roadMarkWidth, 0, roadMarkWidth, height),
    )
    pygame.draw.rect(
        screen,
        lineColor,
        (width / 2 + roadWidth / 2 - roadMarkWidth * 2, 0, roadMarkWidth, height),
    )
    y_position = -dashOffset
    while y_position < height:
        pygame.draw.rect(
            screen,
            lineColor,
            (
                width / 2 - middle_line_width / 2,
                y_position,
                middle_line_width,
                dash_length,
            ),
        )
        y_position += dash_length + space_between_dashes


def initialize_cars():
    try:
        car = pygame.image.load("Porsche.png")
        oppositCar_images = [pygame.image.load(f"car{i}.png") for i in range(1, 9)]
    except FileNotFoundError:
        print("Missing car image files")
        exit()
    # Position the Porsche at the right edge of the road to avoid initial collisions
    car_loc = car.get_rect(
        center=(
            width / 2 + roadWidth / 2 - car.get_width() / 2 - roadMarkWidth * 2,
            height * 0.8,
        )
    )
    return car, car_loc, oppositCar_images


def draw_cars(car, car_loc):
    screen.blit(car, car_loc)


def load_tree_image():
    try:
        return {
            "tree1": pygame.image.load("tree1.png"),
            "tree2": pygame.image.load("tree2.png"),
        }
    except FileNotFoundError:
        print("Missing tree image files")
        exit()


# Preload assets
generate_tree_positions()

# Initialize player car
car, car_loc, oppositCar_images = initialize_cars()


def initialize_enemy_cars(num_cars=5):
    """Initialize enemy cars with proper spacing."""
    enemy_cars.clear()

    # Determine how many cars for each lane
    left_lane_cars = num_cars // 2
    right_lane_cars = num_cars - left_lane_cars

    # Minimum vertical distance between cars
    min_vertical_distance = 500

    # Left lane cars (moving down)
    for i in range(left_lane_cars):
        # Alternate between the two columns
        lane_x = lane_x_left_col1 if i % 2 == 0 else lane_x_left_col2
        car_image = pygame.transform.rotate(random.choice(oppositCar_images), 180)
        car_y = -200 - (i * min_vertical_distance)
        enemy_car_rect = car_image.get_rect(center=(lane_x, car_y))
        enemy_cars.append((car_image, enemy_car_rect))

    # Right lane cars (moving up)
    for i in range(right_lane_cars):
        # Alternate between the two columns
        lane_x = lane_x_right_col1 if i % 2 == 0 else lane_x_right_col2
        car_image = random.choice(oppositCar_images)
        car_y = height + 200 + (i * min_vertical_distance)
        enemy_car_rect = car_image.get_rect(center=(lane_x, car_y))
        enemy_cars.append((car_image, enemy_car_rect))



def load_collision_image():
    try:
        collision1 = pygame.image.load("collision1.png")
        collision2 = pygame.image.load("collision2.png")
        collision3 = pygame.image.load("collision3.png")
        return collision1, collision2, collision3
    except FileNotFoundError:
        print("Missing collision image files")
        exit()
        
        
def display_collision(car_loc):
    # Load the collision images
    collision1, collision2, collision3 = load_collision_image()
    
    # Create a list of collision images
    collision_images = [collision1, collision2, collision3]
    
    # Redraw the background for each image to ensure clean display
    for image in collision_images:
        # Redraw the scene to clear previous collision image
        draw_road()
        draw_trees(load_tree_image())
        draw_oppositCar(enemy_cars, screen)
        
        # Draw the collision image at the car's location
        screen.blit(image, car_loc)
        
        # Update the display to show the collision
        pygame.display.update()
        
        # Wait for 5 seconds for each image
        pygame.time.delay(200)

def print_GameOver():
    font = pygame.font.SysFont('impact, fantasy', 180, True, True)
    text = font.render("Game Over", True, (255, 0, 0))
    text_rect = text.get_rect(center=(width // 2, height // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(4000)
    
    if(keys[K_ESCAPE]):
        pygame.quit()
        exit()



initialize_enemy_cars()

# Main loop
running = True
clock = pygame.time.Clock()
current_player_speed = player_min_speed
is_accelerating = False
board_image = load_board_image()
is_moving_backward = False

while running:
    clock.tick(20)
    is_accelerating = False
    is_moving_backward = False

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False

    keys = pygame.key.get_pressed()

    # First handle key presses and calculate player speed
    if keys[K_SPACE]:
        current_player_speed = 0
        # Prevent vertical movement while speed is zero
        car_loc.y = max(car_loc.y, 600)  # Keep the car at a minimum vertical position
    elif keys[K_UP]:
        # Speeds
        player_base_speed += 0.25
        is_accelerating = True
        if current_player_speed < player_max_speed:
            current_player_speed += player_acceleration
            if current_player_speed > player_max_speed:
                current_player_speed = player_max_speed
        if car_loc.top > 600:
            car_loc.y -= player_base_speed
        else:
            car_loc.y = 600
        dashOffset -= current_player_speed * scroll_speed_multiplier
        move_trees(current_player_speed * scroll_speed_multiplier)

    if keys[K_RCTRL]:
        if current_player_speed <= 0:
            current_player_speed = player_min_speed
        else:
            current_player_speed -= player_acceleration * 0.6

    if keys[K_DOWN] and car_loc.bottom < height:
        car_loc.y += player_base_speed
        if current_player_speed > player_min_speed:
            current_player_speed -= player_deceleration
            if current_player_speed < player_min_speed:
                current_player_speed = player_min_speed
        dashOffset += current_player_speed * scroll_speed_multiplier
        move_trees(-current_player_speed * scroll_speed_multiplier)
        # Check if we should move backward
        if current_player_speed <= 0:
            is_moving_backward = True
            dashOffset -= player_base_speed * scroll_speed_multiplier
            move_trees(player_base_speed * scroll_speed_multiplier)
        else:
            # Normal slow down behavior
            dashOffset += current_player_speed / 2 * scroll_speed_multiplier
            move_trees(-current_player_speed / 2 * scroll_speed_multiplier)

    if keys[K_LEFT] and car_loc.left > width / 2 - roadWidth / 2:
        car_loc.x -= player_base_speed

    if keys[K_RIGHT] and car_loc.right < width / 2 + roadWidth / 2:
        car_loc.x += player_base_speed

    if not is_accelerating and not keys[K_DOWN]:
        if current_player_speed > player_min_speed:
            current_player_speed -= player_deceleration
            if current_player_speed < player_min_speed:
                current_player_speed = player_min_speed
        dashOffset -= current_player_speed * scroll_speed_multiplier
        move_trees(current_player_speed * scroll_speed_multiplier)

    # Now update the board position based on player's movement
    if current_player_speed > 0:
        # Moving forward - board moves down
        board_y += current_player_speed * scroll_speed_multiplier
    elif is_moving_backward:
        # Moving backward - board moves up
        board_y -= player_base_speed
        treesPositions[0][1] -= player_base_speed
    # When stopped, board doesn't move

    # Reset board position when it goes off-screen and change city name
    if board_y > height:
        board_y = -board_image.get_height()
        current_city = random.choice(city_names)
        board_side = random.choice([-1, 1])
    # If board moves above the screen (when going backwards)
    elif board_y < -board_image.get_height():
        board_y = height
        current_city = random.choice(city_names)
        board_side = random.choice([-1, 1])

    elapsed_time = pygame.time.get_ticks() - start_time
    if elapsed_time >= scroll_speed_increase_time:
        scroll_speed_multiplier = 2

    if(keys[K_ESCAPE]):
        pygame.quit()
        exit()

    # Pass the current player speed to update_oppositCar
    update_oppositCar(
        enemy_cars,
        left_lane_car_speed,
        height,
        width,
        roadWidth,
        scroll_speed_multiplier,
        current_player_speed,
    )
    dashOffset %= dash_length + space_between_dashes

    # Keep adding cars if we have fewer than expected
    if len(enemy_cars) < 5:
        # Add a new car
        lane_side = random.choice(["left", "right"])
        lane_x = (
            width / 2 - roadWidth / 4
            if lane_side == "left"
            else width / 2 + roadWidth / 4
        )

        if lane_side == "left":
            car_image = pygame.transform.rotate(random.choice(oppositCar_images), 180)
            car_y = -200 - random.randint(
                300, 800
            )  # Spawn further above screen with larger random range
        else:
            car_image = random.choice(oppositCar_images)
            # Spawn below or above based on current relative speed
            if current_player_speed < right_lane_car_speed:
                car_y = height + random.randint(300, 800)  # Spawn further below screen
            else:
                car_y = -200 - random.randint(300, 800)  # Spawn further above screen

        new_car_rect = car_image.get_rect(center=(lane_x, car_y))

        # Only add if it doesn't overlap - use larger spacing (600)
        if not is_overlapping(new_car_rect, enemy_cars, 600):
            enemy_cars.append((car_image, new_car_rect))

    # Draw everything in correct order
    draw_road()
    draw_trees(load_tree_image())
    draw_oppositCar(enemy_cars, screen)
    draw_cars(car, car_loc)
    draw_board(
        board_image, pygame.font.Font(None, 20)
    )  # Increased font size for better visibility
    draw_timer()
    pygame.display.update()

    # Check for collisions
    for _, enemy_car in enemy_cars:
        if car_loc.colliderect(enemy_car):
            # First show the collision image
            display_collision(car_loc)
            # Then show game over screen
            print_GameOver()
            running = False
            break

pygame.quit()