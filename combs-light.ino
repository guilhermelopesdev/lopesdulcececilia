// Definição dos pinos dos LEDs no ESP32
const int numLeds = 15; // Total de LEDs
const int ledPins[numLeds] = {2, 22, 0, 4, 16, 17, 5, 18, 19, 12, 14, 27, 26, 25, 23};

// Nota MIDI inicial para acionar os LEDs
const int midiStartNote = 20; 

// Estados dos LEDs
bool ledStates[numLeds] = {false}; 

#define DEBUG false

void setup() {
  Serial.begin(115200); // Comunicação via USB para Hairless MIDI

  // Configura os pinos dos LEDs como saída e inicializa apagados
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
    ledStates[i] = false;
  }

  if (DEBUG) Serial.println("Setup concluído.");
}

void loop() {
  readMidiMessages(); // Lê e processa mensagens MIDI recebidas
}

// Função para ler mensagens MIDI recebidas via USB (Hairless MIDI)
void readMidiMessages() {
  while (Serial.available() >= 3) { // Verifica se há pelo menos 3 bytes disponíveis
    byte command = Serial.read();
    byte note = Serial.read();
    byte velocity = Serial.read();

    if (DEBUG) {
      Serial.print("MIDI Command: 0x"); Serial.print(command, HEX);
      Serial.print(" Note: "); Serial.print(note);
      Serial.print(" Velocity: "); Serial.println(velocity);
    }

    // Se a nota MIDI está dentro do intervalo dos LEDs
    if (note >= midiStartNote && note < midiStartNote + numLeds) {
      int ledIndex = note - midiStartNote; // Calcula o índice do LED correspondente

      if (command == 0x90 && velocity > 0) { // Note On
        toggleLed(ledIndex, true);
      } else if (command == 0x80 || (command == 0x90 && velocity == 0)) { // Note Off
        toggleLed(ledIndex, false);
      }
    }
  }
}

// Função para alternar o estado de um LED
void toggleLed(int ledIndex, bool state) {
  if (ledIndex >= 0 && ledIndex < numLeds) {
    digitalWrite(ledPins[ledIndex], state ? HIGH : LOW);
    ledStates[ledIndex] = state;
  }
}
