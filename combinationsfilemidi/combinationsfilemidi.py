import mido
from pywinauto import Application

# Nome fixo do dispositivo MIDI a ser usado
MIDI_DEVICE_NAME = "Seu_Dispositivo_MIDI_Aqui"  # Substitua pelo nome exato do dispositivo

# Mapeamento de teclas MIDI para ações
MIDI_TO_ACTION = {
    60: "export",  # Nota C4 (Middle C) - Abrir Export Combinations
    62: "import",  # Nota D4 - Abrir Import Combinations
}

# Nome da janela do GrandOrgue
GRAND_ORGUE_WINDOW_TITLE = "GrandOrgue"

def handle_midi_message(msg, app):
    """Lida com mensagens MIDI."""
    if msg.type == 'note_on' and msg.velocity > 0:  # Tecla pressionada
        note = msg.note
        if note in MIDI_TO_ACTION:
            action = MIDI_TO_ACTION[note]
            if action == "export":
                open_export_combinations(app)
            elif action == "import":
                open_import_combinations(app)

def open_export_combinations(app):
    """Executa Export Combinations sem focar a janela."""
    window = app.window(title_re=GRAND_ORGUE_WINDOW_TITLE)
    window.menu_select("File->Export combinations")

def open_import_combinations(app):
    """Executa Import Combinations sem focar a janela."""
    window = app.window(title_re=GRAND_ORGUE_WINDOW_TITLE)
    window.menu_select("File->Import combinations")

def main():
    """Programa principal para monitorar mensagens MIDI."""
    # Verifica se o dispositivo MIDI está disponível
    available_devices = mido.get_input_names()
    if MIDI_DEVICE_NAME not in available_devices:
        print(f"Erro: O dispositivo MIDI '{MIDI_DEVICE_NAME}' não foi encontrado.")
        print("Dispositivos disponíveis:")
        for name in available_devices:
            print(f" - {name}")
        return

    # Conecta ao GrandOrgue
    try:
        app = Application().connect(title_re=GRAND_ORGUE_WINDOW_TITLE)
        print(f"Conectado à janela '{GRAND_ORGUE_WINDOW_TITLE}'.")
    except Exception as e:
        print(f"Erro ao conectar ao GrandOrgue: {e}")
        return

    # Abre o dispositivo MIDI para leitura
    with mido.open_input(MIDI_DEVICE_NAME) as midi_input:
        print(f"Usando dispositivo MIDI: {MIDI_DEVICE_NAME}")
        print("Escutando mensagens MIDI...")
        for msg in midi_input:
            handle_midi_message(msg, app)

if __name__ == "__main__":
    main()

