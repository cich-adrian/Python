# Ping Simulator in JunOS Style

## Opis projektu
Symulator komendy `ping` inspirowany JunOS, napisany w Pythonie, umożliwia diagnostykę sieci za pomocą protokołu ICMP. Narzędzie obsługuje podstawowe parametry, takie jak liczba pakietów, rozmiar danych czy czas oczekiwania na odpowiedź. Projekt działa w środowisku Linux i wykorzystuje surowe gniazda ICMP. Szczegółowa dokumentacja znajduje się w załącznikach.

## Funkcjonalności
- **Wysyłanie pakietów ICMP** z parametrami:
  - Liczba pakietów (`--count`), domyślnie 5.
  - Rozmiar pakietu (`--size`), domyślnie 64 B.
  - Interwał między pakietami (`--wait`), domyślnie 1 sekunda.
- **Statystyki połączeń**:
  - Liczba wysłanych/odebranych pakietów.
  - RTT (min, avg, max).
  - Procent utraconych pakietów.
- Obsługa przerwań (`CTRL+C`) oraz timeoutów.
- Tryb szybkiego wysyłania pakietów (`--rapid`).

## Wymagania
- Python 3.x
- Uprawnienia administratora (root) w systemie Linux.

## Instalacja i uruchomienie
1. **Kopiowanie skryptu** na system Linux:
   ```bash
   scp ping_simulator.py user@linux_host:/home/user/ping/
2. **Ustawienie uprawnień do wykonania**:
    ```bash
    chmod +x ping_simulator.py
3. **Uruchomienie skryptu (przykład)**:
    ```bash
    sudo ./ping_simulator.py 8.8.8.8 --count 5 --size 128
