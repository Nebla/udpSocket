#!/bin/bash
#
# chkconfig: 35 90 12
# description: Foo server
#
# Get function from functions library
. /lib/lsb/init-functions
# Start the service FOO
start() {
        echo "Starting TiX server.."
        screen -A -L -m -d -S udpServerTiempos sudo python /home/pfitba/tix_production/udpServerTiempos.py &
        echo "Started."
        ### Create the lock file ###
        # touch /var/lock/subsys/TIX
        # success $"TIX server startup"
        # echo
}
# Restart the service FOO
stop() {
        echo "Stopping TiX server."
        pkill -f UdpServer
        ### Now, delete the lock file ###
        # rm -f /var/lock/subsys/TIX
}
### main logic ###
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  status)
        status FOO
        ;;
  restart|reload|condrestart)
        stop
        start
        ;;
  *)
        echo $"Usage: $0 {start|stop|restart|reload|status}"
        exit 1
esac
exit 0
