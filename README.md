# Instalacja
## 1. Zależności
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
Description=Push Metrics
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Metrics
ExecStart=/home/ubuntu/Metrics/venv/bin/python /home/ubuntu/Metrics/push_metrics.py
Restart=always

[Install]
WantedBy=multi-user.target

## 3. Uruchamianie usługi 
`sudo systemctl daemon-reexec`

`sudo systemctl enable push-metrics`

`sudo systemctl start push-metrics`



# Aktualizacja
`cd Metrics`

`git pull orign master`

`pip install -r requirements.txt`

`sudo systemctl restart push-metrics`

# Typy metryk

## gauge - metryki o zmiennych wartościach w czasie

| Nazwa                        | Opis                                                                |
|------------------------------|---------------------------------------------------------------------|
| `gpu_utilization`            | Aktualne użycie GPU (%)                                             |
| `gpu_memory_used`            | Ilość użytej pamięci GPU (MB)                                       |
| `gpu_memory_total`           | Całkowita dostępna pamięć GPU (MB)                                  |
| `gpu_memory_free`            | Dostępna (wolna) pamięć GPU (MB)                                    |
| `gpu_temperature`            | Temperatura GPU (°C)                                                |
| `gpu_power_watts`            | Aktualne zużycie energii przez GPU (W)                              |
| `gpu_power_limit_watts`      | Limit poboru mocy dla GPU (W)                                       |
| `cpu_temperature`            | Temperatura CPU (°C)                                                |
| `cpu_usage_percent`          | Całkowite użycie CPU (%)                                            |
| `cpu_load_average_1m`        | Średnie obciążenie CPU z ostatniej 1 minuty                         |
| `cpu_load_average_5m`        | Średnie obciążenie CPU z ostatnich 5 minut                          |
| `cpu_load_average_15m`       | Średnie obciążenie CPU z ostatnich 15 minut                         |
| `cpu_count_logical`          | Liczba logicznych rdzeni CPU                                        |
| `cpu_count_physical`         | Liczba fizycznych rdzeni CPU                                        |
| `cpu_context_switches`       | Liczba przełączeń kontekstu CPU                                     |
| `cpu_interrupts`             | Liczba przerwań obsłużonych przez CPU                               |
| `memory_total_bytes`         | Całkowita dostępna pamięć RAM (bajty)                               |
| `memory_used_bytes`          | Ilość aktualnie użytej pamięci RAM (bajty)                          |
| `memory_free_bytes`          | Ilość wolnej pamięci RAM (bajty)                                    |
| `memory_available_bytes`     | Ilość dostępnej pamięci RAM dla nowych procesów (bajty)             |
| `memory_percent`             | Użycie pamięci RAM (%)                                              |
| `swap_total_bytes`           | Całkowita dostępna przestrzeń swap (bajty)                          |
| `swap_used_bytes`            | Używana przestrzeń swap (bajty)                                     |
| `swap_percent`               | Procent użycia swap (%)                                             |
| `disk_used_bytes`            | Ilość zajętego miejsca na dyskach (bajty)                           |
| `disk_total_bytes`           | Całkowita przestrzeń dyskowa (bajty)                                |
| `disk_free_bytes`            | Wolna przestrzeń dyskowa (bajty)                                    |
| `disk_usage_percent`         | Procent użycia przestrzeni dyskowej                                 |
| `process_count_total`        | Liczba aktualnie działających procesów                              |
| `process_threads_total`      | Suma aktywnych wątków wszystkich procesów                           |
|`process_cpu_usage_percent`   | Użycie CPU przez konkretny proces (>5%)                             |
|`nvidia_driver_version_string`|	Wersja sterownika NVIDIA                                           |
|`system_os_version_string`	   | Wersja systemu operacyjnego                                         |
|`heartbeat_timestamp`	       | Znacznik czasu ostatniego wysłania metryk                           |
|`up`	                         | Wartość 1 oznaczająca, że skrypt działa poprawnie                   |

---

## counter - metryki monotoniczne (rosnące)

| Nazwa                        | Opis                                                                |
|------------------------------|---------------------------------------------------------------------|
| `disk_io_read_bytes_total`   | Całkowita liczba bajtów odczytanych z dysków                        |
| `disk_io_write_bytes_total`  | Całkowita liczba bajtów zapisanych na dyskach                       |
| `net_io_sent_bytes_total`    | Całkowita liczba bajtów wysłanych przez interfejsy sieciowe         |
| `net_io_recv_bytes_total`    | Całkowita liczba bajtów odebranych przez interfejsy sieciowe        |


