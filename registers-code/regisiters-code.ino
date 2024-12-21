//STABLE AND FINAL VERSION

#include <Wire.h>

const int numButtons = 20; // Total de 20 botões
const int buttonPins[numButtons] = {22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 2, 3, 4, 5};
const int numLeds = 20; // Total de 20 LEDs
const int ledPins[numLeds] = {23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 6, 7, 8, 9};

const int triggerPin = 14; // Porta que será acionada após receber a mensagem MIDI

int buttonState[numButtons] = {HIGH}; // Estado inicial HIGH (botões soltos)
int lastButtonState[numButtons] = {HIGH}; // Estado inicial HIGH (botões soltos)
unsigned long lastDebounceTime[numButtons] = {0};
unsigned long debounceDelay = 50; // Tempo de debounce

bool ledStates[numLeds] = {false}; // Estado atual dos LEDs

bool midiReceived = false; // Flag para verificar se uma mensagem MIDI foi recebida

void setup() {
  Serial.begin(115200); // Inicia a comunicação serial na taxa de baud MIDI padrão
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP); // Configura os pinos dos botões como entrada com pull-up interno
  }
  for (int i = 0; i < numLeds; i++) {
    pinMode(ledPins[i], OUTPUT); // Configura os pinos dos LEDs como saída
    digitalWrite(ledPins[i], LOW); // Garante que todos os LEDs estão apagados inicialmente
  }

  pinMode(triggerPin, OUTPUT); // Configura a porta 14 como saída
  digitalWrite(triggerPin, LOW); // Garante que a porta 14 está apagada inicialmente

  // Adiciona um pequeno atraso para estabilizar o sistema
  delay(1000);

  // Verificação adicional para garantir que todos os LEDs estejam apagados
  for (int i = 0; i < numLeds; i++) {
    digitalWrite(ledPins[i], LOW);
    ledStates[i] = false;
  }

  // Aguarda a recepção de qualquer informação MIDI
  waitForMidi();
}

void loop() {
  checkButtons();
  readMidiMessages();
}

void checkButtons() {
  // Verifica o estado dos botões com debounce
  for (int i = 0; i < numButtons; i++) {
    int reading = digitalRead(buttonPins[i]);

    if (reading != buttonState[i]) {
      lastDebounceTime[i] = millis();
    }

    if ((millis() - lastDebounceTime[i]) > debounceDelay) {
      if (reading != lastButtonState[i]) {
        lastButtonState[i] = reading;

        if (lastButtonState[i] == LOW) {
          // Botão foi pressionado
          int note = i + 1; // Nota MIDI ajustada
          sendNoteOn(note);
          Serial.print("Botão pressionado: ");
          Serial.print(i);
          Serial.print(" Nota MIDI: ");
          Serial.println(note);
        } else {
          // Botão foi solto
          int note = i + 1; // Nota MIDI ajustada
          sendNoteOff(note);
          Serial.print("Botão solto: ");
          Serial.print(i);
          Serial.print(" Nota MIDI: ");
          Serial.println(note);
        }
      }
    }

    buttonState[i] = reading;
  }
}

void sendNoteOn(byte note) {
  Serial.write(0x90); // Status byte for Note On, channel 1
  Serial.write(note);
  Serial.write(127); // Maximum velocity
}

void sendNoteOff(byte note) {
  Serial.write(0x80); // Status byte for Note Off, channel 1
  Serial.write(note);
  Serial.write(0); // Velocity zero
}

void readMidiMessages() {
  // Lê mensagens MIDI recebidas e as armazena no buffer
  while (Serial.available() >= 3) {
    byte command = Serial.read();
    byte note = Serial.read();
    byte velocity = Serial.read();
    if ((command & 0xF0) == 0x90 && velocity > 0) { // Note On
      handleNoteOn(note, velocity);
    } else if ((command & 0xF0) == 0x80 || ((command & 0xF0) == 0x90 && velocity == 0)) { // Note Off
      handleNoteOff(note);
    }
  }
}

void handleNoteOn(byte note, byte velocity) {
  if (note >= 1 && note <= 20) {
    int ledIndex = note - 1; // Ajusta o índice do LED de acordo com a nota MIDI
    if (ledIndex < numLeds) {
      ledStates[ledIndex] = true; // Liga o LED
      digitalWrite(ledPins[ledIndex], HIGH); // Liga o LED
      Serial.print("LED ");
      Serial.print(ledIndex + 1);
      Serial.println(" ligado.");
    }
  }
}

void handleNoteOff(byte note) {
  if (note >= 1 && note <= 20) {
    int ledIndex = note - 1; // Ajusta o índice do LED de acordo com a nota MIDI
    if (ledIndex < numLeds) {
      ledStates[ledIndex] = false; // Desliga o LED
      digitalWrite(ledPins[ledIndex], LOW); // Desliga o LED
      Serial.print("LED ");
      Serial.print(ledIndex + 1);
      Serial.println(" desligado.");
    }
  }
}

void waitForMidi() {
  while (!midiReceived) {
    if (Serial.available() > 0) {
      midiReceived = true; // Mensagem MIDI recebida
      digitalWrite(triggerPin, HIGH); // Liga a porta 14
      Serial.println("Mensagem MIDI recebida, prosseguindo para o loop.");
    }
  }
}