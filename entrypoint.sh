alembic upgrade head &&
uvicorn app:app --host 0.0.0.0 --proxy-headers --log-config logging/logging.ini $@
