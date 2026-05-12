# 🚀 DevOps Demo — Prometheus & Grafana Sınıf Sunumu

Bu proje, **Prometheus** ve **Grafana**'nın temel özelliklerini canlı olarak göstermek için hazırlanmış bir sunum demo'sudur.

---

## 🏃 Hızlı Başlangıç

```bash
# 1. Projeyi başlat
docker-compose up --build -d

# 2. Servislerin hazır olmasını bekle (yaklaşık 30 saniye)
docker-compose ps

# 3. Trafik üretecini başlat (yeni terminal)
pip install requests
python load_generator.py
```

| Servis | URL | Giriş |
|---|---|---|
| 🌐 Flask Uygulaması | http://localhost:5000 | — |
| 📊 Prometheus | http://localhost:9090 | — |
| 📈 Grafana | http://localhost:3000 | efelikk / Efe!iKK2oo3? |
| 🐳 Portainer | https://localhost:9443 | — |

---

## 📖 Sunum Akışı (Adım Adım)

### 1️⃣ Prometheus Nedir? (5 dk)

> **Açıklama:** Prometheus, zamana dayalı (time-series) metrik toplayan açık kaynak bir izleme sistemidir. Uygulamalar `/metrics` endpoint'i aracılığıyla veri sunar, Prometheus bu endpoint'i belirli aralıklarla çeker (pull model).

**Gösterilecekler:**
- http://localhost:9090 → **Status > Targets** — flask-demo-app **UP** görünmeli
- http://localhost:5000/metrics — Ham Prometheus metrik formatı
- Prometheus'da **Graph** sekmesi → `http_requests_total` yazıp çalıştır

---

### 2️⃣ 4 Metrik Tipi (8 dk)

#### 🔢 Counter — Sadece Artar
```promql
# Toplam istek sayısı
http_requests_total

# Son 1 dakikadaki istek hızı (req/s)
rate(http_requests_total[1m])

# Son 5 dakikadaki artış
increase(http_requests_total[5m])
```

#### 📊 Gauge — Artabilir ve Azalabilir
```promql
# Anlık CPU kullanımı
app_cpu_usage_percent

# Anlık aktif kullanıcı sayısı
active_users

# Sepetteki ürün sayısı
shop_items_in_cart
```

#### 📐 Histogram — Dağılım Analizi
```promql
# P95 yanıt süresi (en yavaş %5'i dışla)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# P50 (medyan)
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))
```

#### 📏 Summary — Quantile Özeti
```promql
# İstek işleme süresi özeti
request_processing_seconds_sum / request_processing_seconds_count
```

---

### 3️⃣ PromQL Sorgu Örnekleri (5 dk)

```promql
# Hata oranı (%)
100 * sum(rate(http_errors_total[5m])) / sum(rate(http_requests_total[5m]))

# Endpoint başına ortalama yanıt süresi
rate(http_request_duration_seconds_sum[1m]) / rate(http_request_duration_seconds_count[1m])

# Aktif kullanıcı var mı? (Boole mantığı)
active_users > 10

# En yavaş endpoint hangisi?
topk(3, rate(http_request_duration_seconds_sum[5m]))
```

---

### 4️⃣ Grafana Dashboard (5 dk)

1. http://localhost:3000 → 
2. Dashboard otomatik yüklü gelir: **"🚀 DevOps Demo — Prometheus & Grafana Sunumu"**
3. Panelleri göster:
   - **Gauge paneller** — CPU, RAM, aktif kullanıcı anlık durum
   - **Time series** — İstek hızı, yanıt süresi trendi
   - **Stat paneller** — Hata sayısı, sipariş durumu

---

### 5️⃣ Canlı Senaryo Demoları (7 dk)

#### Senaryo A: Normal Trafik
```bash
python load_generator.py
```
→ Grafana'da istek hızı ve CPU grafiklerinin canlı değişimini izle

#### Senaryo B: Yük Artışı (Traffic Spike)
```bash
python load_generator.py --spike
```
→ Grafana'da dramatik yükseliş ve normalleşme grafiğini göster

#### Senaryo C: Hata Fırtınası
```bash
python load_generator.py --error
```
→ Hata oranı panelinin renk değiştirmesini (yeşil → sarı → kırmızı) göster

---

### 6️⃣ Alerting Kuralları (3 dk)

Prometheus → **Alerts** sekmesi:
- `HighErrorRate` — Saniyede 0.5'ten fazla hata
- `SlowResponseTime` — P95 yanıt süresi > 1 saniye
- `HighCPUUsage` — CPU > %80
- `HighUserLoad` — Aktif kullanıcı > 90

```bash
# /error endpoint'ini hızla çağırarak alerti tetikle
python load_generator.py --error
# Sonra Prometheus → Alerts → HighErrorRate: FIRING görmelisin
```

---

## 🛑 Durdurma

```bash
docker-compose down
# Verilerle birlikte tamamen temizle:
docker-compose down -v
```

---

## 🏗️ Proje Yapısı

```
DevOps_cicd_demo/
├── app.py                          # Flask uygulaması (4 metrik tipi)
├── Dockerfile                      # Python container tanımı
├── docker-compose.yml              # Tüm servisler
├── prometheus.yml                  # Prometheus konfigürasyonu
├── load_generator.py               # Trafik üreteci
├── alerts/
│   └── rules.yml                   # Alerting kuralları
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── prometheus.yml      # Otomatik Prometheus bağlantısı
    │   └── dashboards/
    │       └── dashboard.yml       # Otomatik dashboard yükleme
    └── dashboards/
        └── demo_dashboard.json     # Hazır sunum dashboard'u
```

---

*Hazırlayan: DevOps Demo Projesi — Sınıf Sunumu için özelleştirilmiştir.*
