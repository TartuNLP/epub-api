if [ "$ENDPOINT_PATH" != "" ];
then
  ENDPOINT_PATH="--root-path $ENDPOINT_PATH"
fi

alembic upgrade head &&
if [ "$CONFIGURATION" == "debug" ]
then
  uvicorn app:app --host 0.0.0.0 --port 80 --log-config logging/logging.debug.ini --proxy-headers $ENDPOINT_PATH;
else
  uvicorn app:app --host 0.0.0.0 --port 80 --log-config logging/logging.ini --proxy-headers $ENDPOINT_PATH;
fi