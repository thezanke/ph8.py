#!/bin/sh

set -e

. ./.venv/bin/activate

exec python src/ph8.py
