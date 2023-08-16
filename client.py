import connection as cn
import random

rot_ = {0: "N", 1: "L", 2: "S", 3: "O"}

def hash_function(estado, rotacao):
    hash_value = (estado * 4) + rotacao + 1
    return hash_value
    
def read_table(posicao, rotacao):
    estado = hash_function(posicao, rotacao) - 1
    
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
    
def write_table(posicao, rotacao, acao, recompensa, a):
    estado = hash_function(posicao, rotacao) - 1

    if estado < 0 or estado > 96:
        return 'out of range'

    with open("resultado.txt", "r") as table:
        linhas = table.readlines()

    valores = linhas[estado].split(' ')

    if acao == 'jump':
        valores[0] = f"{recompensa:.{6}f}"
    elif acao == 'left':
        valores[1] = f"{recompensa:.{6}f}"
    else:
        valores[2] = f"{recompensa:.{6}f}"

    for i in range(len(valores)):
        val = float(valores[i])
        valores[i] = (str(val * (1 - a) + recompensa * a))

    linhas[estado] = ' '.join(valores) + '\n'

    with open("resultado.txt", "w") as table:
        table.writelines(linhas)

def best_move(posicao, rotacao):
    valores = read_table(posicao, rotacao)
    left, right, jump = float(valores['left']), float(valores['right']), float(valores['jump'])

    retorno = 'jump'
    if(right > jump and right > left):
        retorno = 'right'
    elif(left > jump):
        retorno = 'left'
    return retorno



writing_table = True
playing = False
playing = True
alpha = 0.3
gamma = 0.95
epsilon = 0.1



if(playing):
    s = cn.connect(157)
    print('[ctrl+c] para encerrar a conexão\n')

    pos, rot = 20, 0

    for i in range(10000):
        if random.uniform(0, 1) < epsilon:
            action = random.choice(['jump', 'left', 'right'])  # Escolha aleatória com probabilidade ε
        else:
            action = best_move(pos, rot)  # Escolha com base na política greedy (1 - ε)


        estado, recompensa = cn.get_state_reward(s, action)
        actual_pos = int(estado[2:7], 2)
        actual_rot = int(estado[7:9], 2)

        
        if(writing_table):
            write_table(pos, rot, action, recompensa, alpha)
        
        if(recompensa == -100):
            print(f'\n ~ morreu: = [{pos}][{rot}-{rot_[rot]}] ~\n')
        else:
            print(f'[{i:04d}] estado: {"{:02d}".format(pos)}-{rot_[rot]} | recompensa: {"{:04d}".format(recompensa)} | {action} | [{estado}]')

        pos, rot= actual_pos, actual_rot        


    s.close()
    print('conexão encerrada')