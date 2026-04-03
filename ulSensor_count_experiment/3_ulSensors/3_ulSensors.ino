// 센서 3개: 전면, 앞-좌대각, 앞-우대각

// 핀 정의
#define TRIG_F 13
#define ECHO_F 12
#define TRIG_L  7   // 앞-좌 대각선
#define ECHO_L  8
#define TRIG_R  9   // 앞-우 대각선
#define ECHO_R 10

#define MOTOR_A_a  3
#define MOTOR_A_b 11
#define MOTOR_B_a  5
#define MOTOR_B_b  6

// 속도 
#define SPEED_R  115
#define SPEED_L  130

// 임계값 
#define DIST_FRONT_STOP  20   // 전방 장애물 감지 기준 (cm)
#define DIST_SIDE_WARN   15   // 측면 보정 기준 (cm)

// 카운트 
int obstacleCount = 0;
const int MAX_COUNT = 30;

float lastDistF = 100, lastDistL = 100, lastDistR = 100;

float getDistance(int trig, int echo, float &lastDist);
void moveForward();
void moveBackward();
void turnLeft();
void turnRight();
void stopMotors();

// ─────────────────────────────────────────
void setup() {
  pinMode(MOTOR_A_a, OUTPUT); pinMode(MOTOR_A_b, OUTPUT);
  pinMode(MOTOR_B_a, OUTPUT); pinMode(MOTOR_B_b, OUTPUT);
  pinMode(TRIG_F, OUTPUT); pinMode(ECHO_F, INPUT);
  pinMode(TRIG_L, OUTPUT); pinMode(ECHO_L, INPUT);
  pinMode(TRIG_R, OUTPUT); pinMode(ECHO_R, INPUT);

  Serial.begin(9600);
  while (true) {
    if (Serial.available()) {
      char c = Serial.read();
      if (c == 'S' || c == 's') break;
    }
  }
}

// ─────────────────────────────────────────
void loop() {
  if (obstacleCount >= MAX_COUNT) {
    stopMotors();
    return;
  }

  unsigned long t = millis();
  float distF = getDistance(TRIG_F, ECHO_F, lastDistF);
  float distL = getDistance(TRIG_L, ECHO_L, lastDistL);
  float distR = getDistance(TRIG_R, ECHO_R, lastDistR);

  String action = "";

  if (distF < DIST_FRONT_STOP) {
    obstacleCount++;
    stopMotors(); delay(200);

    bool leftOpen  = distR >= distL;
    bool rightOpen = distL >  distR;

    if (leftOpen) {
      action = "LEFT_OBSTACLE";
      turnLeft(); delay(500); stopMotors();

    } else if (rightOpen) {
      action = "RIGHT_OBSTACLE";
      turnRight(); delay(500); stopMotors();

    } else {
      action = "REVERSE_OBSTACLE";
      moveBackward(); delay(400); stopMotors(); delay(200);
      if (distL >= distR) {
        turnLeft();  delay(500);
      } else {
        turnRight(); delay(500);
      }
      stopMotors();
    }

  } else {
    if (distL < DIST_SIDE_WARN && distR >= DIST_SIDE_WARN) {
      action = "ADJUST_RIGHT";
      turnLeft(); delay(200);
    } else if (distR < DIST_SIDE_WARN && distL >= DIST_SIDE_WARN) {
      action = "ADJUST_LEFT";
      turnRight(); delay(200);
    } else {
      action = "DRIVING";
    }
    moveForward();
  }

  Serial.print(t);      Serial.print(",");
  Serial.print(distF);  Serial.print(",");
  Serial.print(distL);  Serial.print(",");
  Serial.print(distR);  Serial.print(",");
  Serial.println(action);

  delay(100);
}

// 거리 측정
float getDistance(int trig, int echo, float &lastDist) {
  digitalWrite(trig, LOW);  delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  unsigned long duration = pulseIn(echo, HIGH, 30000);
  if (duration == 0) return lastDist;
  float dist = duration * 0.034 / 2.0;
  if (dist < 2 || dist > 100) return lastDist;
  lastDist = dist;
  return dist;
}

// 모터 제어
void moveForward() {
  analogWrite(MOTOR_A_a, SPEED_R); digitalWrite(MOTOR_A_b, LOW);
  analogWrite(MOTOR_B_a, SPEED_L); digitalWrite(MOTOR_B_b, LOW);
}
void moveBackward() {
  digitalWrite(MOTOR_A_a, LOW); analogWrite(MOTOR_A_b, SPEED_R);
  digitalWrite(MOTOR_B_a, LOW); analogWrite(MOTOR_B_b, SPEED_L);
}
void turnLeft() {
  analogWrite(MOTOR_A_a, SPEED_R); digitalWrite(MOTOR_A_b, LOW);
  digitalWrite(MOTOR_B_a, LOW);    analogWrite(MOTOR_B_b, SPEED_L);
}
void turnRight() {
  digitalWrite(MOTOR_A_a, LOW);    analogWrite(MOTOR_A_b, SPEED_R);
  analogWrite(MOTOR_B_a, SPEED_L); digitalWrite(MOTOR_B_b, LOW);
}
void stopMotors() {
  digitalWrite(MOTOR_A_a, LOW); digitalWrite(MOTOR_A_b, LOW);
  digitalWrite(MOTOR_B_a, LOW); digitalWrite(MOTOR_B_b, LOW);
}
