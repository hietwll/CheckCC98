nohup python -u SecSell.py > log.dat 2>&1 &
ps aux|grep '[S]ecSell.py'|awk '{print $2}'|xargs kill -9
