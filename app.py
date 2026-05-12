import time
import random
import threading
from flask import Flask, Response, jsonify, request
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    generate_latest, CONTENT_TYPE_LATEST
)

app = Flask(__name__)

# ─────────────────────────────────────────────
#  PROMETHEUS METRİKLERİ
# ─────────────────────────────────────────────

# COUNTER — sadece artar, hiç azalmaz
http_requests_total = Counter(
    'http_requests_total',
    'Toplam HTTP istek sayısı',
    ['method', 'endpoint', 'status']
)

http_errors_total = Counter(
    'http_errors_total',
    'Toplam hata sayısı',
    ['endpoint']
)

# GAUGE — artabilir ve azalabilir
active_users = Gauge(
    'active_users',
    'Anlık aktif kullanıcı sayısı'
)

cpu_usage_percent = Gauge(
    'app_cpu_usage_percent',
    'Simüle edilmiş CPU kullanımı (%)'
)

memory_usage_mb = Gauge(
    'app_memory_usage_mb',
    'Simüle edilmiş bellek kullanımı (MB)'
)

items_in_cart = Gauge(
    'shop_items_in_cart',
    'Sepetteki toplam ürün sayısı'
)

# HISTOGRAM — değerleri bucket'lara koyar (latency için ideal)
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP istek yanıt süresi (saniye)',
    ['endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# SUMMARY — quantile (yüzdelik dilim) hesaplar
request_processing_summary = Summary(
    'request_processing_seconds',
    'İstek işleme süresi özeti'
)

orders_total = Counter(
    'shop_orders_total',
    'Toplam sipariş sayısı',
    ['status']  # success, failed, pending
)

# ─────────────────────────────────────────────
#  YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────

def track_request(endpoint, status_code, duration):
    """Metrik kaydeder"""
    method = request.method if request else 'GET'
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=str(status_code)
    ).inc()
    http_request_duration_seconds.labels(endpoint=endpoint).observe(duration)

# ─────────────────────────────────────────────
#  BACKGROUND THREAD — Canlı Veri Simülasyonu
# ─────────────────────────────────────────────

def simulate_system_metrics():
    """Gerçekçi sistem metriklerini sürekli günceller"""
    cpu_base = 30.0
    mem_base = 256.0
    user_base = 50
    cart_base = 120

    while True:
        # CPU: zaman içinde dalgalanır
        cpu_spike = random.choice([0, 0, 0, random.uniform(20, 40)])
        cpu_val = max(5, min(95, cpu_base + random.uniform(-5, 5) + cpu_spike))
        cpu_base = cpu_base * 0.9 + cpu_val * 0.1
        cpu_usage_percent.set(round(cpu_val, 1))

        # Bellek: yavaş yavaş artar, zaman zaman temizlenir
        mem_val = mem_base + random.uniform(-10, 15)
        if mem_val > 512:
            mem_val = 200 + random.uniform(0, 50)
        mem_base = mem_val
        memory_usage_mb.set(round(mem_val, 1))

        # Aktif kullanıcılar: gün içi yoğunluk simülasyonu
        user_val = max(0, user_base + random.randint(-8, 12))
        user_base = user_base * 0.95 + user_val * 0.05
        active_users.set(int(user_val))

        # Sepet: alışveriş aktivitesi
        cart_change = random.randint(-5, 10)
        cart_base = max(0, cart_base + cart_change)
        items_in_cart.set(cart_base)

        time.sleep(3)

# Thread'i başlat
bg_thread = threading.Thread(target=simulate_system_metrics, daemon=True)
bg_thread.start()

# ─────────────────────────────────────────────
#  ENDPOINT'LER
# ─────────────────────────────────────────────

@app.route("/")
def home():
    """Ana sayfa — temel Counter örneği"""
    start = time.time()
    time.sleep(random.uniform(0.01, 0.05))
    duration = time.time() - start

    track_request("/", 200, duration)
    request_processing_summary.observe(duration)

    return """
    <html>
    <head>
      <title>🚀 DevOps Demo — Prometheus & Grafana</title>
      <style>
        body { font-family: Arial, sans-serif; background: #0f0f23; color: #ccd6f6;
               display: flex; flex-direction: column; align-items: center;
               justify-content: center; min-height: 100vh; margin: 0; }
        h1   { color: #64ffda; font-size: 2.5rem; }
        p    { color: #8892b0; }
        .links { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; margin-top: 2rem; }
        a    { background: #112240; color: #64ffda; padding: 0.8rem 1.5rem;
               border-radius: 8px; text-decoration: none; border: 1px solid #64ffda;
               transition: all 0.3s; font-size: 0.9rem; }
        a:hover { background: #64ffda; color: #0f0f23; }
        .badge { background: #112240; border: 1px solid #233554; padding: 1rem 2rem;
                 border-radius: 12px; margin-top: 1rem; }
      </style>
    </head>
    <body>
      <h1>🚀 Prometheus & Grafana Demo</h1>
      <div class="badge">
        <p>📊 <strong>Prometheus:</strong> <a href="http://localhost:9090" target="_blank">localhost:9090</a></p>
        <p>📈 <strong>Grafana:</strong> <a href="http://localhost:3000" target="_blank">localhost:3000</a></p>
        <p>🐳 <strong>Portainer:</strong> <a href="https://localhost:9443" target="_blank">localhost:9443</a></p>
      </div>
      <div class="links">
        <a href="/buy">🛒 /buy — Satın Al (yavaş endpoint)</a>
        <a href="/api/data">📡 /api/data — API</a>
        <a href="/api/users">👥 /api/users — Kullanıcılar</a>
        <a href="/checkout">💳 /checkout — Sipariş</a>
        <a href="/error">❌ /error — Hata Üret</a>
        <a href="/metrics">🔬 /metrics — Ham Metrikler</a>
      </div>
    </body>
    </html>
    """, 200

@app.route("/buy")
def buy():
    """Yavaş endpoint — Histogram'da uzun bucket'ları görmek için"""
    start = time.time()
    # Gerçekçi bir DB/ödeme gecikmesi simülasyonu
    delay = random.uniform(0.1, 1.5)
    time.sleep(delay)
    duration = time.time() - start

    items_in_cart.inc(random.randint(1, 3))
    track_request("/buy", 200, duration)
    request_processing_summary.observe(duration)

    return jsonify({
        "status": "added_to_cart",
        "item": random.choice(["Laptop", "Telefon", "Kulaklık", "Klavye", "Mouse"]),
        "response_time_ms": round(duration * 1000, 2),
        "message": "Ürün sepete eklendi ✓"
    })

@app.route("/api/data")
def api_data():
    """Orta hızlı endpoint"""
    start = time.time()
    time.sleep(random.uniform(0.02, 0.2))
    duration = time.time() - start

    track_request("/api/data", 200, duration)

    return jsonify({
        "timestamp": time.time(),
        "active_users": int(active_users._value.get()),
        "cpu_usage": round(cpu_usage_percent._value.get(), 1),
        "memory_mb": round(memory_usage_mb._value.get(), 1),
        "items_in_cart": int(items_in_cart._value.get()),
        "response_time_ms": round(duration * 1000, 2)
    })

@app.route("/api/users")
def api_users():
    """Kullanıcı listesi endpoint'i"""
    start = time.time()
    time.sleep(random.uniform(0.01, 0.08))
    duration = time.time() - start

    track_request("/api/users", 200, duration)

    users = [
        {"id": i, "name": f"Kullanici_{i}", "online": random.choice([True, False])}
        for i in range(1, random.randint(5, 15))
    ]
    return jsonify({"users": users, "total": len(users)})

@app.route("/checkout")
def checkout():
    """Sipariş tamamlama — başarı/başarısız oranı"""
    start = time.time()
    time.sleep(random.uniform(0.2, 0.8))
    duration = time.time() - start

    # %80 başarı, %15 bekliyor, %5 hata
    outcome = random.choices(
        ['success', 'pending', 'failed'],
        weights=[80, 15, 5]
    )[0]

    orders_total.labels(status=outcome).inc()
    items_in_cart.set(max(0, items_in_cart._value.get() - random.randint(1, 5)))

    status_code = 200 if outcome != 'failed' else 500
    track_request("/checkout", status_code, duration)

    if outcome == 'failed':
        http_errors_total.labels(endpoint='/checkout').inc()

    return jsonify({
        "order_status": outcome,
        "order_id": f"ORD-{random.randint(10000, 99999)}",
        "amount": round(random.uniform(50, 2000), 2),
        "currency": "TRY"
    }), status_code

@app.route("/error")
def error():
    """Kasıtlı hata — hata metriklerini görmek için"""
    start = time.time()
    time.sleep(random.uniform(0.01, 0.1))
    duration = time.time() - start

    http_errors_total.labels(endpoint='/error').inc()
    track_request("/error", 500, duration)

    return jsonify({
        "error": "Internal Server Error",
        "message": "Bu hata kasıtlı olarak üretildi — hata metriklerini görmek için!",
        "tip": "Prometheus'da http_errors_total metriğini kontrol edin"
    }), 500

@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint'i"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": time.time()})

# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)