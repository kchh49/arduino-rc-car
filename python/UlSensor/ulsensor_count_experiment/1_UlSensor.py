import serial
import csv
import time
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# 설정
PORT           = 'COM4'
BAUD_RATE      = 9600
MAX_OBSTACLES  = 30
CSV_FILENAME   = '(파일명 변경).csv'
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
input("Enter 누르면 RC카 출발 ('S' 전송)...")
py_serial.reset_input_buffer()
py_serial.write(b'S')
py_serial.flush()
print("[시작됨] 'S' 전송 RC카 출발!\n")
print(f"{'시간':>7} | {'전면':>6} | {'서보L':>6} | {'서보R':>6} | 상태")
print("-" * 50)

no_data_count = 0

try:
    while obstacle_count < MAX_OBSTACLES:
        line = py_serial.readline().decode('utf-8', errors='ignore').strip()

        if not line:
            no_data_count += 1
            if no_data_count >= 10:
                print("\n[종료] 데이터가 더 없음")
                break
            continue

        no_data_count = 0
        if not line[0].isdigit():
            continue

        parts = line.split(',')
        if len(parts) != 6:
            continue

        try:
            t         = int(parts[0]) / 1000
            distF     = float(parts[1])
            distLeft  = float(parts[2])
            distRight = float(parts[3])
            direction = parts[4].strip()
            status    = parts[5].strip()

            if status == 'OBSTACLE':
                obstacle_count += 1

            data.append([t, distF, distLeft, distRight, direction, status, obstacle_count])
            print(f"{t:>6.1f}s | {distF:>6.1f} | {distLeft:>6.1f} | {distRight:>6.1f} | {direction},{status}")

        except ValueError:
            continue

except KeyboardInterrupt:
    print("\n[중단] Ctrl+C")

finally:
    py_serial.close()
    print("[시리얼 종료]")

if not data:
    print("[오류] 데이터 없음")
    exit()

# CSV 저장
with open(CSV_FILENAME, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['time', 'distF', 'distLeft', 'distRight', 'direction', 'status', 'obstacle_count'])
    writer.writerows(data)
print(f"\n[저장] {CSV_FILENAME}  ({len(data)}행)")

# 데이터 분리
times      = [d[0] for d in data]
distFs     = [d[1] for d in data]
distLefts  = [d[2] for d in data]
distRights = [d[3] for d in data]
statuses   = [d[5] for d in data]

left_idx  = [i for i, d in enumerate(data) if d[4] == 'LEFT'  and d[5] == 'OBSTACLE']
right_idx = [i for i, d in enumerate(data) if d[4] == 'RIGHT' and d[5] == 'OBSTACLE']
total_time = times[-1] - times[0]

print(f"총 시간: {total_time:.1f}초 | DRIVING: {sum(1 for s in statuses if s=='DRIVING')}회 | 장애물: {obstacle_count}회")

# 그래프
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
fig.suptitle(
    f'RC카 1센서(서보) 주행  |  {total_time:.1f}초  |  장애물 {obstacle_count}회'
    f'  (좌{len(left_idx)} 우{len(right_idx)})',
    fontsize=12, fontweight='bold'
)

# (1)전면 거리
ax1.scatter(times, distFs, color='crimson', s=8, alpha=0.6, label='전면(F)')
ax1.axhline(y=20, color='crimson', linestyle='--', alpha=0.4, label='정지 기준(20cm)')
ax1.scatter([times[i] for i in left_idx],  [distFs[i] for i in left_idx],
            color='royalblue', s=12, zorder=5, marker='o', label=f'좌회피({len(left_idx)})')
ax1.scatter([times[i] for i in right_idx], [distFs[i] for i in right_idx],
            color='seagreen',  s=12, zorder=5, marker='o', label=f'우회피({len(right_idx)})')
ax1.set_ylabel('거리 (cm)')
ax1.set_title('전면 거리')
ax1.legend(loc='upper right', fontsize=8)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 105)

# (2) 서보 스캔 거리 (장애물 감지 시에만)
all_idx = left_idx + right_idx

ax2.scatter([times[i] for i in all_idx], [distLefts[i]  for i in all_idx],
            color='royalblue', s=30, zorder=5, marker='o', label='서보 좌 거리')
ax2.scatter([times[i] for i in all_idx], [distRights[i] for i in all_idx],
            color='seagreen',  s=30, zorder=5, marker='o', label='서보 우 거리')
ax2.set_xlabel('시간 (초)')
ax2.set_ylabel('거리 (cm)')
ax2.set_title('서보 스캔 거리 (장애물 감지 시)')
ax2.legend(loc='upper right', fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 105)

plt.tight_layout()
plt.savefig(GRAPH_FILENAME, dpi=150, bbox_inches='tight')
print(f"[저장] {GRAPH_FILENAME}")
plt.show()
