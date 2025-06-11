#!/usr/bin/env bash
set -o errexit

# This script handles SQLite database persistence on Render
# It copies the database to the persistent disk if it doesn't exist there,
# or copies it from the persistent disk if it does exist there.

echo "==> Setting up SQLite database persistence..."

# Define the paths
PERSISTENT_DIR="/var/data"
PROJECT_DIR="$(pwd)/smart_resume_matcher"
DATABASE_NAME="db.sqlite3"
PERSISTENT_DB_PATH="$PERSISTENT_DIR/$DATABASE_NAME"
PROJECT_DB_PATH="$PROJECT_DIR/$DATABASE_NAME"

# Create persistent directory if it doesn't exist
if [ ! -d "$PERSISTENT_DIR" ]; then
  echo "==> Creating persistent directory $PERSISTENT_DIR"
  mkdir -p "$PERSISTENT_DIR"
fi

# Check if database exists in persistent storage
if [ -f "$PERSISTENT_DB_PATH" ]; then
  echo "==> Found existing database in persistent storage"
  echo "==> Copying database from persistent storage to project directory"
  cp "$PERSISTENT_DB_PATH" "$PROJECT_DB_PATH"
  echo "==> Setting proper permissions"
  chmod 664 "$PROJECT_DB_PATH"
else
  echo "==> No existing database found in persistent storage"
  if [ -f "$PROJECT_DB_PATH" ]; then
    echo "==> Copying project database to persistent storage"
    cp "$PROJECT_DB_PATH" "$PERSISTENT_DB_PATH"
    echo "==> Setting proper permissions"
    chmod 664 "$PERSISTENT_DB_PATH"
  else
    echo "==> No database found in project directory either"
    echo "==> Will create a new one during migrations"
  fi
fi

echo "==> Database persistence setup complete"
