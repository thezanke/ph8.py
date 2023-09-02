#/bin/sh

poetry run watchmedo auto-restart \
  --directory=. \
  --pattern=*.py \
  --recursive \
  -- python src/ph8.py
