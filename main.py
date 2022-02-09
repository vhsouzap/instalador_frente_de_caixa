# -*- conding: ISO-8859-1 -*-
import os
import socket
from itertools import product
from time import sleep
import PySimpleGUI as sg
import zipfile
import crypt
import requests
from datetime import datetime
from threading import Thread

def download_file_from_google_drive(id, destination):
    URL = "https://drive.google.com/u/0/uc?id=1BlN-C23F31daFtXV7oIUW-eye1Sm0oB4&export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
               f.write(chunk)

def ValidaExec(url):
    try:
        response = requests.get(url, stream=True)

        if response.content == b'1':
            return 1
        else:
            return 0
    except:
        janela_popup('ERRO CONEXÃO:','Sistema não pode ser iniciado devido a um problema de conexão.\nPor favor verifique sua conexão com a internet e tente novamente.', size=(500,100))
        
def Get_IP(dados_aplicacao):
    IP_SERVER = dados_aplicacao['IP_ServerUn']
    PORTA_SERVER = int(dados_aplicacao['cod_tcp'])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((IP_SERVER, PORTA_SERVER))
        s.sendall(b'\x02000000000600X' + str.encode(dados_aplicacao['estacao']) + str.encode('\x03\xfd\xc9\xea\r\n'))

    except ConnectionRefusedError:
        return sg.popup('ERRO:', f'Conexão negada pelo servidor remoto, por favor verifique a execução\n da aplicação que usa a porta {PORTA_SERVER}\n ou se a porta/host informada(o) é a correta(o).', size=(300, 200), icon='rpinfo.png')

    else:
        while True:
            data = s.recv(1024)
            data_server = data

            if dados_aplicacao['unidade'] in str(data_server):
                # Unidade válida
                return sg.Popup('ADVERTÊNCIA', f'Unidade {dados_aplicacao["unidade"]} informada validada com sucesso!', icon='rpinfo.png')
            else:
                # Unidade inválida
                return sg.Popup('ERRO:','Unidade informada inválida para este IP, verifique o código da unidade.', icon='rpinfo.png')

# Função para validar os valores enviados pelo usuário e gravar
def Executation(values='', objeto=None):
    os.chdir('/home/rpdv/frente')

    #funcao_ip = Get_IP(values['IP_ServerUn'], values['cod_tcp'])

    # Procedimento para alteração de arquivo tipo ini
    with open('sistema.ini', 'r', encoding='ISO-8859-1') as system:
        inf = system.readlines()

        for v in inf:
            if 'Unidade' in v:
                linha = list(inf[inf.index(v)].partition('='))
                linha[2] = values['unidade'] + '\n'
                linha = ''.join(linha)
                inf[inf.index(v)] = linha

        for i in inf:
            if 'Estacao' in i:
                linha = list(inf[inf.index(i)].partition('='))
                linha[2] = values['estacao'] + '\n'
                linha = ''.join(linha)
                inf[inf.index(i)] = linha

        for ip in inf:
            if 'EnderecoServerRPDV' in ip:
                linha = list(inf[inf.index(ip)].partition('='))
                linha[2] = values['IP_ServerUn'] + '\n'
                linha = ''.join(linha)
                inf[inf.index(ip)] = linha

        for port in inf:
            if 'PortaServerRPDV' in port:
                linha = list(inf[inf.index(port)].partition('='))
                linha[2] = values['cod_tcp'] + '\n'
                linha = ''.join(linha)
                inf[inf.index(port)] = linha

        system.close()

    with open('sistema.ini', 'w', encoding='ISO-8859-1') as system:
        system.writelines(inf)

    os.chdir('/home/rpdv/')
    with open('iniciarsudo.sh', 'r', encoding='ISO-8859-1') as inc:
        linhas = inc.readlines()
        linha = list(linhas[6].partition('1'))

        if not values['PassIncFile'] in linhas[6]:
            linha[1] = values['PassIncFile']

        linha = ''.join(linha)
        linhas[6] = linha
        inc.close()

    with open('iniciarsudo.sh', 'w', encoding='ISO-8859-1') as inc:
        inc.writelines(linhas)
        inc.close()

    if objeto != 'not' and objeto != None:
        comunicar_serverun.un_hide()

    return janela_popup('CONFIRMAÇÃO:', f'Configuração realizada com sucesso!!\nDeseja iniciar o frente de caixa?')

def Instalation(usuario):
    conexao = os.system('ping -c 3 www.google.com.br')

    os.chdir('/home/' + str(usuario))
    if os.path.exists('Frente_LUBUNTU.zip') == False:
        print('Realizando download dos arquivos necessários....... Aguarde ....... ')
        file_id = 'https://drive.google.com/u/0/uc?id=1BlN-C23F31daFtXV7oIUW-eye1Sm0oB4&export=download'
        destination = '/home/' + str(usuario) + '/Frente_LUBUNTU.zip'
        download_file_from_google_drive(file_id, destination)
        print(f'Arquivos baixados com sucesso em {os.getcwd()}')
    else:
        print('Arquivos baixados...')
        print('Descompactando arquivos para instalação.....')

    if os.path.exists('Frente_LUBUNTU') == False:
        if os.path.exists('Frente_LUBUNTU.zip') == True:
            z = zipfile.ZipFile('Frente_LUBUNTU.zip', 'r')
            z.extractall()
            z.close()
            sleep(3)
            os.system('chmod 777 *')
            print('Arquivos descompactados....')
    else:
        print(f'Arquivos já descompactados em {os.getcwd()}.....')

    os.chdir('/home/rpdv/Frente_LUBUNTU')
    os.system('chmod +x instalar.sh')
    print('Executando instalar.sh no bash.....Aguarde')
    os.system('echo "S" | ./instalar.sh > log_bash.txt')
    leitura('log_bash.txt', caminho=os.getcwd())
    sleep(2)
    print('Executando procedimento de links simbólicos....')
    os.chdir('/home/rpdv/frente')
    os.system('chmod 777 *')
    os.system('./atualiza.sh >> log_atualiza.txt')
    leitura('log_atualiza.txt', caminho=os.getcwd())
    
    return None

def Instalation_progressbar(usuario):
    lista_progress = []

    os.chdir('/home/' + str(usuario))

    if os.path.exists('Frente_LUBUNTU.zip') == False:
        file_id = 'https://drive.google.com/u/0/uc?id=1BlN-C23F31daFtXV7oIUW-eye1Sm0oB4&export=download'
        destination = '/home/' + str(usuario) + '/Frente_LUBUNTU.zip'
        download_file_from_google_drive(file_id, destination)

        for i in range(20):
            lista_progress.append(i)
            ProgressBar(i)

    else:
        for i in range(20):
            lista_progress.append(i)
            ProgressBar(i)

    if os.path.exists('Frente_LUBUNTU') == False:
        z = zipfile.ZipFile('Frente_LUBUNTU.zip', 'r')
        z.extractall()
        z.close()
        sleep(3)
        os.system('chmod 777 *')

        for i in range(len(lista_progress), 51):
            lista_progress.append(i)
            ProgressBar(i)

    else:
        for i in range(len(lista_progress), 51):
            lista_progress.append(i)
            ProgressBar(i)

    os.chdir('/home/rpdv/Frente_LUBUNTU')
    os.system('chmod +x instalar.sh')

    for i in range(len(lista_progress), 76):
        lista_progress.append(i)
        ProgressBar(i)

    if os.path.exists('instalar.sh') == True:
        os.system('echo "S" | ./instalar.sh > /dev/null 2>&1')
        os.chdir('/home/rpdv/frente')
        os.system('chmod 777 *')
    else:
        return sg.popup('ERRO:', 'Arquivo de instalação não encontrado.')

    for i in range(len(lista_progress), 91):
        lista_progress.append(i)
        ProgressBar(i)

    os.system('./atualiza.sh > /dev/null 2>&1')

    for i in range(len(lista_progress), 101):
        lista_progress.append(i)
        ProgressBar(i)

    return 0

def ProgressBar(current_value_progress):
        sleep(0.07)
        sg.one_line_progress_meter('Progresso:', current_value=current_value_progress, max_value=100, orientation='h', bar_color=('red', 'black'), button_color=('white', 'black'), size=(40, 30), keep_on_top=True, disable_minimize=False)

def leitura(arquivo, caminho):
    os.chdir(caminho)

    with open(arquivo, 'r', encoding='ISO-8859-1') as file:
        linhas = file.readlines()

        for i in linhas:
            sleep(0.03)
            print(i.strip())

def decrypt():

    user = list(os.popen('users').read())

    for i in user:
        if '\n' in i:
            user.remove(user[user.index(i)])
            user = ''.join(user)

    word = ['CAIXA', 'caixa','123456', 'rpdv', 'suporte', 'suporte0303*', 'wrpdv', '2511', 'rickli 01 @']

    with open('/etc/shadow', 'r', encoding='ISO-8859-1') as passwd:
        linhas = passwd.readlines()

        for i in linhas:
            if user in i:
                salt = i[5:17]
                hash = i[17:103]

        for h in word:
            if crypt.crypt(h, salt) == (salt + hash):
                senha = h
                return senha, user

# Função que verifica a existência do arquivo dentro do diretorio e se este arquivo possui uma unidade válida para retornar para o formulário, caso não exista retorna mensagem de informações ao input
def _fileOpenInfomationUN(objeto, element='', usuario=''):

    if element[0] != None:
        objeto['PassIncFile'].update(value=element[0])
    else:
        objeto['PassIncFile'].update(value=element[0])

    if os.path.exists('/home/rpdv/frente/sistema.ini'):

        os.chdir('/home/rpdv/frente')

        with open('sistema.ini', 'r', encoding='ISO-8859-1') as file:
            file_sys = file.readlines()
            linha = file_sys[2].partition('=')

            # Verifica se o arquivo possui unidade válida configurada e retorna para a função principal
            if linha[2] != '000\n' and linha[2] != '00\n' and linha[2] != '0\n' and linha != '':
                linha = linha[2]
                objeto['unidade'].update(value=linha.strip())

            # Verifica se o arquivo possui porta ServerUn - TCP configurada
            if file_sys[9] != '':
                porta = file_sys[9].partition('=')
                porta = porta[2]
                objeto['cod_tcp'].update(value=porta.strip())
            else:
                pass
    else:
        return objeto['unidade'].update(value='Arquivo sistema.ini não encontrado.'), sg.popup('Arquivo sistema.ini não encontrado, por favor verifique a existência dele em /home/rpdv/frente.',
            title='ERRO:', icon='rpinfo.png')

def _ListsOutPutInputs():
    lista = []
    indices = []

    for elemento in range(0, 10):
        lista.append(str(elemento))

    resultado_permutacao = list(product(lista, repeat=3))

    for tuple in resultado_permutacao:
        indices.append(resultado_permutacao.index(tuple))

        for indice in indices:
            resultado_permutacao[indice] = ''.join(resultado_permutacao[indice])
            indices = []

    if '000' and '999' in resultado_permutacao:
        resultado_permutacao.remove('000')
        resultado_permutacao.remove('999')

        return resultado_permutacao

def _ExecutarEventos_window2_Inputs(value, objeto, window_error=None):

    valores = dict()
    verification = _ListsOutPutInputs()

    if value['estacao'] == '000' or value['estacao'] == '999' or value['estacao'] == '':
        return objeto['estacao'].update(value=verification[0])
    else:
        if value['estacao'] != '0' and value['estacao'] != '00' and value['estacao'] != '000' and value['estacao'] != '999':
            if value['estacao'] in verification:
                valores['estacao'] = value['estacao']
            elif value['estacao'] == '':
                valores['estacao'] = '001'

    if value['unidade'] == '000' or value['unidade'] == '999':
        return objeto['unidade'].update(value='001')
    else:
        if value['unidade'] != '0' and value['unidade'] != '00' and value['unidade'] != '000' and value['unidade'] != '999' and value['unidade'] != '':
            if value['unidade'] in verification:
                valores['unidade'] = value['unidade']
            else:
                valores['unidade'] = '001'

    if value['IP_ServerUn'] != '127.0.0.1' and value['IP_ServerUn'] != '':
        valores['IP_ServerUn'] = value['IP_ServerUn']
    else:
        valores['IP_ServerUn'] = '192.168.0.1'

    if len(value['cod_tcp']) <= 6:
        valores['cod_tcp'] = value['cod_tcp']

    if value['PassIncFile'] != '0' and value['PassIncFile'] != '00' and value['PassIncFile'] != '000':
        valores['PassIncFile'] = value['PassIncFile']

    return valores


# Verifica evento disparado no momento do click em algum input do formulário
def _on_click_event_input(evento):
    if evento == 'estacao':
        var = 0
        return var

    elif evento == 'unidade':
        var = 1
        return var

    elif evento == 'IP_ServerUn':
        var = 2
        return var

    elif evento == 'cod_tcp':
        var = 3
        return var

    elif evento == 'PassIncFile':
        var = 4
        return var


# Valida os eventos disparados enquanto pressiona o botão continuar e enter - muda o foco do objeto conforme pressionamentos
def _ValidationKeyboardEvents(objeto, controlSetFocus):
    if controlSetFocus == 'SetEstac':
        objeto['estacao'].SetFocus(force=True)

    elif controlSetFocus == 1:
        _ExecutarEventos_window2_Inputs(value, janela2_exec)
        objeto['unidade'].SetFocus(force=True)

    elif controlSetFocus == 2:
        _ExecutarEventos_window2_Inputs(value, janela2_exec)
        objeto['IP_ServerUn'].SetFocus(force=True)

    elif controlSetFocus == 3:
        objeto['cod_tcp'].SetFocus(force=True)
        _ExecutarEventos_window2_Inputs(value, janela2_exec)

    elif controlSetFocus == 4:
        objeto['PassIncFile'].SetFocus(force=True)
        _ExecutarEventos_window2_Inputs(value, janela2_exec)

    elif controlSetFocus == 0:
        _ExecutarEventos_window2_Inputs(value, janela2_exec)
        objeto['estacao'].SetFocus(force=True)


# Define o layout da janela principal
def janela1():
    sg.theme('DarkBrown4')

    layout = [
        [sg.Text('---------------------------------------------------------------------------------------------------------')],
        [sg.Text('OLÁ, SEJA BEM VINDO AO INSTALADOR DO FRENTE DE CAIXA!', background_color='white', text_color='black')],
        [sg.Text('---------------------------------------------------------------------------------------------------------')],
        [sg.Text('Instalar o Frente?')],
        (sg.Checkbox('Sim..', default=True, enable_events=True, key='Instalar'),
         sg.Checkbox('Não..', enable_events=True, key='NaoInstalar')),
        [sg.Text('Configurar o sistema.ini e demais parâmetros após instalação?')],
        [sg.Checkbox('Sim..', default=False, enable_events=True, key='Configurar'),
         sg.Checkbox('Não..', default=True, enable_events=True, key='NaoConfigurar')],
        [sg.Text('Iniciar o frente após instalação?')],
        [sg.Checkbox('Sim..', default=True, enable_events=True, key='Iniciar_Frente'),
         sg.Checkbox('Não..', default=False, enable_events=True, key='Nao_Iniciar_Frente')],
        [sg.Text('Tentar encontrar IP ServerUn automaticamente?')],
        [sg.Checkbox('Sim..', default=False, enable_events=True, key='Encontra_Ip'),
         sg.Checkbox('Não..', default=True, enable_events=True, key='Nao_Encontra_Ip')],
        #[sg.Text('Configurar inicialização Frente?')],
        #[sg.Checkbox('Sim..', default=False, enable_events=True, key='Configurar_Senha'),
         #sg.Checkbox('Não..', default=True, enable_events=True, key='Nao_Configurar_Senha')],
        [sg.Text('Exibir tela de LOG?')],
         [sg.Checkbox('Sim..', default=False, enable_events=True, key='Exibir_Sim'), sg.Checkbox('Não..', enable_events=True, default=True, key='Exibir_Nao')],
        #[sg.Text('Descriptografia de senha root: ')],
        #[sg.Checkbox('Sim..', default=True, enable_events=True, key='Crypt'),
         #sg.Checkbox('Não..', enable_events=True, default=False, key='NoCrypt')],
        [sg.Button('Continuar', key='Next', enable_events=True, tooltip='Envia informações e retorna uma nova janela de inserção de dados.'),
         sg.Button('Sair', key='Close', enable_events=True, tooltip='Não faz nada ; D')],
        [sg.Text('                                                                             Version: 1.0.1')]
    ]

    return sg.Window('Inicialização', return_keyboard_events=True, size=(455, 390), layout=layout, icon='rpinfo.png', finalize=True)


# Define o layout da janela secundária
def janela2():
    sg.theme('DarkBrown4')

    layout2 = [
        [sg.Text('Digite o número da estação a ser configurada (sistema.ini): ', tooltip='Se a estação já estiver configurada em sistema.ini input recebe valor'), sg.Input(enable_events=True, key='estacao')],
        [sg.Text('Digite o código da unidade desejada: '), sg.Input(enable_events=True, key='unidade')],
        [sg.Text('Digite o IP do Servidor do PDV: ', tooltip='Passa para o arquivo sistema.ini o IP digitado'), sg.Input(enable_events=True, key='IP_ServerUn')],
        [sg.Text('Digite porta TCP - ServerUn: '), sg.Input(enable_events=True, key='cod_tcp')],
        [sg.Text('Digite o pass root para iniciarsudo.sh: '), sg.Input(enable_events=True, key='PassIncFile', disabled=False)],
        [sg.Button('Continuar', key='continue', enable_events=True), sg.Button('Voltar', key='back', auto_size_button=True)]
    ]

    return sg.Window('Parâmetros de configuração: ', return_keyboard_events=True, size=(880, 190), icon='rpinfo.png',
                     layout=layout2, finalize=True)


def janela3():
    sg.theme('DarkBrown4')

    layout3 = [
        [sg.Text('Monitoramento de processo de execução',
                 tooltip='Mostra os processos executados durante instalação.')],
        [sg.Output(size=(780, 190))]
    ]

    return sg.Window('Monitoramento', return_keyboard_events=True, layout=layout3, icon='rpinfo.png', finalize=True, size=(900, 500))


def janela_popup(titulo_janela='', mensagem='', size=(300, 100)):
    sg.theme('DarkBrown4')
    layout4 = [
        [sg.Text(mensagem)],
        [sg.Button('Sim', key='Sim_msg'), sg.Button('Não', key='Nao_msg')]
    ]

    layout5 = [
        [sg.Text(mensagem)],
        [sg.Button('OK', key='btn_ok')]
    ]

    if titulo_janela == 'CONFIRMAÇÃO:': #or 'ATENÇÃO:' or 'ADVERTÊNCIA:':
        return sg.Window(titulo_janela, return_keyboard_events=True, icon='rpinfo.png', layout=layout4, finalize=True, size=size)

    elif titulo_janela == 'ATENÇÃO:':
        return sg.Window(titulo_janela, return_keyboard_events=True, icon='rpinfo.png', layout=layout4, finalize=True, size=size)

    elif titulo_janela == 'ADVERTÊNCIA:':
        return sg.Window(titulo_janela, return_keyboard_events=True, icon='rpinfo.png', layout=layout4, finalize=True, size=size)

    elif titulo_janela == 'ERRO:': #or 'ERRO CONEXÃO:' or 'EXIBIÇÃO:':
        return sg.Window(titulo_janela, return_keyboard_events=True, icon='rpinfo.png', layout=layout5, finalize=True, size=size)

    elif titulo_janela == 'ERRO CONEXÃO:':
        return sg.Window(titulo_janela, return_keyboard_events=True, icon='rpinfo.png', layout=layout5, finalize=True, size=size)

    elif titulo_janela == 'EXIBIÇÃO:':
        return sg.Window(titulo_janela, return_keyboard_events=True, icon='rpinfo.png', layout=layout5, finalize=True, size=size)


def Trata_Dados_Primarios(bytes):
    VALORES = []

    data = list(bytes)

    for i in data:
        if '|' in i:
            data[data.index(i)] = '\n'
    try:
        with open('bytes.txt', 'w', encoding='ISO-8859-1') as file:
            file.writelines(data)
            file.close()

        with open('bytes.txt', 'r', encoding='ISO-8859-1') as file_r:
            linhas = file_r.readlines()
            USER_FTP = linhas[0]
            USER_FTP = USER_FTP[13:24]
            PASS_FTP = linhas[1]
            PORTA_FTP = linhas[2]
            PORTA_INI = linhas[3]
            UNIDADE = linhas[4]

        if '\n' in USER_FTP:
            USER_FTP = list(USER_FTP)
            USER_FTP.remove('\n')

        if '\n' in PASS_FTP:
            PASS_FTP = list(PASS_FTP)
            PASS_FTP.remove('\n')
            PASS_FTP = ''.join(PASS_FTP)

        if '\n' in PORTA_FTP:
            PORTA_FTP = list(PORTA_FTP)
            PORTA_FTP.remove('\n')
            PORTA_FTP = ''.join(PORTA_FTP)

        if '\n' in PORTA_INI:
            PORTA_INI = list(PORTA_INI)
            PORTA_INI.remove('\n')
            PORTA_INI = ''.join(PORTA_INI)

        if '\n' in UNIDADE:
            UNIDADE = list(UNIDADE)
            UNIDADE.remove('\n')
            UNIDADE = ''.join(UNIDADE)

        VALORES.append(USER_FTP)
        VALORES.append(PASS_FTP)
        VALORES.append(PORTA_FTP)
        VALORES.append(PORTA_INI)
        VALORES.append(UNIDADE)

        return VALORES
    except:
        return None


def Tratamento_Dados_Secundarios(dados, arquivo):
    lista = list(dados)

    with open(arquivo, 'w', encoding='ISO-8859-1') as file:
        file.writelines(lista)

    with open(arquivo, 'r', encoding='ISO-8859-1') as file_id:
        linhas = file_id.readlines()

        for i in linhas:
            if 'PORT' in i:
                PORTA_FTP = list(i)
                for i2 in PORTA_FTP:
                    if ',' in i2:
                        PORTA_FTP[PORTA_FTP.index(i2)] = '\n'
                PORTA_FTP = ''.join(PORTA_FTP)
                file_id.close()

    with open(arquivo, 'w', encoding='ISO-8859-1') as novo:
        novo.writelines(PORTA_FTP)
        novo.close()

    with open(arquivo, 'r', encoding='ISO-8859-1') as file:
        linhas = file.readlines()
        id1 = linhas[4]
        id2 = linhas[5]

    return id1, id2


def CalculaPorta(id1, id2):
    id1 = list(id1)
    id2 = list(id2)

    for i in id1:
        if '\n' in i:
            id1.remove(id1[id1.index(i)])
            id1 = ''.join(id1)

    for o in id2:
        if '\n' in o:
            id2.remove(id2[id2.index(o)])
            id2 = ''.join(id2)

    P = (int(id1)*255) + int(id1) + int(id2)

    return P


def Trata_arquivo_configuracao(arquivo):
    if arquivo == 'config.cfg':
        with open('config.cfg', 'r', encoding='ISO-8859-1') as file:
            linhas = file.readlines()
            for i in linhas:

                if i == '\n':
                    linhas.remove(linhas[linhas.index(i)])

            with open('config.cfg','w', encoding='ISO-8859-1') as config:
                config.writelines(linhas)
                return 0

def Tratamento_Dados_Ftp(bytes):
    for i in bytes:
        if i == ' ':
            bytes[bytes.index(i)] = '\n'
            ''.join(bytes)

    with open('dados_ftp.txt', 'w', encoding='ISO-8859-1') as file:
        file.writelines(bytes)
        file.close()

    with open('dados_ftp.txt', 'r', encoding='ISO-8859-1') as read:
        linhas = read.readlines()

        for i in linhas:
            if 'CONFIG' in i:
                arquivo_download = linhas[linhas.index(i)]
                read.close()
                tratar = list(arquivo_download)
                for i in tratar:
                    if i == '\n':
                        tratar.remove(tratar[arquivo_download.index(i)])
                return ''.join(tratar)

def ComunicaoServer(ip, porta, estacao, unidade, unidade_server=''):
    # Socket segunda conexão FTP
    ftp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Socket 2 ftp 2 conexão
    ftp2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Socket que vai receber as informações primárias da aplicação
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(porta)))
        s.sendall(str.encode('\x02000000000600X' + estacao + '\x03\xfd\xc9\xea\r\n'))
        dados_primarios = s.recv(1024)

        recv_pr = Trata_Dados_Primarios(list(dados_primarios.decode('ISO-8859-1')))

        #Validação da unidade informada pelo usuário da unidade corresponde no servidor informado.
        if recv_pr[4] == unidade:
            Conx_pr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Conx_pr.connect((ip, int(recv_pr[2])))
            rc = Conx_pr.recv(1024)

            #log = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #log.connect((ip, 11011))
            Validar = 0

            config = []

            while True:
                s.sendall(b'\x02000000000604NOOP\x030\xfd\xc9\xea\r\n')

                if b'Bem vindo ' in rc:
                    Conx_pr.sendall(str.encode('USER ' + recv_pr[0] + '\r\n'))
                    rc = Conx_pr.recv(1024)

                elif b'Especifique a senha.' in rc:
                    Conx_pr.sendall(str.encode('PASS ' + recv_pr[1] + '\r\n'))
                    rc = Conx_pr.recv(1024)

                elif b'Login efetuado com sucesso.' in rc:
                    Conx_pr.sendall(b'PASV\r\n')
                    rc = Conx_pr.recv(1024)

                elif b'PORT' in rc:
                    dados_porta_ftp = Tratamento_Dados_Secundarios(rc.decode('ISO-8859-1'), 'bytes2.txt')
                    porta_ftp = CalculaPorta(dados_porta_ftp[0], dados_porta_ftp[1])

                    if Validar == 0:
                        ftp.connect((ip, int(porta_ftp)))
                        Conx_pr.sendall(str.encode('LIST /' + estacao + '\r\n'))
                        sleep(1)
                        Validar = 1
                        dados_ftp1 = ftp.recv(8192)

                        if dados_ftp1 != b'':
                            arquivo = Tratamento_Dados_Ftp(list(dados_ftp1.decode('ISO-8859-1')))

                            if 'CONFIG' in arquivo:
                                ftp.close()
                                Conx_pr.sendall(b'PASV\r\n')
                                Conx_pr.sendall(b'CWD /\r\n')
                                Conx_pr.sendall(str.encode('CWD /' + estacao +'\r\n'))

                                if Validar == 1:
                                    ftp2.connect((ip, int(porta_ftp)))
                                    Conx_pr.send(str.encode('RETR ' + arquivo + '\r\n'))
                                    sleep(4)
                                    Validar = 2

                                    while True:
                                        dados_ftp = ftp2.recv(8192)
                                        config.append(dados_ftp.decode('ISO-8859-1'))

                                        if not dados_ftp:
                                                with open('/home/rpdv/frente/config.cfg', 'w', encoding='ISO-8859-1') as confi:
                                                    confi.writelines(config)
                                                    Trata_arquivo_configuracao('/home/rpdv/config.cfg')
                                                    Conx_pr.sendall(str.encode('DELE ' + arquivo + '\r\n'))
                                                    Conx_pr.close()
                                                    return janela_popup('EXIBIÇÃO:', f'Arquivo {arquivo} recebido com sucesso de {ip}! :)', size=(600, 100)), 0
                                break
                        else:
                            return janela_popup('ERRO:', f'Nenhum arquivo de configuração encontrado em {ip}. :D', size=(500, 100)), 1
        else:
            return janela_popup('ERRO:', f'Unidade {unidade} não corresponde a unidade {unidade_server} do servidor IP: {ip}. Por favor, verifique os dados informados e tente novamente. :D', size=(800,100)), 1

    except ConnectionRefusedError:
        return janela_popup('ERRO CONEXÃO:', f'Não foi possível conectar-se ao host {ip}, verifique a execução do servidor e tente novamente. :D', size=(700,100)), 1

def encrypt():
    response = requests.get('https://drive.google.com/u/0/uc?id=1s7J7D8UPytOgzh1Go9TpbK6o3T2-FGgu&export=dolwnload', stream=True)

    if response.content == b'a\\xde%\\xc9T{\\x1e\\x9c\\xfb\\xddi\\xeeZ\\x18\\x9b\\xdb':
        return None
    if response.content == b'T\\x16x\\xeb\\x11\\xce\\xb6\\x0e\\x1e\\xc8\\x07\\x85\\xd3\\x19\\x8b\\x1d':
        return 0

def auto_start(usuario):
    os.chdir('/home/' + usuario.strip() + '/')
    conf_logof_full(usuario)

    try:
        os.system('cp -r ~/.config/lxsession/Lubuntu/autostart /home/' + usuario + '/Área\ de\ Trabalho/')

        with open('/home/' + usuario + '/Área de Trabalho/autostart', 'r', encoding='ISO-8859-1') as auto_play:
            l = auto_play.readlines()


            if './iniciarsudo.sh\n' in l:
                return 0
            else:
                l.append('cd /home/' + usuario +'/' + '\n')
                l.append('./iniciarsudo.sh' + '\n')

                with open('/home/' + usuario + '/Área de Trabalho/autostart', 'w', encoding='ISO-8859-1') as auto_play2:
                    auto_play2.writelines(l)
                    auto_play2.close()

                os.system('mv /home/' + usuario + '/Área\ de\ Trabalho/autostart ~/.config/lxsession/Lubuntu/')
                os.system('chmod 777 ~/.config/lxsession/Lubuntu/')

    except FileNotFoundError:
        os.system('cp -r ~/.lconfig/lxsession/Lubuntu/autostart /home/' + usuario + '/Desktop/')

        with open('/home/' + usuario + '/Desktop/autostart', 'r', encoding='ISO-8859-1') as auto_play:
            l = auto_play.readlines()

            if './iniciarsudo.sh\n' in l:
                return 0
            else:
                l.append('cd /home/' + usuario + '/' + '\n')
                l.append('./iniciarsudo.sh' + '\n')

                with open('/home/' + usuario + '/Desktop/autostart', 'w', encoding='ISO-8859-1') as auto_play2:
                    auto_play2.writelines(l)
                    auto_play2.close()

                os.system('mv /home/' + usuario + '/Desktop/autostart ~/.config/lxsession/Lubuntu/')
                os.system('chmod 777 ~/.config/lxsession/Lubuntu/')

def conf_logof_full(usuario):
    with open('/etc/lightdm/lightdm.conf', 'r', encoding='ISO-8859-1') as auto:

        arq = auto.readlines()

        for i in arq:
            if 'autologin-user=' in i:
                linha = arq[arq.index(i)]
                linha = list(linha.partition('='))
                if linha[2] == '\n':
                    linha[2] = usuario + '\n'
                    linha = ''.join(linha)
                    arq[arq.index(i)] = linha

    with open('/home/rpdv/lightdm.conf', 'w', encoding='ISO-8859-1') as file:
        file.writelines(arq)
        os.system('mv /home/rpdv/lightdm.conf /etc/lightdm/')
        os.chdir('/etc/lightdm/')
        os.system('chmod 777 * lightdm.conf')
        file.close()


def criar_ip(ip, mascara):
    contador = 0
    list(ip)
    format_ip = []
    lista_ips = []

    for i in ip:
        if i == '.':
            contador += 1
            format_ip.append('.')

        elif contador != 3:
            format_ip.append(i)

    for ip in range(mascara):
        lista_ips.append(''.join(format_ip) + str(ip))


def calc_sub_network(ip, mascara):
    ips = 0

    if mascara == '255.255.255.255':
        ips = 1

    elif mascara == '255.255.255.254':
        ips = 2

    elif mascara == '255.255.255.252':
        ips = 2

    elif mascara == '255.255.255.248':
        ips = 4

    elif mascara == '255.255.255.240':
        ips = 14

    elif mascara == '255.255.255.224':
        ips = 32

    elif mascara == '255.255.255.192':
        ips = 64

    elif mascara == '255.255.255.128':
        ips = 126

    elif mascara == '255.255.255.0':
        ips = 254

    criar_ip(ip, ips)


def captura_masc():
    caminho = '/home/' + os.popen('users').read().strip()

    # if os.path.exists(caminho + '/interface_rede#.txt') == True:
    #    os.system('rm -rf ' + caminho + '/interface_rede#.txt')

    inf_interface = os.popen('route -n').read()

    if os.path.exists(caminho + '/interface_rede#.txt') == False:
        with open(caminho + '/interface_rede#.txt', 'w', encoding='ISO-8859-1') as network:
            network.writelines(inf_interface)
            os.system('chmod 777 ' + caminho + '/interface_rede#.txt')

        with open(caminho + '/interface_rede#.txt', 'r', encoding='ISO-8859-1') as masc:
            l = masc.readlines()
            l = l[3]
            l = list(l)

            for i in l:
                if i == ' ':
                    l[l.index(i)] = '\n'

            with open(caminho + '/interface_rede#.txt', 'w', encoding='ISO-8859-1') as masc2:
                masc2.writelines(l)
                masc.close()

            with open(caminho + '/interface_rede#.txt', 'r', encoding='ISO-8859-1') as mascara:
                m = mascara.readlines()
                ip = list(m[0].strip())

                for i in m:
                    if '255' in i:
                        mascara_rede = i.strip()
                        calc_sub_network(ip, mascara_rede)

                #ip = list(m[0].strip())


#valida_inst = ValidaExec('https://drive.google.com/u/0/uc?id=1s7J7D8UPytOgzh1Go9TpbK6o3T2-FGgu&export=download')
valida_inst = encrypt()

janela1_exec = janela1()

janela2_exec = janela2()
janela2_exec.hide()

janela_atencao_Next = janela_popup('ATENÇÃO:', 'Pasta Frente já existe em /home/rpdv/. Reinstalar?', size=(400, 100))
janela_atencao_Next.hide()

comunicar_serverun = janela_popup('CONFIRMAÇÃO:','Deseja efetuar comunicação com o ServerUn para receber arquivo de configuração?? ', size=(600,100))
comunicar_serverun.hide()

janela_erro = janela_popup('ERRO CONEXÃO:','Uma conexão foi tentada, porém, não pôde ser estabelecida.\nPor favor verifique sua conexão e tente novamente.', size=(500,100))
janela_erro.hide()

msg = janela_popup('EXIBIÇÃO:', 'Já existe configuração para inicialização.\nConfiguração não efetuada.')
msg.hide()

#erro_valor = janela_popup('ERRO:', 'FATAL ERROR: Existe algum valor inválido informado\nPor favor repasse os valores e tente novamente.', size=(500,100))
#erro_valor.hide()

controlSetFocus = 0

contador = 0

#Variavel que informa se o CheckBox iniciar frente está habilitado
iniciar = 0

#Variavel de controle para CheckBox instalar frente
install = 0

#Variavel que controle erros ocasionados durante alguns processos de execuções
erro = 0

valor_check = 1

if valida_inst == None:
    while True:

        window, event, value = sg.read_all_windows()

        # try:
        if event == 'NaoInstalar':
            janela1_exec['Instalar'].update(value=False)
            janela1_exec['NaoInstalar'].update(value=True)

        if event == 'NaoInstalar' and value.get('Configurar'):
            janela1_exec['Configurar'].update(value=False)
            janela1_exec['NaoConfigurar'].update(value=True)

        elif event == 'Configurar' and value.get('NaoInstalar'):
            janela1_exec['Instalar'].update(value=True)
            janela1_exec['NaoConfigurar'].update(value=False)
            janela1_exec['NaoInstalar'].update(value=False)

        elif event == 'Instalar':
            janela1_exec['NaoInstalar'].update(value=False)
            janela1_exec['Instalar'].update(value=True)

        elif event == 'Configurar':
            janela1_exec['NaoConfigurar'].update(value=False)
            janela1_exec['Configurar'].update(value=True)

        elif event == 'NaoConfigurar':
            janela1_exec['NaoConfigurar'].update(value=True)
            janela1_exec['Configurar'].update(value=False)

        elif event == 'Configurar_Senha':
            janela1_exec['Nao_Configurar_Senha'].update(value=False)
            janela1_exec['Configurar_Senha'].update(value=True)

        elif event == 'Nao_Configurar_Senha':
            janela1_exec['Nao_Configurar_Senha'].update(value=True)
            janela1_exec['Configurar_Senha'].update(value=False)

        elif event == 'Iniciar_Frente':
            janela1_exec['Nao_Iniciar_Frente'].update(value=False)
            janela1_exec['Iniciar_Frente'].update(value=True)

        elif event == 'Nao_Iniciar_Frente':
            janela1_exec['Iniciar_Frente'].update(value=False)
            janela1_exec['Nao_Iniciar_Frente'].update(value=True)

        elif event == 'Crypt':
            janela1_exec['NoCrypt'].update(value=False)
            janela1_exec['Crypt'].update(value=True)

        elif event == 'NoCrypt':
            janela1_exec['Crypt'].update(value=False)
            janela1_exec['NoCrypt'].update(value=True)

        elif window == janela1_exec and event == 'Escape:27':
            break

        elif window == janela1_exec and (event == 'Right:114'):
            sg.Button.set_focus(janela1_exec['Close'])

        elif window == janela1_exec and (event == 'Left:113'):
            sg.Button.set_focus(janela1_exec['Next'])

        elif window == janela1_exec and event == 'Exibir_Sim':
            janela1_exec['Exibir_Nao'].update(value=False)
            janela1_exec['Exibir_Sim'].update(value=True)

        elif window == janela1_exec and event == 'Exibir_Nao':
            janela1_exec['Exibir_Nao'].update(value=True)
            janela1_exec['Exibir_Sim'].update(value=False)

        elif window == janela1_exec and (event == 'Next' or event == '\r'):
            try:
                encrypt = decrypt()

                #_---------------------------VERIFICAR ARQUITETURA DE PROCEDIMENTO------------------------------------_
                if os.path.exists('/home/rpdv/frente') == True:
                    if value.get('Configurar') == True:
                        valor_check = 0 # Sim
                    else:
                        valor_check = 1 # Nao

                    if value.get('Exibir_Nao') == True:
                        valor_check_ex = 0 #Sim
                    else:
                        valor_check_ex = 1 #Nao

                    if value.get('Instalar') == False:
                        install = 2
                    else:
                        install = 0

                    if value.get('Iniciar_Frente') == True:
                        iniciar = 1

                    if install != 2:
                        janela_atencao_Next.un_hide()

                # _---------------------------VERIFICAR ARQUITETURA DE PROCEDIMENTO------------------------------------_

                else:

                    if value.get('Instalar') == True:
                        install = 2
                        janela1_exec.hide()

                        if value.get('Exibir_Sim') == True:
                            janela3_exec = janela3()
                            janela3_exec.un_hide()
                            validar = Instalation(encrypt[1])
                            janela3_exec.close()
                        else:
                            validar = Instalation_progressbar(encrypt[1])
                            #validar = MultiProcess(encrypt[1])

                    if value.get('Configurar') == True:
                        if os.path.exists('/home/rpdv/frente'):
                            janela2_exec.un_hide()
                            janela2_exec['estacao'].SetFocus(force=True)

                            if encrypt[0] == None:
                                janela2_exec['PassIncFile'].update(disabled=True)

                            _fileOpenInfomationUN(janela2_exec, element=encrypt, usuario=encrypt[1])
                        else:
                            janela1_exec.un_hide()
                    else:
                        janela1_exec.un_hide()
            except:
                pass

        elif window == janela1_exec and (event == 'Close' or event == sg.WIN_CLOSED):
            break

        elif window == janela2_exec and event == 'back':
            janela2_exec.hide()
            janela1_exec.un_hide()

        elif window == janela2_exec and event == 'Escape:27':
            janela2_exec.hide()
            janela1_exec.un_hide()

        elif window == janela2_exec and event == sg.WIN_CLOSED:
            janela2_exec.hide()
            janela1_exec.un_hide()

        elif window == janela2_exec and event == '\r':

            if controlSetFocus == 0:
                controlSetFocus = 1  # Setar na função foco no campo unidade
                _ValidationKeyboardEvents(janela2_exec, controlSetFocus=controlSetFocus)

            elif controlSetFocus == 1:
                controlSetFocus = 2  # Setar na função foco campo IP_ServerUn ao pressionar novamente enter
                _ValidationKeyboardEvents(janela2_exec, controlSetFocus=controlSetFocus)

            elif controlSetFocus == 2:
                controlSetFocus = 3  # Seta foco no campo cod_tcp ao pressionar novamente enter
                _ValidationKeyboardEvents(janela2_exec, controlSetFocus=controlSetFocus)

            elif controlSetFocus == 3:
                if valor_check == 1:
                    controlSetFocus = 4  # Se o CheckBox do campo PassIncFile estiver ativo como nao, seta foco no campo estacao
                    _ValidationKeyboardEvents(janela2_exec, controlSetFocus)
                    controlSetFocus = 0
                else:
                    controlSetFocus = 4  # Se o campo PassIncFile estiver ativo seta foco no campo PassIncFile
                    _ValidationKeyboardEvents(janela2_exec, controlSetFocus=controlSetFocus)
                    controlSetFocus = 'SetEstac'

            elif controlSetFocus == 'SetEstac':
                janela2_exec['estacao'].SetFocus(force=True)
                controlSetFocus = 0

        elif window == janela_atencao_Next and (event == 'Nao_msg'):
            #if iniciar == 1:
            if valor_check == 0:
                janela1_exec.hide()
                janela2_exec.un_hide()
                janela_atencao_Next.hide()
                janela2_exec['estacao'].SetFocus(force=True)
                _fileOpenInfomationUN(janela2_exec, element=encrypt, usuario=encrypt[1])
            else:
                janela1_exec.un_hide()
                window.hide()

        # Procedimento após validação existência pasta frente ao pressionar continuar em janela1 validando os eventos executados
        elif window == janela_atencao_Next and event == 'Sim_msg':
            if valor_check_ex == 0:
                janela1_exec.hide()
                janela_atencao_Next.hide()
                validar = Instalation_progressbar(encrypt[1])
                install = 1
                #validar = MultiProcess(encrypt[1])
            else:
                janela_atencao_Next.hide()
                os.system('rm -rf /home/rpdv/frente')
                janela1_exec.hide()
                janela3_exec = janela3()
                janela3_exec.un_hide()
                validar = Instalation(encrypt[1])

                if validar[0] == 0:
                    janela3_exec.close()

            if valor_check == 0:
                if os.path.exists('/home/rpdv/frente'):
                    janela2_exec.un_hide()
                    janela2_exec['estacao'].SetFocus(force=True)

                    if encrypt[0] == None:
                        janela2_exec['PassIncFile'].update(disabled=True)

                    _fileOpenInfomationUN(janela2_exec, element=encrypt, usuario=encrypt[1])
                else:
                    janela1_exec.un_hide()
            else:
                janela1_exec.un_hide()

        elif event == 'Right:114' and window == janela_atencao_Next:
            sg.Button.set_focus(janela_atencao_Next['Nao_msg'])

        elif event == 'Left:113' and window == janela_atencao_Next:
            sg.Button.set_focus(janela_atencao_Next['Sim_msg'])

        evento = _on_click_event_input(event)

        # Procedimento para verificar em qual input o usuário clicou
        if evento == 0 or evento == 1 or evento == 2 or evento == 3 or evento == 4:
            if evento == 0:
                controlSetFocus = 0

            elif evento == 1:
                controlSetFocus = 1

            elif evento == 2:
                controlSetFocus = 2

            elif evento == 3:
                controlSetFocus = 3

            #Se usuário clicou no input habilitado de root linux
            elif evento == 4:
                controlSetFocus = 'SetEstac'

        elif window == janela2_exec and event == 'continue':

            # Função para validar os valores recebidos pelo usuário
            infrm = _ExecutarEventos_window2_Inputs(value, janela2_exec)

            #Executa procedimento de alteração de parametros passados pelo usuario
            exec = Executation(infrm, infrm['IP_ServerUn'])
            exec.hide()

        elif erro == 1 and window == janela_erro:
            window.hide()
            janela1_exec.un_hide()

        elif window and event == 'Sim_msg' or event == 'btn_ok':
            comunica = 0

            try:
                if event == 'Sim_msg' and window == comunicar_serverun:
                    comunicar_serverun.close()

                    #Realiza conexão com ServerUn
                    con = ComunicaoServer(infrm['IP_ServerUn'], infrm['cod_tcp'], infrm['estacao'], infrm['unidade'])

                if event == 'btn_ok':
                    # Valida se houveram erros na comunicação com ServerUn
                    if con[1] == 1:
                        window.hide()
                        comunicar_serverun = janela_popup('CONFIRMAÇÃO:', 'Deseja efetuar comunicação com o ServerUn para receber arquivo de configuração?? ', size=(600, 100))
                        comunicar_serverun.hide()
                        janela2_exec.un_hide()
                    else:
                        window.hide()

                        if valor_check == 1 and iniciar != 1:
                            iniciar_frente = janela_popup('CONFIRMAÇÃO:', 'Configuração realizada com sucesso. \nDeseja iniciar o frente de caixa?')

                        if iniciar != 1:
                            exec.un_hide()
                        else:
                            iniciar_frente = janela_popup('CONFIRMAÇÃO:', 'Configuração realizada com sucesso. \nDeseja iniciar o frente?')

                if window == iniciar_frente and event == 'Sim_msg':
                    auto_ = auto_start('rpdv')

                    if auto_ == 0:
                        exec.hide()
                        msg.un_hide()
                    else:
                        # os.system('reboot')
                        print('Reiniciando a máquina1111111')

                elif window == iniciar_frente and event == 'Nao_msg':
                    window.hide()
                    janela2_exec.un_hide()

            except NameError:
                if window == exec and event == 'Sim_msg':
                    auto_ = auto_start('rpdv')

                    if auto_ == 0:
                        exec.hide()
                        msg.un_hide()

                elif window == msg and event == 'btn_ok':
                    window.close()
                    os.system('reboot')

        elif window == comunicar_serverun and event == 'Nao_msg':
            comunicar_serverun.close()

            if iniciar == 1:
                exec.un_hide()
            else:
                janela_popup('EXIBIÇÃO:', 'Configuração realizada com sucesso.')

        try:
            if window == comunicar_serverun and event == 'Right:114':
                sg.Button.set_focus(window['Nao_msg'])

            elif window == comunicar_serverun and event == 'Left:113':
                sg.Button.set_focus(window['Sim_msg'])

            elif window == exec and event == 'Right:114':
                sg.Button.set_focus(window['Nao_msg'])

            elif window == exec and event == 'Left:113':
                sg.Button.set_focus(window['Sim_msg'])

            elif window == exec and event == 'Nao_msg':
                exec.close()
                break
        except:
            pass
else:
    janela_popup('ERRO CONEXÃO:', 'Sistema não pode ser iniciado devido a um problema de conexão.\nPor favor verifique sua conexão com a internet e tente novamente.', size=(320,100))