# Server Inventory — 009

## Discovery

- **Provider**: Netcup
- **Hostname**: v2202508292476370494.powersrv.de
- **Public IP**: 152.53.227.37
- **Location**: Nuremberg
- **Datacenter**: Netcup

## Hardware

| Attribute    | Value              |
|-------------|-------------------|
| Model       | VPS 1000 ARM G11  |
| Architecture| aarch64 (ARM64)   |
| CPU Cores   | 6                  |
| RAM         | 7.8 GiB            |
| Disk        | 256 GiB (vda)     |
| Disk Layout | vda1: 243M (EFI), vda2: 977M (boot), vda3: 254.8G (root) |
| Virtualization | KVM           |

## OS

- **Distribution**: Debian GNU/Linux 12 (bookworm)
- **Kernel**: Linux 6.1.0-49-arm64
- **Packages**: Docker CE 29.5.3, Docker Compose v5.1.4, Git 2.39.5, UFW

## Network

| Port | Service | Source         |
|------|---------|----------------|
| 22   | SSH     | Any            |
| 80   | HTTP    | Any (redirect) |
| 443  | HTTPS   | Any            |

## Storage

```
/opt/trainer-platform/
├── repo/               — Git repository clone
├── deploy/             — Docker Compose, Caddyfile
├── env/                — Environment files (permissions 600)
├── data/
│   ├── postgres/       — PostgreSQL data (Docker volume)
│   └── backups/        — Daily PostgreSQL backups (7-day retention)
├── logs/               — Application logs
└── scripts/            — Backup and rollback scripts
```

## Users

- `root` — system administrator (SSH key access)
- `trainer` — deployment user (docker group, SSH key access)
