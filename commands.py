import socket

commands = {
    "D1": "D1:",
    "D2": "D2:",
    "D1_st": "D1: Stuck",
    "D2_st": "D2: Stuck",
    "D1_au": "D1: Auto",
    "D2_au": "D2: Auto",
    "D1_ma": "D1: Manual",
    "D2_ma": "D2: Manual",
    "D1_op": "D1: Operational",
    "D2_op": "D2: Operational",
    "D1_face": "D1: Found face!",
    "D2_face": "D2: Found face!",
    "Ma": "Manual",
    "Au": "Auto",
    "Face": "Face",
    "Op": "Operational",
    "Off": "Offline",
    "On": "Online",
    "He": "Help",
    "sock_2273": "tcp://" + str(socket.gethostbyname(socket.gethostname())) + ":2273",
    "sock_2274": "tcp://" + str(socket.gethostbyname(socket.gethostname())) + ":2274",
    "sock_2275": "tcp://" + str(socket.gethostbyname(socket.gethostname())) + ":2275",
    "sock_2276": "tcp://" + str(socket.gethostbyname(socket.gethostname())) + ":2276",

}
