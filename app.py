import sys
import mido
import threading
import platform
import win32gui
import pygetwindow as gw
import json
import os

# Detecta o sistema operacional
is_windows = platform.system() == "Windows"

# Função para obter o diretório onde o script está localizado
def get_script_directory():
    return os.path.dirname(os.path.abspath(__file__))

# Função para listar janelas abertas no Windows usando pywin32
def get_open_windows():
    def enum_windows_callback(hwnd, windows_list):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if window_title:
                windows_list.append(window_title)

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows

# Função para ativar uma janela no Windows
def activate_window(window_name):
    try:
        # Encontre a janela com o nome especificado
        windows = gw.getWindowsWithTitle(window_name)
        if windows:
            window = windows[0]
            if window.isMinimized:
                window.restore()  # Restaura se a janela estiver minimizada
            window.activate()  # Coloca a janela no primeiro plano
            print(f"Janela '{window_name}' ativada e restaurada.")
    except Exception as e:
        print(f"Erro ao ativar a janela: {e}")

# Função para capturar eventos MIDI
def midi_listener(midi_port_name):
    try:
        midi_in = mido.open_input(midi_port_name)  # Usando open_input para abrir a porta MIDI
        print(f"Conectado à porta MIDI {midi_port_name}")

        while True:
            for msg in midi_in.iter_pending():
                if msg.type == 'note_on':  # Verifica se a mensagem MIDI é 'note_on'
                    note = msg.note
                    velocity = msg.velocity
                    if velocity > 0:  # Verifica se a tecla foi pressionada
                        print(f"Nota MIDI recebida: {note}")
                        window_name = midi_mappings.get(note)
                        if window_name:
                            print(f"Ativando a janela: {window_name} para a nota {note}")
                            activate_window(window_name)  # Ativa a janela mapeada para a nota MIDI
    except Exception as e:
        print(f"Erro ao escutar MIDI: {e}")

# Função para iniciar a escuta MIDI em thread separada
def start_midi_listener():
    midi_port_name = "cantusmidi 0"  # Define a porta MIDI fixa com o número 0
    print(f"Usando a porta MIDI fixa: {midi_port_name}")
    try:
        midi_ports = mido.get_input_names()
        print(f"Portas MIDI disponíveis: {midi_ports}")
        if midi_port_name in midi_ports:
            threading.Thread(target=midi_listener, args=(midi_port_name,), daemon=True).start()
        else:
            print(f"Erro: Porta MIDI '{midi_port_name}' não encontrada.")
    except Exception as e:
        print(f"Erro ao iniciar thread de escuta MIDI: {e}")

def list_and_refresh_windows():
    print("Listando janelas disponíveis:")
    windows = get_open_windows()
    print("Janelas detectadas:")
    for i, window in enumerate(windows):
        print(f"{i+1}. {window}")
    return windows

# Mapeamento de notas MIDI para janelas
midi_mappings = {
    1: 'Cantus MIDI',
    2: 'AnyDesk',
    3: 'GrandOrgue demo V1',
    4: 'GrandOrgue v3.15.3-1 - GrandOrgue demo V1',
    5: 'Configurações',
    6: 'loopMIDI',
    7: 'Microsoft Text Input Application',
    8: 'Program Manager',
    9: 'C:\\Windows\\py.exe',
    10: 'app.py - C:\\Organ Files\\cantusmidi\\app.py (3.9.0)'
}

def main():
    # Antes de iniciar a escuta MIDI, liste as janelas disponíveis
    available_windows = list_and_refresh_windows()
    
    # Inicie a escuta MIDI imediatamente após a listagem das janelas
    start_midi_listener()

    # Manter o programa em execução
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nPrograma encerrado.")

if __name__ == "__main__":
    main()
