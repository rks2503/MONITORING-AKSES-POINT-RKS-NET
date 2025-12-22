# Monitoring Dashboard Area Cibingbin01

Dashboard untuk monitoring Access Point di Area Cibingbin01.

## Fitur
- ✅ Tampilan tabel dengan kolom: No, Nama Router, IP AP, Status, Last Update
- ✅ Auto-refresh setiap 60 detik
- ✅ Summary statistics (Total Router, AP Online, AP Offline, Uptime %)
- ✅ Notifikasi browser jika AP down
- ✅ Mobile responsive
- ✅ Real-time monitoring via GitHub Actions

## Setup

### 1. Fork Repository
Klik "Fork" di kanan atas untuk copy repository ke akun Anda.

### 2. Konfigurasi Mikrotik GR3
```bash
# Enable API
/ip service set api disabled=no port=8728

# Buat user monitoring
/user add name=monitor password=PASSWORD_ANDA group=read
# MikroTik API Tester

Script Python untuk testing koneksi ke MikroTik RouterOS API.

## 🚀 Cara Penggunaan

### Instalasi
```bash
pip install -r requirements.txt
