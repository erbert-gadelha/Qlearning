import connection as cn
import random

class State:
    def __init__ (self, pos, rot):
        self.pos = pos
        self.rot = rot
        self.action = None
        self.reward = None
        self.enum_rot_ = {0: "N", 1: "L", 2: "S", 3: "O"}
    
    def __str__(self):
        return f"{self.pos:02d}:{self.enum_rot_[self.rot]}-'{self.action}':{self.reward:.{6}f}'"
    
    def set(self, pos, rot):
        self.pos = pos
        self.rot = rot

def hash_function(estado, rotacao):
    hash_value = (estado * 4) + rotacao + 1
    return hash_value
    
def read_table(state):
    estado = hash_function(state.pos, state.rot) - 1
    
    with open("resultado.txt", "r") as table:
        linhas = table.readlines()
    
    if(estado < 0 or estado >= len(linhas)):
        return 'out of range'

    valores = linhas[estado].split(' ')
    
    return {
        'jump': float(valores[0]),
        'left': float(valores[1]),
        'right': float(valores[2]),
    }
    
def write_table(state: State, a):
    if(state == None):
        return
    
    index = hash_function(state.pos, state.rot) - 1

    if index < 0 or index > 96:
        return 'out of range'

    with open("resultado.txt", "r") as table:
        linhas = table.readlines()

    valores = linhas[index].split(' ')

    if state.action == 'jump':
        valores[0] = f"{state.reward:.{6}f}"
    elif state.action == 'left':
        valores[1] = f"{state.reward:.{6}f}"
    else:
        valores[2] = f"{state.reward:.{6}f}\n"

    '''
    for i in range(len(valores)):
        val = float(valores[i])
        valores[i] = (str(val * (1 - a) + state.reward * a))
    '''

    linhas[index] = ' '.join(valores)

    with open("resultado.txt", "w") as table:
        table.writelines(linhas)

def set_next_state(cur_state: State, action, next_state: State, reward):
    if(cur_state == None):
        print('state is None')
        return
    
    if(action == 'jump'):
        index = (cur_state.pos * 3)
    elif(action == 'left'):
        index = (cur_state.pos * 3) + 1
    else:
        index = (cur_state.pos * 3) + 2


    with open("next_states.txt", "r") as file:
        file_lines = file.readlines()

    if index < 0 or index >= len(file_lines):
        print('out of range')
        return
    
    aux = get_next_state(cur_state, action)

    if(aux == None):
        reward = (reward + aux['reward']) / 2

    file_lines[index] = f"{next_state.pos} {next_state.rot} {reward}\n"

    with open("next_states.txt", "w") as file:
        file.writelines(file_lines)

def get_next_state(cur_state: State, action):
    if(cur_state == None):
        print('state is None')
        return
    
    if(action == 'jump'):
        index = (cur_state.pos * 3)
    elif(action == 'left'):
        index = (cur_state.pos * 3) + 1
    else:
        index = (cur_state.pos * 3) + 2

    with open("next_states.txt", "r") as file:
        file_lines = file.readlines()

    if index < 0 or index >= len(file_lines):
        print('out of range')
        return

    data = file_lines[index].split(' ')
    if(len(data) != 3):
        return None
    return {'pos': int(data[0]), 'rot': int(data[1]), 'reward': float(data[2])}

def best_action(state: State, epsilon: float):

    if random.uniform(0, 1) < epsilon:
        return random.choice(['jump', 'left', 'right'])  # Escolhe aleatório

    valores = read_table(state)
    left, right, jump = float(valores['left']), float(valores['right']), float(valores['jump'])

    retorno = 'jump'
    if(right > jump and right > left):
        retorno = 'right'
    elif(left > jump):
        retorno = 'left'
    return retorno

def calculate(state: State, action: str, gamma: float):
    temp1 = get_next_state(state, action)
    if(temp1 == None):
        return 0
    
    temp1 = State(temp1['pos'], temp1['rot'])
    temp2 = read_table(temp1)
    temp3 = best_action(temp1, 0)
    
    return read_table(state)[action]*(1-gamma) + temp2[temp3] * gamma


writing_table = True
isPlaying = True
alpha = 0.3
gamma = 0.95
epsilon = 0.1

#isPlaying = False
if(isPlaying):
    s = cn.connect(157)
    print('[ctrl+c] para encerrar a conexão\n')

    initial = 20
    cur_state = State(initial, 0)
    prev_state = None

    for i in range(5000):

        action = best_action(cur_state, epsilon)  # Escolhe a melhor acao

        estado, recompensa = cn.get_state_reward(s, action)
        receivd_pos = int(estado[2:7], 2)
        receivd_rot = int(estado[7:9], 2)

        cur_state.reward = recompensa
        cur_state.action = action

        set_next_state(cur_state, action, State(receivd_pos, receivd_rot), recompensa)
        
        if(writing_table):
            write_table(cur_state, alpha)

            if(prev_state != None):
                prev_state.reward = calculate(prev_state, prev_state.action, gamma)
                write_table(prev_state, alpha)
        
        if(recompensa == -100):
            print(f' ~ morreu: [{cur_state}] ~\n')
            prev_state = None
        else:
            print(f'[{i:04d}] estado: {cur_state} | recompensa: {"{:04d}".format(recompensa)} | {action} | [{estado}]')

        if(prev_state == None):
            prev_state = State(initial,0)
        
        prev_state.set(cur_state.pos, cur_state.rot)
        prev_state.action = cur_state.action
        prev_state.reward = cur_state.reward

        cur_state.set(receivd_pos, receivd_rot)
        cur_state.action = action

    print('conexão encerrada')