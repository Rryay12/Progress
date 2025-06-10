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

pygame.init()

font = pygame.font.SysFont(None, 36)
text = font.render("Hello, world!", True, (255, 255, 255))

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

centerline1 = [(671.6, 115.5),
(541.7, 120.3),
(402.0, 114.6),
(248.2, 124.1),
(193.1, 177.1),
(184.7, 262.3),
(172.0, 351.3),
(119.8, 441.3),
(111.3, 527.5),
(111.3, 602.3),
(124.0, 694.1),
(183.3, 757.6),
(320.2, 784.1),
(442.9, 792.6),
(579.8, 787.9),
(721.0, 785.0),
(846.6, 784.1),
(962.3, 782.2),
(1104.8, 780.3),
(1257.3, 782.2),
(1367.3, 772.7),
(1457.7, 720.6),
(1450.6, 643.0),
(1404.0, 598.5),
(1267.1, 562.5),
(1119.0, 556.8),
(969.4, 563.4),
(859.3, 583.3),
(705.4, 616.5),
(541.7, 647.7),
(410.5, 607.0),
(366.7, 525.6),
(378.0, 449.8),
(465.5, 398.7),
(582.7, 385.4),
(665.9, 402.5),
(737.9, 426.1),
(785.9, 435.6),
(840.9, 425.2),
(874.8, 401.5),
(900.2, 367.4),
(949.6, 344.7),
(1021.6, 348.5),
(1082.3, 370.3),
(1134.5, 404.4),
(1176.8, 430.9),
(1250.2, 455.5),
(1320.8, 435.6),
(1346.2, 378.8),
(1337.7, 310.6),
(1302.4, 269.9),
(1248.8, 224.4),
(1117.5, 181.8),
(996.2, 151.5),
(736.5, 119.3),]

centerline2 = [(1189.5, 129.7),
(1103.4, 137.3),
(989.1, 143.0),
(864.9, 162.9),
(791.5, 218.8),
(711.1, 266.1),
(595.4, 271.8),
(486.7, 247.2),
(424.6, 215.0),
(347.0, 177.1),
(231.2, 182.8),
(159.3, 240.5),
(139.5, 322.0),
(153.6, 398.7),
(227.0, 458.3),
(351.2, 509.5),
(404.8, 578.6),
(419.0, 687.5),
(538.9, 728.2),
(778.8, 750.9),
(838.1, 704.5),
(811.3, 645.8),
(745.0, 596.6),
(671.6, 547.3),
(627.8, 492.4),
(656.0, 432.8),
(726.6, 404.4),
(829.6, 411.0),
(910.1, 455.5),
(975.0, 512.3),
(1038.5, 559.7),
(1148.6, 613.6),
(1258.7, 608.9),
(1329.2, 563.4),
(1356.0, 495.3),
(1364.5, 426.1),
(1365.9, 355.1),
(1340.5, 277.5),
(1306.7, 227.3),
(1255.8, 187.5),]

centerline3 = [(1279.8, 136.4),
(1220.6, 142.0),
(1141.5, 161.0),
(1024.4, 188.4),
(850.8, 184.7),
(739.3, 153.4),
(622.2, 138.3),
(451.4, 134.5),
(328.6, 140.2),
(224.2, 174.2),
(183.3, 237.7),
(148.0, 319.1),
(138.1, 418.6),
(145.2, 512.3),
(201.6, 636.4),
(248.2, 688.4),
(310.3, 716.9),
(472.6, 729.2),
(543.1, 715.9),
(644.8, 663.8),
(764.7, 637.3),
(904.4, 643.0),
(1107.7, 674.2),
(1261.5, 674.2),
(1326.4, 643.0),
(1416.7, 553.0),
(1440.7, 474.4),
(1443.5, 341.9),
(1429.4, 242.4),
(1397.0, 188.4),
(1357.5, 157.2),]

centerline4 = [(1415.3, 126.9),
(1277.0, 133.5),
(1124.6, 154.4),
(922.8, 188.4),
(729.4, 243.4),
(495.2, 344.7),
(342.7, 415.7),
(156.5, 500.0),
(149.4, 586.2),
(220.0, 659.1),
(369.6, 699.8),
(554.4, 696.0),
(689.9, 685.6),
(859.3, 676.1),
(979.2, 690.3),
(1154.2, 716.9),
(1279.8, 735.8),
(1397.0, 719.7),
(1432.3, 620.3),
(1391.3, 568.2),
(1288.3, 502.8),
(1238.9, 480.1),
(1116.1, 455.5),
(1013.1, 388.3),
(1001.8, 322.0),
(1099.2, 275.6),
(1246.0, 250.0),
(1344.8, 235.8),
(1457.7, 216.9),
(1490.1, 185.6),
(1478.8, 144.9),]

centerline5 = [(1344.8, 161.0),
(1165.5, 148.7),
(1000.4, 153.4),
(788.7, 157.2),
(551.6, 155.3),
(354.0, 166.7),
(225.6, 171.4),
(207.3, 232.0),
(208.7, 317.2),
(214.3, 448.9),
(238.3, 565.3),
(245.4, 677.1),
(275.0, 715.0),
(387.9, 723.5),
(455.6, 683.7),
(457.1, 648.7),
(447.2, 586.2),
(452.8, 524.6),
(455.6, 442.2),
(451.4, 364.6),
(468.3, 331.4),
(529.0, 313.4),
(644.8, 316.3),
(668.8, 361.7),
(680.0, 452.7),
(691.3, 519.9),
(708.3, 602.3),
(725.2, 661.9),
(764.7, 691.3),
(822.6, 701.7),
(890.3, 674.2),
(908.7, 621.2),
(912.9, 536.0),
(917.1, 465.0),
(921.4, 371.2),
(927.0, 323.9),
(963.7, 304.0),
(1032.9, 303.0),
(1138.7, 319.1),
(1161.3, 358.9),
(1164.1, 445.1),
(1176.8, 577.7),
(1196.6, 643.0),
(1291.1, 706.4),
(1364.5, 707.4),
(1404.0, 672.3),
(1460.5, 586.2),
(1470.4, 487.7),
(1474.6, 388.3),
(1477.4, 307.8),
(1453.4, 239.6),
(1429.4, 208.3),]

centerline6 = [(752.0, 394.9),
(735.1, 359.8),
(688.5, 304.9),
(623.6, 247.2),
(479.6, 169.5),
(273.6, 139.2),
(166.3, 183.7),
(138.1, 299.2),
(156.5, 358.9),
(251.0, 480.1),
(372.4, 557.8),
(550.2, 628.8),
(634.9, 686.6),
(797.2, 733.9),
(896.0, 735.8),
(1032.9, 695.1),
(1128.8, 645.8),
(1206.5, 561.6),
(1277.0, 469.7),
(1312.3, 385.4),
(1339.1, 306.8),
(1327.8, 242.4),
(1251.6, 160.0),
(1179.6, 153.4),
(1011.7, 202.7),
(986.3, 261.4),
(965.1, 369.3),
(953.8, 467.8),
(922.8, 536.0),
(876.2, 555.9),
(774.6, 500.9),
(774.6, 473.5),]

centerline7 = [(1268.5, 179.0),
(1134.5, 169.5),
(1107.7, 147.7),
(975.0, 140.2),
(936.9, 147.7),
(866.3, 201.7),
(842.3, 231.1),
(767.5, 260.4),
(661.7, 262.3),
(606.7, 237.7),
(544.6, 200.8),
(489.5, 164.8),
(385.1, 140.2),
(265.1, 162.9),
(236.9, 197.9),
(229.8, 262.3),
(222.8, 319.1),
(284.9, 353.2),
(344.2, 373.1),
(379.4, 398.7),
(411.9, 449.8),
(399.2, 479.2),
(355.4, 504.7),
(251.0, 545.5),
(215.7, 580.5),
(205.8, 662.9),
(235.5, 698.9),
(342.7, 741.5),
(490.9, 755.7),
(520.6, 744.3),
(537.5, 715.9),
(516.3, 657.2),
(523.4, 626.9),
(578.4, 565.3),
(634.9, 564.4),
(699.8, 597.5),
(788.7, 652.5),
(845.2, 697.9),
(929.8, 720.6),
(969.4, 707.4),
(989.1, 672.3),
(982.1, 634.5),
(938.3, 570.1),
(910.1, 507.6),
(911.5, 477.3),
(975.0, 467.8),
(1076.6, 507.6),
(1116.1, 571.0),
(1176.8, 642.0),
(1306.7, 666.7),
(1391.3, 642.0),
(1418.1, 561.6),
(1408.3, 510.4),
(1358.9, 465.9),
(1315.1, 435.6),
(1229.0, 373.1),
(1223.4, 334.3),
(1268.5, 285.0),
(1380.0, 234.8),
(1430.8, 213.1),
(1426.6, 168.6),
(1381.5, 145.8),
(1319.4, 142.0),
(1262.9, 147.7),]

centerline8 = [(1374.4, 153.4),
(1271.4, 152.5),
(1080.8, 160.0),
(840.9, 159.1),
(650.4, 152.5),
(452.8, 154.4),
(252.4, 160.0),
(172.0, 192.2),
(160.7, 294.5),
(173.4, 508.5),
(188.9, 625.0),
(207.3, 726.3),
(245.4, 765.2),
(321.6, 781.3),
(548.8, 776.5),
(846.6, 779.4),
(1097.8, 776.5),
(1254.4, 772.7),
(1363.1, 760.4),
(1397.0, 723.5),
(1412.5, 591.9),
(1413.9, 423.3),
(1419.6, 318.2),
(1421.0, 244.3),
(1418.1, 184.7),]


centerline_list = [centerline1,centerline2,centerline3,centerline4,centerline5,centerline6,centerline8,centerline8]

class game:
    def __init__(self,inner_points,outer_points,angle_list,start_point,draw_keys=True,checkpoint_pos = 0,starting_angle=180):
        self.draw_keys = draw_keys
        
        self.my_font = pygame.font.SysFont('Comic Sans MS', 30)

        self.checkpoint_score = 10
        self.speed_score_mult = 0.03
        
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

        # Bonus for staying alive (time alive reward)

        # Penalty for standing still
        if self.car.get_speed() < 0.5:
            self.current_point -= 0.1 # discourage inactivity or stalling
        else:
            self.current_point += 0.1

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
            self.current_point = -20
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
        

class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_dim, 64)
        self.fc2 = nn.Linear(64, 128)
        self.fc3 = nn.Linear(128, 64)
        self.out = nn.Linear(64, action_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.out(x)
    
    
Transition = namedtuple('Transition',('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)    
    
angle_list = [10,30,60,90,160,200,270,300,330,350]
#angle_list = [i for i in range(0,360,10)]


count = 10
version = 7


loss_list = []
loss_mean_list = []

import numpy as np
import random

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

from collections import namedtuple, deque

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

GAMMA = 0.999
LR = 0.001
BATCH_SIZE = 64
MEMORY_SIZE = 500_000

EPS_START = 1
EPS_END = 0.03
EPS_DECAY = 0.995

TARGET_UPDATE = 100  
EPISODES = 1000
TIME = 500

TRACKCHANGE_FREQ = 50
# Actions
actions = [(-1, -1), (-1, 0), (-1, 1),
           (0, -1), (0, 0), (0, 1),
           (1, -1), (1, 0), (1, 1)]

# Transition tuple
Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward', 'done'))

# Replay memory class
class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)

    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

# DQN model
class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 64)
        self.out = nn.Linear(64, action_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.out(x)

# Initialize

policy_dqn = DQN(16, 9).to(device)
target_dqn = DQN(16, 9).to(device)

def select_action(state, epsilon):
    if random.random() < epsilon:
        return random.randint(0, 8)
    with torch.no_grad():
        state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(device)
        return policy_dqn(state).argmax(dim=1).item()

import keyboard 

pygame.init()
pygame.font.init()

pathname ="/Users/ard/Desktop/Coding_2/F1_laptime_project/Miyazaki_tokkou/Kamikaze_43-16.pth"

my_font = pygame.font.SysFont('Comic Sans MS', 30)

policy_dqn = DQN(16, 9).to(device)
policy_dqn.load_state_dict(torch.load(pathname))

time = 0


centerline1 = [(671.6, 115.5),
(541.7, 120.3),
(402.0, 114.6),
(248.2, 124.1),
(193.1, 177.1),
(184.7, 262.3),
(172.0, 351.3),
(119.8, 441.3),
(111.3, 527.5),
(111.3, 602.3),
(124.0, 694.1),
(183.3, 757.6),
(320.2, 784.1),
(442.9, 792.6),
(579.8, 787.9),
(721.0, 785.0),
(846.6, 784.1),
(962.3, 782.2),
(1104.8, 780.3),
(1257.3, 782.2),
(1367.3, 772.7),
(1457.7, 720.6),
(1450.6, 643.0),
(1404.0, 598.5),
(1267.1, 562.5),
(1119.0, 556.8),
(969.4, 563.4),
(859.3, 583.3),
(705.4, 616.5),
(541.7, 647.7),
(410.5, 607.0),
(366.7, 525.6),
(378.0, 449.8),
(465.5, 398.7),
(582.7, 385.4),
(665.9, 402.5),
(737.9, 426.1),
(785.9, 435.6),
(840.9, 425.2),
(874.8, 401.5),
(900.2, 367.4),
(949.6, 344.7),
(1021.6, 348.5),
(1082.3, 370.3),
(1134.5, 404.4),
(1176.8, 430.9),
(1250.2, 455.5),
(1320.8, 435.6),
(1346.2, 378.8),
(1337.7, 310.6),
(1302.4, 269.9),
(1248.8, 224.4),
(1117.5, 181.8),
(996.2, 151.5),
(736.5, 119.3),]

centerline2 = [(1189.5, 129.7),
(1103.4, 137.3),
(989.1, 143.0),
(864.9, 162.9),
(791.5, 218.8),
(711.1, 266.1),
(595.4, 271.8),
(486.7, 247.2),
(424.6, 215.0),
(347.0, 177.1),
(231.2, 182.8),
(159.3, 240.5),
(139.5, 322.0),
(153.6, 398.7),
(227.0, 458.3),
(351.2, 509.5),
(404.8, 578.6),
(419.0, 687.5),
(538.9, 728.2),
(778.8, 750.9),
(838.1, 704.5),
(811.3, 645.8),
(745.0, 596.6),
(671.6, 547.3),
(627.8, 492.4),
(656.0, 432.8),
(726.6, 404.4),
(829.6, 411.0),
(910.1, 455.5),
(975.0, 512.3),
(1038.5, 559.7),
(1148.6, 613.6),
(1258.7, 608.9),
(1329.2, 563.4),
(1356.0, 495.3),
(1364.5, 426.1),
(1365.9, 355.1),
(1340.5, 277.5),
(1306.7, 227.3),
(1255.8, 187.5),]

centerline3 = [(1279.8, 136.4),
(1220.6, 142.0),
(1141.5, 161.0),
(1024.4, 188.4),
(850.8, 184.7),
(739.3, 153.4),
(622.2, 138.3),
(451.4, 134.5),
(328.6, 140.2),
(224.2, 174.2),
(183.3, 237.7),
(148.0, 319.1),
(138.1, 418.6),
(145.2, 512.3),
(201.6, 636.4),
(248.2, 688.4),
(310.3, 716.9),
(472.6, 729.2),
(543.1, 715.9),
(644.8, 663.8),
(764.7, 637.3),
(904.4, 643.0),
(1107.7, 674.2),
(1261.5, 674.2),
(1326.4, 643.0),
(1416.7, 553.0),
(1440.7, 474.4),
(1443.5, 341.9),
(1429.4, 242.4),
(1397.0, 188.4),
(1357.5, 157.2),]

centerline4 = [(1415.3, 126.9),
(1277.0, 133.5),
(1124.6, 154.4),
(922.8, 188.4),
(729.4, 243.4),
(495.2, 344.7),
(342.7, 415.7),
(156.5, 500.0),
(149.4, 586.2),
(220.0, 659.1),
(369.6, 699.8),
(554.4, 696.0),
(689.9, 685.6),
(859.3, 676.1),
(979.2, 690.3),
(1154.2, 716.9),
(1279.8, 735.8),
(1397.0, 719.7),
(1432.3, 620.3),
(1391.3, 568.2),
(1288.3, 502.8),
(1238.9, 480.1),
(1116.1, 455.5),
(1013.1, 388.3),
(1001.8, 322.0),
(1099.2, 275.6),
(1246.0, 250.0),
(1344.8, 235.8),
(1457.7, 216.9),
(1490.1, 185.6),
(1478.8, 144.9),]

centerline5 = [(1344.8, 161.0),
(1165.5, 148.7),
(1000.4, 153.4),
(788.7, 157.2),
(551.6, 155.3),
(354.0, 166.7),
(225.6, 171.4),
(207.3, 232.0),
(208.7, 317.2),
(214.3, 448.9),
(238.3, 565.3),
(245.4, 677.1),
(275.0, 715.0),
(387.9, 723.5),
(455.6, 683.7),
(457.1, 648.7),
(447.2, 586.2),
(452.8, 524.6),
(455.6, 442.2),
(451.4, 364.6),
(468.3, 331.4),
(529.0, 313.4),
(644.8, 316.3),
(668.8, 361.7),
(680.0, 452.7),
(691.3, 519.9),
(708.3, 602.3),
(725.2, 661.9),
(764.7, 691.3),
(822.6, 701.7),
(890.3, 674.2),
(908.7, 621.2),
(912.9, 536.0),
(917.1, 465.0),
(921.4, 371.2),
(927.0, 323.9),
(963.7, 304.0),
(1032.9, 303.0),
(1138.7, 319.1),
(1161.3, 358.9),
(1164.1, 445.1),
(1176.8, 577.7),
(1196.6, 643.0),
(1291.1, 706.4),
(1364.5, 707.4),
(1404.0, 672.3),
(1460.5, 586.2),
(1470.4, 487.7),
(1474.6, 388.3),
(1477.4, 307.8),
(1453.4, 239.6),
(1429.4, 208.3),]

centerline6 = [(752.0, 394.9),
(735.1, 359.8),
(688.5, 304.9),
(623.6, 247.2),
(479.6, 169.5),
(273.6, 139.2),
(166.3, 183.7),
(138.1, 299.2),
(156.5, 358.9),
(251.0, 480.1),
(372.4, 557.8),
(550.2, 628.8),
(634.9, 686.6),
(797.2, 733.9),
(896.0, 735.8),
(1032.9, 695.1),
(1128.8, 645.8),
(1206.5, 561.6),
(1277.0, 469.7),
(1312.3, 385.4),
(1339.1, 306.8),
(1327.8, 242.4),
(1251.6, 160.0),
(1179.6, 153.4),
(1011.7, 202.7),
(986.3, 261.4),
(965.1, 369.3),
(953.8, 467.8),
(922.8, 536.0),
(876.2, 555.9),
(774.6, 500.9),
(774.6, 473.5),]

centerline7 = [(1268.5, 179.0),
(1134.5, 169.5),
(1107.7, 147.7),
(975.0, 140.2),
(936.9, 147.7),
(866.3, 201.7),
(842.3, 231.1),
(767.5, 260.4),
(661.7, 262.3),
(606.7, 237.7),
(544.6, 200.8),
(489.5, 164.8),
(385.1, 140.2),
(265.1, 162.9),
(236.9, 197.9),
(229.8, 262.3),
(222.8, 319.1),
(284.9, 353.2),
(344.2, 373.1),
(379.4, 398.7),
(411.9, 449.8),
(399.2, 479.2),
(355.4, 504.7),
(251.0, 545.5),
(215.7, 580.5),
(205.8, 662.9),
(235.5, 698.9),
(342.7, 741.5),
(490.9, 755.7),
(520.6, 744.3),
(537.5, 715.9),
(516.3, 657.2),
(523.4, 626.9),
(578.4, 565.3),
(634.9, 564.4),
(699.8, 597.5),
(788.7, 652.5),
(845.2, 697.9),
(929.8, 720.6),
(969.4, 707.4),
(989.1, 672.3),
(982.1, 634.5),
(938.3, 570.1),
(910.1, 507.6),
(911.5, 477.3),
(975.0, 467.8),
(1076.6, 507.6),
(1116.1, 571.0),
(1176.8, 642.0),
(1306.7, 666.7),
(1391.3, 642.0),
(1418.1, 561.6),
(1408.3, 510.4),
(1358.9, 465.9),
(1315.1, 435.6),
(1229.0, 373.1),
(1223.4, 334.3),
(1268.5, 285.0),
(1380.0, 234.8),
(1430.8, 213.1),
(1426.6, 168.6),
(1381.5, 145.8),
(1319.4, 142.0),
(1262.9, 147.7),]

centerline8 = [(1374.4, 153.4),
(1271.4, 152.5),
(1080.8, 160.0),
(840.9, 159.1),
(650.4, 152.5),
(452.8, 154.4),
(252.4, 160.0),
(172.0, 192.2),
(160.7, 294.5),
(173.4, 508.5),
(188.9, 625.0),
(207.3, 726.3),
(245.4, 765.2),
(321.6, 781.3),
(548.8, 776.5),
(846.6, 779.4),
(1097.8, 776.5),
(1254.4, 772.7),
(1363.1, 760.4),
(1397.0, 723.5),
(1412.5, 591.9),
(1413.9, 423.3),
(1419.6, 318.2),
(1421.0, 244.3),
(1418.1, 184.7),]


centerline_list = [centerline1,centerline2,centerline3,centerline4,centerline5,centerline6,centerline8,centerline8]


inner_points,outer_points = generate_track(centerline_list[random.randint(0,7)],100)
x,y,angle,check = calculate_start(inner_points,outer_points)
newgame = game(inner_points, outer_points, angle_list,(x, y), True,check,angle)
state = newgame.get_state()
done = False
state =  newgame.get_state()
action = select_action(state, 0.005)
done = not newgame.update(actions[action])
time+=1

from pynput import keyboard
import random
import threading

key_pressed = False

def on_press(key):
    global key_pressed
    try:
        if key.char == 'r':
            key_pressed = True
            return False  # Stop listener after detecting 'r'
    except AttributeError:
        pass

def start_listener():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# Start the keyboard listener once
start_listener()
doing = True
while doing:
    # Generate new track
    inner_points, outer_points = generate_track(centerline_list[random.randint(0, 7)], 100)
    x, y, angle, check = calculate_start(inner_points, outer_points)
    
    # Start new game
    newgame = game(inner_points, outer_points, angle_list, (x, y), True, check, angle)
    state = newgame.get_state()
    done = False
    time = 0

    while not done and newgame.car.speed > 0.01:
        # Game loop logic
        state = newgame.get_state()
        action = select_action(state, 0)
        done = not newgame.update(actions[action])
        time += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # user closes the window
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    print("You pressed R — restarting!")
                    done = True
                if event.key == pygame.K_RETURN:
                    print("ending...")
                    doing = False