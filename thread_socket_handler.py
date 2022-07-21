import threading
from time import sleep
import zmq
from commands import commands

class ThreadSocketHandler:
    def __init__(self):
        #Logs for dogs, hihi
        self.context = zmq.Context()

        self.log_dog1 = ['log start']
        self.log_dog2 = ['log start']

        self.info_dog_1 = commands.get("Off") # a dog is offline untill a message has been recived from them
        self.info_dog_2 = commands.get("Off") # It only recives a message from the auto script right now, so if it starts in manual it wont sat Operational. 

        self.timer_dog1 = 0
        self.timer_dog2 = 0
        self.timer_log_dog1 = 0
        self.timer_log_dog2 = 0

        self.t1 = threading.Thread(target=self.start_proxy, daemon=True)
        self.t2 = threading.Thread(target=self.recive_logs, daemon=True )
        self.t3 = threading.Thread(target=self.recive_alerts, daemon=True )
        self.t4 = threading.Thread(target=self.check_if_dog_online, daemon=True )
        self.t5 = threading.Thread(target=self.check_if_dog_offline, daemon=True )

    def __del__(self):
        self.t1.join()
        self.t2.join()
        self.t3.join()
        self.t4.join()
        self.t5.join()
        
    def run(self):
        self.sockets()
        self.t1.start()
        sleep(5) # Proxy might need some time to start, might even need longer than this, no harm in starting sooner but the values from the proxy might be slow to arive
        self.t2.start()
        self.t3.start()
        self.t4.start()
        self.t5.start()

    def sockets(self):
        """
        Important, the sockets subsribe and publishes one to many, many to one. 
        Therefore indentifier are needed when sending things over the sockets. Like if you want to talk to dog 1 u need D1:, dog 2: D2: in the string being sent
        The same goes for the other direction, make sure the "dogs" sends an identifier when trying to send information with Dog 1: D1:, Dog 2: D2:
        Try to bind as many as possible in the server, the server automatically checks its ip and uses that
        """
        # PROXY
        self.xsub_sock = self.context.socket(zmq.XSUB)
        self.xpub_sock = self.context.socket(zmq.XPUB)
        self.xsub_sock.bind(commands.get("sock_2275"))
        self.xpub_sock.bind(commands.get("sock_2276"))

        self.sub_sock_daemon = self.context.socket(zmq.SUB)
        self.sub_sock_daemon.connect(commands.get("sock_2276"))
        self.sub_sock_daemon.setsockopt_string(zmq.SUBSCRIBE, '')

        # Bind the socket for communication to the clients (Pi:s, dogs whatever)
        self.pub_sock_pi = self.context.socket(zmq.PUB)
        self.pub_sock_pi.bind(commands.get("sock_2273"))

        self.sub_sock_alerts = self.context.socket(zmq.SUB)
        self.sub_sock_alerts.bind(commands.get("sock_2274"))
        self.sub_sock_alerts.setsockopt(zmq.SUBSCRIBE, b'')

    #started with a thread
    def start_proxy(self):
        zmq.proxy(self.xsub_sock, self.xpub_sock)

    #started with a thread
    def recive_logs(self):
        while True:
            r = self.sub_sock_daemon.recv().decode('utf-8')
            # add in diffrent logs for dog 1 and dog 2
            if (r.find(commands.get("D1")) != -1):
                self.timer_log_dog1 += 1
                if len(self.log_dog1) > 10:
                    self.log_dog1.clear()
                self.log_dog1.append(r.replace(commands.get("D1"), '').strip()) # Remove the dog 1 tag
            
            if (r.find(commands.get("D2")) != -1):
                self.timer_log_dog2 += 1
                if len(self.log_dog2) > 10:
                    self.log_dog2.clear()
                self.log_dog2.append(r.replace(commands.get("D2"), "").strip()) # Remove the dog 2 tag
            # if it start reciving from daemon it is online, but might not yet have started (since the Daemon starts when the pi starts not when the dog starts)
            if ((self.info_dog_1 == commands.get("Off")) and (r.find(commands.get("D1")) != -1)):
                self.info_dog_1 = commands.get("On")
            if ((self.info_dog_2 == commands.get("Off")) and (r.find(commands.get("D2")) != -1)):
                self.info_dog_2 = commands.get("On")

    #started with a thread
    def recive_alerts(self):
        while True:
            r = self.sub_sock_alerts.recv().decode('utf-8')
            if (r.find(commands.get("D1_st")) != -1):
                self.info_dog_1 = commands.get("He")
                #timer_dog1 is to check if it went online, bit weird but practically means that the manuell_auto.py script has stopped, dosnt mean the pi is off
                self.timer_dog1 += 1
            elif (r.find(commands.get("D1_op")) != -1):
                self.info_dog_1 = commands.get("Op")
                self.timer_dog1 += 1
            elif (r.find(commands.get("D1_face")) != -1):
                self.info_dog_1 = commands.get("Face")
                self.timer_dog1 += 1
            elif (r.find(commands.get("D1_au")) != -1):
                self.info_dog_1 = commands.get("Au")
                self.timer_dog1 += 1
            elif (r.find(commands.get("D1_ma")) != -1):
                self.info_dog_1 = commands.get("Ma")
                self.timer_dog1 += 1

            if (r.find(commands.get("D2_st")) != -1):
                self.info_dog_2 = commands.get("He")
                self.timer_dog2 += 1
            elif (r.find(commands.get("D2_op")) != -1):
                self.info_dog_2 = commands.get("Op")
                self.timer_dog2 += 1
            elif (r.find(commands.get("D2_face")) != -1):
                self.info_dog_2 = commands.get("Face")
                self.timer_dog2 += 1
            elif (r.find(commands.get("D2_au")) != -1):
                self.info_dog_2 = commands.get("Au")
                self.timer_dog2 += 1
            elif (r.find(commands.get("D2_ma")) != -1):
                self.info_dog_2 = commands.get("Ma")
                self.timer_dog2 += 1

    #started with a thread          
    def check_if_dog_offline(self):
        while True:
            old_timervalue_log_dog1 = self.timer_log_dog1
            old_timervalue_log_dog2 = self.timer_log_dog2

            sleep(3) # should be enough, if a pi is ON it sends a new log value like every second isch, so a sleep for 3 seconds should be more then enough
            if(old_timervalue_log_dog1 == self.timer_log_dog1):
                self.info_dog_1 = commands.get("Off")

            if(old_timervalue_log_dog2 == self.timer_log_dog2):
                self.info_dog_2 = commands.get("Off")

    #started with a thread
    def check_if_dog_online(self):
        while True:
            old_timervalue_dog1 = self.timer_dog1
            old_timervalue_dog2 = self.timer_dog2

            sleep(17) # Seems like a good value

            # if the value hasnt changed anything in 15 seconds the dog probably stopped, but not for certainty did it go Offline (prob tho, but should be handeled by the daemon)
            if(old_timervalue_dog1 == self.timer_dog1 and (self.info_dog_1 == commands.get("D1_op") or self.info_dog_1 == commands.get("D1_st"))):
                self.info_dog_1 = commands.get("On")

            if(old_timervalue_dog2 == self.timer_dog2 and (self.info_dog_1 == commands.get("D2_op") or self.info_dog_1 == commands.get("D2_st"))):
                self.info_dog_2 = commands.get("On")
