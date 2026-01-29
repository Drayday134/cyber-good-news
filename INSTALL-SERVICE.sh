#!/bin/bash
# Install Cyber Good News as a systemd service

echo "Installing Cyber Good News service..."

# Copy service file
sudo cp /home/dragon/cyber-good-news/cyber-good-news.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable cyber-good-news
sudo systemctl start cyber-good-news

echo "Service installed and started!"
echo "Check status: sudo systemctl status cyber-good-news"
echo "View logs: tail -f /home/dragon/cyber-good-news/logs/service.log"
