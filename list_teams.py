#!/usr/bin/env python3

"""
Given csv of student ID and ;-separated list of projects in order of preference
 - input list of projects to consider
 - find all possible combinations of teams
 - score each team
 - list teams with lowest score

Can change scoring in calculate_team_score function:
 - equal to rank: 1 for 1st, 2 for 2nd etc 
 - rank^2

Be careful with extra characters if copy/paste from excel or similar

G. Facini
Nov 2023
"""

import pandas as pd
from itertools import combinations, chain, product
import random

# Function to get remaining students
def get_remaining_students(all_students, current_teams):
    # Check if the input is a list of lists
    if current_teams and isinstance(current_teams[0], list):
        # Flatten the list of lists
        assigned_students = [student for team in current_teams for student in team]
    else:
        # It's a single list, use it as is
        assigned_students = current_teams

    return [student for student in all_students if student not in assigned_students]

# Function to generate next set of teams
def generate_next_teams(remaining_students, team_size):
    teams = list(combinations(remaining_students, team_size)) 
    #print(teams)
    #print(f"\t{len(remaining_students)} pick {team_size} = {len(teams)}")
    return teams

def calculate_team_score(team, student_ranks):
    score = 0
    for student in team:
        # Find the preferences list for the student
        # score = rank
        #score += student_ranks[ student ]
        # score = rank^2
        score += student_ranks[ student ]*student_ranks[ student ]
    return score

def get_student_rank(df, project_name): 
    # empty dictionary
    student_rank = {}
    for index, row in df.iterrows():
        student_id = row['ID']
        #print(f"\t student {student_id}")
        #print(f"\t \t prefs {row['preferences']}")
        try:
            # Find the rank of the project in the student's preference list
            # Add 1 because index starts at 0 but ranks start at 1
            rank = row['preferences'].index(project_name) + 1
        except ValueError:
            # This handles the case where the project is not in the student's preferences
            # flat rank for anyone who did not get fill in the form 
            #  - gives preference to others who have filled in the form
            #  - adds cost for adding person anywhere
            rank = 2.5

        student_rank[student_id] = rank

    return student_rank


# Define your projects and maximum team sizes
# Pick projects to run - 4 with highest average ranking
#MediaTek Research UK;Peak AI;UCL Comp. Rad. Biology and Oncology;The Guardian;Sention Technologies;The London Data Company;
max_sizes = {'MediaTek Research UK': 4, 'UCL Comp. Rad. Biology and Oncology': 3, 'The Guardian': 3, 'Peak AI': 3}
projects = list(max_sizes.keys())

# Read the CSV and split the preferences
# careful for extra spaces and special characters that excel or numbers might put in
df = pd.read_csv('prefs.csv')
df.columns = df.columns.str.strip()
df['preferences'] = df['list of projects'].str.split(';')
# list of students (IDs)
students = df['ID'].tolist()
print("Check that these IDs match the list of student IDs in input")
print(students)

# get student ranking for each project 
student_rank_project_0 = get_student_rank(df, projects[0])
student_rank_project_1 = get_student_rank(df, projects[1])
student_rank_project_2 = get_student_rank(df, projects[2])
student_rank_project_3 = get_student_rank(df, projects[3])

# Now student_pref_project_0 is a dictionary of student ID to their preference for project 0
print("Check that the list of ranks matches the input for each of the projects")
print(projects[0])
print(student_rank_project_0)
print(projects[1])
print(student_rank_project_1)
print(projects[2])
print(student_rank_project_2)
print(projects[3])
print(student_rank_project_3)

# Generate teams for the first project
first_project_teams = generate_next_teams(students, max_sizes[projects[0]])

print(len(first_project_teams))
print(len(students))
print(len(get_remaining_students(students, first_project_teams[0])))

all_teams = []

## Brute force to find the best configuration
best_score = float('inf')
best_configurations = []

# Loop through the combinations for the first project
#print("Team 1")
for team1 in first_project_teams:
    remaining_students1 = get_remaining_students(students, team1)
    # list of lists where inner list is a list of student IDs on each team
    second_project_teams = generate_next_teams(remaining_students1, max_sizes[projects[1]])

    #print("Team 2")
    for team2 in second_project_teams:
        remaining_students2 = get_remaining_students(students, team1+team2)
        # list of lists where inner list is a list of student IDs on each team
        third_project_teams = generate_next_teams(remaining_students2, max_sizes[projects[2]])

        #print("Team 3")
        for team3 in third_project_teams:
            remaining_students3 = get_remaining_students(students, team1+team2+team3)
            #print(len(remaining_students3))
            # list of lists where inner list is a list of student IDs on each team
            fourth_project_teams = generate_next_teams(remaining_students3, max_sizes[projects[3]])

            #print("Team 4")
            for team4 in fourth_project_teams:

                all_teams.append( [team1, team2, team3, team4] )
                
# calculate score - for the AM
                score1 = calculate_team_score( team1, student_rank_project_0 )
                score  = score1
                if score > best_score: continue

                score2 = calculate_team_score( team2, student_rank_project_1 )
                score += score2
                if score > best_score: continue

                score3 = calculate_team_score( team3, student_rank_project_2 )
                score += score3
                if score > best_score: continue

                score4 = calculate_team_score( team4, student_rank_project_3 )
                score += score4
                if score > best_score: continue
                #print(score)

                teams  = [team1,  team2,  team3,  team4]
                scores = [score1, score2, score3, score4]

			    # Calculate score for this configuration
                if score == best_score:
                    best_configurations.append([teams, scores])
#                    print(f" -- best size {len(best_configurations)}")
                if score < best_score:
                    print(f" - new best {score}")
                    best_score = score
                    best_configurations.clear()
                    best_configurations.append([teams, scores])

print(f"Teams created   : {len(all_teams)}")
print(f"Best score      : {best_score}")
print(f"Number of teams : {len(best_configurations)}")
#print(f"Best Team Configurations: {best_configurations}")
print(f"Best Team Configurations:")
print(f"{projects[0]} \t {projects[1]} \t {projects[2]} \t {projects[3]}")
for config in best_configurations:
    print("\t T", config[0])
    print("\t S", config[1])


print("Randomly pick")
random.seed(91123)
random_choice = random.choice(best_configurations)
print(f"{projects[0]}: \t {random_choice[0][0]}")
print(f"{projects[1]}: \t {random_choice[0][1]}")
print(f"{projects[2]}: \t {random_choice[0][2]}")
print(f"{projects[3]}: \t {random_choice[0][3]}")
print(f"Scores: {random_choice[1]}")
