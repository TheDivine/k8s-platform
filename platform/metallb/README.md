# MetalLB (Bare Metal Load Balancer)

This folder is the centralized location for MetalLB installation and configuration.

## What belongs here
- MetalLB install manifests
- IP address pools
- L2 advertisements

## How to apply (example)
```bash
kubectl apply -f platform/metallb/
```

## Notes
- Customize IP pools to match your LAN range.
