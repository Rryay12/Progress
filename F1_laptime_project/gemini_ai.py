import pygame
import random
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import math
from collections import namedtuple, deque
import logging
import os

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Placeholder Classes and Functions (REPLACE WITH YOUR ACTUAL IMPLEMENTATIONS) ---
# These are minimal implementations to allow the main script to run.
# You MUST replace these with your actual Car, RaceTrack, extention_line, and line_segments_intersection classes.

class Car:
    def __init__(self,initial_x,initial_y,initial_angle,time_elapsed):
        self.x = initial_x
        self.y = initial_y
        self.time_elapsed = time_elapsed
        
        self.speed = 1
        self.vector_angle = initial_angle
        
        self.car_angle = initial_angle
        
        self.steering_angle = 0
        self.accel = 0

        self.grip = 3
        self.steering_grip = 1.5 
        
        self.CAR_WIDTH = 20
        self.CAR_HEIGHT = 10
        self.CAR_COLOR = (0, 255, 0)
        
        self.max_angle = 80
        self.max_speed = 8
        
        self.friction_coef = 0.01
        
        self.accel_const = 0.1 
        self.brake_const = 0.1
        self.steering_const = 10
        
    def calculate_all(self):
        self.car_angle = self.car_angle * (1-self.steering_grip*self.time_elapsed) + (self.steering_angle+self.car_angle) * self.steering_grip*self.time_elapsed
        self.vector_angle = self.vector_angle * (1-self.grip*self.time_elapsed) + self.car_angle * self.grip*self.time_elapsed
        
        potential_speed = self.speed+self.accel*self.time_elapsed
        
        if((potential_speed < self.max_speed)&(potential_speed > 0)):
            self.speed = self.speed+self.accel*self.time_elapsed
        
    def update_position(self):
        self.x = self.x + self.speed*np.cos(np.radians(self.vector_angle))
        self.y = self.y + self.speed*np.sin(np.radians(self.vector_angle))
        
    def speed_up(self):
        self.accel += self.accel_const
        
    def brake(self):
        self.accel -= self.speed*self.brake_const
        
    def nothing(self):
        self.accel = 0

    def friction(self):
        self.speed -= self.speed*self.friction_coef
        
    def turn_right(self):
        if(self.steering_angle < self.max_angle):
            self.steering_angle += self.steering_const
        else:
            self.steering_angle = self.max_angle
            
    def reset_turn(self):
        if(np.abs(self.steering_angle)  < 1):
            self.steering_angle =0
        elif(self.steering_angle<0):
            self.steering_angle +=self.steering_const
        elif(self.steering_angle>0):
            self.steering_angle -=self.steering_const

    def turn_left(self):
        if(self.steering_angle > -self.max_angle):
            self.steering_angle -= self.steering_const
        else:
            self.steering_angle = -self.max_angle

    def draw(self, screen):
        car_surf = pygame.Surface((self.CAR_WIDTH, self.CAR_HEIGHT), pygame.SRCALPHA)
        car_surf.fill(self.CAR_COLOR)
        rotated_car = pygame.transform.rotate(car_surf, -self.car_angle)
        screen.blit(rotated_car, (self.x - rotated_car.get_width() / 2, self.y - rotated_car.get_height() / 2))
        
    def reset_all(self):
        self.x = 0
        self.y = 0
        
        self.speed = 0
        self.vector_angle = 0
        
        self.car_angle = 0
        
        self.steering_angle = 0
        self.accel = 0
        
    def get_vals(self):
        return self.x,self.y,self.car_angle
    
    def get_pos(self):
        return (self.x,self.y)

    def get_speed(self):
        return self.speed
        


class RaceTrack:
    """Placeholder for the RaceTrack class."""
    def __init__(self, inner_points, outer_points):
        self.inner_points = inner_points
        self.outer_points = outer_points

    def plot_track(self, screen):
        # Placeholder: Draw the track
        if len(self.inner_points) > 1:
            pygame.draw.polygon(screen, (50, 50, 50), self.outer_points, 0) # Fill outer track
            pygame.draw.polygon(screen, (0, 0, 0), self.inner_points, 0)  # Fill inner track
            pygame.draw.aalines(screen, (255, 255, 255), True, self.outer_points)
            pygame.draw.aalines(screen, (255, 255, 255), True, self.inner_points)


class extention_line:
    """Placeholder for the extention_line (sensor ray) class."""
    def __init__(self, angle, car, outer_points, inner_points, screen):
        self.angle = angle
        self.car = car
        self.outer_points = outer_points
        self.inner_points = inner_points
        self.screen = screen
        self.distance = 0.0
        self.intersection_point = None

    def update(self):
        # Placeholder: Calculate sensor ray intersection with track
        # This is a simplified version. Your actual line-intersection logic goes here.
        car_pos = self.car.get_pos()
        sensor_angle = (self.car.car_angle + self.angle) % 360
        # Create a far point for the ray
        ray_end_x = car_pos[0] + 2000 * math.cos(np.radians(sensor_angle))
        ray_end_y = car_pos[1] + 2000 * math.sin(np.radians(sensor_angle))
        ray_end_point = (ray_end_x, ray_end_y)

        min_dist = float('inf')
        closest_intersection = None

        # Check intersection with outer track
        for i in range(len(self.outer_points)):
            p1 = self.outer_points[i-1]
            p2 = self.outer_points[i]
            intersection = line_segments_intersection(car_pos, ray_end_point, p1, p2)
            if intersection:
                dist = math.hypot(intersection[0] - car_pos[0], intersection[1] - car_pos[1])
                if dist < min_dist:
                    min_dist = dist
                    closest_intersection = intersection

        # Check intersection with inner track
        for i in range(len(self.inner_points)):
            p1 = self.inner_points[i-1]
            p2 = self.inner_points[i]
            intersection = line_segments_intersection(car_pos, ray_end_point, p1, p2)
            if intersection:
                dist = math.hypot(intersection[0] - car_pos[0], intersection[1] - car_pos[1])
                if dist < min_dist:
                    min_dist = dist
                    closest_intersection = intersection

        self.distance = min_dist if min_dist != float('inf') else 2000 # Max sensor range
        self.intersection_point = closest_intersection

    def get_distance(self):
        return self.distance

    def plot(self):
        if self.intersection_point:
            pygame.draw.line(self.screen, (0, 255, 255), self.car.get_pos(), self.intersection_point, 1)


def line_segments_intersection(p1, p2, p3, p4):
    """
    Placeholder: Calculates the intersection point of two line segments.
    Returns the intersection point (x, y) or None if no intersection.
    """
    # Line 1 (p1-p2)
    x1, y1 = p1
    x2, y2 = p2
    # Line 2 (p3-p4)
    x3, y3 = p3
    x4, y4 = p4

    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return None  # Lines are parallel or collinear

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

    if 0 <= t <= 1 and 0 <= u <= 1:
        # Intersection point
        intersect_x = x1 + t * (x2 - x1)
        intersect_y = y1 + t * (y2 - y1)
        return (intersect_x, intersect_y)
    return None # No intersection within segments

# --- Game Configuration ---
class Config:
    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900
    FONT_SIZE = 30
    FPS = 60

    # Game rewards
    CHECKPOINT_SCORE = 3.0
    SPEED_REWARD_MULTIPLIER = 0.01 # Adjusted for more impact
    TIME_ALIVE_REWARD = 0.01
    STILL_PENALTY = 0.02
    COLLISION_PENALTY = -10.0

    # State normalization
    MAX_SENSOR_DISTANCE = 2000 # Max distance a sensor can read

    # RL Hyperparameters
    GAMMA = 0.99
    LR = 0.0005 # Slightly reduced learning rate for stability
    BATCH_SIZE = 64
    MEMORY_SIZE = 500_000

    EPS_START = 1.0
    EPS_END = 0.03
    EPS_DECAY = 0.9995 # Slightly faster decay

    TARGET_UPDATE_FREQ = 100 # How often to update the target network (hard copy)
    TAU = 0.005 # For soft updates (if used)

    EPISODES = 5000
    MAX_STEPS_PER_EPISODE = 1000 # Renamed TIME to MAX_STEPS_PER_EPISODE for clarity

    # Actions mapping: (acceleration, steering)
    ACTIONS = [
        (-1, -1), # Brake, turn left
        (-1, 0),  # Brake, straight
        (-1, 1),  # Brake, turn right
        (0, -1),  # No accel, turn left
        (0, 0),   # No accel, straight
        (0, 1),   # No accel, turn right
        (1, -1),  # Accel, turn left
        (1, 0),   # Accel, straight
        (1, 1)    # Accel, turn right
    ]
    ACTION_DIM = len(ACTIONS)
    STATE_DIM = 18 # Based on your get_state() output

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


    POLICY_SAVE_DIR = "policies"
    POLICY_SAVE_PREFIX = "policy_no_"

# --- Game Class ---
class Game:
    """
    Represents the racing car simulation environment.
    Handles car physics, track interaction, and reward calculation.
    """
    def __init__(self, inner_points, outer_points, angle_list, start_point,
                 draw_visuals=True, checkpoint_pos=0, starting_angle=180):
        """
        Initializes the game environment.

        Args:
            inner_points (list): List of points defining the inner track boundary.
            outer_points (list): List of points defining the outer track boundary.
            angle_list (list): List of angles for the sensor rays.
            start_point (tuple): (x, y) coordinates for the car's starting position.
            draw_visuals (bool): If True, Pygame visuals will be drawn.
            checkpoint_pos (int): Starting index for the current checkpoint.
            starting_angle (float): Initial angle of the car.
        """
        self.draw_visuals = draw_visuals
        self.my_font = pygame.font.SysFont('Comic Sans MS', Config.FONT_SIZE)

        self.checkpoint_score = Config.CHECKPOINT_SCORE
        self.speed_reward_multiplier = Config.SPEED_REWARD_MULTIPLIER
        self.time_alive_reward = Config.TIME_ALIVE_REWARD
        self.still_penalty = Config.STILL_PENALTY
        self.collision_penalty = Config.COLLISION_PENALTY

        self.car = Car(start_point[0], start_point[1], starting_angle, 1/Config.FPS)
        self.inner_points = inner_points
        self.outer_points = outer_points

        self.current_action = (0, 0) # Stores the last action taken
        self.last_car_pos = (0, 0)
        self.current_car_pos = self.car.get_pos()

        self.checkpoint_p3 = (0, 0) # Point 3 of current checkpoint line
        self.checkpoint_p4 = (0, 0) # Point 4 of current checkpoint line
        self.checkpoint_position = checkpoint_pos

        self.episode_log = [] # Log of (reward, action, state) for the current episode
        self.current_step_reward = 0.0
        self.total_episode_score = 0.0

        if self.draw_visuals:
            self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
            pygame.display.set_caption('Racing Car Simulation')
        else:
            # Create a dummy screen if not drawing, to avoid errors in placeholder classes
            self.screen = pygame.Surface((1, 1))

        self.track = RaceTrack(inner_points, outer_points)

        self.sensor_lines = []
        for angle in angle_list:
            self.sensor_lines.append(extention_line(angle, self.car, self.outer_points, self.inner_points, self.screen))

        # Perform an initial update to set up initial state and positions
        self._update_car_physics_and_sensors(Config.ACTIONS[4]) # (0,0) action for initial state
        self._calculate_score()


    def get_state(self) -> list:
        """
        Returns the current state representation of the environment.
        """
        distances = [s_line.get_distance() for s_line in self.sensor_lines]
        normalized_distances = [dist / Config.MAX_SENSOR_DISTANCE for dist in distances]

        return normalized_distances + [
            self.car.speed / self.car.max_speed,
            math.sin(np.radians(self.car.car_angle)), math.cos(np.radians(self.car.car_angle)),
            math.sin(np.radians(self.car.vector_angle)), math.cos(np.radians(self.car.vector_angle)),
            math.sin(np.radians(self.car.steering_angle)), math.cos(np.radians(self.car.steering_angle)),
            self.car.accel
        ]

    def _calculate_score(self):
        """
        Calculates the reward for the current step.
        """
        self.current_step_reward = 0.0

        # Reward for reaching checkpoints
        # Ensure checkpoint_position wraps around for continuous laps
        self.checkpoint_p3 = self.inner_points[self.checkpoint_position % len(self.inner_points)]
        self.checkpoint_p4 = self.outer_points[self.checkpoint_position % len(self.outer_points)]

        if line_segments_intersection(self.last_car_pos, self.current_car_pos, self.checkpoint_p3, self.checkpoint_p4):
            self.current_step_reward += self.checkpoint_score
            self.checkpoint_position += 1
            logging.debug(f"Checkpoint {self.checkpoint_position} reached!")

        # Bonus for staying alive (time alive reward)
        self.current_step_reward += self.time_alive_reward

        # Reward for speed
        self.current_step_reward += self.car.get_speed() * self.speed_reward_multiplier

        # Penalty for standing still
        if self.car.get_speed() < 0.5:
            self.current_step_reward -= self.still_penalty

        self.total_episode_score += self.current_step_reward

    def _is_collided_with_track(self) -> bool:
        """
        Checks if the car has collided with the track boundaries.
        """
        # Check against outer track
        for i in range(len(self.outer_points)):
            p1 = self.outer_points[i-1]
            p2 = self.outer_points[i]
            if line_segments_intersection(p1, p2, self.current_car_pos, self.last_car_pos) is not None:
                return True

        # Check against inner track
        for i in range(len(self.inner_points)):
            p1 = self.inner_points[i-1]
            p2 = self.inner_points[i]
            if line_segments_intersection(p1, p2, self.current_car_pos, self.last_car_pos) is not None:
                return True
        return False

    def _plot_checkpoint(self):
        """Draws the current checkpoint line on the screen."""
        pygame.draw.line(self.screen, (0, 255, 0), self.checkpoint_p3, self.checkpoint_p4)

    def _draw_key_indicator(self, filled: bool, coor: tuple, side: int):
        """Draws a visual indicator for key presses."""
        if filled:
            pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(coor[0], coor[1], side, side), width=0)
        else:
            pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(coor[0], coor[1], side, side), width=1)

    def _apply_action_to_car(self, action_tuple: tuple):
        """Applies the given action to the car and updates key indicators if drawing."""
        self.current_action = action_tuple

        if self.draw_visuals:
            # Define key indicator positions
            up = (1500, 700)
            down = (1500, 750)
            left = (1450, 750)
            right = (1550, 750)

            # Reset all indicators
            self._draw_key_indicator(False, up, 25)
            self._draw_key_indicator(False, down, 25)
            self._draw_key_indicator(False, left, 25)
            self._draw_key_indicator(False, right, 25)

            # Apply action and highlight active keys
            if action_tuple[0] == 1:
                self.car.speed_up()
                self._draw_key_indicator(True, up, 25)
            elif action_tuple[0] == -1:
                self.car.brake()
                self._draw_key_indicator(True, down, 25)
            else:
                self.car.nothing()

            if action_tuple[1] == 1:
                self.car.turn_left()
                self._draw_key_indicator(True, left, 25)
            elif action_tuple[1] == -1:
                self.car.turn_right()
                self._draw_key_indicator(True, right, 25)
            else:
                self.car.reset_turn()
        else:
            # Apply action without drawing
            if action_tuple[0] == 1:
                self.car.speed_up()
            elif action_tuple[0] == -1:
                self.car.brake()
            else:
                self.car.nothing()

            if action_tuple[1] == 1:
                self.car.turn_left()
            elif action_tuple[1] == -1:
                self.car.turn_right()
            else:
                self.car.reset_turn()

    def _update_car_physics_and_sensors(self, action_tuple: tuple):
        """Updates car physics and sensor readings."""
        self.last_car_pos = self.current_car_pos
        self.current_car_pos = self.car.get_pos()

        # Update sensor readings
        for s_line in self.sensor_lines:
            s_line.update()

        # Apply action and update car physics
        self._apply_action_to_car(action_tuple)
        self.car.friction()
        self.car.calculate_all()
        self.car.update_position()

    def step(self, action_index: int) -> tuple:
        """
        Performs one step in the environment given an action.

        Args:
            action_index (int): Index of the action to take from Config.ACTIONS.

        Returns:
            tuple: (next_state, reward, done, info)
                next_state (list): The new state of the environment.
                reward (float): The reward received in this step.
                done (bool): True if the episode has ended, False otherwise.
                info (dict): Additional information (empty for now).
        """
        action_tuple = Config.ACTIONS[action_index]
        done = False

        # Update car physics and sensors
        self._update_car_physics_and_sensors(action_tuple)

        # Calculate reward for the current step
        self._calculate_score()

        # Check for collision
        if self._is_collided_with_track():
            self.current_step_reward = self.collision_penalty # Apply collision penalty
            self.total_episode_score += self.current_step_reward # Add penalty to total score
            done = True
            logging.debug("Collision detected! Episode over.")

        # Log current step's data
        self.episode_log.append([self.current_step_reward, self.current_action, self.get_state()])

        # Render visuals if enabled
        if self.draw_visuals:
            self.screen.fill((0, 0, 0))
            self.track.plot_track(self.screen)
            self.car.draw(self.screen)

            for s_line in self.sensor_lines:
                s_line.plot()

            self._plot_checkpoint()

            # Display total score
            text_surface = self.my_font.render(f"Score: {self.total_episode_score:.2f}", True, (255, 255, 0))
            self.screen.blit(text_surface, (50, 50))
            pygame.display.update()
            pygame.time.Clock().tick(Config.FPS)

        return self.get_state(), self.current_step_reward, done, {}

    def reset(self, start_pos_angle_checkpoint: tuple) -> list:
        """
        Resets the environment to a new starting state.

        Args:
            start_pos_angle_checkpoint (tuple): (x, y, angle, checkpoint_index) for reset.

        Returns:
            list: The initial state of the reset environment.
        """
        x, y, angle, checkpoint_idx = start_pos_angle_checkpoint
        self.car = Car(x, y, angle, 1/Config.FPS)
        self.checkpoint_position = checkpoint_idx
        self.current_action = (0, 0)
        self.last_car_pos = (0, 0)
        self.current_car_pos = self.car.get_pos()
        self.episode_log = []
        self.current_step_reward = 0.0
        self.total_episode_score = 0.0

        # Re-initialize sensor lines with the new car instance
        self.sensor_lines = []
        for sensor_angle in self.original_angle_list: # Assuming you store this
            self.sensor_lines.append(extention_line(sensor_angle, self.car, self.outer_points, self.inner_points, self.screen))

        # Perform an initial update to set up initial state and positions
        self._update_car_physics_and_sensors(Config.ACTIONS[4]) # (0,0) action for initial state
        self._calculate_score()

        return self.get_state()

    def get_total_episode_score(self) -> float:
        """Returns the total score accumulated in the current episode."""
        return self.total_episode_score

    def get_episode_log(self) -> list:
        """Returns the log of (reward, action, state) for the current episode."""
        return self.episode_log

# --- Utility Functions ---
def calculate_angle(in_point: tuple, out_point: tuple) -> float:
    """Calculates the angle of a line segment."""
    dx = out_point[0] - in_point[0]
    dy = out_point[1] - in_point[1]
    angle_rad = np.arctan2(dy, dx)
    angle_deg = np.degrees(angle_rad) # Angle relative to x-axis
    return angle_deg

def calculate_midpoint(p1: tuple, p2: tuple) -> tuple:
    """Calculates the midpoint between two points."""
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2

def calculate_start_params(inner_points: list, outer_points: list) -> tuple:
    """
    Calculates a random starting position, angle, and checkpoint for the car.
    """
    checkpoint_start_idx = random.randint(0, len(inner_points) - 1)
    inner = inner_points[checkpoint_start_idx]
    outer = outer_points[checkpoint_start_idx]

    pos_x, pos_y = calculate_midpoint(inner, outer)
    # Calculate angle perpendicular to the checkpoint line, pointing towards the track
    angle = calculate_angle(inner, outer) + 90 # Adjust to point towards the track
    return pos_x, pos_y, angle, checkpoint_start_idx

# --- DQN Model ---
class DQN(nn.Module):
    """Deep Q-Network model."""
    def __init__(self, state_dim: int, action_dim: int):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 64)
        self.out = nn.Linear(64, action_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.out(x)

# --- Replay Memory ---
Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward', 'done'))

class ReplayMemory:
    """Experience Replay Memory."""
    def __init__(self, capacity: int):
        self.memory = deque(maxlen=capacity)

    def push(self, *args):
        """Saves a transition."""
        self.memory.append(Transition(*args))

    def sample(self, batch_size: int) -> list:
        """Randomly samples a batch of transitions."""
        return random.sample(self.memory, batch_size)

    def __len__(self) -> int:
        """Returns the current size of the memory."""
        return len(self.memory)

# --- Main Training Loop ---
def main():
    pygame.init() # Initialize Pygame

    # Example track points (REPLACE WITH YOUR ACTUAL TRACK DATA)
    # These points define a simple rectangular track for demonstration
    inner_points = [(500, 200), (1100, 200), (1100, 700), (500, 700)]
    outer_points = [(400, 100), (1200, 100), (1200, 800), (400, 800)]
    # angle_list = [-90, -45, 0, 45, 90] # Example sensor angles - Has 5 elements

    # --- FIX: Update angle_list to have 10 elements to match STATE_DIM = 18 (10 + 8 = 18) ---
    # You can adjust these angles based on how you want your sensors to be positioned.
    # This is just an example list with 10 angles.
    angle_list = [-135, -90, -60, -30, -15, 15, 30, 60, 90, 135] # Example sensor angles - Now has 10 elements
    # -----------------------------------------------------------------------------------


    # Create directory for saving policies if it doesn't exist
    os.makedirs(Config.POLICY_SAVE_DIR, exist_ok=True)

    memory = ReplayMemory(Config.MEMORY_SIZE)
    policy_dqn = DQN(Config.STATE_DIM, Config.ACTION_DIM).to(Config.device)
    target_dqn = DQN(Config.STATE_DIM, Config.ACTION_DIM).to(Config.device)

    # Load existing policy if available
    # This logic assumes 'count' and 'version' track the latest saved model
    # You might want a more robust way to find the latest model, e.g., by timestamp
    start_episode = 0
    model_count = 0
    model_version = 0

    # Simple logic to try and load the latest model
    # In a real scenario, you'd iterate through files or store metadata
    try:
        # Assuming you want to resume from the highest count/version found
        # This part needs to be more sophisticated if you have many saved models
        # For simplicity, let's assume we start fresh or load a specific one.
        # If you want to resume, you'd need to load `count` and `version` too.
        # For this example, we'll just try to load the last one saved.
        # You'd need a way to track the last `count` and `version`
        # For now, let's assume no prior models are loaded unless specified.
        pass # No loading by default for this example, start fresh
    except FileNotFoundError:
        logging.info("No pre-trained policy found, starting training from scratch.")
    except Exception as e:
        logging.warning(f"Error loading policy: {e}. Starting training from scratch.")

    target_dqn.load_state_dict(policy_dqn.state_dict())
    target_dqn.eval() # Set target network to evaluation mode

    optimizer = optim.Adam(policy_dqn.parameters(), lr=Config.LR)
    criterion = nn.SmoothL1Loss()

    epsilon = Config.EPS_START
    # No need to adjust EPS_START dynamically, it decays from its initial value

    episode_total_scores = []
    episode_losses_mean = []

    for episode in range(start_episode, Config.EPISODES):
        is_evaluation_episode = (episode % Config.TARGET_UPDATE_FREQ == 0) # Use TARGET_UPDATE_FREQ for evaluation
        draw_visuals_this_episode = is_evaluation_episode # Draw visuals only for evaluation episodes

        # Calculate starting position, angle, and checkpoint
        start_x, start_y, start_angle, start_checkpoint = calculate_start_params(inner_points, outer_points)

        env = Game(inner_points, outer_points, angle_list,
                   (start_x, start_y), draw_visuals_this_episode, start_checkpoint, start_angle)
        # Store original angle list for reset
        env.original_angle_list = angle_list # Store the updated angle_list

        state = env.get_state()
        current_episode_loss_list = []

        for t in range(Config.MAX_STEPS_PER_EPISODE):
            # Select action based on epsilon-greedy policy
            if random.random() < epsilon and not is_evaluation_episode:
                action_index = random.randint(0, Config.ACTION_DIM - 1)
            else:
                with torch.no_grad():
                    state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(Config.device)
                    q_values = policy_dqn(state_tensor)
                    action_index = q_values.argmax(dim=1).item()

            # Take a step in the environment
            next_state, reward, done, _ = env.step(action_index)

            # Store the transition in replay memory
            memory.push(
                torch.tensor(state, dtype=torch.float32),
                action_index,
                torch.tensor(next_state, dtype=torch.float32),
                reward,
                done
            )

            state = next_state # Update current state

            # Perform a learning step if enough samples are in memory
            if len(memory) >= Config.BATCH_SIZE:
                transitions = memory.sample(Config.BATCH_SIZE)
                batch = Transition(*zip(*transitions))

                # Convert batch to tensors
                states_batch = torch.stack(batch.state).to(Config.device)
                actions_batch = torch.tensor(batch.action, dtype=torch.long).to(Config.device)
                rewards_batch = torch.tensor(batch.reward, dtype=torch.float32).to(Config.device)
                next_states_batch = torch.stack(batch.next_state).to(Config.device)
                dones_batch = torch.tensor(batch.done, dtype=torch.float32).to(Config.device)

                # Compute Q-values for current states
                q_values = policy_dqn(states_batch).gather(1, actions_batch.unsqueeze(1)).squeeze(1)

                # Compute V(s') for next states using Double DQN
                with torch.no_grad():
                    # Select best action from policy network
                    next_action_selection = policy_dqn(next_states_batch).argmax(dim=1)
                    # Evaluate that action using target network
                    next_q_values = target_dqn(next_states_batch).gather(1, next_action_selection.unsqueeze(1)).squeeze(1)

                # Compute the expected Q-values
                expected_q_values = rewards_batch + Config.GAMMA * next_q_values * (1 - dones_batch)

                # Compute loss
                loss = criterion(q_values, expected_q_values.detach())
                current_episode_loss_list.append(loss.item()) # Use .item() for scalar value

                # Optimize the model
                optimizer.zero_grad()
                loss.backward()
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(policy_dqn.parameters(), max_norm=1.0)
                optimizer.step()

            if done:
                break # End episode if car collides

        # Epsilon decay
        epsilon = max(Config.EPS_END, epsilon * Config.EPS_DECAY)

        # Log episode results
        episode_score = env.get_total_episode_score()
        episode_total_scores.append(episode_score)
        avg_loss = np.mean(current_episode_loss_list) if current_episode_loss_list else 0.0
        episode_losses_mean.append(avg_loss)

        logging.info(f"Episode {episode + 1}/{Config.EPISODES}, Score: {episode_score:.2f}, "
                     f"Epsilon: {epsilon:.3f}, Avg Loss: {avg_loss:.4f}")

        # Update target network and save policy
        if episode % Config.TARGET_UPDATE_FREQ == Config.TARGET_UPDATE_FREQ - 1:
            # Hard update (copy weights)
            target_dqn.load_state_dict(policy_dqn.state_dict())
            # Soft update (uncomment and use TAU if preferred)
            # for target_param, policy_param in zip(target_dqn.parameters(), policy_dqn.parameters()):
            #     target_param.data.copy_(Config.TAU * policy_param.data + (1.0 - Config.TAU) * target_param.data)

            # Save policy
            model_count += 1
            policy_path = os.path.join(Config.POLICY_SAVE_DIR, f"{Config.POLICY_SAVE_PREFIX}{model_count}-{model_version}.pth")
            torch.save(policy_dqn.state_dict(), policy_path)
            logging.info(f"Policy saved to {policy_path}")
            model_version += 1 # Increment version for next save

            # Save scores and losses to CSV
            np.savetxt(os.path.join(Config.POLICY_SAVE_DIR, "episode_scores.csv"), episode_total_scores, delimiter=",", fmt='%s')
            np.savetxt(os.path.join(Config.POLICY_SAVE_DIR, "episode_losses.csv"), episode_losses_mean, delimiter=",", fmt='%s')
            logging.info("Scores and losses saved.")


    pygame.quit() # Quit Pygame when training is complete

if __name__ == "__main__":
    main()