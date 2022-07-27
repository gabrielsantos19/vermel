#include <Servo.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <QC3Control.h>

#define CE A0
#define CSN A1
/* Não configuráveis - https://nrf24.github.io/RF24/
#define SCK 13
#define MOSI 11
#define MISO 12
#define IRQ - */
#define ENA 5
#define IN1 6
#define IN2 8
#define SG90_PWM 9
#define QC3_DATA_MAIS 3 // Verde
#define QC3_DATA_MENOS 4 // Branco


struct Estado {
  uint8_t modulo;
  uint8_t direcao;
  int8_t sentido;
};


RF24 radio(CE, CSN);
Servo sg90;
QC3Control quickCharge(QC3_DATA_MAIS, QC3_DATA_MENOS);
uint8_t addresses[][6] = {"1Node", "2Node"};
Estado estado_aplicado;
Estado estado_desejado;
unsigned long marca;
unsigned long tempo_estado_desejado;


void aplicar_modulo() {
  analogWrite(ENA, estado_desejado.modulo);
  estado_aplicado.modulo = estado_desejado.modulo;
}

void aplicar_direcao() {
  if(estado_desejado.direcao > 29 && estado_desejado.direcao < 140) {
    sg90.write(estado_desejado.direcao);
    estado_aplicado.direcao = estado_desejado.direcao;
  }
}

void aplicar_sentido() {
  if(estado_desejado.sentido == 1) {
    digitalWrite(IN1, 1);
    digitalWrite(IN2, 0);
  } else if(estado_desejado.sentido == -1) {
    digitalWrite(IN1, 0);
    digitalWrite(IN2, 1);
  } else {
    digitalWrite(IN1, 0);
    digitalWrite(IN2, 0);
  }
  estado_aplicado.sentido = estado_desejado.sentido;
}

void atualizar() {
  if(estado_aplicado.direcao != estado_desejado.direcao) {
    aplicar_direcao();
  }

  if(estado_aplicado.sentido != estado_desejado.sentido) {
    aplicar_sentido();
  }

  if(estado_aplicado.modulo != estado_desejado.modulo) {
    aplicar_modulo();
  }
}

void setup() {
  estado_desejado.modulo = 0;
  estado_desejado.direcao = 55;
  estado_desejado.sentido = 0;
  
  radio.begin();
  radio.openReadingPipe(1, addresses[0]);
  radio.startListening();

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  sg90.attach(SG90_PWM);

  aplicar_modulo();
  aplicar_direcao();
  aplicar_sentido();

  quickCharge.begin();
  quickCharge.set5V();
  quickCharge.set12V();
}

void loop() {
  if(radio.available()) {
    radio.read(&estado_desejado, sizeof(Estado));
    tempo_estado_desejado = millis();
  }

  // Reseta o sentido se não receber mensagens em 500ms
  marca = millis();
  if(marca - tempo_estado_desejado > 500) {
    estado_desejado.modulo = 0;
    estado_desejado.sentido = 0;
  }
  
  atualizar();
}
