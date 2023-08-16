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
        #return f"{self.pos:02d}:{self.enum_rot_[self.rot]}-'{self.action}':{self.reward:.{6}f}'"
        return f"{self.pos:02d}:{self.enum_rot_[self.rot]}"
    
    def set(self, pos, rot):
        self.pos = pos
        self.rot = rot

def hash_function(state: State):
    hash_code = (state.pos * 4) + state.rot + 1
    return hash_code
    
def read_table(state: State):
    if(state == None):
        return None

    estado = hash_function(state) - 1
    
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
        return None
    
    index = hash_function(state) - 1
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

    with open("resultado.txt", "w") as table:
        linhas[index] = ' '.join(valores)
        table.writelines(linhas)

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
    s = cn.connect(2037)
    print('[ctrl+c] para encerrar a conexão\n')

    pos, rot = 20, 0

    for i in range(10000):
        if random.uniform(0, 1) < epsilon:
            action = random.choice(['jump', 'left', 'right'])  # Escolha aleatória com probabilidade ε
        else:
            action = best_move(pos, rot)  # Escolha com base na política greedy (1 - ε)


        estado, recompensa = cn.get_state_reward(s, action)
        receivd_pos = int(estado[2:7], 2)
        receivd_rot = int(estado[7:9], 2)

        cur_state.reward = recompensa
        cur_state.action = action

        
        if(writing_table):
            write_table(pos, rot, action, recompensa, alpha)
        
        if(recompensa == -100):
            print(f' ~ morreu: [{cur_state}] ~\n')
            if(writing_table):
                write_table(cur_state, alpha)
            cur_state = State(initial, 0)
            continue
        
        print(f'[{i:04d}] estado: {cur_state} | recompensa: {"{:04d}".format(recompensa)} | {read_table(cur_state)}')

        if(writing_table):
            write_table(cur_state, alpha)

        if(prev_state == None):
            prev_state = State(initial,0)
        
        prev_state.set(cur_state.pos, cur_state.rot)
        prev_state.action = cur_state.action
        prev_state.reward = cur_state.reward

        cur_state.set(actual_pos, actual_rot)
        cur_state.action = action
        cur_state.rot = actual_rot

    print('conexão encerrada')