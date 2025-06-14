import numpy as np
import pandas as pd
import pygame 
import math
import matplotlib.pyplot as plt
import json
import random

import torch
import torch.nn as nn
import torch.nn.functional as F

from collections import namedtuple, deque
import torch.optim as optim

import torch
import torch.nn as nn
import torch.nn.functional as F

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
        self.steering_grip =4
        
        self.CAR_WIDTH = 20
        self.CAR_HEIGHT = 10
        self.CAR_COLOR = (0, 255, 0)
        
        self.max_angle = 40
        self.max_speed = 11
        
        self.friction_coef = 0.01
        
        self.accel_const = 0.2
        self.brake_const = 0.15
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
        self.accel -= (self.speed*self.brake_const + self.brake_const)
        
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

class extention_line:
    
    def __init__(self,angle,car:Car,outside_line,inside_line,screen):
      self.angle_from_car = angle
      self.car = car
      self.outside_line = outside_line
      self.inside_line = inside_line
      self.shortest_point = (0,0)
      self.screen = screen
      self.smallest = (0,(0,0))
    
    def get_distance(self):
        return self.smallest[0]
    
    def update(self):
        self.x,self.y,self.angle = self.car.get_vals()
        self.point1,self.point2= self.generate_long_segment_from_point((self.x,self.y),self.angle+self.angle_from_car)
        self.shortest_point = self.shortest_intersection()
    
    def plot(self):
        pygame.draw.line(self.screen,(255,255,255),self.point1,self.point2)
        pygame.draw.circle(self.screen,(255,0,0),self.shortest_point,10)
        
    def find_dist(self,x,y):

        return np.sqrt((x-self.car.x)**2+(y-self.car.y)**2)
    
    def shortest_intersection(self):
        point_list = []
        for i in range(len(self.outside_line)):
            p1 = self.outside_line[i-1]
            p2 = self.outside_line[i]
            
            intersection = line_segments_intersection(p1,p2,self.point1,self.point2)
            if (intersection is not None):
                point_list.append((self.find_dist(intersection[0],intersection[1]),intersection))
                
        for i in range(len(self.inside_line)):
            p1 = self.inside_line[i-1]
            p2 = self.inside_line[i]
            
            intersection = line_segments_intersection(p1,p2,self.point1,self.point2)
            if (intersection is not None):
                point_list.append((self.find_dist(intersection[0],intersection[1]),intersection))
                
        if len(point_list) > 0:
            self.smallest = min(point_list, key=lambda i: i[0])

            return self.smallest[1]
        else:
            return self.smallest[1]           
    
    def generate_long_segment_from_point(self,point, angle_degrees, length=10000):
        x, y = point
        angle_radians = math.radians(angle_degrees)

        dx = math.cos(angle_radians) * length
        dy = math.sin(angle_radians) * length

        end_point = (x + dx, y + dy)
        return point, end_point

def line_segments_intersection(p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        denom = (y4 - y3)*(x2 - x1) - (x4 - x3)*(y2 - y1)

        if denom == 0:
            return None

        t = ((x4 - x3)*(y1 - y3) - (y4 - y3)*(x1 - x3)) / denom
        u = ((x2 - x1)*(y1 - y3) - (y2 - y1)*(x1 - x3)) / denom

        if 0 <= t <= 1 and 0 <= u <= 1:
            intersect_x = x1 + t * (x2 - x1)
            intersect_y = y1 + t * (y2 - y1)
            return (intersect_x, intersect_y)

        return None
    
class RaceTrack:
    def __init__(self,inner_points,outer_points):
        self.inner_points = inner_points
        self.outer_points = outer_points
        
        self.track_color = (50,50,50)
        self.border_color = (255,90,90)
        self.inner_color = (255,255,255)
    
    def plot_track(self,surface):
        pygame.draw.polygon(surface,self.track_color,self.outer_points,0)
        pygame.draw.polygon(surface,self.inner_color,self.inner_points,0)
        pygame.draw.lines(surface,self.border_color,True,self.inner_points,5)
        pygame.draw.lines(surface,self.border_color,True,self.outer_points,5)
        
    
        
def generate_track(centerline, width=100):
    inner = []
    outer = []
    n = len(centerline)
    for i in range(n):
        p1 = centerline[i - 1]
        p2 = centerline[i]
        p3 = centerline[(i + 1) % n]

        # Calculate the direction between p1 and p3 (smoothed)
        dx = p3[0] - p1[0]
        dy = p3[1] - p1[1]
        length = math.hypot(dx, dy)
        if length == 0:
            perp_dx, perp_dy = 0, 0
        else:
            perp_dx = -dy / length
            perp_dy = dx / length

        offset_x = perp_dx * width / 2
        offset_y = perp_dy * width / 2

        inner.append((p2[0] - offset_x, p2[1] - offset_y))
        outer.append((p2[0] + offset_x, p2[1] + offset_y))
    
    return inner, outer


class game:
    def __init__(self,inner_points,outer_points,angle_list,start_point,draw_keys=True,checkpoint_pos = 0,starting_angle=180):
        self.draw_keys = draw_keys
        
        self.my_font = pygame.font.SysFont('Comic Sans MS', 30)

        self.checkpoint_score = 0.5
        self.speed_score_mult = 0.01
        self.crash_penalty = -1
        
        self.start_point = start_point
        
        self.car = Car(self.start_point[0],self.start_point[1],starting_angle,1/60)
        self.inner_points = inner_points
        self.outer_points = outer_points
        
        self.action = (0,0)
        
        self.last_pos = (0,0)
        self.current_pos = (0,0)
        
        self.p3 = (0,0)
        self.p4 = (0,0)
        
        self.checkpoint_position = checkpoint_pos
        
        self.log = []
        
        self.current_point = 0
        self.total_score = 0
        
        SCREEN_WIDTH = 1600
        SCREEN_HEIGHT = 900
        
        self.track = RaceTrack(inner_points,outer_points)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Racing Car Simulation')
        
        self.line_list = []
        for angle in angle_list:
            self.line_list.append(extention_line(angle,self.car,self.outer_points,self.inner_points,self.screen))
            
        self.state = self.get_state()
            
        self.safe_update((0,0))
        
    def get_state(self):
        distances = [i.get_distance() for i in self.line_list]
        MAX_DISTANCE = 1835
        return_action = [
            dist / MAX_DISTANCE for dist in distances      
        ] + [
            self.car.speed / self.car.max_speed,                              
            math.sin(np.radians(self.car.vector_angle-self.car.car_angle)), math.cos(np.radians(self.car.vector_angle-self.car.car_angle)),
            math.sin(np.radians(self.car.steering_angle)), math.cos(np.radians(self.car.steering_angle)),
            self.car.accel                                          
        ]
        
        return return_action
        
            
    def get_score(self):
        self.current_point = 0

        # Reward for reaching checkpoints
        self.p3 = self.inner_points[self.checkpoint_position % len(self.inner_points)]
        self.p4 = self.outer_points[self.checkpoint_position % len(self.outer_points)]
        if line_segments_intersection(self.last_pos, self.current_pos, self.p3, self.p4):
            self.current_point += self.checkpoint_score  # +100
            self.checkpoint_position += 1
        
        self.current_point += (self.car.speed-0.3)*self.speed_score_mult

        self.total_score += self.current_point
        
    def is_collided_with_track(self):
        for i in range(len(self.outer_points)):
            p1 = self.outer_points[i-1]
            p2 = self.outer_points[i]
            
            intersection = line_segments_intersection(p1,p2,self.current_pos,self.last_pos)
            if (intersection is not None):
                return True
                
        for i in range(len(self.inner_points)):
            p1 = self.inner_points[i-1]
            p2 = self.inner_points[i]
            
            intersection = line_segments_intersection(p1,p2,self.current_pos,self.last_pos)
            if (intersection is not None):
                return True
            
        return False
    
    def plot_checkpoint(self):
        pygame.draw.line(self.screen,(0,255,0),self.p3,self.p4)
    
    def log_score(self):
        score = self.current_point
        self.log.append([score,(self.action),self.get_state()])
    
    def take_action(self,action):
        if self.draw_keys:
            up = (1500,700)
            down = (1500,750)
            left = (1450,750)
            right = (1550,750)
            
            self.draw_key(False,up,25)
            self.draw_key(False,down,25)
            self.draw_key(False,left,25)
            self.draw_key(False,right,25)
        
        if action[0] == 1:
            self.car.speed_up()
            if self.draw_keys:
                self.draw_key(True,up,25)
            
        elif action[0] == -1:
            self.car.brake()
            if self.draw_keys:
                self.draw_key(True,down,25)
        else:
            self.car.nothing()
            
        if action[1] == 1:
            self.car.turn_left()
            if self.draw_keys:
                self.draw_key(True,left,25)
        elif action[1] == -1:
            self.car.turn_right()
            if self.draw_keys:
                self.draw_key(True,right,25)
        else:
            self.car.reset_turn()
            
        self.action = action

    
    def draw_key(self,filled,coor,side):
        if filled:
            pygame.draw.rect(self.screen,(255,255,255), pygame.Rect(coor[0],coor[1],side,side),width=0)
        else:
            pygame.draw.rect(self.screen,(255,255,255), pygame.Rect(coor[0],coor[1],side,side),width=1)
    
    def update(self, action_):
        self.last_pos = self.current_pos
        self.current_pos = self.car.get_pos()

        if self.draw_keys:
            self.screen.fill((0, 0, 0))  
            self.track.plot_track(self.screen)
            self.car.draw(self.screen)

        for line in self.line_list:
            line.update()
            if self.draw_keys:
                line.plot()

        self.take_action(action_)

        self.car.friction()
        self.car.calculate_all()
        self.car.update_position()

        self.plot_checkpoint() if self.draw_keys else None

        if self.is_collided_with_track():
            self.current_point = self.crash_penalty
            self.total_score += self.current_point
            return False

        self.get_score()
        self.log_score()

        if self.draw_keys:
            text_surface = self.my_font.render(str(self.total_score), True, (255, 255, 0))
            self.screen.blit(text_surface, (50, 50))
            pygame.display.update()
            pygame.time.Clock().tick(60)
        else:
            pygame.time.Clock().tick(1000)

        return True
    
    def safe_update(self, action_):
        self.last_pos = self.current_pos
        self.current_pos = self.car.get_pos()

        for line in self.line_list:
            line.update()

        self.take_action(action_)
        self.car.friction()
        self.car.calculate_all()
        self.car.update_position()
        self.get_score()
        self.log_score()

            
    def return_log(self):
        return self.log
    
    def return_total_score(self):
        return self.total_score
    
    def return_score(self):
        return self.current_point
        
    

def calculate_angle(in_point, out_point):
    dx = out_point[0] - in_point[0]
    dy = out_point[1] - in_point[1]
    
    # atan2 gives angle in radians, handling direction properly
    angle_rad = np.arctan2(dy, dx)
    angle_deg = np.degrees(angle_rad)-90
    
    return angle_deg  # angle relative to x-axis (0 degrees is to the right)

def calculate_position(p1, p2):
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2

def calculate_start(in_pt,out_pt):
    checkpoint_start = random.randint(0, len(in_pt) - 1)
    inner = in_pt[checkpoint_start]
    outer = out_pt[checkpoint_start]
    
    pos_x, pos_y = calculate_position(inner, outer)
    angle = calculate_angle(inner, outer)
    
    return pos_x, pos_y, angle, checkpoint_start