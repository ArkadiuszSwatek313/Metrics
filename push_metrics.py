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

    for mtype, names in metric_types.items():
        for name in names:
            metrics.append(f"# TYPE {name} {mtype}")

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

    # === Sieć ===
    net = psutil.net_io_counters()
    if net:
        metrics.append(f"net_io_sent_bytes_total {net.bytes_sent}")
        metrics.append(f"net_io_recv_bytes_total {net.bytes_recv}")

    # === Procesy ===
    metrics.append(f"process_count_total {len(psutil.pids())}")
    metrics.append(f"process_threads_total {sum(p.num_threads() for p in psutil.process_iter())}")

    # === GPU (NVIDIA) ===
    try:
        output = subprocess.check_output([
            'nvidia-smi',
            '--query-gpu=utilization.gpu,memory.used,memory.total,memory.free,power.draw,power.limit,temperature.gpu',
            '--format=csv,noheader,nounits'
        ]).decode('utf-8')
        for line in output.strip().split('\n'):
            util, mem_used, mem_total, mem_free, power_draw, power_limit, temp = map(float, line.split(', '))
            metrics.extend([
                f"gpu_utilization {util}",
                f"gpu_memory_used {mem_used}",
                f"gpu_memory_total {mem_total}",
                f"gpu_memory_free {mem_free}",
                f"gpu_power_watts {power_draw}",
                f"gpu_power_limit_watts {power_limit}",
                f"gpu_temperature {temp}"
            ])
    except:
        pass

    # === CPU temperature (Linux) ===
    try:
        output = subprocess.check_output(['sensors']).decode('utf-8')
        for line in output.splitlines():
            if "Core 0" in line or "Package id" in line:
                match = re.search(r'\+?(\d+\.\d+)', line)
                if match:
                    metrics.append(f"cpu_temperature {float(match.group(1))}")
                    break
    except:
        pass

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
