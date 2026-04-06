import serial
import csv
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

PORT = 'COM(포트번호변경)'  # 블루투스 포트. (포트번호변경) 자리에 숫자 넣기
BAUD_RATE = 9600
CSV_FILE = '(파일명 변경).csv'    # 파일명 설정
GRAPH_FILE = '(파일명 변경).png'  # 그래프명 설정
data = []

try:
    py_serial = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"Connected! Port: {PORT}")
except Exception as e:
    print(f"Connection error: {e}")
    exit()

input("Press Enter to start RC car...")
py_serial.write(b'S')
print("Started! Press Ctrl+C to stop")

try:
    while True:
        line = py_serial.readline().decode('utf-8', errors='ignore').strip()
        if ',' in line:
            parts = line.split(',')
            if len(parts) == 6:
                t = int(parts[0]) / 1000
                dist = parts[1]
                distLeft = parts[2]
                distRight = parts[3]
                direction = parts[4]
                status = parts[5]
                data.append([t, dist, distLeft, distRight, direction, status])
                print(f"Time:{t:.1f}s | Front:{dist}cm | Left:{distLeft}cm Right:{distRight}cm | Dir:{direction} | {status}")

except KeyboardInterrupt:
    print("\nDone!")
finally:
    py_serial.close()

if not data:
    print("No data!")
    exit()

with open(CSV_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['time', 'dist', 'distLeft', 'distRight', 'direction', 'status'])
    writer.writerows(data)
print(f"Saved to {CSV_FILE}")

times = [float(d[0]) for d in data]
distances = [float(d[1]) if d[1] != '-1' else None for d in data]
statuses = [d[5] for d in data]

colors = {'DRIVING': 'blue', 'OBSTACLE': 'red'}
color_list = [colors.get(s.strip(), 'gray') for s in statuses]

fig, axes = plt.subplots(2, 1, figsize=(12, 8))

axes[0].scatter(times, distances, c=color_list, s=10)
axes[0].axhline(y=20, color='red', linestyle='--', label='Threshold (20cm)')
axes[0].set_ylabel('Distance (cm)')
axes[0].set_title('Obstacle Avoidance - Distance over Time')
axes[0].legend()
axes[0].grid(True)

status_map = {'DRIVING': 1, 'OBSTACLE': 2}
status_nums = [status_map.get(d[5].strip(), 0) for d in data]
axes[1].scatter(times, status_nums, c=color_list, s=10)
axes[1].set_yticks([1, 2])
axes[1].set_yticklabels(['DRIVING', 'OBSTACLE'])
axes[1].set_xlabel('Time (s)')
axes[1].set_title('Obstacle Avoidance - Status over Time')
axes[1].grid(True)

patches = [mpatches.Patch(color=v, label=k) for k, v in colors.items()]
axes[1].legend(handles=patches)

plt.tight_layout()
plt.savefig(GRAPH_FILE, dpi=150)
print(f"Saved to {GRAPH_FILE}")
plt.show()