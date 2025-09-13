import connection
import random
import os

class CleanQLearning:
    def __init__(self, alpha=0.1, gamma=0.97, epsilon=0.9,
                epsilon_decay=0.995, episodes=2000):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.episodes = episodes
        
        self.actions = ["left", "right", "jump"]
        self.num_states = 96
        self.num_actions = 3
        
        self.q_table = self.load_or_create_table()
        self.routes = []

    def load_or_create_table(self):
        if os.path.exists("q-table.md"):
            try:
                with open("q-table.md", 'r') as f:
                    lines = f.readlines()[2:]  # Skip header
                
                q_table = []
                for line in lines:
                    if line.strip():
                        values = list(map(float, line.strip().split()))
                        if len(values) == 3:
                            q_table.append(values)
                
                if len(q_table) == self.num_states:
                    return q_table
            except:
                pass
        
        return [[0.1 for _ in range(self.num_actions)] for _ in range(self.num_states)]

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 2)
        else:
            return self.q_table[state].index(max(self.q_table[state]))

    def update_q_table(self, state, action, reward, next_state, done):
        max_q_next = 0 if done else max(self.q_table[next_state])
        target = reward + self.gamma * max_q_next
        current_q = self.q_table[state][action]
        self.q_table[state][action] = current_q + self.alpha * (target - current_q)

    def is_episode_finished(self, reward, steps):
        if reward == 300:
            return True, "SUCCESS"
        elif reward == -100:
            return True, "DEATH"
        elif steps >= 500:
            return True, "TIMEOUT"
        else:
            return False, "CONTINUE"

    def get_state_info(self, state):
        platform = state >> 2
        direction = state & 0b11
        direction_names = ["Norte", "Leste", "Sul", "Oeste"]
        return platform, direction, direction_names[direction]

    def train_agent(self, socket):
        successes = 0
        deaths = 0
        timeouts = 0
        
        for episode in range(self.episodes):
            current_state = 0
            episode_steps = 0
            done = False
            route = []
            
            while not done:
                platform, direction, dir_name = self.get_state_info(current_state)
                action_idx = self.choose_action(current_state)
                action = self.actions[action_idx]
                
                route.append(f"P{platform} {dir_name} -> {action}")
                
                try:
                    next_state_str, reward_str = connection.get_state_reward(socket, action)
                    next_state = int(next_state_str, 2)
                    reward = float(reward_str)
                except:
                    reward = -100
                    next_state = 0
                    done = True
                    break
                
                done, status = self.is_episode_finished(reward, episode_steps)
                self.update_q_table(current_state, action_idx, reward, next_state, done)
                
                if status == "SUCCESS":
                    successes += 1
                    self.routes.append({
                        'episode': episode + 1,
                        'route': route,
                        'steps': episode_steps,
                        'status': status
                    })
                elif status == "DEATH":
                    deaths += 1
                elif status == "TIMEOUT":
                    timeouts += 1
                
                current_state = next_state
                episode_steps += 1
            
            self.epsilon = max(self.epsilon * self.epsilon_decay, 0.01)
            
            if (episode + 1) % 100 == 0:
                recent_successes = sum(1 for i in range(max(0, episode-99), episode+1)
                                     if any(r['episode'] == i+1 for r in self.routes))
                success_rate = recent_successes
                print(f"Episódio {episode+1:4d} | Sucessos últimos 100: {success_rate:2d} | ε: {self.epsilon:.3f}")
        
        final_success_rate = (successes / self.episodes) * 100
        print(f"\nResultado Final: {successes}/{self.episodes} sucessos ({final_success_rate:.2f}%)")
        
        self.save_files()
        return final_success_rate

    def test_policy(self, socket, num_tests=20):
        successes = 0
        original_epsilon = self.epsilon
        self.epsilon = 0
        
        for test in range(num_tests):
            current_state = 0
            steps = 0
            done = False
            
            while not done and steps < 300:
                action_idx = self.q_table[current_state].index(max(self.q_table[current_state]))
                action = self.actions[action_idx]
                
                try:
                    next_state_str, reward_str = connection.get_state_reward(socket, action)
                    next_state = int(next_state_str, 2)
                    reward = float(reward_str)
                except:
                    break
                
                done, status = self.is_episode_finished(reward, steps)
                if status == "SUCCESS":
                    successes += 1
                
                current_state = next_state
                steps += 1
        
        self.epsilon = original_epsilon
        test_success_rate = (successes / num_tests) * 100
        print(f"Teste: {successes}/{num_tests} sucessos ({test_success_rate:.2f}%)")
        return test_success_rate

    def save_files(self):
        # Salva rotas
        with open("route.md", 'w') as f:
            f.write("# Rotas de Sucesso\n\n")
            for route_data in self.routes:
                f.write(f"## Episódio {route_data['episode']} ({route_data['steps']} passos)\n")
                for step in route_data['route']:
                    f.write(f"- {step}\n")
                f.write("\n")
        
        # Salva Q-table
        with open("q-table.md", 'w') as f:
            f.write("# Q-Table\n\n")
            f.write("| Estado | Left | Right | Jump | Plataforma | Direção |\n")
            f.write("|--------|------|-------|------|------------|----------|\n")
            
            direction_names = ["Norte", "Leste", "Sul", "Oeste"]
            for state in range(self.num_states):
                platform = state >> 2
                direction = state & 0b11
                dir_name = direction_names[direction]
                
                left_val = f"{self.q_table[state][0]:.3f}"
                right_val = f"{self.q_table[state][1]:.3f}"
                jump_val = f"{self.q_table[state][2]:.3f}"
                
                f.write(f"| {state:2d} | {left_val:>8} | {right_val:>9} | {jump_val:>8} | {platform:2d} | {dir_name} |\n")


if __name__ == "__main__":
    socket = connection.connect(2037)
    if socket == 0:
        print("Falha na conexão!")
        exit()
    
    agent = CleanQLearning(episodes=10000)
    agent.train_agent(socket)
    agent.test_policy(socket)
