# Instalacja
## 1. Instalacja zależności
`sudo apt install -y python3 python3-venv git lm-sensors`

## 2. Klonowanie repozytorium
`git clone https://github.com/ArkadiuszSwatek313/Metrics.git`

`cd Metrics`

## 3. Środowisko wirtualne
`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

## 4. Konfiguracja adresu Pushgateway
`echo 'PUSHGATEWAY_URL=http://xxx.xxx.xxx.xxx:9091' > .env`

## 5. Uruchomienie
`python push_metrics.py`

# Autostart
## 1. Tworzenie pliku
`sudo nano /etc/systemd/system/push-metrics.service`

## 2. Zawartość pliku
[Unit]

Description=Push Metrics for %i

After=network.target


[Service]

Type=simple

User=%i

WorkingDirectory=/home/%i/Metrics

ExecStart=/home/%i/Metrics/venv/bin/python /home/%i/Metrics/push_metrics.py

Restart=always



[Install]

WantedBy=multi-user.target

## 3. Uruchamianie usługi 
`sudo systemctl daemon-reexec`

`sudo systemctl enable push-metrics@$(whoami)`

`sudo systemctl start push-metrics@$(whoami)`

# Aktualizacja
`cd Metrics`

`git pull origin master`

`pip install -r requirements.txt`

`sudo systemctl restart push-metrics@$(whoami)`

# Typy metryk

## CPU
| Metryka                         | Opis                                                 |
|---------------------------------|------------------------------------------------------|
|`cpu_usage_percent` | aktualne użycie CPU (wszystkich rdzeni) w procentach |
|`cpu_load_average_1m` |średnie obciążenie systemu z ostatniej 1 minuty |
|`cpu_load_average_5m` | średnie obciążenie systemu z ostatnich 5 minut |
|`cpu_load_average_15m` | średnie obciążenie systemu z ostatnich 15 minut|
|`cpu_count_logical` | liczba logicznych rdzeni CPU |
|`cpu_count_physical` | liczba fizycznych rdzeni CPU|
|`cpu_context_switches` | liczba przełączeń kontekstu CPU|
|`cpu_interrupts` | liczba przerwań CPU|
|`cpu_temperature` | temperatura CPU (z wielu czujników)|

## GPU (NVIDIA)
| Metryka                         | Opis                                                 |
|---------------------------------|------------------------------------------------------|
|`gpu_utilization` | wykorzystanie GPU w procentach|
|`gpu_memory_used` | użycie pamięci GPU|
|`gpu_memory_total` | całkowita pamięć GPU|
|`gpu_memory_free` | dostępna pamięć GPU|
|`gpu_power_watts` | aktualne zużycie energii przez GPU|
|`gpu_power_limit_watts` | limit energii dla GPU|
|`gpu_temperature` | temperatura GPU|
|`gpu_fan_speed_percent` | prędkość wentylatora GPU w procentach|
|`gpu_memory_total_sum` | suma całkowitej pamięci wszystkich GPU|
|`nvidia_driver_version_numeric` | wersja sterownika NVIDIA jako liczba|

## Pamięć RAM
| Metryka                         | Opis                                                 |
|---------------------------------|------------------------------------------------------|
|`memory_total_bytes` | całkowita pamięć RAM |
|`memory_used_bytes` | zajęta pamięć RAM |
|`memory_free_bytes` | wolna pamięć RAM |
|`memory_available_bytes` | dostępna pamięć RAM (dla aplikacji) |
|`memory_percent` | procent zajętej pamięci RAM |
|`swap_total_bytes` | całkowity rozmiar SWAP |
|`swap_used_bytes` | zużyty SWAP |
|`swap_percent` | procent użycia SWAP |

## Dysk
| Metryka                         | Opis                                                 |
|---------------------------------|------------------------------------------------------|
|`disk_used_bytes` | zajęta przestrzeń dyskowa |
|`disk_total_bytes` | całkowita przestrzeń dyskowa |
|`disk_free_bytes` | wolna przestrzeń dyskowa |
|`disk_usage_percent` | procent zużycia przestrzeni dyskowej |
|`disk_io_read_bytes_total` | łączna liczba bajtów odczytanych z dysku |
|`disk_io_write_bytes_total` | łączna liczba bajtów zapisanych na dysk |
|`physical_disk_used_bytes` | suma użytej przestrzeni na wszystkich partycjach fizycznych |


## Inne
| Metryka                         | Opis                                                 |
|---------------------------------|------------------------------------------------------|
|`net_io_sent_bytes_total` | łączna liczba wysłanych bajtów|
|`net_io_recv_bytes_total` | łączna liczba odebranych bajtów|
|`process_count_total` | liczba aktywnych procesów|
|`process_threads_total` | liczba aktywnych wątków|
|`process_cpu_usage_percent` | procent użycia CPU przez proces (jeśli > 5%)|
|`system_os_version_numeric` | wersja systemu operacyjnego (Ubuntu) jako liczba|
|`heartbeat_timestamp` | znacznik czasu ostatniego pushu (ms)|


