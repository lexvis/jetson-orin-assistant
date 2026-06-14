# WireGuard admin access (outbound-only, no inbound router ports)

The Jetson runs a WG **client** that dials out to a WG **server** on your VPS.
You reach the Jetson over the private tunnel — your home router opens no ports.

## Topology
```
You ──► VPS (WG server, public endpoint) ◄──outbound── Jetson (WG client)
```

## Notes
- Generate keys **on each device** (`wg genkey | tee privatekey | wg pubkey`).
  Never commit private keys — `wireguard/*.conf` is gitignored (only
  `*.example.conf` is tracked).
- The WhatsApp Cloud API webhook is received on the VPS and relayed to the
  Jetson over this tunnel, so inbound webhooks never hit your home network.
- Keep `PersistentKeepalive = 25` on the Jetson side so the outbound tunnel
  stays up behind NAT.
