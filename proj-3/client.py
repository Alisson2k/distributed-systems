import grpc
import util

COMMANDS = ['create', 'read', 'update', 'delete']

class Client(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def start(self):
        try:
            with grpc.insecure_channel(f'{self.ip}:{self.port}') as channel:
                self.channel = channel
                print(f'[+] Conectado com sucesso em [{self.ip}:{self.port}]!')
                self._run()
        except:
            print("[-] Erro durante a conexão com o servidor")

    def _run(self):
        while True:
            try:
                text = input("[+] Digite o comando, digite [help] se tiver alguma duvida: ")

                if text == 'help':
                    print("""
***************************************************************
* create {Receita}:{Descrição} - Adiciona uma receita         *
* read {Receita} - Retorna a receita                          *
* update {Receita}:{Descrição} - Atualiza a descrição receita *    
* delete {Receita} - Remove a receita                         *
*                                                             *
* Caso queira desconectar o cliente digite: x                 *
***************************************************************
                          """)
                elif text.lower() == 'x':
                    print('[*] Desconectado!')
                    break
                else:
                    try:
                        self._resolve_command(text)
                    except:
                        print("[*] Comando invalido! Tente novamente...")

            except KeyboardInterrupt:
                print("\n[-] Forçando a parada via terminal")
                break

    def _resolve_command(self, command):
        comando = command.split(' ')[0]
        if comando not in COMMANDS:
            raise Exception

        resto = command[len(comando)+1:].split(":")
        if len(resto) == 1 and comando in ['read', 'delete']:
            self.treat_command(comando, resto[0], None)
        elif len(resto) == 2 and comando in ['create', 'update']:
            self.treat_command(comando, resto[0], resto[1])
        else:
            raise Exception

    def treat_command(self, comando, chave, valor):
        response = util.treat_command(self.channel, comando, chave, valor)
        if response is not None:
            print(f'[+] {response.resposta}')

class Main(object):

    def start(self):
        while True:
            print("[+] Iniciando cliente")
            ip = input("[+] Digite o IP do servidor: ")
            port = input("[+] Digite a porta do servidor: ")

            client = Client(ip, port)
            client.start()

            choice = input("[+] Deseja encerrar a conexao? [S/N] ")
            if choice.lower() == 's':
                break

if __name__ == "__main__":
    Main().start()
