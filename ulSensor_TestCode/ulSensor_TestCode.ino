#define TRIG 13
#define ECHO 12

void setup() {
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  long duration = pulseIn(ECHO, HIGH, 30000);
  long dist = duration * 0.034 / 2;
  Serial.print("Distance: "); Serial.print(dist); Serial.println("cm");
  delay(200);
}
