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
base_url = 'https://kenpom.com/index.php?y=2021'

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
    #separates Team Name from Seed. Why must you do this to me KenPom???
    def sep(TeamName):
        Seed = []
        Name = ''
        for t in TeamName:

            try:
                Seed.append(float(t))
            except ValueError:
                Name = Name + t

        l = len(Name)
        Name = Name[:l-1]

        if Seed:
            return Name, Seed[0]

        else:
            return Name, False
    
    #makes sure Team is on KenPom
    def NameCheck(TeamName):
        try:
            boolean_findings = df[1].str.contains(TeamName)

            total_occurence = boolean_findings.sum()

            if(total_occurence) == 0 and TeamName != df[1][0]:
                print('Error: Team name not found. Check KenPom and try again (Capitalization matters!).')
                return False

            #the sum for the best team is still zero, so we have to account for this exception
            elif TeamName == df[1][0]:
                return True
    
            else:
                return True

        except:
            print('Error: Team name not found. Check KenPom and try again (Capitalization matters!). Make sure team has correct seed.')
            return False
    
    #finds Adjusted Offensive Efficiency of team
    def AdjOSearch(Team):
        AdjO = float(df[df[1] == Team][5])
        return(AdjO)

    #finds Adjusted Defensive Efficiency of team
    def AdjDSearch(Team):
        AdjD = float(df[df[1] == Team][7])
        return(AdjD)

    #finds Adjusted Tempo of team
    def AdjTSearch(Team):
        AdjT = float(df[df[1] == Team][9])
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
        ANameAndSeed = input('Team A Name and Seed (Name and Seed separated with space. Ex: "Gonzaga 1"): ')
        if NameCheck(ANameAndSeed) and sep(ANameAndSeed)[1]:
            TeamA = sep(ANameAndSeed)[0]
            ASeed = sep(ANameAndSeed)[1]
            NamedTeamA = True

        else:
            NamedTeamA = False

    AdjOA = AdjOSearch(ANameAndSeed)
    AdjDA = AdjDSearch(ANameAndSeed)
    ATempo = AdjTSearch(ANameAndSeed)

    # Team B name + check to make sure it's on KenPom
    NamedTeamB = False
    while not NamedTeamB:
        BNameAndSeed = input('Team B Name and Seed (Name and Seed separated with space. Ex: "Gonzaga 1"): ')
        if NameCheck(BNameAndSeed) and sep(BNameAndSeed)[1]:
            TeamB = sep(BNameAndSeed)[0]
            BSeed = sep(BNameAndSeed)[1]
            NamedTeamB = True

        else:
            NamedTeamB = False

    AdjOB = AdjOSearch(BNameAndSeed)
    AdjDB = AdjDSearch(BNameAndSeed)
    BTempo = AdjTSearch(BNameAndSeed)

    #round needed to calculate expected points + check to make sure it's a number between 1 and 6
    EnteredRound = False
    while not EnteredRound:
        try:
            round = int(input('Round of matchup (Round 1 = 1, Round 2 = 2, Sweet 16 = 3, Elite 8 = 4, Final Four = 5. Championship = 6): ')) - 1
            if round >= 0 and round <= 5:
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

    print('Adjusted probability of ' + TeamA + ' winning: ' + str(AdjAProb))
    print('Adjusted probability of ' + TeamB + ' winning: ' + str(AdjBProb))

    initialpoints = 2**round

    #expected value for the teams (including non-bonus points):
    #NOTE: is this initial points + seed or initial points * seed?
    #AReturn = AdjAProb * (initialpoints + ASeed)
    #BReturn = AdjBProb * (initialpoints + BSeed)

    #in the case that the bonus is initial points * seed, not +
    AReturn = AdjAProb**1.5 * (initialpoints * int(ASeed))
    BReturn = AdjBProb**1.5 * (initialpoints * int(BSeed))

    print(TeamA + ' expected winnings: %s' % str(AReturn))
    print(TeamB + ' expected winnings: %s' % str(BReturn))
    
    print('The expected tempo for this matchup is: ' + str(tempo(ATempo, BTempo)))

    print('The expected points scored for ' + TeamA + ': ' + str(points(AdjOA, AdjOB, AdjDA, AdjDB)[0]))
    print('The expected points scored for ' + TeamB + ': ' + str(points(AdjOA, AdjOB, AdjDA, AdjDB)[1]))

    #print('The expected total points scored for both teams: ' + str(points(AdjOA, AdjOB, AdjDA, AdjDB)[2])))

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