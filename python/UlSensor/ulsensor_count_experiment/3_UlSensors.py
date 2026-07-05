import serial
import csv
import time
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# 설정
PORT          = 'COM(포트번호변경)'
BAUD_RATE     = 9600
MAX_OBSTACLES = 30
CSV_FILENAME  = '(파일명 변경).csv'
GRAPH_FILENAME = '(파일명 변경).png'

data = []
obstacle_count = 0

# 시리얼 연결
try:
    py_serial = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"[연결됨] Port: {PORT}, Baud: {BAUD_RATE}")
except Exception as e:
    print(f"[연결 실패] {e}")
    exit()

# 시작 신호
input("Enter 누르면 RC카 출발 (S 전송)...")
py_serial.reset_input_buffer()
py_serial.write(b"S")
py_serial.flush()
print("[시작됨] S 전송 RC카 출발!")
print(f"시간    | 전면   | 대각L  | 대각R  | 상태")
print("-" * 50)

no_data_count = 0

try:
    while obstacle_count < MAX_OBSTACLES:
        line = py_serial.readline().decode("utf-8", errors="ignore").strip()
        if not line:
            no_data_count += 1
            if no_data_count >= 10:
                print("[종료] 데이터가 더 없음")
                break
            continue
        no_data_count = 0
        if not line[0].isdigit():
            continue
        parts = line.split(",")
        if len(parts) != 5:
            continue
        try:
            t      = int(parts[0]) / 1000
            distF  = float(parts[1])
            distL  = float(parts[2])
            distR  = float(parts[3])
            status = parts[4].strip()
            if "OBSTACLE" in status or "REVERSE" in status:
                obstacle_count += 1
            data.append([t, distF, distL, distR, status, obstacle_count])
            print(f"{t:>6.1f}s | {distF:>6.1f} | {distL:>6.1f} | {distR:>6.1f} | {status}")
        except ValueError:
            continue
except KeyboardInterrupt:
    print("[중단] Ctrl+C")
finally:
    py_serial.close()
    print("[시리얼 종료]")

if not data:
    print("[오류] 데이터 없음")
    exit()

with open(CSV_FILENAME, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "distF", "distL", "distR", "status", "obstacle_count"])
    writer.writerows(data)
print(f"[저장] {CSV_FILENAME}  ({len(data)}행)")

times    = [d[0] for d in data]
distFs   = [d[1] for d in data]
distLs   = [d[2] for d in data]
distRs   = [d[3] for d in data]
statuses = [d[4] for d in data]

# --- 인덱스 분류 ---
left_idx    = [i for i, s in enumerate(statuses) if 'LEFT'    in s and 'OBSTACLE' in s]
right_idx   = [i for i, s in enumerate(statuses) if 'RIGHT'   in s and 'OBSTACLE' in s]
reverse_idx = [i for i, s in enumerate(statuses) if 'REVERSE' in s]

total_time = times[-1] - times[0]

# --- 그래프 ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
fig.suptitle(
    f'RC카 주행 데이터  |  총 주행 {total_time:.1f}초  |  장애물 {len(left_idx)+len(right_idx)+len(reverse_idx)}회'
    f'  (좌회전 {len(left_idx)}  우회전 {len(right_idx)}  후진 {len(reverse_idx)})',
    fontsize=12, fontweight='bold'
)

# (1) 전방 센서 — 점
ax1.scatter(times, distFs, color='crimson', s=8, alpha=0.6, label='전방', zorder=2)
ax1.axhline(y=20, color='crimson', linestyle='--', alpha=0.4, label='정지 기준 (20cm)')
ax1.scatter([times[i] for i in left_idx],    [distFs[i] for i in left_idx],
            color='royalblue',  s=12, zorder=5, marker='o', label=f'좌회전 ({len(left_idx)})')
ax1.scatter([times[i] for i in right_idx],   [distFs[i] for i in right_idx],
            color='seagreen',   s=12, zorder=5, marker='o', label=f'우회전 ({len(right_idx)})')
ax1.scatter([times[i] for i in reverse_idx], [distFs[i] for i in reverse_idx],
            color='darkorange', s=12, zorder=5, marker='o', label=f'후진 ({len(reverse_idx)})')
ax1.set_ylabel('거리 (cm)')
ax1.set_title('전방 센서')
ax1.legend(loc='upper right', fontsize=8)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 105)

# (2) 좌우 센서 — 점
ax2.scatter(times, distLs, color='royalblue', s=8, alpha=0.7, label='왼쪽')
ax2.scatter(times, distRs, color='seagreen',  s=8, alpha=0.7, label='오른쪽')
ax2.axhline(y=15, color='orange', linestyle='--', alpha=0.5, label='측면 경고 (15cm)')
ax2.scatter([times[i] for i in left_idx],    [distLs[i] for i in left_idx],
            color='royalblue',  s=12, zorder=5, marker='o')
ax2.scatter([times[i] for i in right_idx],   [distRs[i] for i in right_idx],
            color='seagreen',   s=12, zorder=5, marker='o')
ax2.scatter([times[i] for i in reverse_idx], [distLs[i] for i in reverse_idx],
            color='darkorange', s=12, zorder=5, marker='o')
ax2.set_xlabel('시간 (초)')
ax2.set_ylabel('거리 (cm)')
ax2.set_title('좌우 센서')
ax2.legend(loc='upper right', fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 105)

plt.tight_layout()
plt.savefig(GRAPH_FILENAME, dpi=150, bbox_inches='tight')
print(f"저장: {GRAPH_FILENAME}")
plt.show()
