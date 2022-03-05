# This will be separated into three parts.
# First calculates pythag (A.K.A. how "good" team X is), accounting for offensive and defensive efficiency.
# Second is log5, which calculates the probability of team A beating team B. Also added expected value to determine which team is more rewarding to choose on average.
# Third calculates expected tempo and scores.
# Don't take this too seriously! Just a fun little project.

import math
import random
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import lxml

#scrapes KenPom:
# Base url
base_url = 'http://kenpom.com/index.php'

f = requests.get(base_url)
soup = BeautifulSoup(f.text, 'lxml')
table_html = soup.find_all('table', {'id': 'ratings-table'})

thead = table_html[0].find_all('thead')

table = table_html[0]
for x in thead:
    table = str(table).replace(str(x), '')

#print(table)

#define df (dataframe)
df = pd.read_html(table)[0]

# allows user to play multiple times.
Play = True
while Play:
    #finds Adjusted Offensive Efficiency of team
    def AdjOSearch(Team):
        AdjO = int(df[df[1] == Team][5])
        return(AdjO)

    #finds Adjusted Defensive Efficiency of team
    def AdjDSearch(Team):
        AdjD = int(df[df[1] == Team][7])
        return(AdjD)

    #finds Adjusted Tempo of team
    def AdjTSearch(Team):
        AdjT = int(df[df[1] == Team][9])
        return AdjT
    
    #calculates pythag of team, aka how "good" they are
    def pythag(AdjO, AdjD):
        
        EW = (AdjO**11.5) / ((AdjO**11.5) + (AdjD**11.5))
        # the following tests pythag calculation:
        # print(str(EW))

        return EW

    # Log5: Prob Team A wins against Team B (similar to ELO method in chess)
    def log5(ProbA, ProbB):

        EWA = (ProbA - ProbA *  ProbB) / (ProbA + ProbB -2 * ProbA * ProbB)

        return EWA

    #predicts tempo (possessions per 40 minutes)
    def tempo(AdjTA, AdjTB):
        
        global ET

        ET = (AdjTA / 67.5) * (AdjTB / 67.5) * 67.5

        return ET

    #finally expected points for team A and team B
    def points(APointsFor, BPointsFor, APointsAgainst, BPointsAgainst):

        #team A expected points
        EAP = (APointsFor / 103.7) * (BPointsAgainst / 103.7) * 103.7
        #accounting for expected tempo:
        EAP = EAP * (ET / 100)

        #team B expected points
        EBP = (BPointsFor / 103.7) * (APointsAgainst / 103.7) * 103.7
        #accounting for expected tempo:
        EBP = EBP * (ET / 100)
        
        return EAP, EBP

    # user input and values for team A and B
    TeamA = input('Team A Name (As seen on KenPom): ')
    ASeed = int(input('Team A official seed: '))
    AdjOA = AdjOSearch(TeamA)
    AdjDA = AdjDSearch(TeamA)
    ATempo = AdjTSearch(TeamA)

    # Team B:
    TeamB = input('Team B Name (As seen on KenPom): ')
    BSeed = int(input('Team B official seed: '))
    AdjOB = AdjOSearch(TeamB)
    AdjDB = AdjDSearch(TeamB)
    BTempo = AdjTSearch(TeamB)

    #round needed to calculate expected points
    round = int(input('Round of matchup (Round 1 = 1, Round 2 = 2, Sweet 16 = 3, Elite 8 = 4, Final Four = 5. Championship = 6): ')) - 1

    #calculates team A expected winning probability: 
    PythagA = pythag(AdjOA, AdjDA)
    # print(str(PythagA))

    # B expected winning probability:
    PythagB = pythag(AdjOB, AdjDB)
    #print(str(PythagB))

    AdjAProb = log5(PythagA, PythagB)
    AdjBProb = 1 - AdjAProb

    print('Adjusted probability of team A winning: ' + str(AdjAProb))
    print('Adjusted probability of team B winning: ' + str(AdjBProb))

    initialpoints = 2**round

    #expected value for the teams (including non-bonus points):
    #NOTE: is this initial points + seed or initial points * seed?
    AReturn = AdjAProb * (initialpoints + ASeed)
    BReturn = AdjBProb * (initialpoints + BSeed)

    #in the case that the bonus is initial points * seed, not +
    #AReturn = AdjAProb * (initialpoints * ASeed)
    #BReturn = AdjBProb * (initialpoints * BSeed)

    print('Team A expected winnings: %s' % str(AReturn))
    print('Team B expected winnings: %s' % str(BReturn))
    
    print('The expected tempo for this matchup is: ' + str(tempo(ATempo, BTempo)))

    print('The expected points scored for team A and team B, respectively: ' + str(points(AdjOA, AdjOB, AdjDA, AdjDB)))

    #this simply allows user to try another simulation
    playagain = False

    while not playagain:
        playagain = input('Do you want to simulate another game? ')
        
        if playagain == 'No' or playagain == 'no' or playagain == 'N' or playagain =='n':
            Play = False

        elif playagain == 'Yes' or playagain == 'yes' or playagain == 'Y' or playagain =='y':
            Play = True

        else:
            playagain = False