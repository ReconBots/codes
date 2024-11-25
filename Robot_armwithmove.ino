#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Inicializa o driver PCA9685
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define NUM_SERVOS  5   // Número total de servos

// Definições de limites para cada articulação
#define LINK0_MIN   102
#define LINK0_MAX   578
#define LINK1_MIN   400
#define LINK1_MAX   450
#define LINK2_MIN   100
#define LINK2_MAX   500
#define LINK3_MIN   345
#define LINK3_MAX   555
#define LINK4_MIN   258
#define LINK4_MAX   473

// Canais do PCA9685 associados aos servos
int servoPins[NUM_SERVOS] = {0, 1, 2, 3, 4}; // Canais dos servos no controlador PCA9685

// Armazena as posições atuais dos servos
int currentPosition[NUM_SERVOS] = {LINK0_MIN, LINK1_MIN, LINK2_MIN, LINK3_MIN, LINK4_MIN};

void setup() {
  Serial.begin(9600);
  Serial.println("Braço robótico pronto para comandos personalizados (faixa PWM).");

  // Inicializa o PCA9685
  pwm.begin();
  pwm.setPWMFreq(50); // Configura frequência de 50 Hz (ideal para servos)

  // Move cada servo para sua posição inicial
  for (int i = 0; i < NUM_SERVOS; i++) {
    pwm.setPWM(servoPins[i], 0, currentPosition[i]);
  }
}

void loop() {
  // Verifica se há comandos disponíveis na interface serial
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Lê o comando recebido
    command.trim(); // Remove espaços em branco no início e no final da string
    processCommand(command); // Processa o comando
  }
}


// Processa os comandos recebidos via Serial
void processCommand(String command) {
  // Divide o comando em partes
  String action = command.substring(0, command.indexOf(' '));
  String params = command.substring(command.indexOf(' ') + 1);

  // Verifica se o comando é "move"
  if (action == "move") {
    int joint = params.substring(0, params.indexOf(' ')).toInt(); // Articulação
    int pwmValue = params.substring(params.indexOf(' ') + 1).toInt(); // Valor PWM

    // Valida a entrada
    if (joint >= 0 && joint < NUM_SERVOS && validatePWM(joint, pwmValue)) {
      moveJointToPWM(joint, pwmValue);
    } else {
      Serial.println("Erro: Comando inválido ou fora dos limites.");
    }
  } else {
    Serial.println("Erro: Comando desconhecido.");
  }
}

// Valida se o valor PWM está dentro do intervalo permitido para a articulação
bool validatePWM(int joint, int pwmValue) {
  switch (joint) {
    case 0: return pwmValue >= LINK0_MIN && pwmValue <= LINK0_MAX;
    case 1: return pwmValue >= LINK1_MIN && pwmValue <= LINK1_MAX;
    case 2: return pwmValue >= LINK2_MIN && pwmValue <= LINK2_MAX;
    case 3: return pwmValue >= LINK3_MIN && pwmValue <= LINK3_MAX;
    case 4: return pwmValue >= LINK4_MIN && pwmValue <= LINK4_MAX;
    default: return false;
  }
}

// Move uma junta específica para um valor PWM desejado
void moveJointToPWM(int joint, int targetPWM) {
  int channel = servoPins[joint];
  int currentPWM = currentPosition[joint];

  // Movimenta o servo suavemente para o valor desejado
  if (currentPWM < targetPWM) {
    for (int pos = currentPWM; pos <= targetPWM; pos++) {
      pwm.setPWM(channel, 0, pos);
      delay(15); // Ajuste a suavidade
    }
  } else {
    for (int pos = currentPWM; pos >= targetPWM; pos--) {
      pwm.setPWM(channel, 0, pos);
      delay(15); // Ajuste a suavidade
    }
  }

  // Atualiza a posição atual
  currentPosition[joint] = targetPWM;
  Serial.print("Articulação ");
  Serial.print(joint);
  Serial.print(" movida para PWM ");
  Serial.println(targetPWM);
}
