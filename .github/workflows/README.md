# CI/CD Pipeline Setup

This repository uses GitHub Actions for automated deployment.

## Setup Instructions

### 1. Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add these secrets:

- `SERVER_HOST`: Your server IP (e.g., `72.61.254.71`)
- `SERVER_USER`: SSH username (e.g., `root`)
- `SSH_PRIVATE_KEY`: Your SSH private key for server access

### 2. Generate SSH Key (if needed)

```bash
ssh-keygen -t rsa -b 4096 -C "github-actions"
# Save as: ~/.ssh/github_actions_deploy

# Copy public key to server
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub root@72.61.254.71

# Copy private key content to GitHub Secrets
cat ~/.ssh/github_actions_deploy
```

### 3. How It Works

- **Automatic Deployment**: Every push to `main` branch triggers deployment
- **Manual Deployment**: Go to Actions tab → Deploy to Server → Run workflow
- **Safety**: Creates database backup before deployment
- **Verification**: Checks server health after deployment

### 4. Deployment Process

1. Pulls latest code from `main` branch
2. Creates database backup
3. Restarts Docker services
4. Verifies server is responding
5. Reports deployment status

## Manual Deployment

If you prefer manual deployment, use the scripts:

```bash
ssh root@72.61.254.71
cd /opt/dice_game
bash scripts/restart_deployment_server.sh local
```

