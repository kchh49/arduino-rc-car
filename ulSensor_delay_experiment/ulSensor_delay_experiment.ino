#include <Servo.h>
#include <SoftwareSerial.h>

// 핀 정의
#define TRIG 13
#define ECHO 12
#define SERVO_PIN 9

#define MOTOR_A_a 3
#define MOTOR_A_b 11
#define MOTOR_B_a 5
#define MOTOR_B_b 6

// 속도 
#define SPEED_R 130
#define SPEED_L 145

SoftwareSerial bluetooth(2, 4); // RX, TX
Servo myServo;
float lastDist = 100;
int obstacleCount = 0;
const int MAX_COUNT = 30;

// ─────────────────────────────────────────
void setup() { 
  pinMode(MOTOR_A_a, OUTPUT); pinMode(MOTOR_A_b, OUTPUT);
  pinMode(MOTOR_B_a, OUTPUT); pinMode(MOTOR_B_b, OUTPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  myServo.attach(SERVO_PIN); //서보모터 9번핀 연결
  myServo.write(90); //서보모터 정면 초기화
  delay(1000); //서보모터가 정면으로 이동할 시간
  myServo.detach();

  bluetooth.begin(9600);

  while (true) {
    if (bluetooth.available()) { 
      char c = bluetooth.read(); 
      if (c == 'S' || c == 's') break; 
    }
  }
}

// ─────────────────────────────────────────
void loop() {
  unsigned long t = millis();
  float dist = getDistance();

   if (obstacleCount >= MAX_COUNT) {
    stopMotors();
    return;  
  }

 if (dist > 0 && dist < 20) {
    obstacleCount++;
    stopMotors();
    delay(300);

    myServo.attach(SERVO_PIN); //장애물 감지했을 때 서보 연결
    myServo.write(150);
    delay(500);
    float distLeft = getDistance();

    myServo.write(30);
    delay(500);
    float distRight = getDistance();

    myServo.write(90);
    delay(300);
    myServo.detach();  //서보 연결 해제

    if (distLeft >= distRight) {
      bluetooth.print(t); bluetooth.print(",");
      bluetooth.print(dist); bluetooth.print(",");
      bluetooth.print(distLeft); bluetooth.print(",");
      bluetooth.print(distRight); bluetooth.print(",");
      bluetooth.println("LEFT,OBSTACLE");
      turnRight(); delay(700); stopMotors();
    } else {
      bluetooth.print(t); bluetooth.print(",");
      bluetooth.print(dist); bluetooth.print(",");
      bluetooth.print(distLeft); bluetooth.print(",");
      bluetooth.print(distRight); bluetooth.print(",");
      bluetooth.println("RIGHT,OBSTACLE");
      turnLeft(); delay(700); stopMotors();
    }

  } else {
    bluetooth.print(t); bluetooth.print(",");
    bluetooth.print(dist); bluetooth.print(",");
    bluetooth.println("-1,-1,-1,DRIVING");
    moveForward();
  }

  delay(300);
}

// 거리 측정
float getDistance() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  unsigned long duration = pulseIn(ECHO, HIGH, 30000);
  if (duration == 0) return lastDist;
  float dist = duration * 0.034 / 2;
  if (dist < 2) return lastDist; //노이즈 처리
  lastDist = dist;
  return dist;
}

// 모터 제어
void moveForward() {
  analogWrite(MOTOR_A_a, SPEED_R); digitalWrite(MOTOR_A_b, LOW);
  analogWrite(MOTOR_B_a, SPEED_L); digitalWrite(MOTOR_B_b, LOW);
}
void turnRight() {
  digitalWrite(MOTOR_A_a, LOW); analogWrite(MOTOR_A_b, SPEED_R);
  analogWrite(MOTOR_B_a, SPEED_L); digitalWrite(MOTOR_B_b, LOW);
}
void turnLeft() {
  analogWrite(MOTOR_A_a, SPEED_R); digitalWrite(MOTOR_A_b, LOW);
  digitalWrite(MOTOR_B_a, LOW); analogWrite(MOTOR_B_b, SPEED_L);
}
void stopMotors() {
  digitalWrite(MOTOR_A_a, LOW); digitalWrite(MOTOR_A_b, LOW);
  digitalWrite(MOTOR_B_a, LOW); digitalWrite(MOTOR_B_b, LOW);
}