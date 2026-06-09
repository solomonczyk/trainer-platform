# HTTPS (nip.io) Setup — 009

## Hostname Strategy

Since no custom domain is available, `nip.io` is used as a wildcard DNS service.

**Staging URL**: `https://trainer.152.53.227.37.nip.io`

## How nip.io Works

`*.152.53.227.37.nip.io` resolves to `152.53.227.37` via the nip.io wildcard DNS.

## TLS Certificate

- **Issuer**: Let's Encrypt (YE1)
- **Subject**: `CN = trainer.152.53.227.37.nip.io`
- **Validity**: 90 days (auto-renewed by Caddy)
- **Auto-renewal**: Caddy automatically renews certificates before expiry

## Caddy Configuration

The Caddyfile uses domain `trainer.152.53.227.37.nip.io` with automatic TLS:

```caddy
trainer.152.53.227.37.nip.io {
    # Automatic HTTPS via Let's Encrypt
    reverse_proxy @health backend:8000
    reverse_proxy @api backend:8000
    reverse_proxy frontend:3000
}
```

## Verification

```bash
# Certificate info
echo | openssl s_client -connect trainer.152.53.227.37.nip.io:443 \
  -servername trainer.152.53.227.37.nip.io 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates

# DNS resolution
getent hosts trainer.152.53.227.37.nip.io
# → 152.53.227.37
```
