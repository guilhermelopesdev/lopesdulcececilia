#include <Wire.h>

// Definição dos pinos e constantes
const int numButtons = 34; // Total de botões
const int buttonPins[numButtons] = {22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, A8, A10, A12, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19};
const int numLeds = 19; // Total de LEDs
const int ledPins[numLeds] = {23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, A9, A11, A13};
const int triggerPin = 14; // Porta que será acionada após receber a mensagem MIDI

// Variáveis para debounce e estado
int buttonState[numButtons] = {HIGH}; // Estado inicial HIGH (botões soltos)
int lastButtonState[numButtons] = {HIGH}; // Estado inicial HIGH (botões soltos)
unsigned long lastDebounceTime[numButtons] = {0};
unsigned long debounceDelay = 50; // Tempo de debounce em milissegundos

// Estados dos LEDs
bool ledStates[numLeds] = {false}; // Estado atual dos LEDs

#define DEBUG false // Define se mensagens de depuração serão enviadas

void setup() {
  Serial.begin(115200); // Inicia a comunicação serial na taxa de baud MIDI padrão

  // Configura os pinos dos botões como entrada com pull-up interno
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }

  // Configura os pinos dos LEDs como saída e apaga-os
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
    ledStates[i] = false; // Inicializa o estado dos LEDs como apagado
  }

  // Configura a porta de trigger como saída e apaga-a
  pinMode(triggerPin, OUTPUT);
  digitalWrite(triggerPin, LOW);

  if (DEBUG) Serial.println("Setup concluído.");
}

void loop() {
  checkButtons();      // Verifica o estado dos botões
  readMidiMessages();  // Lê e processa mensagens MIDI recebidas
}

// Função para verificar o estado dos botões com debounce
void checkButtons() {
  for (int i = 0; i < numButtons; i++) {
    int reading = digitalRead(buttonPins[i]);

    // Se o estado mudou, registra o tempo da alteração
    if (reading != buttonState[i]) {
      lastDebounceTime[i] = millis();
    }

    // Verifica se o tempo de debounce passou
    if ((millis() - lastDebounceTime[i]) > debounceDelay) {
      // Se o estado mudou de fato
      if (reading != lastButtonState[i]) {
        lastButtonState[i] = reading;

        int note = i + 1; // Nota MIDI ajustada (botão 0 -> nota 1)

        if (lastButtonState[i] == LOW) { // Botão pressionado
          sendNoteOn(note);  // Apenas envia a mensagem MIDI
        } else { // Botão solto
          sendNoteOff(note); // Envia mensagem Note Off
        }

        if (DEBUG) {
          Serial.print("Botão "); Serial.print(i);
          Serial.println((lastButtonState[i] == LOW) ? " pressionado." : " solto.");
        }
      }
    }

    // Atualiza o estado atual do botão
    buttonState[i] = reading;
  }
}

// Função para enviar uma mensagem MIDI Note On
void sendNoteOn(byte note) {
  Serial.write(0x90); // Status byte para Note On, canal 1
  Serial.write(note);
  Serial.write(127); // Velocidade máxima
}

// Função para enviar uma mensagem MIDI Note Off
void sendNoteOff(byte note) {
  Serial.write(0x80); // Status byte para Note Off, canal 1
  Serial.write(note);
  Serial.write(0); // Velocidade zero
}

// Função para alternar o estado de um LED
void toggleLed(int ledIndex, bool state) {
  if (ledIndex >= 0 && ledIndex < numLeds) {
    digitalWrite(ledPins[ledIndex], state ? HIGH : LOW);
    ledStates[ledIndex] = state; // Atualiza o estado do LED
  }
}

// Função para ler mensagens MIDI recebidas
void readMidiMessages() {
  while (Serial.available() >= 3) {
    byte command = Serial.read();
    byte note = Serial.read();
    byte velocity = Serial.read();

    // Processar a mensagem MIDI recebida
    if (command == 0x90 && velocity > 0) { // Note On
      toggleLed(note - 1, true); // Acende o LED correspondente
    } else if (command == 0x80 || (command == 0x90 && velocity == 0)) { // Note Off
      toggleLed(note - 1, false); // Apaga o LED correspondente
    }

    if (DEBUG) {
      Serial.print("MIDI Command: 0x"); Serial.print(command, HEX);
      Serial.print(" Note: "); Serial.print(note);
      Serial.print(" Velocity: "); Serial.println(velocity);
    }
  }
}
