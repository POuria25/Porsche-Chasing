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
board_y = -200
board_speed = 5
city_names = ["Belval", "Kirchberg", "Schieren", "Ettelbruck", "Wiltz"]
current_city = random.choice(city_names)

# Speeds
player_base_speed = 15  # Base speed for lateral movement
player_min_speed = 0    # Minimum forward speed
player_max_speed = 62   # Maximum forward speed
player_acceleration = 0.5  # How quickly player accelerates
player_deceleration = 0.3  # How quickly player decelerates

# All other cars keep constant speed
left_lane_car_speed = 10
right_lane_car_speed = 10  # Base speed for cars in the right lane
tree_speed = 5

# Current player speed (will change with acceleration/deceleration)
current_player_speed = player_min_speed

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
    # Create a larger buffer zone around the new car to ensure greater spacing
    buffer_zone = pygame.Rect(
        new_rect.x - 10,  # Add horizontal buffer as well
        new_rect.y - min_vertical_spacing // 2, 
        new_rect.width + 20,  # Wider buffer
        new_rect.height + min_vertical_spacing
    )
    
    # Check against all existing cars
    for _, car in existing_cars:
        # Create an extended zone for each existing car
        car_extended = pygame.Rect(
            car.x - 10,
            car.y - min_vertical_spacing // 2,
            car.width + 20,
            car.height + min_vertical_spacing
        )
        
        # If either buffer zones collide, we have an overlap
        if buffer_zone.colliderect(car_extended):
            return True
    return False

def update_oppositCar(enemy_cars, car_speed, height, width, roadWidth, scroll_speed_multiplier, current_player_speed):
    # Create a list to store cars to keep
    cars_to_keep = []
    
    for car_image, car in enemy_cars[:]:
        # Determine direction based on lane position
        is_left_lane = car.centerx < width / 2
        
        # Flag to track if we need to replace this car
        replace_car = False

        # Left lane cars move down at constant speed
        if is_left_lane:
            #car.y += right_lane_car_speed
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
                replace_car = True
                new_car_image = pygame.transform.rotate(random.choice(oppositCar_images), 180)
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
                    # Keep this car as is
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

def draw_board(board_image, font):
    global board_y, current_city
    board_x = 50 if board_side == -1 else width - board_image.get_width() - 50
    screen.blit(board_image, (board_x, board_y))
    city_text = font.render(current_city, True, (0, 0, 0))
    text_x = board_x + (board_image.get_width() - city_text.get_width()) // 2
    text_y = board_y + (board_image.get_height() - city_text.get_height()) // 2
    screen.blit(city_text, (text_x, text_y))

def move_trees(speed):
    for tree in treesPositions:
        tree[1] += speed
        if tree[1] > height:
            side = random.choice([-1, 1])
            if side == -1:
                tree[0] = random.randint(50, int(width / 2 - roadWidth / 2 - 50))
            else:
                tree[0] = random.randint(int(width / 2 + roadWidth / 2 + 50), width - 50)
            tree[1] = -30

def draw_road():
    screen.fill(grassColor)
    pygame.draw.rect(screen, roadColor, (width / 2 - roadWidth / 2, 0, roadWidth, height))
    pygame.draw.rect(screen, lineColor, (width / 2 - roadWidth / 2 + roadMarkWidth, 0, roadMarkWidth, height))
    pygame.draw.rect(screen, lineColor, (width / 2 + roadWidth / 2 - roadMarkWidth * 2, 0, roadMarkWidth, height))
    y_position = -dashOffset
    while y_position < height:
        pygame.draw.rect(screen, lineColor,
                         (width / 2 - middle_line_width / 2, y_position, middle_line_width, dash_length))
        y_position += dash_length + space_between_dashes

def initialize_cars():
    try:
        car = pygame.image.load("Porsche.png")
        oppositCar_images = [
            pygame.image.load(f"car{i}.png") for i in range(1, 9)
        ]
    except FileNotFoundError:
        print("Missing car image files")
        exit()
    # Position the Porsche at the right edge of the road to avoid initial collisions
    car_loc = car.get_rect(center=(width / 2 + roadWidth / 2 - car.get_width()/2 - roadMarkWidth * 2, height * 0.8))
    return car, car_loc, oppositCar_images

def draw_cars(car, car_loc):
    screen.blit(car, car_loc)

def load_tree_image():
    try:
        return {"tree1": pygame.image.load("tree1.png"), "tree2": pygame.image.load("tree2.png")}
    except FileNotFoundError:
        print("Missing tree image files")
        exit()

# Preload assets
tree_images = load_tree_image()
board_image = load_board_image()
font = pygame.font.Font(None, 30)
generate_tree_positions()

# Initialize player car
car, car_loc, oppositCar_images = initialize_cars()

def initialize_enemy_cars(num_cars=5):
    """Initialize enemy cars with proper spacing."""
    enemy_cars.clear()
    left_lane_cars = num_cars // 2
    right_lane_cars = num_cars - left_lane_cars
    
    # Much larger spacing to prevent overlaps
    min_vertical_distance = 500
    
    # Left lane cars (moving down)
    for i in range(left_lane_cars):
        lane_x = width / 2 - roadWidth / 4
        car_image = pygame.transform.rotate(random.choice(oppositCar_images), 180)
        # Place cars with significant distance between them
        car_y = -200 - (i * min_vertical_distance)
        enemy_car_rect = car_image.get_rect(center=(lane_x, car_y))
        enemy_cars.append((car_image, enemy_car_rect))

    # Right lane cars (initially moving up since player starts slow)
    for i in range(right_lane_cars):
        lane_x = width / 2 + roadWidth / 4
        car_image = random.choice(oppositCar_images)
        # Position right lane cars with even more spacing
        car_y = height + 200 + (i * min_vertical_distance)  # Start below the screen with large spacing
        enemy_car_rect = car_image.get_rect(center=(lane_x, car_y))
        enemy_cars.append((car_image, enemy_car_rect))

initialize_enemy_cars()

# Main loop
running = True
clock = pygame.time.Clock()
current_player_speed = player_min_speed
is_accelerating = False

while running:
    clock.tick(60)
    is_accelerating = False

    elapsed_time = pygame.time.get_ticks() - start_time
    if elapsed_time >= scroll_speed_increase_time:
        scroll_speed_multiplier = 2

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False

    keys = pygame.key.get_pressed()
    if keys[K_SPACE]:
        current_player_speed = 0
        # Prevent vertical movement while speed is zero
        car_loc.y = max(car_loc.y, 600)  # Keep the car at a minimum vertical position
    elif keys[K_UP]:
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
        board_y += board_speed
        if board_y > height:
            board_y = -board_image.get_height()
            board_side = random.choice([-1, 1])
            current_city = random.choice(city_names)
    if keys[K_RCTRL]:
        if current_player_speed <= 0:
            current_player_speed = player_min_speed
        else:    
            current_player_speed -= player_acceleration * 0.6
    if keys[K_DOWN] and car_loc.bottom < height:
        car_loc.y += player_base_speed
        if current_player_speed > player_min_speed:
            current_player_speed -= player_deceleration * 2
            if current_player_speed < player_min_speed:
                current_player_speed = player_min_speed
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

    # Pass the current player speed to update_oppositCar
    update_oppositCar(enemy_cars, left_lane_car_speed, height, width, roadWidth, scroll_speed_multiplier, current_player_speed)
    dashOffset %= (dash_length + space_between_dashes)

    board_timer += 5
    current_interval = board_interval[current_interval_index]
    if board_timer >= current_interval:
        board_timer = 0
        current_interval_index = (current_interval_index + 1) % len(board_interval)
        board_side = random.choice([-1, 1])
        board_y = -board_image.get_height()
        current_city = random.choice(city_names)

    # Keep adding cars if we have fewer than expected
    if len(enemy_cars) < 5:
        # Add a new car
        lane_side = random.choice(["left", "right"])
        lane_x = width / 2 - roadWidth / 4 if lane_side == "left" else width / 2 + roadWidth / 4
        
        if lane_side == "left":
            car_image = pygame.transform.rotate(random.choice(oppositCar_images), 180)
            car_y = -200 - random.randint(300, 800)  # Spawn further above screen with larger random range
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
    draw_trees(tree_images)
    draw_oppositCar(enemy_cars, screen)
    draw_cars(car, car_loc)
    draw_board(board_image, font)
    pygame.display.update()

    for _, enemy_car in enemy_cars:
        if car_loc.colliderect(enemy_car):
            print("Collision! Game Over!")
            running = False
            break

pygame.quit()