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
    #makes sure Team is on KenPom
    def NameCheck(TeamName):
        boolean_findings = df[1].str.contains(TeamName)

        total_occurence = boolean_findings.sum()

        if(total_occurence) == 0 and TeamName != df[1][0]:
            print('Error: Team name not found. Check KenPom and try again.')
            return False

        #the sum for the best team is still zero, so we have to account for this exception
        elif TeamName == df[1][0]:
            return True
    
        else:
            return True
    
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

        AvgTempo = df[9].mean()

        ET = (AdjTA / AvgTempo) * (AdjTB / AvgTempo) * AvgTempo

        return ET

    #finally expected points for team A and team B
    def points(APointsFor, BPointsFor, APointsAgainst, BPointsAgainst):
        
        AvgPoints = df[5].mean()

        #team A expected points
        EAP = (APointsFor / AvgPoints) * (BPointsAgainst / AvgPoints) * AvgPoints
        #accounting for expected tempo:
        EAP = EAP * (ET / 100)

        #team B expected points
        EBP = (BPointsFor / AvgPoints) * (APointsAgainst / AvgPoints) * AvgPoints
        #accounting for expected tempo:
        EBP = EBP * (ET / 100)
        
        return EAP, EBP

    # user input and values for team A and B
    #Team A Name + check to make sure it's on KenPom
    NamedTeamA = False
    while not NamedTeamA:
        TeamA = input('Team A Name (As seen on KenPom): ')
        if NameCheck(TeamA) == True:
            NamedTeamA = True

        else:
            NamedTeamA = False

    #Team A seed + check to make sure it's between 1 and 16
    EnteredASeed = False
    while not EnteredASeed:
        try:
            ASeed = int(input('Team A official seed: '))
            
            if ASeed >= 1 and ASeed <= 16:
                EnteredASeed = True
            
            else:
                print('Seed must be a number between 1 and 16. Try again.')
                EnteredASeed = False

        except:
            print('Seed must be a number between 1 and 16. Try again.')
            EnteredASeed = False
    
    AdjOA = AdjOSearch(TeamA)
    AdjDA = AdjDSearch(TeamA)
    ATempo = AdjTSearch(TeamA)

    # Team B name + check to make sure it's on KenPom
    NamedTeamB = False
    while not NamedTeamB:
        TeamB = input('Team B Name (As seen on KenPom): ')
        if NameCheck(TeamB) == True:
            NamedTeamB = True

        else:
            NamedTeamB = False
    
    #Team B seed + check to make sure it's between 1 and 16
    EnteredBSeed = False
    while not EnteredBSeed:
        try:
            BSeed = int(input('Team B official seed: '))
            
            if BSeed >= 1 and BSeed <= 16:
                EnteredBSeed = True
            
            else:
                print('Seed must be a number between 1 and 16. Try again.')
                EnteredBSeed = False

        except:
            print('Seed must be a number between 1 and 16. Try again.')
            EnteredBSeed = False

    AdjOB = AdjOSearch(TeamB)
    AdjDB = AdjDSearch(TeamB)
    BTempo = AdjTSearch(TeamB)

    #round needed to calculate expected points + check to make sure it's a number between 1 and 6
    EnteredRound = False
    while not EnteredRound:
        try:
            round = int(input('Round of matchup (Round 1 = 1, Round 2 = 2, Sweet 16 = 3, Elite 8 = 4, Final Four = 5. Championship = 6): ')) - 1
            if round >= 1 and round <= 6:
                EnteredRound = True

            else:
                print('Error: Round must be a number between 1 and 6. Try again.')
                EnteredRound = False

        except:
            print('Error: Round must be a number between 1 and 6. Try again.')
            EnteredRound = False

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