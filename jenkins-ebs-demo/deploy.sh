#!/bin/bash
set -euo pipefail

APP_DIR="/opt/ebs-demo"
DATA_DIR="/mnt/ebs-data"
SERVICE_FILE="/etc/systemd/system/ebs-demo.service"

# Prevent accidentally storing demo data on the root filesystem.
if ! mountpoint -q "$DATA_DIR"; then
  echo "ERROR: $DATA_DIR is not a mount point. Attach and mount the separate EBS data volume first."
  exit 2
fi

dnf install -y python3
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"
chown -R ec2-user:ec2-user "$APP_DIR"
chown -R ec2-user:ec2-user "$DATA_DIR"

cat > "$SERVICE_FILE" <<'UNIT'
[Unit]
Description=Jenkins EBS Demo Flask Application
After=network.target
RequiresMountsFor=/mnt/ebs-data

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/ebs-demo
Environment=EBS_DATA_DIR=/mnt/ebs-data
ExecStart=/opt/ebs-demo/venv/bin/python /opt/ebs-demo/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable ebs-demo
systemctl restart ebs-demo
systemctl --no-pager --full status ebs-demo
echo "Deployment completed."
