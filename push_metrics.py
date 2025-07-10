import subprocess
import re
import socket
import time
import psutil
import requests
import os
import logging
from dotenv import load_dotenv


load_dotenv()

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("push_metrics.log", mode='a'),
        logging.StreamHandler()
    ]
)


PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")
JOB_NAME = "system_metrics"
HOSTNAME = socket.gethostname()


def collect_metrics():
    metrics = []

    # === Deklaracje typów ===
    metric_types = {
        "gauge": [
            "gpu_utilization", "gpu_memory_used", "gpu_memory_total", "gpu_memory_free",
            "gpu_temperature", "gpu_power_watts", "gpu_power_limit_watts", "cpu_temperature",
            "cpu_usage_percent", "cpu_load_average_1m", "cpu_load_average_5m", "cpu_load_average_15m",
            "cpu_count_logical", "cpu_count_physical", "cpu_context_switches", "cpu_interrupts",
            "memory_total_bytes", "memory_used_bytes", "memory_free_bytes", "memory_available_bytes",
            "memory_percent", "swap_total_bytes", "swap_used_bytes", "swap_percent",
            "disk_used_bytes", "disk_total_bytes", "disk_free_bytes", "disk_usage_percent",
            "process_count_total", "process_threads_total"
        ],
        "counter": [
            "disk_io_read_bytes_total", "disk_io_write_bytes_total",
            "net_io_sent_bytes_total", "net_io_recv_bytes_total"
        ]
    }

    added_types = set()
    for mtype, names in metric_types.items():
        for name in names:
            if name not in added_types:
                metrics.append(f"# TYPE {name} {mtype}")
                added_types.add(name)

    # === CPU ===
    metrics.append(f"cpu_usage_percent {psutil.cpu_percent(interval=1)}")
    if hasattr(os, "getloadavg"):
        load1, load5, load15 = os.getloadavg()
        metrics.extend([
            f"cpu_load_average_1m {load1}",
            f"cpu_load_average_5m {load5}",
            f"cpu_load_average_15m {load15}"
        ])
    metrics.append(f"cpu_count_logical {psutil.cpu_count(logical=True)}")
    metrics.append(f"cpu_count_physical {psutil.cpu_count(logical=False)}")

    cpu_stats = psutil.cpu_stats()
    metrics.append(f"cpu_context_switches {cpu_stats.ctx_switches}")
    metrics.append(f"cpu_interrupts {cpu_stats.interrupts}")

    # === Pamięć ===
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    metrics.extend([
        f"memory_total_bytes {mem.total}",
        f"memory_used_bytes {mem.used}",
        f"memory_free_bytes {mem.free}",
        f"memory_available_bytes {mem.available}",
        f"memory_percent {mem.percent}",
        f"swap_total_bytes {swap.total}",
        f"swap_used_bytes {swap.used}",
        f"swap_percent {swap.percent}"
    ])

    # === Dysk ===
    disk = psutil.disk_usage('/')
    metrics.extend([
        f"disk_used_bytes {disk.used}",
        f"disk_total_bytes {disk.total}",
        f"disk_free_bytes {disk.free}",
        f"disk_usage_percent {disk.percent}"
    ])
    io = psutil.disk_io_counters()
    if io:
        metrics.append(f"disk_io_read_bytes_total {io.read_bytes}")
        metrics.append(f"disk_io_write_bytes_total {io.write_bytes}")
    try:
        output = subprocess.check_output(['lsblk', '-b', '-dn', '-o', 'SIZE']).decode()
        total_physical_disk_bytes = sum(int(line.strip()) for line in output.strip().splitlines())
        metrics.append(f"# HELP physical_disk_total_bytes Total physical disk capacity (including unallocated)")
        metrics.append(f"# TYPE physical_disk_total_bytes gauge")
        metrics.append(
            f"physical_disk_total_bytes{{job=\"{JOB_NAME}\",instance=\"{HOSTNAME}\"}} {total_physical_disk_bytes}")
    except Exception as e:
        logging.warning(f"Failed to get physical disk size: {e}")

    # === Sieć ===
    net = psutil.net_io_counters()
    if net:
        metrics.append(f"net_io_sent_bytes_total {net.bytes_sent}")
        metrics.append(f"net_io_recv_bytes_total {net.bytes_recv}")

    # === Procesy ===
    metrics.append(f"process_count_total {len(psutil.pids())}")
    total_threads = 0
    for p in psutil.process_iter():
        try:
            total_threads += p.num_threads()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    metrics.append(f"process_threads_total {total_threads}")

    try:
        for proc in psutil.process_iter():
            try:
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        time.sleep(1)

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                cpu = proc.cpu_percent(interval=None)
                if cpu > 5.0:
                    name = proc.info['name'].replace(' ', '_').replace('-', '_')
                    pid = proc.info['pid']
                    metrics.append(
                        f'process_cpu_usage_percent{{pid="{pid}",name="{name}",job="{JOB_NAME}",instance="{HOSTNAME}"}} {cpu:.2f}')
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logging.warning(f"Process CPU usage error: {e}")

    # === GPU (NVIDIA) ===
    try:
        output = subprocess.check_output([
            'nvidia-smi',
            '--query-gpu=utilization.gpu,memory.used,memory.total,memory.free,power.draw,power.limit,temperature.gpu',
            '--format=csv,noheader,nounits'
        ]).decode('utf-8')
        for idx, line in enumerate(output.strip().split('\n')):
            util, mem_used, mem_total, mem_free, power_draw, power_limit, temp = map(float, line.split(', '))
            metrics.extend([
                f'gpu_utilization{{gpu="{idx}"}} {util}',
                f'gpu_memory_used{{gpu="{idx}"}} {mem_used}',
                f'gpu_memory_total{{gpu="{idx}"}} {mem_total}',
                f'gpu_memory_free{{gpu="{idx}"}} {mem_free}',
                f'gpu_power_watts{{gpu="{idx}"}} {power_draw}',
                f'gpu_power_limit_watts{{gpu="{idx}"}} {power_limit}',
                f'gpu_temperature{{gpu="{idx}"}} {temp}'
            ])
    except:
        pass

    try:
        output = subprocess.check_output(["nvidia-smi"], stderr=subprocess.STDOUT).decode()
        match = re.search(r"Driver Version:\s+(\S+)", output)
        if match:
            driver_version = match.group(1)
            metrics.append(f'# HELP nvidia_driver_version_numeric NVIDIA driver version as numeric value')
            metrics.append(f'# TYPE nvidia_driver_version_numeric gauge')
            metrics.append(
                f'nvidia_driver_version_numeric{{job="{JOB_NAME}",instance="{HOSTNAME}"}} {driver_version}')
    except Exception as e:
        logging.warning(f"Failed to convert NVIDIA driver version to numeric: {e}")

    # === CPU temperature ===
    try:
        output = subprocess.check_output(['sensors'], stderr=subprocess.STDOUT).decode('utf-8')
        for line in output.splitlines():
            if re.search(r'(Core\s+\d+|Package id|Tctl|Tdie)', line):
                match = re.search(r'\+?(\d+\.\d+)', line)
                if match:
                    temp = float(match.group(1))
                    metrics.append(f"cpu_temperature{{sensor=\"{line.strip().split(':')[0]}\"}} {temp}")
    except Exception as e:
        logging.warning(f"CPU temperature read error: {e}")

    # === Ubuntu version ===
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("VERSION_ID="):
                    raw_version = line.strip().split("=")[1].strip('"')
                    break

        version_float = float(raw_version)
        metrics.append(f'# HELP system_os_version_numeric OS version as numeric value')
        metrics.append(f'# TYPE system_os_version_numeric gauge')
        metrics.append(f'system_os_version_numeric{{job="{JOB_NAME}",instance="{HOSTNAME}"}} {version_float}')
    except Exception as e:
        logging.warning(f"OS version numeric parse error: {e}")

    # === Heartbeat ===
    metrics.append(f'heartbeat_timestamp{{job="{JOB_NAME}",instance="{HOSTNAME}"}} {int(time.time())}')
    metrics.append(f'up{{job="{JOB_NAME}",instance="{HOSTNAME}"}} 1')

    return "\n".join(metrics) + "\n"

def push_to_pushgateway(metrics: str):
    url = f"{PUSHGATEWAY_URL}/metrics/job/{JOB_NAME}/instance/{HOSTNAME}"
    headers = {"Content-Type": "text/plain"}
    try:
        response = requests.post(url, data=metrics, headers=headers)
        if response.status_code == 200:
            logging.info("Pushed metrics - Status: Accepted")
        else:
            logging.warning(f"Pushed metrics - Status: {response.status_code}")
            logging.warning(f"Response: {response.text}")
    except Exception as e:
        logging.error(f"Push error: {e}")


if __name__ == "__main__":
    while True:
        m = collect_metrics()
        push_to_pushgateway(m)
        time.sleep(10)
