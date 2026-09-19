# This python file is for testing core functions and the algorithms
# Before running these code, make sure the terminal is in the correct path (if its not, there might be an error such as can't find micro:bit.csv file)
# If you're in the wrong path you can type "cd" and "cd.." in the terminal to change path

import pandas as pd
import random
from Wildfire_Risk_and_Spread_Simulation_Model import fire_probability, count_fire_neighbours, whole_forest_fire_risk, update_forest

def test_csv_read():
    df = pd.read_csv("microbit.csv", sep=',')

    if 'temp' in df.columns and 'Light' in df.columns:
        print("CSV Test Passed✅")
    else:
        print("CSV Test Failed❌")

def test_fire_probability():
    prob_1 = fire_probability(10,100,2)
    prob_2 = fire_probability(30,200,3)
    prob_3 = fire_probability(50,250,8)
    state = "Out of range"

    if prob_1 > 0 and prob_2 > 0 and prob_1 <=0.9 and prob_2 <= 0.9:
        state = "In range"
    
    if state == "In range":
        if prob_1 == 0.23: # Expected Value = 0.23 = 0.08-0.1+0.05*2+0.005*10+0.001*100
            print("Fire Probability Test 1 Passed✅")
        else:
            print("Fire Probability Test 1 Failed❌")

        if prob_2 == 0.73: # Expected value = 0.73 = 0.08+0.05*3+0.01*30+0.001*200
            print("Fire Probability Test 2 Passed✅")
        else:
            print("Fire Probability Test 2 Failed❌")
    else:
        print("Fire Probability Test 1 Failed❌\nFire Probability Test 2 Failed❌")
    
    if prob_3 == 0.9:
        print("Fire probability 3 Passed✅")
    else:
        print("Fire Probability 3 Failed❌")

def test_count_fire_neighbours():
    forest = [
        ["F","T","T"],
        ["T","T","T"],
        ["T","T","F"]
    ]
    result = count_fire_neighbours(forest,1,1,"F",3)

    if result == 2:
        print("Neighbour Count Test Passed✅")
    else:
        print("Neighbour Count Test Failed❌")

def test_whole_forest_fire_risk():
    size = 20
    fire = "F"
    forest = [["T" for i in range(size)] for j in range(size)]

    fire_positions = [(0,0), (5,5), (10,10), (15,15), (19,19)]
    for r, c in fire_positions:
        forest[r][c] = fire

    risk,_ = whole_forest_fire_risk(size, forest, 30, 200, fire)
    if risk == "Moderate": # Expected = Moderate = 7+4+5 = 16, 15 < 16 < 20 (parameter)
        print("Whole Forest Fire Risk Test Passed✅")
    else:
        print("Whole Forest Fire Risk Test Failed❌")

def test_adaptive_sprinkler_activation():
    size = 20
    forest = [["T" for i in range(size)] for j in range(size)]
    burn_time = {}
    original_material = {}

    fire_loc = (10, 10)
    forest[fire_loc[0]][fire_loc[1]] = "F"
    burn_time[fire_loc] = 0
    original_material[fire_loc] = "T" 

    new_forest, zone = update_forest(forest, 35, 250, size, "F", "B", "T", "t", "D", "d", burn_time, original_material, "High")

    if len(zone) > 0:
        # A radius of 4 around (10,10) should make a 9x9 grid (81 cells)
        print(f"Adaptive Sprinkler Activation Test Passed✅ (Zone size: {len(zone)})")
    else:
        print("Adaptive Sprinkler Activation Test Failed❌ (Zone was empty)")

def test_fire_spread():
    size = 20
    forest = [["T" for i in range(size)] for j in range(size)]
    fire_loc = (10, 10)
    forest[fire_loc[0]][fire_loc[1]] = "F"

    burn_time = {fire_loc: 0}
    original_material = {fire_loc: "T"}

    random.seed(42) 

    new_forest, _ = update_forest(forest, 35, 250, size, "F", "B", "T", "t", "D", "d", burn_time, original_material, "High")

    # Check if the forest changed (a spread or a burn-down)
    if new_forest != forest:
        print("Fire Spread Test Passed✅")
    else:
        print("Fire Spread Test Failed❌ (No change detected in grid)")


test_csv_read()
test_fire_probability()
test_count_fire_neighbours()
test_whole_forest_fire_risk()
test_adaptive_sprinkler_activation()
test_fire_spread()