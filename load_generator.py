"""load_generator.py — Prometheus & Grafana Sunum Trafik Üreteci.

─────────────────────────────────────────────────────────────
Kullanım:
    python load_generator.py           # Normal mod (karma trafik)
    python load_generator.py --spike   # Yük artışı senaryosu
    python load_generator.py --error   # Hata senaryosu
"""

import requests
import time
import random
import sys
import threading

BASE_URL = "http://localhost:5000"

# Endpoint ağırlıkları (olasılık dağılımı)
NORMAL_ENDPOINTS = [
    ("/", 30),  # Ana sayfa — en çok ziyaret
    ("/api/data", 25),  # API — sık kullanılan
    ("/api/users", 20),  # Kullanıcı listesi
    ("/buy", 15),  # Sepete ekle — yavaş
    ("/checkout", 8),  # Sipariş — kritik
    ("/error", 2),  # Hata — az ama var
]


def weighted_choice(options):
    endpoints, weights = zip(*options)
    return random.choices(endpoints, weights=weights, k=1)[0]


def make_request(endpoint, session):
    try:
        resp = session.get(f"{BASE_URL}{endpoint}", timeout=5)
        status = resp.status_code
        duration_ms = resp.elapsed.total_seconds() * 1000
        status_icon = "✅" if status < 400 else "❌"
        print(f"  {status_icon} {endpoint:<15} → {status}  ({duration_ms:.0f}ms)")
    except Exception as e:
        print(f"  🔴 {endpoint:<15} → BAĞLANTI HATASI: {e}")


def normal_traffic(rps=3):
    """Generate normal karma traffic at the specified rate."""
    print(f"\n🟢 Normal trafik başlatılıyor... ({rps} req/s)")
    print("   Ctrl+C ile durdurabilirsiniz.\n")
    session = requests.Session()
    while True:
        endpoint = weighted_choice(NORMAL_ENDPOINTS)
        threading.Thread(target=make_request, args=(endpoint, session), daemon=True).start()
        time.sleep(1 / rps)


def spike_traffic():
    """Simulate spike traffic scenario."""
    print("\n⚡ YÜK ARTIŞI SENARYOSU başlatıldı!")
    print("   Prometheus ve Grafana'da ani yükselişi izleyin.\n")
    session = requests.Session()

    phases = [
        ("Düşük trafik", 10, 2, "/"),
        ("Normal trafik", 15, 5, "/api/data"),
        ("YÜK ARTIŞI 🔥", 10, 20, "/buy"),
        ("Zirve noktası", 10, 30, "/api/users"),
        ("Normalleşme", 15, 5, "/"),
    ]

    for phase_name, duration_s, rps, endpoint in phases:
        print(f"\n📍 Faz: {phase_name} — {rps} req/s, {duration_s} saniye")
        end = time.time() + duration_s
        while time.time() < end:
            threading.Thread(target=make_request, args=(endpoint, session), daemon=True).start()
            time.sleep(1 / rps)

    print("\n✅ Spike senaryosu tamamlandı!")


def error_storm():
    """Simulate error storm to increase error rate in Grafana."""
    print("\n🔴 HATA SENARYOSU başlatıldı!")
    print("   Prometheus'da http_errors_total metriğini izleyin.\n")
    session = requests.Session()

    for i in range(50):
        endpoint = random.choice(["/error", "/error", "/error", "/checkout"])
        threading.Thread(target=make_request, args=(endpoint, session), daemon=True).start()
        time.sleep(0.3)

    print("\n✅ Hata senaryosu tamamlandı!")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║   🚀 Prometheus & Grafana Sunum Trafik Üreteci   ║
║   ─────────────────────────────────────────────  ║
║   Grafana:    http://localhost:3000              ║
║   Prometheus: http://localhost:9090              ║
║   Uygulama:   http://localhost:5000              ║
╚══════════════════════════════════════════════════╝
    """)

    mode = sys.argv[1] if len(sys.argv) > 1 else "--normal"

    try:
        if mode == "--spike":
            spike_traffic()
        elif mode == "--error":
            error_storm()
        else:
            normal_traffic(rps=3)
    except KeyboardInterrupt:
        print("\n\n⏹️  Trafik üreteci durduruldu.")
