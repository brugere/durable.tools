# Environment Setup Guide

## Overview

This project now supports two distinct environments:

1. **Local Development** - For coding, testing, and debugging
2. **Production (VPS)** - For live deployment and serving users

## Quick Start

### Local Development

```bash
# Start local environment
npm run dev:start

# View logs
npm run dev:logs

# Stop when done
npm run dev:stop
```

**Access URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Production Deployment

```bash
# Deploy to VPS
npm run deploy

# Or manually
docker compose -f docker-compose.prod.yml up -d
```

**Access URLs:**
- Website: https://eco-lavelinge.fr
- API: https://eco-lavelinge.fr/v1/

## Environment Files

| File | Purpose | Use Case |
|------|---------|----------|
| `docker-compose.local.yml` | Local development | Hot reload, direct access, debugging |
| `docker-compose.prod.yml` | Production (VPS) | Nginx proxy, SSL, production builds |
| `docker-compose.yml` | Legacy | Backward compatibility (deprecated) |

## Development Helper Script

The `scripts/dev.sh` script provides convenient commands:

```bash
./scripts/dev.sh start      # Start local environment
./scripts/dev.sh stop       # Stop local environment
./scripts/dev.sh restart    # Restart local environment
./scripts/dev.sh build      # Rebuild and start
./scripts/dev.sh logs       # View logs
./scripts/dev.sh status     # Show container status
./scripts/dev.sh shell <service>  # Open shell in container
./scripts/dev.sh clean      # Clean up containers and volumes
./scripts/dev.sh help       # Show all available commands
```

## Key Differences

### Local Development
- ✅ Hot reload for frontend and backend
- ✅ Direct access to services (no proxy)
- ✅ Source code mounted for live editing
- ✅ Development-optimized builds
- ❌ No SSL/TLS
- ❌ No Nginx reverse proxy

### Production (VPS)
- ✅ Nginx reverse proxy with SSL/TLS
- ✅ Production-optimized builds
- ✅ Services exposed only internally
- ✅ Automatic HTTPS enforcement
- ❌ No hot reload
- ❌ No direct service access

## Switching Between Environments

1. **To work locally:**
   ```bash
   npm run dev:start
   # Edit code, see changes immediately
   npm run dev:stop
   ```

2. **To deploy to production:**
   ```bash
   npm run deploy
   # Code automatically deployed to VPS
   ```

## Troubleshooting

### Local Environment Issues
- **Port conflicts**: Check if ports 3000/8000 are free
- **Build errors**: Run `npm run dev:build` to rebuild
- **Container issues**: Run `npm run dev:clean` to reset

### Production Issues
- **Deployment fails**: Check VPS connectivity and SSH keys
- **SSL issues**: Verify Let's Encrypt certificates
- **Service down**: Check Docker containers on VPS

## Best Practices

1. **Always use `[skip deploy]`** in commit messages when working locally
2. **Test locally first** before deploying to production
3. **Use the dev helper script** for local development
4. **Keep production and local configs separate**
5. **Regular deployments** via Git hooks (automatic on main branch)
