#!/bin/bash
# WebApex Forge Engine — Stap 5: Deploy
# Deployt de geassembleerde website op de klant hosting

set -e

KLANT_DIR="$1"
SERVER_IP="$2"
SSH_USER="$3"
SSH_KEY="$4"
DOMEIN="$5"

if [ -z "$KLANT_DIR" ] || [ -z "$SERVER_IP" ]; then
    echo "Gebruik: ./deploy.sh <klant_dir> <server_ip> <ssh_user> <ssh_key> <domein>"
    exit 1
fi

echo ""
echo "🚀 WebApex Forge — Stap 5: Deployen"
echo ""

SLUG=$(basename "$KLANT_DIR" | sed 's/client-//')

echo "  → Server: $SERVER_IP"
echo "  → Klant:  $SLUG"
echo "  → Domein: $DOMEIN"
echo ""

# Kopieer project naar server
echo "  ↑ Uploaden naar server..."
rsync -avz --exclude '.git' --exclude '__pycache__' \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    "$KLANT_DIR/" "$SSH_USER@$SERVER_IP:/var/www/$SLUG/"

echo "  ✅ Upload klaar"

# Start Docker containers op server
echo "  ↻ Docker starten..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" << REMOTE
    cd /var/www/$SLUG
    docker-compose pull
    docker-compose up -d --build
    echo "Containers gestart"
REMOTE

echo "  ✅ Docker actief"

# SSL certificaat via Let's Encrypt
if [ ! -z "$DOMEIN" ]; then
    echo "  🔒 SSL certificaat aanvragen..."
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" << REMOTE
        certbot --nginx -d $DOMEIN -d www.$DOMEIN \
            --non-interactive --agree-tos \
            --email support@webapex.nl || echo "SSL later instellen"
REMOTE
    echo "  ✅ SSL geconfigureerd"
fi

echo ""
echo "✅ Deployment klaar!"
echo ""
echo "  🌐 Website: https://$DOMEIN"
echo "  ⚙️  Admin:   https://$DOMEIN/admin"
echo "  📡 API:     https://$DOMEIN/api/docs"
echo ""
