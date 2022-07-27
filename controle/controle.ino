#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE 3
#define CSN 2
/* Não configuráveis - https://nrf24.github.io/RF24/
#define SCK 13
#define MOSI 11
#define MISO 12
#define IRQ - */


struct Estado {
  uint8_t modulo;
  uint8_t direcao;
  int8_t sentido;
};


RF24 radio(CE, CSN);
uint8_t addresses[][6] = {"1Node", "2Node"};
Estado estado_desejado;
char entrada;


void setup()
{
  Serial.begin(9600);
  Serial.print("afdsfads8f78");

  estado_desejado.modulo = 0;
  estado_desejado.direcao = 90;
  estado_desejado.sentido = 0;
  
  radio.begin();
  radio.openWritingPipe(addresses[0]);
  radio.stopListening();
}

void loop()
{
  if(Serial.available()) {
    Serial.readBytes((char*) &estado_desejado, 3);
    Serial.print("Módulo: ");
    Serial.print(estado_desejado.modulo);
    Serial.print(" Direcao: ");
    Serial.print(estado_desejado.direcao);
    Serial.print(" Sentido: ");
    Serial.print(estado_desejado.sentido);
    Serial.println();
  }
  
  radio.write(&estado_desejado, sizeof(Estado));
  delay(30);
}
