# Deployment Dashboard dengan systemd

Unit [`tuban-dashboard.service`](tuban-dashboard.service) menjalankan Streamlit di `127.0.0.1:8501`. Unit [`cloudflared-tunnel.service`](cloudflared-tunnel.service) meneruskan lalu lintas dari Cloudflare Tunnel ke alamat tersebut.

## Prasyarat

- Server Linux dengan systemd, Python 3.12+, dan `uv` tersedia saat menjalankan `sudo`.
- Untuk akses publik melalui tunnel: `cloudflared` terpasang di `/usr/bin/cloudflared`, user sistem `cloudflared` tersedia, dan rute aplikasi publik pada Cloudflare diarahkan ke `http://127.0.0.1:8501`.

## Pasang dashboard

Jalankan dari root repositori di server. Buat user sistem sekali, lalu pasang salinan repositori di `/opt/tuban-dashboard/current`:

```bash
sudo useradd --system --user-group --home /var/lib/tuban-dashboard --shell /usr/sbin/nologin tuban-dashboard
sudo install -d -o tuban-dashboard -g tuban-dashboard /opt/tuban-dashboard/current
git archive HEAD | sudo tar -x -C /opt/tuban-dashboard/current
```

Gunakan direktori `current` yang kosong. `git archive HEAD` hanya menyalin isi commit aktif, tanpa `.git` atau lingkungan virtual lokal.

```bash
sudo UV_PROJECT_ENVIRONMENT=/opt/tuban-dashboard/.venv uv sync --locked --extra dashboard \
  --project /opt/tuban-dashboard/current
sudo chown -R tuban-dashboard:tuban-dashboard /opt/tuban-dashboard
sudo install -m 0644 deploy/systemd/tuban-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tuban-dashboard.service
```

Buat virtual environment langsung di lokasi yang dipakai unit; memindahkan virtual environment dapat merusak jalur absolut pada skripnya. Setelah layanan aktif, `curl --fail http://127.0.0.1:8501/_stcore/health` seharusnya mengembalikan `ok`.

## Aktifkan Cloudflare Tunnel

Simpan token tunnel di `/etc/cloudflared/tunnel-token` dengan pemilik `cloudflared` dan mode `0600`. Jangan menambahkan token ke Git atau ke unit systemd.

```bash
sudo install -m 0644 deploy/systemd/cloudflared-tunnel.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cloudflared-tunnel.service
```

Kedua unit menggunakan `StateDirectory` untuk membuat `/var/lib/tuban-dashboard` dan `/var/lib/cloudflared` dengan mode `0750`. Jika layanan gagal, periksa log dengan `sudo journalctl -u tuban-dashboard.service -u cloudflared-tunnel.service`.
