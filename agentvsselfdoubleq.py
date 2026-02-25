import random
import tictactoe
import pickle
import math
import json

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = {}
        self.q1_table = {}
        self.q2_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def get_q_values(self, state):

        if state not in self.q_table:
            #self.q_table[state] = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
            self.q_table[state] = [0.0]* 9
        return self.q_table[state]
    
    def get_q1(self, state):

        if state not in self.q1_table:
            self.q1_table[state] = [0.0]* 9
        return self.q1_table[state]
    
    def get_q2(self, state):

        if state not in self.q2_table:
            self.q2_table[state] = [0.0]* 9
        return self.q2_table[state]

    
    def choose_action(self, state, available_moves):

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_moves)
        
        #q_values = self.get_q_values(state)
        q1_vals = self.get_q1(state)
        q2_vals = self.get_q2(state)
        valid_q = {i:q1_vals[i-1] + q2_vals[i-1] for i in available_moves}
        return max(valid_q, key=valid_q.get)
    
    def update(self, state, action, reward, next_state, available_moves, done):

        old_q1 = self.get_q1(state)[action-1]
        old_q2 = self.get_q2(state)[action-1]

        if done:
            self.q1_table[state][action-1] += self.alpha * (reward - old_q1)
            self.q2_table[state][action-1] += self.alpha * (reward - old_q2)
            return
        
        if random.random() < 0.5:
            next_q1_values = self.get_q1(next_state)
            best_next_action = max(available_moves, key=lambda x: next_q1_values[x-1])
            target = reward + self.gamma * self.get_q2(next_state)[best_next_action-1]
            self.q1_table[state][action-1] += self.alpha * (target - old_q1)
        else:

            next_q2_values = self.get_q2(next_state)
            best_next_action = max(available_moves, key=lambda x: next_q2_values[x-1])
            target = reward + self.gamma * self.get_q1(next_state)[best_next_action-1]
            self.q2_table[state][action-1] += self.alpha * (target - old_q2)




    '''
    def update(self, state, action, reward, next_state, done):
        old_q = self.get_q_values(state)[action-1]

        if done:
            target = reward
        else:
            # 1. Get all Q-values for the next state
            next_q_values = self.get_q_values(next_state)
            
            # 2. Find which indices are actually empty (not 88 and not 99)
            valid_moves = [i for i in range(9) if next_state[i] != 88 and next_state[i] != 99]
            
            if not valid_moves: # If board is completely full
                target = reward
            else:
                # 3. Only take the max Q-value from the VALID moves
                next_max_q = max([next_q_values[i] for i in valid_moves])
                target = reward + self.gamma * next_max_q

        self.q_table[state][action-1] += self.alpha * (target - old_q)

'''

if __name__ == "__main__":

    game = tictactoe.Tictactoe()
    t = game.board_setup()
    board = [1,2,3,4,5,6,7,8,9]
    available_moves = [1,2,3,4,5,6,7,8,9]
    #agent = QLearningAgent()
    agent_X = QLearningAgent(epsilon=1.0)
    agent_O = QLearningAgent(epsilon=1.0)
    episodes = 1000000
    max_epsilon = 1.0
    min_epsilon = 0.01
    decay_rate = 0.000005
    for episode in range(episodes):
        agent_X.epsilon = min_epsilon + (max_epsilon - min_epsilon) * math.exp(-decay_rate * episode)
        agent_O.epsilon = min_epsilon + (max_epsilon - min_epsilon) * math.exp(-decay_rate * episode)
        game.ttt_reset(t)
        board = [1,2,3,4,5,6,7,8,9]
        available_moves = [1,2,3,4,5,6,7,8,9]

        state_X, action_X = None, None
        state_O, action_O = None, None
            
        while True:
            
            state = tuple(board)
            move_X = agent_X.choose_action(state, available_moves)
            #available_moves.pop(move)
            available_moves.remove(move_X)
            board[move_X-1] = 99
            game.ttt_makeMove(t, move_X)
            next_state = tuple(board)
            if state_O is not None:
                if game.ttt_hasWinner(t):
                    #print("You Win")
                    agent_O.update(state_O, action_O, -100, next_state,available_moves,  True)
                    agent_X.update(state, move_X, 10, next_state,available_moves,  True)
                    break
                elif game.ttt_isDraw(t):
                    #print("Game Draw")
                    agent_O.update(state_O, action_O, 4, next_state,available_moves,  True)
                    agent_X.update(state, move_X, 4, next_state,available_moves,  True)
                    break
                else:
                    agent_O.update(state_O, action_O, 0, next_state, available_moves, False)
            
           
            state_X = state
            action_X = move_X
            state = tuple(board)
            game.ttt_switchPlayer(t)
            move_O = agent_O.choose_action(state, available_moves)
            game.ttt_makeMove(t, move_O)
            #available_moves.pop(move)
            available_moves.remove(move_O)
            board[move_O-1] = 88
            next_state = tuple(board)
            if state_X is not None:
                if game.ttt_hasWinner(t):
                    #print("Your Opp won")
                    agent_X.update(state_X, action_X, -100, next_state, available_moves, True)
                    agent_O.update(state, move_O, 10, next_state,available_moves,  True)
                    break
                elif game.ttt_isDraw(t):
                    agent_X.update(state_X, action_X, 4, next_state,available_moves,  True)
                    agent_O.update(state, move_O, 4, next_state, available_moves, True)
                    break
                else:
                    agent_X.update(state_X, action_X, 0, next_state, available_moves, False)

            state_O = state
            action_O = move_O
            game.ttt_switchPlayer(t)

        if episode % 1000 == 0:
            print(f"Completed {episode} training games...")

    print("Training Complete! Q-Table size:", len(agent_X.q_table))

    with open("agent_brain.pkl", "wb") as f:
        #pickle.dump(agent_X.q_table, f)
        pickle.dump(agent_O.q_table, f)
    print("Q-Table successfully saved to agent_brain.pkl")

    print("Combining Q1 and Q2 tables for export...")
    exportable_q_table = {}

    # 1. Get every unique state that exists in EITHER table
    all_states = set(agent_O.q1_table.keys()).union(set(agent_O.q2_table.keys()))

    # 2. Add the values of Q1 and Q2 together for every state
    for state in all_states:
        # If a state is missing from one table, default to an array of zeroes
        q1_values = agent_O.q1_table.get(state, [0.0] * 9)
        q2_values = agent_O.q2_table.get(state, [0.0] * 9)
        
        # Sum the values element by element
        combined_values = [q1 + q2 for q1, q2 in zip(q1_values, q2_values)]
        
        exportable_q_table[str(state)] = combined_values

    # 3. Save to JSON for your web app
    with open("agent_brain_double_q.json", "w") as f:
        json.dump(exportable_q_table, f)

    print("Double Q-Learning Brain successfully merged and exported to agent_brain.json!")
    print("Brain successfully exported to agent_brain.json!")
