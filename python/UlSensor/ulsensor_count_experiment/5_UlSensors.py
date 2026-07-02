import serial
import csv
import time
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams["font.family"] = "Malgun Gothic"
matplotlib.rcParams["axes.unicode_minus"] = False

# 설정
PORT          = 'COM(포트번호변경)'  # 블루투스 포트. (포트번호변경) 자리에 숫자 넣기
BAUD_RATE     = 9600
MAX_OBSTACLES = 30 #장애물 30번 감지하면 자동 종료
CSV_FILENAME  = '(파일명 변경).csv'    # 파일명 설정
GRAPH_FILENAME = '(파일명 변경).png'  # 그래프명 설정

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
print(f"시간    | 전면   | 대각L  | 대각R  | 측면L  | 측면R  | 상태")
print("-" * 65)

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
        if len(parts) != 7:
            continue
        try:
            t      = int(parts[0]) / 1000
            distF  = float(parts[1])
            distL  = float(parts[2])
            distR  = float(parts[3])
            distSL = float(parts[4])
            distSR = float(parts[5])
            status = parts[6].strip()

            if "OBSTACLE" in status or "REVERSE" in status:
                obstacle_count += 1

            data.append([t, distF, distL, distR, distSL, distSR, status, obstacle_count])

            print(f"{t:>6.1f}s | {distF:>6.1f} | {distL:>6.1f} | {distR:>6.1f} | {distSL:>6.1f} | {distSR:>6.1f} | {status}")

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

# CSV 저장
with open(CSV_FILENAME, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "distF", "distL", "distR", "distSL", "distSR", "status", "obstacle_count"])
    writer.writerows(data)
print(f"[저장] {CSV_FILENAME}  ({len(data)}행)")

# 데이터 분리
times    = [d[0] for d in data]
distFs   = [d[1] for d in data]
distLs   = [d[2] for d in data]
distRs   = [d[3] for d in data]
distSLs  = [d[4] for d in data]
distSRs  = [d[5] for d in data]
statuses = [d[6] for d in data]

# 상태별 인덱스 분류
left_idx    = [i for i, s in enumerate(statuses) if "LEFT"    in s and "OBSTACLE" in s]
right_idx   = [i for i, s in enumerate(statuses) if "RIGHT"   in s and "OBSTACLE" in s]
reverse_idx = [i for i, s in enumerate(statuses) if "REVERSE" in s]
adj_r_idx   = [i for i, s in enumerate(statuses) if s == "ADJUST_RIGHT"]
adj_l_idx   = [i for i, s in enumerate(statuses) if s == "ADJUST_LEFT"]
total_time  = times[-1] - times[0]

print(f"총 시간: {total_time:.1f}초 | DRIVING: {sum(1 for s in statuses if s=='DRIVING')}회 | 장애물: {obstacle_count}회")
print(f"ADJUST_RIGHT: {len(adj_r_idx)}회 | ADJUST_LEFT: {len(adj_l_idx)}회")

# 회피/보정 시점 마커 함수
def plot_obstacle_markers(ax, y_vals):
    if left_idx:
        ax.scatter([times[i] for i in left_idx],    [y_vals[i] for i in left_idx],
                   color="royalblue",  s=12, zorder=5, marker="o")
    if right_idx:
        ax.scatter([times[i] for i in right_idx],   [y_vals[i] for i in right_idx],
                   color="seagreen",   s=12, zorder=5, marker="o")
    if reverse_idx:
        ax.scatter([times[i] for i in reverse_idx], [y_vals[i] for i in reverse_idx],
                   color="darkorange", s=12, zorder=5, marker="o")

# 그래프 (3개 서브플롯)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
fig.suptitle(
    f"RC카 5센서 주행  |  {total_time:.1f}초  |  장애물 {obstacle_count}회"
    f"  (좌{len(left_idx)} 우{len(right_idx)} 후{len(reverse_idx)})"
    f"  |  보정 R:{len(adj_r_idx)} L:{len(adj_l_idx)}",
    fontsize=11, fontweight="bold"
)

# (1) 전면
ax1.scatter(times, distFs, color="crimson", s=8, alpha=0.6, label="전면(F)")
ax1.axhline(y=20, color="crimson",    linestyle="--", alpha=0.4, label="정지 기준(20cm)")
ax1.scatter([times[i] for i in left_idx],    [distFs[i] for i in left_idx],
            color="royalblue",  s=12, zorder=5, marker="o", label=f"좌회피({len(left_idx)})")
ax1.scatter([times[i] for i in right_idx],   [distFs[i] for i in right_idx],
            color="seagreen",   s=12, zorder=5, marker="o", label=f"우회피({len(right_idx)})")
ax1.scatter([times[i] for i in reverse_idx], [distFs[i] for i in reverse_idx],
            color="darkorange", s=12, zorder=5, marker="o", label=f"후진({len(reverse_idx)})")
ax1.set_ylabel("거리 (cm)")
ax1.set_title("전면 거리")
ax1.legend(loc="upper right", fontsize=8)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 105)

# (2) 측면
ax2.scatter(times, distSLs, color="royalblue", s=8, alpha=0.7, label="순수 왼쪽(SL)")
ax2.scatter(times, distSRs, color="seagreen",  s=8, alpha=0.7, label="순수 오른쪽(SR)")
ax2.axhline(y=15, color="orange", linestyle="--", alpha=0.5, label="측면 보정(15cm)")
plot_obstacle_markers(ax2, distSLs)
ax2.scatter([times[i] for i in adj_r_idx], [distSLs[i] for i in adj_r_idx],
            color="violet", s=10, zorder=4, marker="^", label=f"ADJUST_RIGHT({len(adj_r_idx)})")
ax2.scatter([times[i] for i in adj_l_idx], [distSLs[i] for i in adj_l_idx],
            color="gold",   s=10, zorder=4, marker="^", label=f"ADJUST_LEFT({len(adj_l_idx)})")
ax2.set_ylabel("거리 (cm)")
ax2.set_title("순수 좌우 센서")
ax2.legend(loc="upper right", fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 105)

# (3) 대각선
ax3.scatter(times, distLs, color="steelblue",      s=8, alpha=0.6, label="좌-전 대각(L)")
ax3.scatter(times, distRs, color="mediumseagreen", s=8, alpha=0.6, label="우-전 대각(R)")
ax3.axhline(y=15, color="steelblue", linestyle="--", alpha=0.4, label="대각 경고(15cm)")
plot_obstacle_markers(ax3, distLs)
ax3.set_xlabel("시간 (초)")
ax3.set_ylabel("거리 (cm)")
ax3.set_title("대각선 거리")
ax3.legend(loc="upper right", fontsize=8)
ax3.grid(True, alpha=0.3)
ax3.set_ylim(0, 105)

plt.tight_layout()
plt.savefig(GRAPH_FILENAME, dpi=150, bbox_inches="tight")
print(f"[저장] {GRAPH_FILENAME}")
plt.show()
