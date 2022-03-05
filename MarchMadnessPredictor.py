# This will be separated into three parts.
# First calculates pythag (A.K.A. how "good" team X is), accounting for offensive and defensive efficiency.
# Second is log5, which calculates the probability of team A beating team B. Also added expected value to determine which team is more rewarding to choose on average.
# Third calculates expected tempo and scores.
# Don't take this too seriously! Just a fun little project.

import math
import random

# allows user to play multiple times.
Play = True
while Play:
    def pythag(AdjO, AdjD):
        
        EW = (AdjO**11.5) / ((AdjO**11.5) + (AdjD**11.5))
        # the following tests pythag calculation:
        # print(str(EW))

        return EW

    # user input for team A and B values
    # Team A:
    ASeed = int(input('Team A official seed: '))
    AdjOA = float(input('Team A adjusted offensive efficiency: '))
    AdjDA = float(input('Team A adjusted defensive efficiency: '))
    ATempo = float(input('Team A Adjusted Tempo: '))
    
    # A expected winning probability:
    PythagA = pythag(AdjOA, AdjDA)
    # print(str(PythagA))

    # Team B:
    BSeed = int(input('Team B official seed: '))
    AdjOB = float(input('Team B adjusted offensive efficiency: '))
    AdjDB = float(input('Team B adjusted defensive efficiency: '))
    BTempo = float(input('Team B Adjusted Tempo: '))

    # B expected winning probability:
    PythagB = pythag(AdjOB, AdjDB)
    #print(str(PythagB))

    # Log5: Prob Team A wins against Team B (similar to ELO method in chess)
    def log5(ProbA, ProbB):

        EWA = (ProbA - ProbA *  ProbB) / (ProbA + ProbB -2 * ProbA * ProbB)

        return EWA

    AdjAProb = log5(PythagA, PythagB)
    AdjBProb = 1 - AdjAProb

    print('Adjusted probability of team A winning: ' + str(AdjAProb))
    print('Adjusted probability of team B winning: ' + str(AdjBProb))

    #round needed to calculate expected points
    round = int(input('Round of matchup (Round 1 = 1, Round 2 = 2, Sweet 16 = 3, Elite 8 = 4, Final Four = 5. Championship = 6): ')) - 1

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
    
    #predicts tempo (possessions per 40 minutes)
    def tempo(AdjTA, AdjTB):
        
        global ET

        ET = (AdjTA / 67.5) * (AdjTB / 67.5) * 67.5

        return ET

    print('The expected tempo for this matchup is: ' + str(tempo(ATempo, BTempo)))

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