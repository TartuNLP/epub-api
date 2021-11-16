if [ "$ROOT_PATH" != "" ];
then
  ROOT_PATH="--root-path $ROOT_PATH"
fi

alembic upgrade head &&
if [ "$CONFIGURATION" == "debug" ]
then
  uvicorn app:app --host 0.0.0.0 --port 80 --log-config logging/logging.debug.ini --proxy-headers $ROOT_PATH;
else
  uvicorn app:app --host 0.0.0.0 --port 80 --log-config logging/logging.ini --proxy-headers $ROOT_PATH;
fi