#!/usr/bin/env python

import sys, os, time
from signal import SIGTERM

def deamonize(stdout='/dev/null', stderr=None, stdin='/dev/null', place='/tmp/', pidfile=None, startmsg='started with pid %s' ):
    # do first fork.
 
    try: 
        pid = os.fork() 
        if (pid > 0):
            sys.exit(0)# leave first parent
    except OSError, e:# on error inform 
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
        
    # separate from parent environment and chenge directory
    os.chdir(place)
    os.umask(0) 
    os.setsid()
    
    # do second fork.
    try: 
        pid = os.fork() 
        if (pid > 0):
            sys.exit(0) # leave second parent
    except OSError, e: # processing possible errors
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    
    # open file discriptor and write start message
    if (not stderr):
        stderr = stdout
    
        print stdin,stdout,stderr
        si = file(stdin, 'r')
        so = file(stdout, 'a+')
        se = file(stderr, 'a+', 0)
        pid = str(os.getpid())
        sys.stderr.write("\n%s\n" % startmsg % pid)
        sys.stderr.flush()
    if pidfile: file(pidfile,'w+').write("%s\n" % pid)
    
    # redefine standart file descriptors 
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def startstop(stdout='/dev/null', stderr=None, stdin='/dev/null', place='/tmp/', pidfile='pid.txt', startmsg='started with pid %s',action='start'):    
    try:
        pf=open(pidfile)
        pid = int(pf.read().strip())
        pf.close()
    except IOError:
        pid = None        
    if ((action == 'stop') or (action == 'restart')):
	if (not pid):
            mess = "stop imposoble, not pid file '%s' .\n"
            sys.stderr.write(mess % pidfile)
            sys.exit(1)
        try:
    	    while 1:
        	os.kill(pid,SIGTERM)
		print pid, "was killid"
        	time.sleep(1)
	except OSError, err:
    	    err = str(err)
        if err.find("No such process") > 0:
            os.remove(pidfile)
            if 'stop' == action:
               sys.exit(0)
               action = 'start'
               pid = None
            else:
               print str(err)
               sys.exit(1)
    elif (action == 'start'):
        if (pid):
            mess = "Start canceled - pid file '%s' exist.\n"
            sys.stderr.write(mess % pidfile)
            sys.exit(1)
        deamonize(stdout,stderr,stdin,place,pidfile,startmsg)
        return
    elif (action == 'status'):
	if pid: 
	    try:
		os.kill(pid,0)
		print "running pid is %i" %pid
	    except:
		print "pid exist but pocess dead"
	else: 
	    print "no running"
	sys.exit(1)
    print "Usage: %s start | stop | restart" % sys.argv[0]
    sys.exit(2)

def test():
    SleepSec=10
    sys.stdout.write ('Message to stdout...\r\n')
    c = 0
    while 1:
        sys.stdout.write ('%d: %s\n' % (c, time.ctime(time.time())) )
        sys.stdout.flush()
        c = c + 1
        time.sleep(SleepSec)

if (__name__ == "__main__"):    
    if len(sys.argv) < 3:
	print 'usage: %s NameDaemon start | stop | restart | status' % sys.argv[0]
	
    elif sys.argv[1]=='wami':
	startstop(stdout="/var/log/winch_ami.log", pidfile="/var/run/winch_ami.pid", place=".", action=sys.argv[2])
        import ami
	
    elif sys.argv[1]=='cuckoo':
	startstop(stdout="/var/log/Cuckoo.log", pidfile="/run/Cuckoo.pid", place=".", action=sys.argv[2])
        import TaxiCuckoo
    elif sys.argv[1]=='taxisms':
	startstop(stdout="/var/log/taxisms.log", pidfile="/run/taxisms.pid", place=".", action=sys.argv[2])
        import SMS_Notifer
    else:
	print "Unknown daemon"
