# Python program to implement server side of chat room.
import socket
import select
import sys
import psycopg2
from passlib.hash import sha256_crypt
import rsa
import cryptocode
import datetime

'''Replace "thread" with "_thread" for python 3'''
from _thread import *

import threading
lock = threading.Lock()

"""The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
file = open("logs.txt", "a")

# checks whether sufficient arguments have been provided
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()

# takes the first argument from command prompt as IP address
IP_address = str(sys.argv[1])

# takes second argument from command prompt as port number
Port = int(sys.argv[2])


# binds the server to an entered IP address and at the
# specified port number.
# The client must be aware of these parameters

server.bind((IP_address, Port))

# listens for 100 active connections. This number can be
# increased as per convenience.

server.listen(100)

username_conn = {}

# connecting to database
dbconn = psycopg2.connect(database="fastchat", user="postgres",
                          password="", host="127.0.0.1", port="5432")
cur = dbconn.cursor()

SERVER_POOL = [('127.0.0.1', 8000), ('127.0.0.1', 8001), ('127.0.0.1', 8002)]
fellow_servers = {}
available = {}


# The following socket would help in contact between load balancer and the server itself
lb = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# This number can be anything we just assumed it to be this as address of the load balancer
lb.connect(('127.0.0.1', 7999))

# Need to make sure load balancer is free to answer queries or not
# We would need boolean value telling us it is free or not
lb_free = True

# Sending the signal to the load balancer that we are source
lb.sendall("s".encode('utf-8'))


# server connects to the ip and port of the server
def letsconnect(ip, port):
    '''
    This function establishes socket connection between the server to the server with the ip and port passed as parameter
    The following codes are received by the server which have the following meanings:

        |  1. wi: Send the text message in encrypted format to the server to which the receiver client is connected
        |  2. ii: Send the image in encrypted format to the server to which the receiver client is connected
        |  3. wg: Send the text message sent by a client in a group in encrypted format to the server to which the receiver client (group member) is connected
        |  4. ig: Send the image sent by a client in a group in encrypted format to the server to which the receiver client (group member) is connected
        |  5. gk: Get the encryoted group private key from the loadbalancer

    :param ip: It is the ip address of the server which wants to establish a socket connection with this server
    :type ip: str
    :param port: It is the port number of the server which wants to establish a socket connection with this server
    :type port: str
    '''
    global SERVER_POOL, fellow_servers, available, lb_free
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((ip, port))
    conn.sendall("s".encode('utf-8'))
    my_address = f"('{IP_address}', {Port})"
    their_address = f"('{ip}', {port})"
    fellow_servers[their_address] = conn
    available[their_address] = True
    # Sending my address
    conn.sendall(str(len(my_address)).zfill(3).encode('utf-8'))
    conn.sendall(my_address.encode('utf-8'))

    # Make infinte while recieve loop
    while (True):
        code = conn.recv(2).decode('utf-8')
        if code == "wi":
            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            from_user = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(conn.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size % 86 == 0:
                msg.append(conn.recv(128))

            # Lets send the message to the user
            uss_conn = username_conn[to_usr]
            uss_conn.sendall("u".encode('utf-8'))

            uss_conn.sendall(str(len(from_user)).zfill(3).encode('utf-8'))
            uss_conn.sendall(from_user.encode('utf-8'))

            username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
            for elem in msg:
                username_conn[to_usr].sendall(elem)

        elif code == "ii":
            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            from_user = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(
                conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size % 86 == 0:
                msg.append(conn.recv(128))

            username_conn[to_usr].sendall('b'.encode('utf-8'))
            username_conn[to_usr].sendall(
                str(len(from_user)).zfill(3).encode('utf-8'))
            username_conn[to_usr].sendall(from_user.encode('utf-8'))
            username_conn[to_usr].sendall(
                str(len(ext)).zfill(1).encode('utf-8'))
            username_conn[to_usr].sendall(ext.encode('utf-8'))
            username_conn[to_usr].sendall(
                str(len(str(size))).zfill(2).encode('utf-8'))
            username_conn[to_usr].sendall(str(size).encode('utf-8'))
            for elem in msg:
                username_conn[to_usr].sendall(elem)

        # sending a group message
        elif code == "wg":
            pvt_key = conn.recv(
                int(conn.recv(4).decode('utf-8')))
            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            from_user = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            to_grp = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(conn.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            # sending messages to servers connected to the receiving client
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size % 86 == 0:
                msg.append(conn.recv(128))

            # Lets send the message to the user
            uss_conn = username_conn[to_usr]
            uss_conn.sendall("g".encode('utf-8'))

            uss_conn.sendall(str(len(pvt_key)).zfill(4).encode('utf-8'))
            uss_conn.sendall(pvt_key)

            uss_conn.sendall(str(len(from_user)).zfill(3).encode('utf-8'))
            uss_conn.sendall(from_user.encode('utf-8'))

            uss_conn.sendall(str(len(to_grp)).zfill(3).encode('utf-8'))
            uss_conn.sendall(to_grp.encode('utf-8'))

            uss_conn.sendall(str(size).zfill(4).encode('utf-8'))
            for elem in msg:
                uss_conn.sendall(elem)

        # sending a message in a group
        elif code == "ig":
            pvt_key = conn.recv(
                int(conn.recv(4).decode('utf-8')))

            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            from_user = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            to_grp = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')

            ext = conn.recv(int(conn.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(
                conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size % 86 == 0:
                msg.append(conn.recv(128))

            username_conn[to_usr].sendall('a'.encode('utf-8'))
            username_conn[to_usr].sendall(
                str(len(pvt_key)).zfill(4).encode('utf-8'))
            username_conn[to_usr].sendall(pvt_key)
            username_conn[to_usr].sendall(
                str(len(from_user)).zfill(3).encode('utf-8'))
            username_conn[to_usr].sendall(from_user.encode('utf-8'))
            username_conn[to_usr].sendall(
                str(len(to_grp)).zfill(3).encode('utf-8'))
            username_conn[to_usr].sendall(to_grp.encode('utf-8'))
            username_conn[to_usr].sendall(
                str(len(ext)).zfill(1).encode('utf-8'))
            username_conn[to_usr].sendall(ext.encode('utf-8'))
            username_conn[to_usr].sendall(
                str(len(str(size))).zfill(2).encode('utf-8'))
            username_conn[to_usr].sendall(str(size).encode('utf-8'))
            for elem in msg:
                username_conn[to_usr].sendall(elem)

        # sending group key to the users so that they
        # can send back their encrypted message
        elif code == "gk":
            to_usr = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            for_grp = conn.recv(
                int(conn.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(conn.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                msg.append(conn.recv(128))
            if not size % 86 == 0:
                msg.append(conn.recv(128))

            # Lets send the message to the user
            uss_conn = username_conn[to_usr]
            uss_conn.sendall("k".encode('utf-8'))
            username_conn[to_usr].sendall(
                str(len(for_grp)).zfill(3).encode('utf-8'))
            username_conn[to_usr].sendall(for_grp.encode('utf-8'))
            username_conn[to_usr].sendall(str(size).zfill(4).encode('utf-8'))
            for elem in msg:
                username_conn[to_usr].sendall(elem)


# starting new thread of a server with all the servers having port number lesser than it
for i in SERVER_POOL:
    if i[1] < Port:
        start_new_thread(letsconnect, (i[0], i[1]))
    else:
        break

# clientthread


def clientthread(conn, addr):
    '''
    This is the thread which receives messages from the client and responds accordingly.
    Messages are sent from the server to the clients connected to that particular server.
    The following codes are received by the server which have the following meaning:

        |  1. cg: Check if the group already exists or not
        |  2. ci: Check if the individual exists or not
        |  3. ng: Create a new group with the client sending the code as admin
        |  4. eg: Check if the group exists and the client sending the code to the server is the admin
        |  5. ai: Add an individual to the group
        |  6. ri: Remove an individual from the group
        |  7. sa: Send the names of all the members of the group to the admin of the group
        |  8. wg: Send the text message in encrypted format to an individual
        |  9. ig: Send an image in an encrypted format to a group
        |  10. wi: Send the text message in encrypted format to an individual
        |  11. ii: Send an image in encrypted format to an individual

    :param conn: It is the connection object of the client which has established a socket connection with the server
    :type conn: socket.socket
    :param addr: It is the address (ip,port) of the client which has established a socket connection with the server
    :type addr: tuple
    '''
    global lb, fellow_servers, username_conn, available, lb_free
    serv_connected = ''
    if (conn.recv(1).decode('utf-8') == "c"):
        # deleting the message if time interval is greater than 2 hours
        to_remove = "DELETE FROM IND_MSG WHERE TIME < NOW() - INTERVAL '2 HOURS' AND (EXTENSION IS NULL OR EXTENSION != 'GROUP KEY') "
        cur.execute(to_remove)
        dbconn.commit()

        username = conn.recv(int(conn.recv(3).decode('utf-8'))).decode('utf-8')
        username_conn[username] = conn

        # Before going further we can arrange that all the previous messages are being sent to
        # the user.
        to_check = f"SELECT * FROM IND_MSG WHERE RECEIVER = '{username}' "
        cur.execute(to_check)
        selected_entry = cur.fetchall()
        conn.sendall(str(len(selected_entry)).zfill(4).encode('utf-8'))
        for e in selected_entry:
            if e[4] == None:
                if e[5] == None:
                    # send a text to individual
                    conn.sendall("in".encode('utf-8'))
                    conn.sendall(str(len(e[0])).zfill(3).encode('utf-8'))
                    conn.sendall(e[0].encode('utf-8'))
                    conn.sendall(str(e[6]).zfill(4).encode('utf-8'))
                    size = int(e[6])
                    iter = size//86
                    for i in range(iter):
                        data = bytes(e[3][i*128:(i+1)*128])
                        conn.sendall(data)

                    if not size % 86 == 0:
                        data = bytes(e[3][iter*128:])
                        conn.sendall(data)

                else:
                    # send an image to individual
                    conn.sendall("iy".encode('utf-8'))
                    conn.sendall(str(len(e[0])).zfill(3).encode('utf-8'))
                    conn.sendall(e[0].encode('utf-8'))
                    conn.sendall(str(len(e[5])).zfill(1).encode('utf-8'))
                    conn.sendall(e[5].encode('utf-8'))
                    conn.sendall(str(len(e[6])).zfill(2).encode('utf-8'))
                    conn.sendall(e[6].encode('utf-8'))
                    size = int(e[6])
                    iter = size//86
                    for i in range(iter):
                        data = bytes(e[3][i*128:(i+1)*128])
                        conn.sendall(data)

                    if not size % 86 == 0:
                        data = bytes(e[3][iter*128:])
                        conn.sendall(data)
            else:
                # if its not a group message
                if e[5] == None:
                    conn.sendall("gn".encode('utf-8'))
                    conn.sendall(
                        str(len(bytes(e[7]))).zfill(4).encode('utf-8'))
                    conn.sendall(bytes(e[7]))
                    conn.sendall(str(len(e[0])).zfill(3).encode('utf-8'))
                    conn.sendall(e[0].encode('utf-8'))
                    conn.sendall(str(len(e[4])).zfill(3).encode('utf-8'))
                    conn.sendall(e[4].encode('utf-8'))
                    conn.sendall(str(e[6]).zfill(4).encode('utf-8'))
                    size = int(e[6])
                    iter = size//86
                    for i in range(iter):
                        data = bytes(e[3][i*128:(i+1)*128])
                        conn.sendall(data)

                    if not size % 86 == 0:
                        data = bytes(e[3][iter*128:])
                        conn.sendall(data)

                # sending group key
                elif e[5] == 'GROUP KEY':
                    conn.sendall("gk".encode('utf-8'))
                    conn.sendall(str(len(e[4])).zfill(3).encode('utf-8'))
                    conn.sendall(e[4].encode('utf-8'))
                    conn.sendall(str(e[6]).zfill(4).encode('utf-8'))
                    size = int(e[6])
                    iter = size//86
                    for i in range(iter):
                        data = bytes(e[3][i*128:(i+1)*128])
                        conn.sendall(data)

                    if not size % 86 == 0:
                        data = bytes(e[3][iter*128:])
                        conn.sendall(data)

                else:
                    # sending group image
                    conn.sendall("gy".encode('utf-8'))
                    conn.sendall(
                        str(len(bytes(e[7]))).zfill(4).encode('utf-8'))
                    conn.sendall(bytes(e[7]))
                    conn.sendall(str(len(e[0])).zfill(3).encode('utf-8'))
                    conn.sendall(e[0].encode('utf-8'))
                    conn.sendall(str(len(e[4])).zfill(3).encode('utf-8'))
                    conn.sendall(e[4].encode('utf-8'))
                    conn.sendall(str(len(e[5])).zfill(1).encode('utf-8'))
                    conn.sendall(e[5].encode('utf-8'))
                    conn.sendall(str(len(e[6])).zfill(2).encode('utf-8'))
                    conn.sendall(e[6].encode('utf-8'))
                    size = int(e[6])
                    iter = size//86
                    for i in range(iter):
                        data = bytes(e[3][i*128:(i+1)*128])
                        conn.sendall(data)

                    if not size % 86 == 0:
                        data = bytes(e[3][iter*128:])
                        conn.sendall(data)

        # deleting messages after they have been sent
        to_do = f"DELETE FROM IND_MSG WHERE RECEIVER = '{username}'"
        cur.execute(to_do)
        dbconn.commit()

        # infinite loop for receiving messages from clients
        while True:
            try:
                # receiving encrypted message from client
                message = conn.recv(512).decode('utf-8')
                if (not message or message == "quit"):
                    to_send = "q".encode('utf-8')
                    conn.sendall(to_send)
                    remove(conn, username)
                    return

                # splitting message using colons
                message = message.split(":")
                code = message[0]

                # receiving group keys
                if code == "gk":
                    grp_name = message[1]
                    grp_pvt_len = conn.recv(4)
                    grp_pvt_key = conn.recv(int(grp_pvt_len.decode('utf-8')))
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' "
                    cur.execute(find_grp)
                    entry_grp = cur.fetchone()
                    num_present = entry_grp[23]
                    index = -1
                    try:
                        index = entry_grp[24:].index(username)
                    except:
                        index = -1
                    if index != -1:
                        column = "pvt_key"+f"{index+1}"
                        update_query = f"UPDATE GROUPS SET {column} = decode('{grp_pvt_key.hex()}', 'hex') WHERE NAME = '{grp_name}' "
                        cur.execute(update_query)
                        dbconn.commit()

                # checking if a group exists or not
                elif code == "cg":
                    grp_name = message[1]
                    usr_name = message[2]
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' "
                    cur.execute(find_grp)
                    entry = cur.fetchone()
                    conn.sendall("e".encode('utf-8'))
                    # if a group with that name doesn't already exist
                    if entry == None:
                        out = "n".encode('utf-8')
                        conn.sendall(out)
                    # if a group with that name exists
                    else:
                        try:
                            index = entry[24:24 +
                                          entry[23]].index(usr_name)
                        except:
                            out = "n".encode('utf-8')
                            conn.sendall(out)
                            continue

                        out = "y".encode('utf-8')
                        conn.sendall(out)

                        lock.acquire()
                        lb.sendall("cg".encode('utf-8'))

                        lb.sendall(str(len(grp_name)).zfill(3).encode('utf-8'))
                        lb.sendall(grp_name.encode('utf-8'))

                        len_key = int(lb.recv(4).decode('utf-8'))
                        keyofrecv = lb.recv(len_key)
                        # lb_free = True
                        lock.release()

                        conn.sendall(
                            str(len(keyofrecv)).zfill(4).encode('utf-8'))
                        conn.sendall(keyofrecv)

                # check if the credentials of an individual exist or not
                elif code == "ci":
                    ind_name = message[1]
                    find_ind = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{ind_name}' "
                    cur.execute(find_ind)
                    entry = cur.fetchone()
                    conn.sendall("e".encode('utf-8'))
                    # a user with that username exists
                    if entry == None:
                        out = "n".encode('utf-8')
                        conn.sendall(out)
                    else:
                        # a user with that username doesnt exist
                        out = "y".encode('utf-8')
                        conn.sendall(out)

                        lock.acquire()
                        lb.sendall("ci".encode('utf-8'))

                        lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                        lb.sendall(ind_name.encode('utf-8'))

                        len_key = int(lb.recv(4).decode('utf-8'))
                        keyofrecv = lb.recv(len_key)
                        lock.release()

                        # sending public key to user
                        conn.sendall(
                            str(len(keyofrecv)).zfill(4).encode('utf-8'))
                        conn.sendall(keyofrecv)

                elif code == "ng":
                    # creating a new group
                    grp_name = message[1]
                    pub_len = conn.recv(4)
                    pub_key = conn.recv(
                        int(pub_len.decode('utf-8')))
                    pvt_len = conn.recv(4)
                    pvt_key = conn.recv(
                        int(pvt_len.decode('utf-8')))
                    # checking if a group with that name exists or not
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' "
                    cur.execute(find_grp)
                    entry = cur.fetchone()
                    if entry == None:
                        # insert entry into group database
                        postgres_insert_query = f"INSERT INTO GROUPS (NAME, ADMIN, PUB_KEY, PVT_KEY1, NUMBER, MEMBER1) VALUES ('{grp_name}', '{username}', decode('{pub_key.hex()}', 'hex'), decode('{pvt_key.hex()}', 'hex'), 1, '{username}')"
                        cur.execute(postgres_insert_query)
                        dbconn.commit()
                        lock.acquire()
                        lb.sendall("ag".encode('utf-8'))
                        lb.sendall(str(len(grp_name)).zfill(3).encode('utf-8'))
                        lb.sendall(grp_name.encode('utf-8'))
                        lb.sendall(str(int(pub_len.decode('utf-8'))
                                       ).zfill(4).encode('utf-8'))
                        lb.sendall(pub_key)
                        lock.release()
                        out = "y".encode('utf-8')
                        conn.sendall(out)
                    else:
                        out = "n".encode('utf-8')
                        conn.sendall(out)

                elif code == "eg":
                    # existing group with admin priveleges
                    grp_name = message[1]
                    # selecting group with the following group name and username
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                    cur.execute(find_grp)
                    entry = cur.fetchone()
                    if entry == None:
                        out = "n".encode('utf-8')
                        conn.sendall(out)
                    else:
                        out = "y".encode('utf-8')
                        conn.sendall(out)

                # add indivudual in a group
                elif code == "ai":
                    grp_name = message[1]
                    # getting the database entry
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                    cur.execute(find_grp)
                    # getting the entry
                    entry_grp = cur.fetchone()
                    ind_name = message[2]
                    # getting the credentials of the user to be added
                    find_ind = f"SELECT * FROM CREDENTIALS WHERE USERNAME = '{ind_name}' "
                    cur.execute(find_ind)
                    entry_ind = cur.fetchone()

                    if entry_ind == None:
                        out = "n".encode('utf-8')  # non-existent user
                        conn.sendall(out)

                    else:
                        if entry_grp[2] == 20:
                            out = "l".encode('utf-8')  # lim-exceeded
                            conn.sendall(out)

                        elif ind_name in entry_grp[24:]:
                            # user is already present in the group
                            out = "t".encode('utf-8')
                            conn.sendall(out)

                        else:
                            num_present = entry_grp[23]
                            try:
                                lock.acquire()
                                # checking if the client exists with the help of loadbalancer
                                lb.sendall("ci".encode('utf-8'))
                                # sending ind_name and getting
                                # public key from loadbalancer
                                # sending it to client
                                # and getting back the encrypted message
                                lb.sendall(str(len(ind_name)).zfill(
                                    3).encode('utf-8'))
                                lb.sendall(ind_name.encode('utf-8'))

                                len_key = int(lb.recv(4).decode('utf-8'))
                                keyofrecv = lb.recv(len_key)
                                conn.sendall('e'.encode('utf-8'))
                                conn.sendall('y'.encode('utf-8'))
                                conn.sendall(
                                    str(len(keyofrecv)).zfill(4).encode('utf-8'))
                                conn.sendall(keyofrecv)

                                conn.sendall('p'.encode('utf-8'))
                                conn.sendall(
                                    str(len(bytes(entry_grp[3]))).zfill(4).encode('utf-8'))
                                conn.sendall(bytes(entry_grp[3]))
                                size = int(conn.recv(4).decode('utf-8'))
                                iter = size//86
                                msg = []
                                for i in range(iter):
                                    msg.append(conn.recv(128))
                                if not size % 86 == 0:
                                    msg.append(conn.recv(128))

                                # Need to get the public key of the fellow
                                lb.sendall("cs".encode('utf-8'))
                                lb.sendall(str(len(ind_name)).zfill(
                                    3).encode('utf-8'))
                                lb.sendall(ind_name.encode('utf-8'))
                                ip_len = int(lb.recv(3).decode('utf-8'))
                                serv_connected = lb.recv(
                                    ip_len).decode('utf-8')
                                lock.release()

                                if (serv_connected == f"('{IP_address}', {Port})"):
                                    # Recieving user is active
                                    username_conn[ind_name].sendall(
                                        'k'.encode('utf-8'))

                                    username_conn[ind_name].sendall(
                                        str(len(grp_name)).zfill(3).encode('utf-8'))
                                    username_conn[ind_name].sendall(
                                        grp_name.encode('utf-8'))

                                    username_conn[ind_name].sendall(
                                        str(size).zfill(4).encode('utf-8'))
                                    for elem in msg:
                                        username_conn[ind_name].sendall(elem)

                                elif (serv_connected == "n"):
                                    # receiving user is inactive
                                    # check table
                                    dt = datetime.datetime.now()
                                    to_store = b''.join(msg)
                                    postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, GRP, EXTENSION, SIZE) VALUES ('{username}', '{ind_name}', '{dt}', decode('{to_store.hex()}', 'hex'), '{grp_name}' ,'GROUP KEY' , {str(size)});'''
                                    cur.execute(postgres_insert_query)
                                    dbconn.commit()

                                else:
                                    # the user is connected to some other server
                                    serv_conn = fellow_servers[serv_connected]
                                    while (available[serv_connected] != True):
                                        continue
                                    available[serv_connected] = False
                                    serv_conn.sendall("gk".encode('utf-8'))
                                    serv_conn.sendall(
                                        str(len(ind_name)).zfill(
                                            3).encode('utf-8')
                                    )
                                    serv_conn.sendall(ind_name.encode('utf-8'))

                                    serv_conn.sendall(
                                        str(len(grp_name)).zfill(3).encode('utf-8'))
                                    serv_conn.sendall(grp_name.encode('utf-8'))

                                    serv_conn.sendall(
                                        str(size).zfill(4).encode('utf-8'))
                                    for elem in msg:
                                        serv_conn.sendall(elem)
                                    available[serv_connected] = True

                                column = "member"+f"{num_present+1}"
                                update_query = f"UPDATE GROUPS SET {column} = '{ind_name}', number = number + 1  WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                                cur.execute(update_query)
                                dbconn.commit()
                                conn.sendall("y".encode('utf-8'))

                            except:
                                conn.sendall("n".encode('utf-8'))

                # remove individual
                elif code == "ri":
                    # getting group nam
                    grp_name = message[1]
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                    cur.execute(find_grp)
                    entry_grp = cur.fetchone()
                    ind_name = message[2]

                    try:
                        # the group exists
                        index = entry_grp[25:].index(ind_name)
                        num_present = entry_grp[23]
                        column1 = "member"+f"{index+2}"
                        column2 = "member"+f"{num_present}"
                        column3 = "pvt_key"+f"{index+2}"
                        column4 = "pvt_key"+f"{num_present}"
                        update_query = f"UPDATE GROUPS SET {column1} = {column2}, {column3} = {column4}, NUMBER = {num_present-1} WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                        cur.execute(update_query)
                        dbconn.commit()
                        update_query = f"UPDATE GROUPS SET {column2} = NULL, {column4} = NULL WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                        cur.execute(update_query)
                        dbconn.commit()
                        out = "y".encode('utf-8')  # pre.
                        conn.sendall(out)
                    except:
                        # the group does not exist
                        out = "n".encode('utf-8')  # not-pre.
                        conn.sendall(out)

                elif code == "sa":
                    # see all individuals of a group
                    # an admin privelege only
                    grp_name = message[1]
                    find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{grp_name}' AND ADMIN = '{username}' "
                    cur.execute(find_grp)
                    entry_grp = cur.fetchone()
                    conn.sendall("s".encode('utf-8'))
                    try:
                        members = ''
                        for m in entry_grp[24:24+entry_grp[23]]:
                            members = members + m + ':'
                        members = members[:-1]
                        conn.sendall(members.encode('utf-8'))
                    except:
                        conn.sendall('n'.encode('utf-8'))

                elif code == "wg":
                    # write message in a group
                    to_grp = message[1]
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    size = int(conn.recv(4).decode('utf-8'))
                    iter = size//86
                    msg = []
                    for i in range(iter):
                        msg.append(conn.recv(128))
                    if not size % 86 == 0:
                        msg.append(conn.recv(128))

                    try:
                        # select the entry of the group with the group name
                        # assuming that group name is unique
                        find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{to_grp}'"
                        cur.execute(find_grp)
                        entry_grp = cur.fetchone()

                        # iterating for all users in the group
                        for to_usr in entry_grp[24:24 + entry_grp[23]]:
                            if to_usr == username:
                                continue

                            index = entry_grp[24:24 +
                                              entry_grp[23]].index(to_usr)

                            # send message only to those who have generated their group private key
                            if entry_grp[3+index] == None:
                                continue

                            pvt_key = bytes(entry_grp[3+index])
                            lock.acquire()

                            # getting the server connected to the client
                            lb.sendall("cs".encode('utf-8'))
                            lb.sendall(str(len(to_usr)).zfill(
                                3).encode('utf-8'))
                            lb.sendall(to_usr.encode('utf-8'))
                            ip_len = int(lb.recv(3).decode('utf-8'))
                            serv_connected = lb.recv(ip_len).decode('utf-8')
                            # lb_free = True
                            lock.release()

                            if (serv_connected == f"('{IP_address}', {Port})"):
                                # Recieving user is active
                                username_conn[to_usr].sendall(
                                    'g'.encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    str(len(pvt_key)).zfill(4).encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    pvt_key)

                                username_conn[to_usr].sendall(
                                    str(len(username)).zfill(3).encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    username.encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    str(len(grp_name)).zfill(3).encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    grp_name.encode('utf-8'))

                                username_conn[to_usr].sendall(
                                    str(size).zfill(4).encode('utf-8'))

                                for elem in msg:
                                    username_conn[to_usr].sendall(elem)

                            elif serv_connected == "n":
                                # check table
                                # if the receiving user is inactive
                                dt = datetime.datetime.now()
                                to_store = b''.join(msg)
                                postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, GRP, SIZE, PVT_KEY) VALUES ('{username}', '{to_usr}', '{dt}', decode('{to_store.hex()}', 'hex'), '{grp_name}', {str(size)}, decode('{pvt_key.hex()}', 'hex'));'''
                                cur.execute(postgres_insert_query)
                                dbconn.commit()

                            else:
                                # if the receiving user is connected to some other server
                                serv_conn = fellow_servers[serv_connected]
                                while (available[serv_connected] == False):
                                    continue

                                available[serv_connected] = False
                                # send code, encrypted private key,
                                # username of receiver, group name
                                # to the receiver
                                serv_conn.sendall("wg".encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(pvt_key)).zfill(4).encode('utf-8'))

                                serv_conn.sendall(
                                    pvt_key)

                                serv_conn.sendall(
                                    str(len(to_usr)).zfill(3).encode('utf-8')
                                )
                                serv_conn.sendall(to_usr.encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(username)).zfill(3).encode('utf-8'))
                                serv_conn.sendall(username.encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(to_grp)).zfill(3).encode('utf-8'))

                                serv_conn.sendall(to_grp.encode('utf-8'))

                                serv_conn.sendall(
                                    str(size).zfill(4).encode('utf-8'))
                                for elem in msg:
                                    serv_conn.sendall(elem)
                                available[serv_connected] = True
                        # grp msg was sent successfully
                        conn.sendall("y".encode('utf-8'))
                    except Exception as e:
                        # unable to send image
                        conn.sendall("n".encode('utf-8'))

                # send an image in group
                elif code == "ig":
                    to_grp = message[1]
                    to_continue = conn.recv(2).decode('utf-8')

                    if to_continue == "ab":
                        continue
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    # receiving extension, size
                    # and computing iters
                    # that is the number of packets in which the message would be sent
                    ext = conn.recv(
                        int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                    size = int(
                        conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                    iter = size//86
                    msg = []
                    for i in range(iter):
                        msg.append(conn.recv(128))
                    if not size % 86 == 0:
                        msg.append(conn.recv(128))
                    try:
                        # selecting entry of database with that group name
                        find_grp = f"SELECT * FROM GROUPS WHERE NAME = '{to_grp}'"
                        cur.execute(find_grp)
                        entry_grp = cur.fetchone()

                        # iterating for all members in the group
                        for to_usr in entry_grp[24:24 + entry_grp[23]]:
                            if to_usr == username:
                                continue
                            # getting the index
                            index = entry_grp[24:24 +
                                              entry_grp[23]].index(to_usr)

                            # send message only to those who have generated their group private key
                            if entry_grp[3+index] == None:
                                continue

                            pvt_key = bytes(entry_grp[3+index])

                            lock.acquire()

                            lb.sendall("cs".encode('utf-8'))
                            lb.sendall(str(len(to_usr)).zfill(
                                3).encode('utf-8'))
                            lb.sendall(to_usr.encode('utf-8'))
                            ip_len = int(lb.recv(3).decode('utf-8'))
                            serv_connected = lb.recv(ip_len).decode('utf-8')
                            lock.release()

                            # cases depending on the state of the client

                            if (serv_connected == f"('{IP_address}', {Port})"):
                                # Recieving user is active
                                username_conn[to_usr].sendall(
                                    'a'.encode('utf-8'))
                                username_conn[to_usr].sendall(
                                    str(len(pvt_key)).zfill(4).encode('utf-8'))
                                username_conn[to_usr].sendall(pvt_key)
                                username_conn[to_usr].sendall(
                                    str(len(to_usr)).zfill(3).encode('utf-8'))
                                username_conn[to_usr].sendall(
                                    to_usr.encode('utf-8'))
                                username_conn[to_usr].sendall(
                                    str(len(grp_name)).zfill(3).encode('utf-8'))
                                username_conn[to_usr].sendall(
                                    grp_name.encode('utf-8'))
                                username_conn[to_usr].sendall(
                                    str(len(ext)).zfill(1).encode('utf-8'))
                                username_conn[to_usr].sendall(
                                    ext.encode('utf-8'))
                                username_conn[to_usr].sendall(
                                    str(len(str(size))).zfill(2).encode('utf-8'))
                                username_conn[to_usr].sendall(
                                    str(size).encode('utf-8'))
                                for elem in msg:
                                    username_conn[to_usr].sendall(elem)

                            elif (serv_connected == "n"):
                                # check table
                                # if the user is inactive
                                dt = datetime.datetime.now()
                                to_store = b''.join(msg)
                                postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, GRP, EXTENSION, SIZE, PVT_KEY) VALUES ('{username}', '{to_usr}', '{dt}', decode('{bytes(to_store).hex()}', 'hex'), '{grp_name}', '{ext}', {str(size)}, decode('{pvt_key.hex()}', 'hex'));'''
                                cur.execute(postgres_insert_query)
                                dbconn.commit()

                            else:
                                # if the receiver is a client connected to some other server
                                serv_conn = fellow_servers[serv_connected]
                                while (available[serv_connected] == False):
                                    continue
                                available[serv_connected] = False
                                serv_conn.sendall("ig".encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(pvt_key)).zfill(4).encode('utf-8'))
                                serv_conn.sendall(pvt_key)

                                serv_conn.sendall(
                                    str(len(to_usr)).zfill(3).encode('utf-8'))
                                serv_conn.sendall(to_usr.encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(username)).zfill(3).encode('utf-8'))
                                serv_conn.sendall(username.encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(grp_name)).zfill(3).encode('utf-8'))
                                serv_conn.sendall(grp_name.encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(ext)).zfill(1).encode('utf-8'))
                                serv_conn.sendall(ext.encode('utf-8'))

                                serv_conn.sendall(
                                    str(len(str(size))).zfill(2).encode('utf-8'))
                                serv_conn.sendall(str(size).encode('utf-8'))
                                for elem in msg:
                                    serv_conn.sendall(elem)
                                available[serv_connected] = True
                        # message was successfully sent
                        conn.sendall("y".encode('utf-8'))
                    except:
                        # failed to send message successfully
                        conn.sendall("n".encode('utf-8'))

                # send a text to an individual
                elif code == "wi":
                    to_usr = message[1]
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    # Updated the max limit of message
                    size = int(conn.recv(4).decode('utf-8'))
                    # dividing a long message into portions that can be sent
                    iter = size//86
                    msg = []
                    for i in range(iter):
                        msg.append(conn.recv(128))
                    if not size % 86 == 0:
                        msg.append(conn.recv(128))
                    try:
                        # Need to get the public key of the fellow
                        lock.acquire()
                        lb.sendall("cs".encode('utf-8'))
                        lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                        lb.sendall(ind_name.encode('utf-8'))
                        ip_len = int(lb.recv(3).decode('utf-8'))
                        serv_connected = lb.recv(ip_len).decode('utf-8')
                        lock.release()

                        if (serv_connected == f"('{IP_address}', {Port})"):
                            # Recieving user is active
                            username_conn[to_usr].sendall('u'.encode('utf-8'))

                            username_conn[to_usr].sendall(
                                str(len(username)).zfill(3).encode('utf-8'))

                            username_conn[to_usr].sendall(
                                username.encode('utf-8'))

                            username_conn[to_usr].sendall(
                                str(size).zfill(4).encode('utf-8'))
                            for elem in msg:
                                username_conn[to_usr].sendall(elem)

                        elif (serv_connected == "n"):
                            # check table
                            # Receiving user is inactive
                            dt = datetime.datetime.now()
                            to_store = b''.join(msg)
                            postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, SIZE) VALUES ('{username}', '{to_usr}', '{dt}', decode('{to_store.hex()}', 'hex'), {str(size)});'''

                            cur.execute(postgres_insert_query)
                            dbconn.commit()

                        else:
                            # the receiving client is connected to another server
                            serv_conn = fellow_servers[serv_connected]
                            while (available[serv_connected] == False):
                                continue
                            available[serv_connected] = False
                            serv_conn.sendall("wi".encode('utf-8'))
                            serv_conn.sendall(
                                str(len(to_usr)).zfill(3).encode('utf-8'))
                            serv_conn.sendall(to_usr.encode('utf-8'))
                            serv_conn.sendall(
                                str(len(username)).zfill(3).encode('utf-8'))
                            serv_conn.sendall(username.encode('utf-8'))
                            serv_conn.sendall(
                                str(size).zfill(4).encode('utf-8'))
                            for elem in msg:
                                serv_conn.sendall(elem)
                            available[serv_connected] = True

                        # message sent successfully
                        conn.sendall("y".encode('utf-8'))

                    except:
                        # message failed to send
                        conn.sendall("n".encode('utf-8'))

                # send an image to individual
                elif code == "ii":
                    to_usr = message[1]
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    to_continue = conn.recv(2).decode('utf-8')
                    if to_continue == "ab":
                        continue
                    ext = conn.recv(
                        int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                    size = int(
                        conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                    iter = size//86
                    msg = []
                    for i in range(iter):
                        msg.append(conn.recv(128))
                    if not size % 86 == 0:
                        msg.append(conn.recv(128))

                    try:
                        # Need to get the public key of the fellow
                        lock.acquire()
                        lb.sendall("cs".encode('utf-8'))
                        lb.sendall(str(len(ind_name)).zfill(3).encode('utf-8'))
                        lb.sendall(ind_name.encode('utf-8'))
                        ip_len = int(lb.recv(3).decode('utf-8'))
                        serv_connected = lb.recv(ip_len).decode('utf-8')
                        lock.release()
                        # lb_free = True

                        if (serv_connected == f"('{IP_address}', {Port})"):
                            # Recieving user is active
                            username_conn[to_usr].sendall('b'.encode('utf-8'))
                            username_conn[to_usr].sendall(
                                str(len(username)).zfill(3).encode('utf-8'))
                            username_conn[to_usr].sendall(
                                username.encode('utf-8'))
                            username_conn[to_usr].sendall(
                                str(len(ext)).zfill(1).encode('utf-8'))
                            username_conn[to_usr].sendall(ext.encode('utf-8'))
                            username_conn[to_usr].sendall(
                                str(len(str(size))).zfill(2).encode('utf-8'))
                            username_conn[to_usr].sendall(
                                str(size).encode('utf-8'))
                            for elem in msg:
                                username_conn[to_usr].sendall(elem)

                        elif (serv_connected == "n"):
                            # check table
                            # Receiving client is inactive
                            dt = datetime.datetime.now()
                            to_store = b''.join(msg)
                            postgres_insert_query = f'''INSERT INTO IND_MSG (SENDER, RECEIVER, TIME, MESSAGE, GRP, EXTENSION, SIZE) VALUES ('{username}', '{to_usr}', '{dt}', decode('{bytes(to_store).hex()}', 'hex'), NULL, '{ext}', {str(size)});'''
                            cur.execute(postgres_insert_query)
                            dbconn.commit()

                        else:
                            # Receiving client is connected to another server
                            serv_conn = fellow_servers[serv_connected]
                            while (available[serv_connected] == False):
                                continue
                            available[serv_connected] = False
                            serv_conn.sendall("ii".encode('utf-8'))

                            serv_conn.sendall(
                                str(len(to_usr)).zfill(3).encode('utf-8'))
                            serv_conn.sendall(to_usr.encode('utf-8'))

                            serv_conn.sendall(
                                str(len(username)).zfill(3).encode('utf-8'))
                            serv_conn.sendall(username.encode('utf-8'))

                            serv_conn.sendall(
                                str(len(ext)).zfill(1).encode('utf-8'))
                            serv_conn.sendall(ext.encode('utf-8'))

                            serv_conn.sendall(
                                str(len(str(size))).zfill(2).encode('utf-8'))
                            serv_conn.sendall(str(size).encode('utf-8'))
                            for elem in msg:
                                serv_conn.sendall(elem)
                            available[serv_connected] = True

                        conn.sendall("y".encode('utf-8'))
                    except:
                        conn.sendall("n".encode('utf-8'))
            except:
                continue

    else:
        # Handle fellow server's requests

        # Lets store for whom this server is made for as tuple
        address = conn.recv(int(conn.recv(3).decode('utf-8'))).decode('utf-8')
        # Update your dictionary
        fellow_servers[address] = conn
        available[address] = True

        # Start the read of infinte while loop here
        # Make infinte while recieve loop
        while True:
            code = conn.recv(2).decode('utf-8')
            # Send a message to individual
            if code == "wi":
                to_usr = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                from_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(4).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size % 86 == 0:
                    msg.append(conn.recv(128))

                # Lets send the message to the user
                uss_conn = username_conn[to_usr]
                uss_conn.sendall("u".encode('utf-8'))

                uss_conn.sendall(str(len(from_user)).zfill(3).encode('utf-8'))
                uss_conn.sendall(from_user.encode('utf-8'))

                username_conn[to_usr].sendall(
                    str(size).zfill(4).encode('utf-8'))
                for elem in msg:
                    username_conn[to_usr].sendall(elem)

            elif code == "ii":
                # send an image to individual
                to_usr = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                from_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                ext = conn.recv(
                    int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                size = int(
                    conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size % 86 == 0:
                    msg.append(conn.recv(128))

                username_conn[to_usr].sendall('b'.encode('utf-8'))
                username_conn[to_usr].sendall(
                    str(len(from_user)).zfill(3).encode('utf-8'))
                username_conn[to_usr].sendall(from_user.encode('utf-8'))
                username_conn[to_usr].sendall(
                    str(len(ext)).zfill(1).encode('utf-8'))
                username_conn[to_usr].sendall(ext.encode('utf-8'))
                username_conn[to_usr].sendall(
                    str(len(str(size))).zfill(2).encode('utf-8'))
                username_conn[to_usr].sendall(str(size).encode('utf-8'))
                for elem in msg:
                    username_conn[to_usr].sendall(elem)

            elif code == "wg":
                # sending a message in group
                pvt_key = conn.recv(
                    int(conn.recv(4).decode('utf-8')))
                to_usr = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                from_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                to_grp = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(4).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size % 86 == 0:
                    msg.append(conn.recv(128))

                # Lets send the message to the user
                uss_conn = username_conn[to_usr]
                uss_conn.sendall("g".encode('utf-8'))

                uss_conn.sendall(str(len(pvt_key)).zfill(4).encode('utf-8'))
                uss_conn.sendall(pvt_key)

                uss_conn.sendall(str(len(from_user)).zfill(3).encode('utf-8'))
                uss_conn.sendall(from_user.encode('utf-8'))

                uss_conn.sendall(str(len(to_grp)).zfill(3).encode('utf-8'))
                uss_conn.sendall(to_grp.encode('utf-8'))

                uss_conn.sendall(str(size).zfill(4).encode('utf-8'))
                for elem in msg:
                    uss_conn.sendall(elem)

            # sending an image in a group
            elif code == "ig":
                pvt_key = conn.recv(
                    int(conn.recv(4).decode('utf-8')))

                to_usr = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                from_user = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                to_grp = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')

                ext = conn.recv(
                    int(conn.recv(1).decode('utf-8'))).decode('utf-8')
                size = int(
                    conn.recv(int(conn.recv(2).decode('utf-8'))).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size % 86 == 0:
                    msg.append(conn.recv(128))

                # sending encrypted privat key, sender name, group name to
                # members of the group
                username_conn[to_usr].sendall('a'.encode('utf-8'))
                username_conn[to_usr].sendall(
                    str(len(pvt_key)).zfill(4).encode('utf-8'))
                username_conn[to_usr].sendall(pvt_key)
                username_conn[to_usr].sendall(
                    str(len(from_user)).zfill(3).encode('utf-8'))
                username_conn[to_usr].sendall(from_user.encode('utf-8'))
                username_conn[to_usr].sendall(
                    str(len(to_grp)).zfill(3).encode('utf-8'))
                username_conn[to_usr].sendall(to_grp.encode('utf-8'))
                username_conn[to_usr].sendall(
                    str(len(ext)).zfill(1).encode('utf-8'))
                username_conn[to_usr].sendall(ext.encode('utf-8'))
                username_conn[to_usr].sendall(
                    str(len(str(size))).zfill(2).encode('utf-8'))
                username_conn[to_usr].sendall(str(size).encode('utf-8'))
                for elem in msg:
                    username_conn[to_usr].sendall(elem)

            # sending group key to the clients connected to this server
            elif code == "gk":
                to_usr = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                for_grp = conn.recv(
                    int(conn.recv(3).decode('utf-8'))).decode('utf-8')
                size = int(conn.recv(4).decode('utf-8'))
                iter = size//86
                msg = []
                for i in range(iter):
                    msg.append(conn.recv(128))
                if not size % 86 == 0:
                    msg.append(conn.recv(128))

                # Lets send the message to the user
                uss_conn = username_conn[to_usr]
                uss_conn.sendall("k".encode('utf-8'))
                username_conn[to_usr].sendall(
                    str(len(for_grp)).zfill(3).encode('utf-8'))
                username_conn[to_usr].sendall(for_grp.encode('utf-8'))
                username_conn[to_usr].sendall(
                    str(size).zfill(4).encode('utf-8'))
                for elem in msg:
                    username_conn[to_usr].sendall(elem)


# The following function simply removes the object
# from the list that was created at the beginning of
# the program


def remove(connection, usr):
    '''
    Removes the connection of the user with the server and loadbalancer that is change the status of the user from online to offline
    The entry in the dictionary with the key as the username of the user is deleted from both the server to which the client is connected and the loadbalancer

    :param connection: Connection with the user which has logged out which needs to be removed
    :type connection: socket.socket
    :param usr: The username of the user who has logged out
    :type usr: str
    '''
    # client logs out
    del username_conn[usr]
    # while (lb_free == False):
    #     continue
    lock.acquire()
    # lb_free = False
    lb.sendall("cl".encode('utf-8'))
    lb.sendall(str(len(usr)).zfill(3).encode('utf-8'))
    lb.sendall(usr.encode('utf-8'))
    lock.release()
    # lb_free = True


'''
    Accepts a connection request and stores two parameters,
    conn which is a socket object for that user, and addr
    which contains the IP address of the client that just
    connected
    It also initiates the client thread
'''

while True:

    # Accepts a connection request and stores two parameters,
    # conn which is a socket object for that user, and addr
    # which contains the IP address of the client that just
    # connected
    conn, addr = server.accept()

    # creates and individual thread for every user
    # that connects
    start_new_thread(clientthread, (conn, addr))

dbconn.close()
conn.close()
server.close()

file.close()
