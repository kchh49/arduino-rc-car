## 초음파 센서 기반 RC카 장애물 회피 실험

초음파 센서를 이용하여 RC카의 장애물 회피 성능을 비교하는 프로젝트입니다.

- 센서 개수(1/3/5개)에 따른 회피 성능 비교
- 센서 측정 주기(delay)에 따른 반응 속도 비교
- Bluetooth Serial 통신을 이용하여 Python에서 실시간 데이터를 수집하고 CSV 및 그래프로 시각화

### 사용 부품

- Arduino Uno
- 초음파 센서 HC-SR04
- 서보 모터
- 블루투스 모듈 HC-06
- DC 모터 x 2

### 핀 연결

| 항목 | delay 실험 | count 1개 | count 3개 | count 5개 |
|------|-----------|-----------|-----------|-----------|
| TRIG_F / ECHO_F | 13 / 12 | 13 / 12 | 13 / 12 | 13 / 12 |
| TRIG_L / ECHO_L | — | — | 7 / 8 | 7 / 8 |
| TRIG_R / ECHO_R | — | — | 9 / 10 | 9 / 10 |
| TRIG_SL / ECHO_SL | — | — | — | 2 / 4 |
| TRIG_SR / ECHO_SR | — | — | — | A0 / A1 |
| SERVO_PIN | 9 | 9 | — | — |
| 블루투스(Arduino) RX / TX | 2 / 4 (SoftwareSerial) | 0 / 1 (HardwareSerial) | 0 / 1 (HardwareSerial) | 0 / 1 (HardwareSerial) |
| MOTOR_A_a / b | 3 / 11 | 3 / 11 | 3 / 11 | 3 / 11 |
| MOTOR_B_a / b | 5 / 6 | 5 / 6 | 5 / 6 | 5 / 6 |

> **주의**: 모터 핀 연결 시 바퀴 회전 방향이 실제 환경에 따라 다를 수 있습니다. 연결 후 직진/후진 방향을 확인하고 필요 시 핀 연결을 반대로 조정하세요.

### 폴더 구조

```
arduino-rc-car/
├── docs/                               # 실험 결과 보고서 PDF
├── ulSensor_TestCode/                  # 초음파 센서 기본 테스트 코드
├── ulSensor_count_experiment/          # 센서 개수별 실험 아두이노 코드
│   ├── 1_ulSensor/
│   ├── 3_ulSensors/
│   └── 5_ulSensors/
├── ulSensor_delay_experiment/          # 측정 주기별 실험 아두이노 코드
└── python/UlSensor/
    ├── ulsensor_count_experiment/      # 센서 개수별 데이터 수집 및 시각화
    │   └── result/                     # CSV 데이터 및 그래프 이미지
    └── ulsensor_delay_experiment/      # 측정 주기별 데이터 수집 및 시각화
        └── result/                     # CSV 데이터 및 그래프 이미지
```

## 실험 구성

### 1. 센서 개수별 비교 실험
- 초음파 센서 1개 (서보 모터로 좌우 스캔) / 3개 (전방+대각선) / 5개 (전방+대각선+측면) 비교
- 각 구성마다 5회 주행 측정
- 아두이노 및 파이썬 코드 모두 장애물 30회 감지 시 자동 종료

### 2. 측정 주기별 비교 실험
- delay 20ms / 100ms / 500ms 조건 비교
- 아두이노 코드는 장애물 30회 감지 시 RC카를 정지
- 파이썬 코드에서 Ctrl+C 입력 시 CSV 및 그래프 저장

## 실행 방법

1. 아두이노 IDE에서 해당 `.ino` 파일 업로드
2. 블루투스 모듈 연결 후 파이썬 스크립트 실행
3. 파이썬에서 Enter 입력 시 'S' 신호 전송, RC카 출발
   
### 센서 개수별 실험
- 장애물 30회 감지 시 자동 종료
- CSV 및 그래프 자동 저장

### 측정 주기별 실험
- 원하는 시점에 Ctrl+C로 종료
- 종료 후 CSV 및 그래프 저장
