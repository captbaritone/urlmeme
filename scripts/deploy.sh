#!/usr/bin/env bash

# Bail on errors
set -e

cd /var/www/meme-url/

echo "Pulling the new version."
git pull

echo "Restarting Apache..."
sudo service apache2 restart

echo "Done!"
