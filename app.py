import json
import os
import mido
import pygetwindow as gw
import platform

# Função para criar o arquivo config.json com um template inicial
def criar_arquivo_config():
    config_template = {
        "midi_in": "Nome do Dispositivo MIDI",  # Nome do dispositivo MIDI de entrada
        "60": { "title": "Janela Nota 60" },    # Mapeamento para a nota 60
        "61": { "title": "Janela Nota 61" },    # Mapeamento para a nota 61
        "100": { "title": "Spotify" }           # Mapeamento para a nota 100 (Spotify)
    }
    with open("config.json", "w") as f:
        json.dump(config_template, f, indent=4)
    print("Arquivo 'config.json' criado com o template básico.")

# Função para carregar o arquivo JSON de configuração
def carregar_config():
    config_path = "config.json"
    if not os.path.exists(config_path):
        print("Arquivo de configuração não encontrado! Criando arquivo...")
        criar_arquivo_config()
        return carregar_config()  # Recursivamente carregar após criar o arquivo
    
    with open(config_path, "r") as f:
        return json.load(f)

# Função para configurar o dispositivo MIDI
def configurar_midi(config):
    midi_in_name = config.get("midi_in", "")
    
    # Se o dispositivo configurado for "test", não tentamos abrir uma porta MIDI
    if midi_in_name == "test":
        print("Modo interativo: Aguardando a entrada manual de notas MIDI.")
        return None  # Retorna None para indicar que não há necessidade de abrir um dispositivo MIDI
    
    if not midi_in_name:
        print("Nenhum dispositivo MIDI de entrada configurado no arquivo JSON!")
        return None
    
    # Listar todos os dispositivos MIDI disponíveis
    available_ports = mido.get_input_names()
    if midi_in_name not in available_ports:
        print(f"Dispositivo MIDI '{midi_in_name}' não encontrado!")
        print("Dispositivos MIDI disponíveis:")
        for port in available_ports:
            print(f"- {port}")
        
        # Opcional: permitir que o usuário escolha um dispositivo válido
        midi_in_name = input("Digite o nome de um dispositivo MIDI válido: ")
        if midi_in_name not in available_ports:
            print("Nome de dispositivo inválido. Tentando criar um novo arquivo com o dispositivo selecionado...")
            config["midi_in"] = midi_in_name
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            print("Arquivo de configuração atualizado com o novo dispositivo MIDI.")
        else:
            print(f"Dispositivo MIDI '{midi_in_name}' encontrado.")
    
    # Abrir o dispositivo MIDI de entrada
    try:
        midi_in = mido.open_input(midi_in_name)
        print(f"Dispositivo MIDI '{midi_in_name}' aberto com sucesso.")
        return midi_in
    except OSError:
        print(f"Erro ao tentar abrir o dispositivo MIDI '{midi_in_name}'. Nenhuma porta MIDI disponível.")
        return None

# Função para trazer uma janela para o primeiro plano (Windows e Mac)
def trazer_janela_para_frente(titulo):
    try:
        if platform.system() == "Windows":
            # Usar win32gui no Windows
            import win32gui
            janela = win32gui.FindWindow(None, titulo)
            if janela:
                win32gui.ShowWindow(janela, 5)  # SW_RESTORE
                win32gui.SetForegroundWindow(janela)  # Trazer para o primeiro plano
            else:
                print(f"Janela com título '{titulo}' não encontrada no Windows!")
        elif platform.system() == "Darwin":  # MacOS
            # Usar Quartz no MacOS
            from AppKit import NSWorkspace
            workspace = NSWorkspace.sharedWorkspace()
            apps = workspace.runningApplications()
            for app in apps:
                if titulo.lower() in app.localizedName().lower():
                    app.activateWithOptions_(1)  # Ativar a aplicação
                    break
            else:
                print(f"Janela com título '{titulo}' não encontrada no macOS!")
        else:
            # Para sistemas não suportados, usaremos pygetwindow
            janelas = gw.getWindowsWithTitle(titulo)
            if janelas:
                janela = janelas[0]
                janela.activate()  # Ativar a janela (coloca no primeiro plano)
            else:
                print(f"Janela com título '{titulo}' não encontrada!")
    except Exception as e:
        print(f"Erro ao trazer a janela para o primeiro plano: {e}")

# Função para processar a mensagem MIDI com a nota recebida
def processar_mensagem_midi(midi_message, config):
    if midi_message.type == 'note_on' or midi_message.type == 'note_off':
        nota = midi_message.note
        print(f"Mensagem MIDI recebida: Nota {nota}")

        # Verificar se a nota tem uma janela associada no arquivo de configuração
        if str(nota) in config:
            titulo_janela = config[str(nota)]["title"]
            print(f"Nota {nota} mapeada para a janela: {titulo_janela}")
            trazer_janela_para_frente(titulo_janela)

# Função para o modo interativo de digitar notas MIDI no terminal
def modo_interativo(config):
    print("\nModo Interativo (aguardando digitação de nota MIDI):")
    print("Digite as notas (60 = Janela Nota 60, 61 = Janela Nota 61, 100 = Spotify), ou 'sair' para encerrar.")
    
    while True:
        try:
            nota_input = input("Digite uma nota MIDI: ")
            if nota_input.lower() == 'sair':
                print("Saindo do modo interativo...")
                break
            # Tentar converter a entrada em um número inteiro
            try:
                nota = int(nota_input)
            except ValueError:
                print(f"Entrada inválida: '{nota_input}' não é uma nota MIDI válida.")
                continue  # Se não for um número, pede novamente

            # Verificar se a nota tem uma janela associada
            if str(nota) in config:
                titulo_janela = config[str(nota)]["title"]
                print(f"Nota {nota} mapeada para a janela: {titulo_janela}")
                trazer_janela_para_frente(titulo_janela)
            else:
                print(f"Nota {nota} não configurada no arquivo.")
        except KeyboardInterrupt:
            print("\nInterrupção pelo usuário (Ctrl+C). Saindo...")
            break

# Função principal para rodar o processo MIDI
def main():
    # Carregar o arquivo JSON de configuração
    config = carregar_config()

    # Se o dispositivo MIDI for "test", entra em modo interativo
    if config["midi_in"] == "test":
        modo_interativo(config)
        return  # Sai após o modo interativo
    
    # Configurar o dispositivo MIDI de entrada
    midi_in = configurar_midi(config)
    if midi_in is None:
        return  # Se o dispositivo MIDI não for encontrado, sai do programa

    # Iniciar o loop de captura de mensagens MIDI
    for midi_message in midi_in:
        processar_mensagem_midi(midi_message, config)

if __name__ == "__main__":
    main()
