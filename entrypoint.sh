#!/bin/sh

sleep 5

echo "Running mongorestore..."
mongorestore --host "$MONGO_DB_HOST" \
             --port "$MONGO_DB_PORT" \
             --username "$MONGO_DB_USER" \
             --password "$MONGO_DB_PASSWORD" \
             --authenticationDatabase admin \
             --drop \
             /app/backup

echo "Starting Django..."
python src/backend/rotten_scores/manage.py migrate
python src/backend/rotten_scores/manage.py runserver 0.0.0.0:8080
