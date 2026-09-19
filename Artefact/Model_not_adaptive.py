# Hello!!! Welcome to my model
# PS: This is my model before adding an adaptive system, i run my 2 what-if simulations here

# 1. What if both temperature and light intensity are high? (temp = 32, light = 245)
# 2. What if both temperature and light intensity are low? (temp = 5, light = 50)
# For my what-if simulations, I hardcoded the values for temp & light instead of extracting data from a csv file
# Therefore, Code for data processing is commented.

# Note: I run this code in VScode
# VScode Extension I am using is Jupyter (I need this extension because iPython.display, clear_output only perfectly function on Jupyter Notebooks)
# Packages I used: pandas, ipython, matplotlib, ipykernel 
# To install the packages, go to terminal and type "pip install {name of package}" E.g. pip install pandas

#%%
# import libraries
import pandas as pd
import random
import time
from IPython.display import clear_output
import matplotlib.pyplot as plt

# Data preprocessing
df = pd.read_csv('microbit.csv',sep=',') # load dataset, comma seperated

# use data collected by my microbit
avg_temp = df['temp'].mean() # take the average temperature
avg_light = df['Light'].mean() # take the average light intensity

# global variables
burnt_history = [] # track burnt tree history over simulation time
time_step = 0 # track simulation time step

# TERMINAL DISPLAY FUNCTIONS
# create a colored terminal block using ANSI escape codes
def color_block(r,g,b,label=" "):
  return f"\033[48;2;{r};{g};{b}m{label}\033[0m"

# create a blue background block for sprinkler visualisation using ANSI escape codes
def blue_background(cell):
  letter = cell[-4:-1]
  return f"\033[48;2;0;121;255m{letter}\033[0m"

# calculate probability of fire based on environment
def fire_probability(temp, light, neighbours):
  base = 0.08 # base ignition probability

  # reduce probability if humidity is high
  base -= humidity(temp, light) 

  # increase probability with the number of burning neighbours
  base += 0.05 * neighbours

  # temperature effect on fire spread
  if temp <= 10:
    base += 0.005 * temp
  elif temp <= 15:
    base += 0.006 * temp
  elif temp <= 20:
    base += 0.008 * temp
  else:
    base += 0.01 * temp

  # light intensity effect on fire spread
  base += 0.001 * light

  return min(base,0.9) # 0.9 is the maximum possible fire probability

# count the number of fire cells nearby (8 direction)
def count_fire_neighbours(forest, i, j, fire, size):
  directions = [
     (1,0), (-1,0), (0,1), (0,-1), 
     (1,1), (1,-1), (-1,1), (-1,-1)
    ]
  count = 0

  # checking all directions
  for dx, dy in directions:
    x = i + dx
    y = j + dy

    if 0 <= x < size and 0 <= y < size:
      if forest[x][y] == fire:
        count += 1

  return count

# count the number of burnt trees in forest
def count_burnt(forest, burnt_tree):
  count = 0
  for row in forest:
    count += row.count(burnt_tree)
  return count

# check if fire still exists in forest
def fire_exists(forest, fire):
  for row in forest:
    if fire in row:
      return True
  return False

# estimate humidity based on temperature and light intensity
# lower temp and lower light = lower humidity
def humidity(temp, light):
  moisture_factor = 0
  if temp < 15:
    moisture_factor += 0.1

  if light < 100:
    moisture_factor += 0.1

  return moisture_factor

# evaluate the whole forest risk using a risk point system
def whole_forest_fire_risk(size,forest,temp, light,fire):
  risk_point = 0
  fire_bank = []

  # temperature contribution to risk score
  if temp >= 28:
    risk_point += 7
  elif temp >= 20:
    risk_point += 5
  elif temp >= 10:
    risk_point += 3
  else:
    risk_point += 1

  # light intensity contribution to risk score
  if light >= 200:
    risk_point += 4
  elif light >= 175:
    risk_point += 3
  elif light >= 100:
    risk_point += 2
  else:
    risk_point += 1

  # count active fire cells
  for i in range(size):
    for j in range(size):
      if forest[i][j] == fire:
        fire_bank.append((i,j))

  # add fire count into risk score
  risk_point += len(fire_bank)

  # map risk score to risk levels
  if risk_point >= 40:
    return "Fatal", color_block(255,0,0," Fatal ")
  elif risk_point >= 35:
    return "Extreme", color_block(255,91,0," Extreme ")
  elif risk_point >= 30:
    return "Critical", color_block(255,110,0," Critical ")
  elif risk_point >= 25:
    return "High", color_block(255,149,0," High ")
  elif risk_point >= 20:
    return "Significant", color_block(255,189,0," Significant ")
  elif risk_point >= 15:
    return "Moderate", color_block(255,236,0," Moderate ")
  elif risk_point >= 10:
    return "Minor", color_block(216,255,0," Minor ")
  else:
    return "Negligible", color_block(130,255,0," Negligible ")
  
# update simulation
def update_forest(forest, temp, light, size, fire, burnt_tree, normal_tree, normal_leave, dead_tree, dead_leave,
                   burn_time, original_material, risk_level):

  # copy forest state for update, this way it avoids overwriting
  new_forest = [row.copy() for row in forest]

  # collects all active fire coordinates
  current_fires = []
  for r in range(size):
    for c in range(size):
      if forest[r][c] == fire:
        current_fires.append((r,c))

  # iterate through forest grid
  for i in range(size):
    for j in range(size):
      cell = forest[i][j]

      if cell in [normal_tree, normal_leave, dead_tree, dead_leave]:
        neighbours = count_fire_neighbours(forest, i, j, fire, size)

        # spread fire if burning neighbour exist
        if neighbours > 0:

          prob = fire_probability(temp, light, neighbours)

          # adjust probability based on vegetation type
          if cell == dead_leave:
            prob += 0.25
          elif cell == normal_leave:
            prob += 0.15
          elif cell == dead_tree:
            prob += 0.08

          # random fire ignition
          if random.random() < min(prob, 0.95):
            new_forest[i][j] = fire
            burn_time[(i,j)] = 0
            original_material[(i,j)] = cell

      # if cell is burning
      elif cell == fire:
        burn_time[(i,j)] += 1
        material = original_material[(i,j)]

        # burning duration depends on vegetation material
        if material == dead_leave:
          burn_duration = 1
        elif material == normal_leave:
          burn_duration = 2
        elif material == dead_tree:
          burn_duration = 3
        else:
          burn_duration = 4

        # convert fire to burnt free after burn duration
        if burn_time[(i,j)] >= burn_duration:
          new_forest[i][j] = burnt_tree
          del burn_time[(i,j)]
          del original_material[(i,j)]

  return new_forest

# MAIN FUNCTION
def forest_simulation(temp,light):
  global burnt_history
  global time_step

  # forest grid size
  size = 20
    
  # vegetation density:
  normal_tree_cover = 0.82
  num_normal_tree = int(size**2*normal_tree_cover)

  normal_leave_cover = 0.1
  num_leave = int(size**2*normal_leave_cover)

  dead_tree_cover = 0.05
  num_dead_tree = int(size**2*dead_tree_cover)

  dead_leave_cover = 0.01
  num_dead_leave = int(size**2*dead_leave_cover)

  # Symbol representation for forest map 
  normal_tree = "T"
  normal_leave = "t"
  soil_block = " "
  dead_tree = "D"
  dead_leave = "d"
  fire = "F"
  burnt = "B"

  # forest initialisation with soil
  forest = [[soil_block for i in range(size)]for j in range(size)]

  # randomly place normal trees
  normal_tree_bank = []
  while len(normal_tree_bank) < num_normal_tree:
    i = random.randint(0,size-1)
    j = random.randint(0,size-1)
    coord = (i,j)
    if coord not in normal_tree_bank:
      normal_tree_bank.append(coord)
    else:
      pass
  for coord in normal_tree_bank:
    x,y = coord
    forest[x][y]=normal_tree

  # collect remaining soil positions
  soil_positions = []
  for i in range(size):
    for j in range(size):
      if forest[i][j] == soil_block:
        soil_positions.append((i,j))

  random.shuffle(soil_positions)

  # place normal leaves
  for x,y in soil_positions[:num_leave]:
    forest[x][y] = normal_leave

  # collect remaining soil positions
  new_soil_positions = []
  for i in range(size):
    for j in range(size):
      if forest[i][j] == soil_block:
        new_soil_positions.append((i,j))
  random.shuffle(new_soil_positions)

  # place dead trees
  for x,y in new_soil_positions[:num_dead_tree]:
    forest[x][y] = dead_tree

  # collect remaining soil positions
  remaining_soil_positions = []
  for i in range(size):
    for j in range(size):
      if forest[i][j] == soil_block:
        remaining_soil_positions.append((i,j))
  random.shuffle(remaining_soil_positions)

  # place dead leaves
  for x,y in remaining_soil_positions[:num_dead_leave]:
    forest[x][y] = dead_leave

  # starting a fire at random tree location
  while True:
    i = random.randint(0,size-1)
    j = random.randint(0,size-1)
    if forest[i][j] == normal_tree:
      forest[i][j] = fire
      break

  # track burn duration for fire cells
  burn_time = {}
  original_material = {}

  original_material[(i,j)] = normal_tree
  burn_time[(i,j)] = 0
  
  # Simulation loop (it runs until there's no fire anymore)
  while fire_exists(forest, fire):
        
    # clear the previous console output
    clear_output(wait=True)

    # get the current forest fire risk
    risk_level, current_risk = whole_forest_fire_risk(size,forest,temp,light,fire)

    # Update forest state
    forest = update_forest(forest, temp, light, size,fire, burnt, normal_tree, normal_leave, dead_tree, dead_leave, burn_time,
                           original_material,risk_level)

    # record burnt tree history
    burnt_history.append(count_burnt(forest, burnt))
    time_step += 1

    # display forest grid
    for i in range(size):
      row_display = ""
      for j in range(size):
        cell = forest[i][j]

        # Assign visualisation color based on cell type
        if cell == "T":
          r,g,b,text = 46,139,87," T "
        elif cell == "t":
          r,g,b,text = 85,170,85," t "
        elif cell == "D":
          r,g,b,text = 100,60,30," D "
        elif cell == "d":
          r,g,b,text = 150,120,80," d "
        elif cell == "F":
          r,g,b,text = 204,0,0," F "
        elif cell == "B":
          r,g,b,text = 70,70,70," B "
        else:
          r,g,b,text = 120,85,60,"   "

        row_display += f"\033[48;2;{r};{g};{b}m{text}\033[0m"

      print(row_display)

    print(f"\nCurrent Fire Risk:{current_risk}")

    # forest key
    print("\nFOREST KEY:")
    print(color_block(46, 139, 87, " T "), " = Tree", end = "\t\t")
    print(color_block(85, 170, 85, " t ") , " = Leaf")
    print(color_block(100, 60, 30, " D ") , " = Dead tree", end = "\t")
    print(color_block(150, 120, 80, " d "), " = Dead leaf")
    print(color_block(120, 85, 60, "   "), " = Soil", end = "\t\t")
    print(color_block(204, 0, 0, " F "), " = Fire")
    print(color_block(70, 70, 70, " B "), "= Burnt")

    # control simulation speed
    time.sleep(0.4)


# run forest simulation using microbit data averages
forest_simulation(avg_temp,avg_light)
# forest_simulation(32,245) # What if (1), temp & light are both high
# forest_simulation(5,50) # What if (2), temp & light are both low

# VISUALISATION OF BURN RATE
plt.figure(figsize=(6,4))

plt.plot(burnt_history)

plt.xlabel("Time Step (Seconds)")
plt.ylabel("Number of Burnt Trees")
plt.title(f"Forest Burn Rate Over Time")

plt.grid()

plt.show()
# %%
