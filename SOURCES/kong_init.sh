#!/bin/sh
### BEGIN INIT INFO
# Provides:          Kong
# Required-Start:    $local_fs $network $named $time $syslog
# Required-Stop:     $local_fs $network $named $time $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       Kong service wrapper (getkong.org)
### END INIT INFO

[ -e /etc/sysconfig/kong ] && . /etc/sysconfig/kong

SCRIPT=/usr/bin/kong
RUNAS=kong

check_health() {
  local CMD="$SCRIPT health >/dev/null 2>&1"
  $CMD
  return $?
}

start() {
  if check_health; then
    echo 'Service already running' >&2
    return 1
  fi

  ulimit -n ${NFILES:-131072}
  echo 'Starting service...' >&2
  local CMD="$SCRIPT start $KONG_ARGS"
  su -c "$CMD" $RUNAS
}

stop() {
  if check_health; then
    echo 'Stopping service...' >&2
    local CMD="$SCRIPT stop"
    su -c "$CMD" $RUNAS
  else
    echo 'Service not running' >&2
    return 1
  fi
}

reload() {
  if check_health; then
    echo 'Service not running' >&2
    return 1
  fi
  echo 'Reloading configuration' >&2
  local CMD="$SCRIPT reload"
  su -c "$CMD" $RUNAS
}

status() {
  local CMD="$SCRIPT health"
  su -c "$CMD" $RUNAS
}


case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  status)
    status
    ;;
  reload)
    reload
    ;;
  restart)
    stop
    start
    ;;
  *)
    echo "Usage: $0 {start|stop|status|restart|reload}"
    exit 2
esac
exit $?
