from __future__ import division, print_function
import random

# I have no idea what these numbers should be yet
MIN_ROUNDS = 300
AVERAGE_ROUNDS = 10000

def payout(*args):
    '''Times 3 because this calculates one person's share'''
    return args.count('h')*3
    
class Game(object):   
    def __init__(self, players, verbose=True):
        self.verbose = verbose
        self.max_rounds = MIN_ROUNDS + int(random.expovariate(1/(AVERAGE_ROUNDS-MIN_ROUNDS)))
        self.round = 0
        self.attempts = 0
        
        self.players = players # to set self.P
        player_ids = range(len(self.players))
        print(player_ids)
        food = [300*(self.P-1)]*self.P
        reputation = [0]*self.P
        self.players = [[p,f,r,i] for p,f,r,i in zip(players,food,reputation,player_ids)]
        header_template = '%s.food\t%s.rep'
        if self.verbose:
            print('\t'.join([header_template % (p[0], p[0]) for p in self.players]))
        
        
    @property
    def m_bonus(self):
        return 2*(self.P-1)
    
    @property
    def P(self):
        return len(self.players)
        
    def calculate_m(self):
        try:
            return random.randrange(1, self.P*(self.P-1))
        except ValueError:
            # m stops existing for 2 players
            return 3
            
        
    def play_round(self):
        # TODO: Refactor this beast
        self.round += 1
        m = self.calculate_m()
        
        random.shuffle(self.players)
        reputation_list = tuple(0 if self.attempts == 0 else p[2]/self.attempts for p in self.players)
        
        strategies = [p[0].hunt_choices(self.round, p[1], 0 if self.attempts == 0 else p[2]/self.attempts,
                                        m, reputation_list) for p in self.players]
        
        self.attempts += self.P-1
        
        for i in range(self.P):
            strategies[i][i] = 's'

        results = [[0 for i in range(self.P)] for j in range(self.P)]                        
        
        for i in range(self.P):
            for j in range(i+1, self.P):
                if i != j:
                    results[i][j] = results[j][i] = payout(strategies[i][j], strategies[j][i])
                
        total_hunts = sum(s.count('h') for s in strategies)//2
        bonus = self.m_bonus if total_hunts >= m else 0
        
        for strat, result, player in zip(strategies, results, self.players):
            food = sum(result)
            hunts = strat.count('h')
            
            player[1] += food-4*hunts-2*(self.P-1)+bonus
            
            player[2] += hunts
            
            player[0].hunt_outcomes(food)
            player[0].round_end(bonus, m, total_hunts)
            
            
        if self.verbose:
#            print([(name, food, hunts/self.attempts) for name, food, hunts in self.players])
#            print([(name, food, hunts/self.attempts, player_id) for name, food, hunts, player_id in sorted(self.players, key=lambda x:x[3])])
            print('\t'.join(["%s\t%s" % (food, hunts/self.attempts) for name, food, hunts, player_id in sorted(self.players, key=lambda x:x[3])]))
                   
        
        if self.game_over():
            raise StopIteration
            
        
    def game_over(self):
        self.players = [p for p in self.players if p[1] > 0]
        return (self.P < 2) or (self.round > self.max_rounds)
        
        
    def play_game(self):
        '''
        Preferred way to run the game to completion
        Written this way so that I can step through rounds one at a time
        '''
        
        while True:
            try:
                self.play_round()
            except StopIteration:
#                print(self.players)
                break
        
