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

---

## counter - metryki monotoniczne (rosnące)

| Nazwa                        | Opis                                                                |
|------------------------------|---------------------------------------------------------------------|
| `disk_io_read_bytes_total`   | Całkowita liczba bajtów odczytanych z dysków                        |
| `disk_io_write_bytes_total`  | Całkowita liczba bajtów zapisanych na dyskach                       |
| `net_io_sent_bytes_total`    | Całkowita liczba bajtów wysłanych przez interfejsy sieciowe         |
| `net_io_recv_bytes_total`    | Całkowita liczba bajtów odebranych przez interfejsy sieciowe        |

