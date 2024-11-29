import sys
import rtmidi
import subprocess
import threading
import platform
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

# Detecta o sistema operacional (macOS, Linux ou Windows)
is_mac = platform.system() == "Darwin"
is_linux = platform.system() == "Linux"
is_windows = platform.system() == "Windows"

# Função para listar janelas abertas
def get_open_windows():
    if is_mac:
        # AppleScript para listar janelas no macOS
        script = '''
        tell application "System Events"
            set window_list to {}
            set theProcesses to (every process whose visible is true)
            repeat with proc in theProcesses
                try
                    set winNames to name of every window of proc
                    set window_list to window_list & winNames
                end try
            end repeat
        end tell
        return window_list
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        windows = result.stdout.strip().split(', ')
    elif is_linux:
        # xdotool para listar janelas no Linux
        result = subprocess.getoutput('xdotool search --onlyvisible --name "" getwindowname %@')
        windows = result.split('\n')
    elif is_windows:
        # pygetwindow para listar janelas no Windows
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle('')
    else:
        windows = []
    return [win.strip() for win in windows if win.strip()]

# Função para ativar uma janela pelo nome
def activate_window(window_name):
    if is_mac:
        # AppleScript para ativar janelas no macOS
        script = f'''
        tell application "System Events"
            set theProcesses to (every process whose visible is true)
            repeat with proc in theProcesses
                try
                    if (name of every window of proc) contains "{window_name}" then
                        set frontmost of proc to true
                        return
                    end if
                end try
            end repeat
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
    elif is_linux:
        # xdotool para ativar janelas no Linux
        window_id = subprocess.getoutput(f'xdotool search --name "{window_name}"')
        if window_id:
            subprocess.call(['xdotool', 'windowactivate', window_id])
    elif is_windows:
        # pygetwindow para ativar janelas no Windows
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(window_name)
        if windows:
            window = windows[0]  # Caso existam várias janelas com o mesmo nome
            window.activate()
            window.restore()  # Restaura a janela caso esteja minimizada
    print(f"Ativando janela: {window_name}")

# Função para capturar eventos MIDI
def midi_listener(midi_port):
    midi_in = rtmidi.MidiIn()
    midi_in.open_port(midi_port)
    while True:
        msg = midi_in.get_message()
        if msg:
            message, deltatime = msg
            status, note, velocity = message
            if status == 144 and velocity > 0:  # Note On message
                window_name = midi_mappings.get(note)
                if window_name:
                    activate_window(window_name)

# Função para iniciar a escuta MIDI em thread separada
def start_midi_listener():
    selected_port = midi_port_var.currentText()
    if selected_port.isdigit():
        threading.Thread(target=midi_listener, args=(int(selected_port),), daemon=True).start()

class MidiWindowSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cantus MIDI")
        self.setGeometry(100, 100, 600, 500)  # Aumentando o tamanho da janela para acomodar os botões

        # Fonte medieval para o título
        title_font = QFont("Times New Roman", 24, QFont.Bold)  # Fonte básica para simular medieval
        title_font.setItalic(True)  # Pode usar itálico para dar um estilo diferente

        # Layout principal
        layout = QVBoxLayout()

        # Título da janela com fonte medieval
        title_label = QLabel("Cantus MIDI")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Frame para seleção da porta MIDI
        midi_frame = QHBoxLayout()
        midi_label = QLabel("Selecione a Porta MIDI:")
        midi_frame.addWidget(midi_label)
        midi_ports = rtmidi.MidiIn().get_ports()
        self.midi_port_var = QComboBox()
        self.midi_port_var.addItems([str(i) for i in range(len(midi_ports))])
        midi_frame.addWidget(self.midi_port_var)
        start_button = QPushButton("Iniciar MIDI")
        start_button.clicked.connect(start_midi_listener)
        midi_frame.addWidget(start_button)
        layout.addLayout(midi_frame)

        # Frame para configuração dos botões (notas MIDI)
        self.window_dropdowns = []
        self.midi_buttons = []  # Lista para armazenar os botões MIDI

        for i in range(10):
            # Criar uma linha com o label e o dropdown para a janela associada à nota MIDI
            frame = QHBoxLayout()
            note_label = QLabel(f"Nota MIDI {i + 1}:")
            frame.addWidget(note_label)
            window_dropdown = QComboBox()
            self.window_dropdowns.append(window_dropdown)
            frame.addWidget(window_dropdown)

            # Criar o botão para ativar a janela correspondente à nota MIDI
            midi_button = QPushButton("Testar")
            midi_button.setFixedSize(60, 30)  # Definir tamanho fixo para o botão
            midi_button.clicked.connect(lambda _, note=i + 1: self.activate_midi_window(note))
            self.midi_buttons.append(midi_button)

            # Adicionando o botão na mesma linha
            frame.addWidget(midi_button)
            layout.addLayout(frame)

        # Botão para atualizar lista de janelas
        refresh_button = QPushButton("Atualizar Janelas")
        refresh_button.clicked.connect(self.refresh_windows)  # Chamando o método da instância
        layout.addWidget(refresh_button)

        # Definir o layout da janela
        self.setLayout(layout)
        self.refresh_windows()  # Atualizar lista de janelas quando a janela for criada

    # Função para atualizar a lista de janelas abertas
    def refresh_windows(self):
        windows = get_open_windows()
        print("Janelas detectadas:", windows)  # Debug: verifique no console
        for i in range(10):
            # Certifique-se de usar a variável de instância da classe
            self.window_dropdowns[i].clear()
            self.window_dropdowns[i].addItems(windows)

    # Função para ativar a janela associada à nota MIDI quando um botão for clicado
    def activate_midi_window(self, note):
        window_name = self.window_dropdowns[note - 1].currentText()
        if window_name:
            activate_window(window_name)

# Função para mapear as notas MIDI para janelas
midi_mappings = {}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MidiWindowSelector()
    window.show()
    sys.exit(app.exec())
