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

from racingGame import *

pygame.init()

font = pygame.font.SysFont(None, 36)
text = font.render("Hello, world!", True, (255, 255, 255))

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
    
angle_list = [10,30,60,90,160,200,270,300,330,350]
angle_list = [i for i in range(-90,90,10)]+[i for i in range(90,270,20)]


count = 0
version = 0


loss_list = []
loss_mean_list = []

import numpy as np
import random

from collections import namedtuple, deque

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

GAMMA = 0.98  # instead of 0.999

LR = 0.0005  # instead of 0.001

BATCH_SIZE = 128  # instead of 64

MEMORY_SIZE = 500_000

EPS_START = 1.0
EPS_END = 0.05  # raised from 0.03 for slightly more long-term exploration
EPS_START_MIN = 0.3  # raised from 0.2 for quicker drop to some exploitation
EPS_DECAY = 0.995  # slowed down decay to allow more exploration (was 0.997)

TARGET_UPDATE = 500  # was 100

EPISODES = 3000  # raised from 2000 to give more time to learn with deeper nets

TIME = 800  # increased from 500 to allow more learning opportunities per episode

TRACKCHANGE_FREQ = 20  # reduced from 50 for better generalization

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
        self.fc1 = nn.Linear(state_dim, 64)
        self.fc2 = nn.Linear(64, 128)
        self.fc3 = nn.Linear(128, 256)
        self.out = nn.Linear(256, action_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.out(x)

# Initialize

path_name = "/Users/ard/Desktop/Coding_2/F1_laptime_project/policy/one_track/test_"
policy_dqn = DQN(len(angle_list)+6, 9).to(device)
target_dqn = DQN(len(angle_list)+6, 9).to(device)
loss = 0

inner_points,outer_points = generate_track(centerline_list[1],100)

x,y,angle,check = calculate_start(inner_points,outer_points)
newgame = game(inner_points, outer_points, angle_list,(x, y), True,check,angle)
state = newgame.get_state()
truncate = False

while True:
    TIME += 100
    memory = ReplayMemory(MEMORY_SIZE)

    
    try:
        policy_dqn.load_state_dict(torch.load(path_name+str(count)+"-"+str(version)+".pth"))
        print(f"got version:{count}.{version}")
    except:
        pass
    count+=1
    target_dqn.load_state_dict(policy_dqn.state_dict())
    target_dqn.eval()

    optimizer = optim.Adam(policy_dqn.parameters(), lr=LR)
    criterion = nn.SmoothL1Loss()

    epsilon = EPS_START
    #EPS_START = max([EPS_START*0.9,EPS_START_MIN])

    def select_action(state, epsilon):
        if random.random() < epsilon:
            return random.randint(0, 8)
        with torch.no_grad():
            state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(device)
            return policy_dqn(state).argmax(dim=1).item()
        
    scorelist = []
    version = 0
    for episode in range(EPISODES):
        test = False
        x,y,angle,check = calculate_start(inner_points,outer_points)
        newgame = game(inner_points, outer_points, angle_list,(x, y), test,check,angle)
        state = newgame.get_state()
        
        episode_loss = []

        for t in range(TIME):
            action = select_action(state, epsilon)
            done = not newgame.update(actions[action])
            reward = newgame.return_score()
            next_state = newgame.get_state()

            memory.push(torch.tensor(state, dtype=torch.float32),
                        action,
                        torch.tensor(next_state, dtype=torch.float32),
                        reward,
                        done)

            state = next_state

            if len(memory) >= BATCH_SIZE:
                transitions = memory.sample(BATCH_SIZE)
                batch = Transition(*zip(*transitions))

                states = torch.stack(batch.state).to(device)
                actions_batch = torch.tensor(batch.action, dtype=torch.long).to(device)
                rewards = torch.tensor(batch.reward, dtype=torch.float32).to(device)
                next_states = torch.stack(batch.next_state).to(device)
                dones = torch.tensor(batch.done, dtype=torch.float32).to(device)

                q_values = policy_dqn(states).gather(1, actions_batch.unsqueeze(1)).squeeze(1)
                next_q_values = target_dqn(next_states).max(1)[0]
                expected_q_values = rewards + GAMMA * next_q_values * (1 - dones)

                loss = criterion(q_values, expected_q_values.detach())
                episode_loss.append(loss.detach().numpy())
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
        
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        print("You pressed R — restarting!")
                        done = True
                    if event.key == pygame.K_RETURN:
                        print("ending...")
                        done = True
                        truncate = True

            if done:
                break

        epsilon = max(EPS_END, epsilon * EPS_DECAY)
        loss_mean_list.append(np.mean(episode_loss))
        
        if episode % TARGET_UPDATE == TARGET_UPDATE-1:
            target_dqn.load_state_dict(policy_dqn.state_dict())
            version += 1
            torch.save(policy_dqn.state_dict(), path_name+str(count)+"-"+str(version)+".pth")
            scorelist.append(newgame.return_total_score())
            np.savetxt("GFG_2.csv",loss_mean_list,delimiter =", ",fmt ='% s')
            
        if episode%TRACKCHANGE_FREQ == 0:
            #inner_points,outer_points = generate_track(centerline_list[random.randint(0,7)],100)
            print("track_not_changed")
            
        loss_list.append(episode_loss)
        

        print(f"Episode {episode + 1}, Score: {newgame.return_total_score()}, Epsilon: {epsilon:.3f}, loss:{float(loss)},q-val: {np.mean(episode_loss)} count: {count} version: {version} trained: {len(memory) >= BATCH_SIZE}")
        
        if(truncate):
            break
    if(truncate):
        break