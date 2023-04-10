# Python program to implement client side of chat room.
from ast import For
import importlib
from operator import truediv
import colorama
from colorama import Fore
import socket
import select
import sys
import threading
from passlib.hash import sha256_crypt
import rsa
import cryptocode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os
import datetime
import re

from _thread import *
lock = threading.Lock()

# these are the allowed extensions
allowed_ext = [".png", ".jpg", ".jpeg", ".txt"]
counter = int(''.join(re.findall(r'\d+', str(datetime.datetime.utcnow()))))

# these are the menus that are to be displpayed
menu_option = []
menu_option.append(f"{Fore.GREEN}***** Main Menu *****\n{Fore.CYAN}Press {Fore.RED}'g' {Fore.CYAN}for managing groups\nPress {Fore.RED}'b' {Fore.CYAN}to send group message\nPress {Fore.RED}'d' {Fore.CYAN}to send direct message\nPress {Fore.RED}'l' {Fore.CYAN}to logout\n")
menu_option.append(f"{Fore.GREEN}***** Group Settings *****\n{Fore.CYAN}Press {Fore.RED}'n' {Fore.CYAN}to create a new group\nPress {Fore.RED}'m' {Fore.CYAN}to manage an existing group\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n")
menu_option.append(f"{Fore.GREEN}***** Manage Existing Group *****\n{Fore.CYAN}Press {Fore.RED}'a' {Fore.CYAN}to add a new member\nPress {Fore.RED}'r' {Fore.CYAN}to remove a member\nPress {Fore.RED}'s' {Fore.CYAN}to see all members in the group\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n")
menu_option.append(f"{Fore.GREEN}***** Group message *****\n{Fore.CYAN}Press {Fore.RED}'t' {Fore.CYAN}to type a message\nPress {Fore.RED}'i' {Fore.CYAN}to send an image or text file\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n")
menu_option.append(f"{Fore.GREEN}***** Direct message *****\n{Fore.CYAN}Press {Fore.RED}'t' {Fore.CYAN}to type a message\nPress {Fore.RED}'i' {Fore.CYAN}to send an image or text file\nPress {Fore.RED}'q' {Fore.CYAN}to go to previous menu\n")

# menu for input options
inp_option = []
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter group name to manage: ")
inp_option.append(
    f"{Fore.LIGHTMAGENTA_EX}Enter username to add to the group: ")
inp_option.append(
    f"{Fore.LIGHTMAGENTA_EX}Enter username to remove from the group: ")
inp_option.append(f"{Fore.LIGHTMAGENTA_EX}Enter group name to create: ")
inp_option.append(
    f"{Fore.LIGHTMAGENTA_EX}Enter group name to which you want to send message: ")
inp_option.append(
    f"{Fore.LIGHTMAGENTA_EX}Enter username to whom you want to send message: ")

# initialising server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print(Fore.RED + "Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])

# Initially connected to load balancer, after getting the server address we will
# remove the connection with the load balancer
server.connect((IP_address, Port))

# initialising global variables
group = ""
user = ""
confirm = ""
to_public = ""
prvt_key = ""
grp_prvt_keys = {}
grp_key_str = ""
usr = ""

last = -1

# defining the user interface


def user_interface(display_menu=0):
    '''
    Function to display the user interface
    It is the thread for sending information to the server
    Different user intefaces are displayed as per the value of the display_menu parameter
    The parameter display_menu can take the following values and the following options are displayed as per the value of the display_menu:

        |  1. display_menu = 0 : Main Menu

            |  1. g: for managing groups
            |  2. b: to send group message
            |  3. d: to send direct message
            |  4. l: to logout

        |  2. display_menu = 1 : Group Settings

            |  1. n: to create a new group
            |  2. m: to manage an existing group
            |  3. q: to go to previous menu

        |  3. display_menu = 2 : Manage Existing Group

            |  1. a: to add a new member
            |  2. r: to remove a member
            |  3. s: to see all members in the group
            |  4. q: to go to previous menu

        |  4. display_menu = 3 : Group message

            |  1. t: to type a message
            |  2. i: to send an image or text file
            |  3: q: to go to previous menu

        |  5. display_menu = 4 : Direct message

            |  1. t: to type a message
            |  2. i: to send an image or text file
            |  3. q: to go to previous menu

    :param display_menu: contains information about which display menu is to be shown
    :type display_menu: int
    '''
    global confirm, last, to_public, prvt_key, grp_key_str, usr
    while (True):
        choice = input(menu_option[display_menu] + Fore.RED)
        if display_menu == 0:

            # to manage group settings
            if choice == 'g':
                display_menu = 1

            # to send group message
            elif choice == 'b':
                grp_name = input(inp_option[4] + Fore.MAGENTA)
                to_send = "{}:{}:{}".format(
                    "cg", grp_name, usr).encode('utf-8')

                # checking limit
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)

                while (last == 1):
                    continue
                lock.acquire()
                last = 1

                # if message is sent
                if (confirm == "y"):
                    confirm = "n"
                    group = grp_name
                    display_menu = 3

                # in case no group is found
                else:
                    print(f"{Fore.RED}No group found\n")
                lock.release()

            # to send direct message
            elif choice == 'd':
                ind_name = input(inp_option[5] + Fore.MAGENTA)
                to_send = "{}:{}".format("ci", ind_name).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1

                # if message is sent successfully
                if (confirm == "y"):
                    confirm = "n"
                    user = ind_name
                    display_menu = 4

                # if user is not found
                else:
                    print(f"{Fore.RED}No user found\n")
                lock.release()

            # to logout
            elif choice == 'l':
                to_send = "quit".encode('utf-8')
                server.sendall(to_send)
                return

            # if the entered option is invalid
            else:
                print(f"{Fore.RED}Invalid option")

        # display menu is 1
        elif display_menu == 1:
            # to create a new group
            if choice == 'n':
                # sending group name to server to verify if that grp_name exists
                grp_name = input(inp_option[3] + Fore.MAGENTA)
                to_send = "{}:{}".format("ng", grp_name).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # generating private and public keys of group
                key = RSA.generate(1024)
                grp_pub_key_str = key.publickey().exportKey('PEM')
                grp_priv_key_str = key.exportKey('PEM')
                encrypted_pvt_key = cryptocode.encrypt(
                    grp_priv_key_str.decode(), pwd)

                # Sending the encrypted private key and public key to server
                server.sendall(
                    str(len(grp_pub_key_str)).zfill(4).encode('utf-8'))
                server.sendall(grp_pub_key_str)
                server.sendall(str(len(encrypted_pvt_key)
                                   ).zfill(4).encode('utf-8'))
                server.sendall(encrypted_pvt_key.encode('utf-8'))
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                # if no group with same name exists
                if (confirm == "y"):
                    confirm = "n"
                    grp_prvt_keys[grp_name] = grp_priv_key_str
                    print(f"{Fore.GREEN}New group created\n")

                # group already exists
                else:
                    print(f"{Fore.RED}Group already exists\n")
                lock.release()

            # to manage group settings
            elif choice == 'm':
                grp_name = input(inp_option[0] + Fore.MAGENTA)
                to_send = "{}:{}".format("eg", grp_name).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                # if the person is the admin of the group
                if (confirm == "y"):
                    confirm = "n"
                    group = grp_name
                    display_menu = 2
                else:
                    print(f"{Fore.RED}No group with admin priveleges found\n")
                lock.release()

            # return to previous menu
            elif choice == 'q':
                display_menu = 0

            # invalud menu option
            else:
                print(f"{Fore.RED}Invalid option")

        # next display menu
        elif display_menu == 2:
            # add new member
            if choice == 'a':
                ind_name = input(inp_option[1] + Fore.MAGENTA)
                to_send = "{}:{}:{}".format(
                    "ai", group, ind_name).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                co = 0
                # is username exists
                if (confirm == "y"):
                    confirm = "n"
                    co = 1
                # max capacity of group is reached
                elif confirm == "l":
                    print(f"{Fore.RED}Group size limit reached\n")
                # user already in group
                elif confirm == "t":
                    print(f"{Fore.RED}User already in group\n")
                else:
                    print(f"{Fore.RED}No user found\n")
                lock.release()
                if co == 1:
                    # importing public key in string format and transfering it
                    public = RSA.importKey(to_public)
                    public = PKCS1_OAEP.new(public)
                    while (last == 1):
                        continue
                    # state locking
                    lock.acquire()
                    last = 1
                    lock.release()
                    size = len(grp_key_str)
                    # sending encrypted group key string to server
                    server.sendall(str(size).zfill(4).encode('utf-8'))
                    iter = size//86
                    for i in range(iter):
                        data = public.encrypt(
                            grp_key_str[i*86:(i+1)*86].encode())
                        server.sendall(data)
                    # dividing package into sizes to send to server
                    if not size % 86 == 0:
                        data = public.encrypt(grp_key_str[iter*86:].encode())
                        server.sendall(data)

                    # receiving message from server
                    while (last == 1):
                        continue
                    lock.acquire()
                    last = 1
                    if (confirm == "y"):
                        confirm = "n"
                        print(f"{Fore.GREEN}User added\n")
                    elif confirm == "l":
                        print(f"{Fore.RED}Group size limit reached\n")
                    elif confirm == "t":
                        print(f"{Fore.RED}User already in group\n")
                    else:
                        # set for all confirm messages
                        print(f"{Fore.RED}No user found\n")
                    lock.release()

            # remove person from group
            elif choice == 'r':
                ind_name = input(inp_option[2] + Fore.MAGENTA)
                to_send = "{}:{}:{}".format(
                    "ri", group, ind_name).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                # user removed
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}User removed\n")
                else:
                    # admin can't be removed and also user not present in group can't be removed
                    print(
                        f"{Fore.RED}No non-admin user found in group with given username\n")
                lock.release()

            # see all members of group is only an admin pivelege
            elif choice == 's':
                to_send = "{}:{}".format("sa", group).encode('utf-8')
                server.sendall(to_send)

                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                confirm = "n"
                lock.release()

            # return to previous menu
            elif choice == 'q':
                display_menu = 1

            # invalid option
            else:
                print(f"{Fore.RED}Invalid option")

        # next display menu
        elif display_menu == 3:
            # user chooses to type
            if choice == 't':
                # sending text in group
                to_send = "wg:{}".format(group).encode('utf-8')
                server.sendall(to_send)
                msg = input(
                    Fore.GREEN + "Please type your message:\n" + Fore.WHITE)
                public = RSA.importKey(to_public)
                public = PKCS1_OAEP.new(public)
                msg = msg.encode('utf-8')

                # if exceeded max length
                if (len(to_send) > 2048):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    # abort
                    server.sendall("ab".encode('utf-8'))
                    continue

                # continue
                server.sendall("co".encode('utf-8'))
                size = len(msg)
                server.sendall(str(size).zfill(4).encode('utf-8'))

                iter = size//86
                for i in range(iter):
                    data = public.encrypt(msg[i*86:(i+1)*86])
                    server.sendall(data)

                if not size % 86 == 0:
                    data = public.encrypt(msg[iter*86:])
                    server.sendall(data)

                file = open("logs.txt", "a")
                file.write(
                    f"{usr} sentTextTo group {group} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
                file.close()

                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                # confirmation received
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    print(f"{Fore.RED}Message failed to send\n")
                lock.release()

            elif choice == 'i':
                # to send image
                to_send = "{}:{}".format("ig", group).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                # asking for address
                img_add = input(
                    f"{Fore.GREEN}Give complete address of image or text file from current working directory:\n" + Fore.MAGENTA)
                split_path = os.path.splitext(img_add)
                if not split_path[1] in allowed_ext:
                    print(f"{Fore.RED}Extension not supported\n")
                    server.sendall("ab".encode('utf-8'))
                    continue
                server.sendall("co".encode('utf-8'))
                try:
                    # open file
                    myfile = open(img_add, 'rb')
                    bytes = myfile.read()
                    size = len(bytes)
                except:
                    print(f"{Fore.RED}Error in loading the file\n")
                    server.sendall("ab".encode('utf-8'))
                    continue
                server.sendall("co".encode('utf-8'))
                public = RSA.importKey(to_public)
                public = PKCS1_OAEP.new(public)

                # sending image in encrypted format
                server.sendall(
                    str(len(split_path[1])).zfill(1).encode('utf-8'))
                server.sendall(split_path[1].encode('utf-8'))
                server.sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                server.sendall(str(size).encode('utf-8'))

                # splitting the image into small sizes
                iter = size//86
                for i in range(iter):
                    data = public.encrypt(bytes[i*86:(i+1)*86])
                    server.sendall(data)

                # if not divisible by 86 last bytes
                if not size % 86 == 0:
                    data = public.encrypt(bytes[iter*86:])
                    server.sendall(data)

                file = open("logs.txt", "a")
                file.write(
                    f"{usr} sentImageTo group {group} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
                file.close()
                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                # if image is sent
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    print(f"{Fore.RED}Message failed to send\n")
                lock.release()
            # if returned to previous menu
            elif choice == 'q':
                display_menu = 0

            else:
                print(f"{Fore.RED}Invalid option")

        elif display_menu == 4:
            if choice == 't':
                to_send = "wi:{}".format(user).encode('utf-8')
                server.sendall(to_send)
                msg = input(
                    Fore.GREEN + "Please type your message:\n" + Fore.WHITE)
                # encrypting using public ky of receiver
                public = RSA.importKey(to_public)
                public = PKCS1_OAEP.new(public)
                msg = msg.encode('utf-8')

                # checking if it does not exceed max length
                if (len(msg) > 2048):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    server.sendall("ab".encode('utf-8'))
                    continue

                server.sendall("co".encode('utf-8'))

                # sending length of message
                size = len(msg)
                server.sendall(str(size).zfill(4).encode('utf-8'))
                iter = size//86
                # encrtpting the message and sending it to the server
                for i in range(iter):
                    data = public.encrypt(msg[i*86:(i+1)*86])
                    server.sendall(data)

                if not size % 86 == 0:
                    data = public.encrypt(msg[iter*86:])
                    server.sendall(data)

                file = open("logs.txt", "a")
                file.write(
                    f"{usr} sentTextTo {user} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
                file.close()

                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                # to send text
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    print(f"{Fore.RED}Message failed to send\n")
                lock.release()

            # sending an image
            elif choice == 'i':
                to_send = "{}:{}".format("ii", user).encode('utf-8')
                if (len(to_send) > 512):
                    print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
                    continue
                server.sendall(to_send)
                img_add = input(
                    # taking address of image
                    f"{Fore.GREEN}Give complete address of image or text file from current working directory:\n" + Fore.MAGENTA)
                split_path = os.path.splitext(img_add)
                # if the extension is not allowed
                if not split_path[1] in allowed_ext:
                    print(f"{Fore.RED}Extension not supported\n")
                    server.sendall("ab".encode('utf-8'))
                    continue
                server.sendall("co".encode('utf-8'))
                try:
                    # reading the image file
                    myfile = open(img_add, 'rb')
                    bytes = myfile.read()
                    size = len(bytes)
                except:
                    # fie not loaded
                    print(f"{Fore.RED}Error in loading the file\n")
                    server.sendall("ab".encode('utf-8'))
                    continue
                server.sendall("co".encode('utf-8'))
                public = RSA.importKey(to_public)
                public = PKCS1_OAEP.new(public)

                # sending image to server in encrypted format
                server.sendall(
                    str(len(split_path[1])).zfill(1).encode('utf-8'))
                server.sendall(split_path[1].encode('utf-8'))
                server.sendall(str(len(str(size))).zfill(2).encode('utf-8'))
                server.sendall(str(size).encode('utf-8'))

                iter = size//86
                for i in range(iter):
                    data = public.encrypt(bytes[i*86:(i+1)*86])
                    server.sendall(data)

                if not size % 86 == 0:
                    data = public.encrypt(bytes[iter*86:])
                    server.sendall(data)

                file = open("logs.txt", "a")
                file.write(
                    f"{usr} sentImageTo {user} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
                file.close()

                while (last == 1):
                    continue
                lock.acquire()
                last = 1
                # if able to send image
                if (confirm == "y"):
                    confirm = "n"
                    print(f"{Fore.GREEN}Message sent\n")
                else:
                    # unable to send image
                    print(f"{Fore.RED}Message failed to send\n")
                lock.release()

            elif choice == 'q':
                display_menu = 0

            else:
                print(f"{Fore.RED}Invalid option")

# receiving thread from the server


def receiving_func():
    '''
    It is thread for receiving information from the server
    Depending on the code received from the server, the parameters will be changed accordingly.
    The codes received from the server have the following meaning:

        |  1. c: Receive another code from the server
        |  2. y: Message has been sent successfully
        |  3. n: Unable to send direct message
        |  4. l: Group is full and hence no further member can be added
        |  5. t: User exists already in the group
        |  6. e: Receiving public key of receiver
        |  7. k: Receiving private key of group
        |  8. p: Decrypting group private key using private key of user
        |  9. s: Server is going to send the usernames of all the members of the group to the admin
        |  10. u: Have to encrypt the message of sender using the public key of receiver sent by server and have to send it back to the server
        |  11. g: Have to encrypt the message of sender using the public key of group sent by server and send the encrypted message back to server
        |  12. a: Received an image file
        |  13. b: Sent an image file
        |  14. q: Client has logged out

    '''
    # setting variables as global
    global last, confirm, to_public, prvt_key, counter, grp_key_str
    while (True):
        while (last == 2):
            continue
        lock.acquire()
        last = 2
        msg_to_come = server.recv(1).decode('utf-8')

        # confirmation text
        if (msg_to_come == "c"):
            confirm = server.recv(1).decode('utf-8')

        # yes
        elif (msg_to_come == "y"):
            confirm = "y"
        # no
        elif (msg_to_come == "n"):
            confirm = "n"

        # group is full and hence no further member can be added
        elif (msg_to_come == "l"):
            confirm = "l"
        # user exists already in grp
        elif (msg_to_come == "t"):
            confirm = "t"
        # receiving public key
        elif (msg_to_come == "e"):
            cnf = server.recv(1).decode('utf-8')
            #not received
            if (cnf == "n"):
                confirm = "n"
            # received
            else:
                cnt = int(server.recv(4).decode('utf-8'))
                to_public = server.recv(cnt).decode('utf-8')
                confirm = "y"
        # receiving pvt key of grp
        elif (msg_to_come == "k"):
            grp = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            # receiving private key of group, decrypting with it's private key and then encrypting it with own password and sending it back to server
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            p_key = b''.join(msg)
            enc_grp_pvt_key = cryptocode.encrypt(p_key.decode(), pwd)
            to_send = "{}:{}:".format("gk", grp).ljust(
                512, '0').encode('utf-8')
            server.sendall(to_send)
            server.sendall(str(len(enc_grp_pvt_key)).zfill(4).encode('utf-8'))
            server.sendall(enc_grp_pvt_key.encode('utf-8'))
            print(Fore.GREEN + f"You were added to group: {grp}")
            last = 1

        # receiving own pvt key
        elif (msg_to_come == "p"):
            grp_key_str = server.recv(
                int(server.recv(4).decode('utf-8'))).decode('utf-8')
            grp_key_str = cryptocode.decrypt(grp_key_str, pwd)

        # see all members of a grp
        elif (msg_to_come == "s"):
            members = server.recv(2048).decode('utf-8')
            # if members not received
            if (members == 'n'):
                confirm = "n"
            else:
                # received all members of grp
                print(Fore.WHITE +
                      "The following members are present in the group:")
                members = members.split(":")
                for member in members:
                    print(Fore.YELLOW+member)
                confirm = "y"

        # direct messaging
        elif (msg_to_come == "u"):
            user = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                # decrypting the private key
                msg.append(prvt_key.decrypt(data))
            # if message is large breaking it into parts
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            file = open("logs.txt", "a")
            file.write(
                f"{usr} receivedTextFrom {user} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
            file.close()
            message = b''.join(msg)
            print(Fore.YELLOW + "<" + user + "> " + message.decode('utf-8'))
            last = 1
        # grp message
        elif (msg_to_come == "g"):
            # receiving keys from server
            g_pvt_key_str = server.recv(
                int(server.recv(4).decode('utf-8'))).decode('utf-8')
            g_pvt_key_str = cryptocode.decrypt(g_pvt_key_str, pwd)
            g_prvt_key = RSA.importKey(g_pvt_key_str.encode())
            g_prvt_key = PKCS1_OAEP.new(g_prvt_key)
            user = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            grp = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            # decrypting the message using own private key
            for i in range(iter):
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            # breaking the message into parts
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))

            file = open("logs.txt", "a")
            file.write(
                f"{usr} receivedTextFrom {user} group {grp} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
            file.close()
            message = b''.join(msg)
            print(Fore.YELLOW + "<Group: " + grp + "> " + "<User: " +
                  user + "> " + message.decode('utf-8'))
            last = 1

        # receive img in grp
        elif (msg_to_come == "a"):
            g_pvt_key_str = server.recv(
                int(server.recv(4).decode('utf-8'))).decode('utf-8')
            g_pvt_key_str = cryptocode.decrypt(g_pvt_key_str, pwd)
            g_prvt_key = RSA.importKey(g_pvt_key_str.encode())
            g_prvt_key = PKCS1_OAEP.new(g_prvt_key)
            user = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            grp = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            ext = server.recv(
                int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(
                int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))

            file = open("logs.txt", "a")
            file.write(
                f"{usr} receivedImageFrom {user} group {grp} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
            file.close()
            message = b''.join(msg)
            print(Fore.YELLOW + "<Group: " + grp + "> " + "<User: " + user + "> " +
                  "Sent a file which is placed at " + f"__received__{usr}__/{grp}_{user}_{counter}{ext}")
            if not os.path.exists(f"__received__{usr}__"):
                os.makedirs(f"__received__{usr}__")
            myfile = open(
                f"__received__{usr}__/{grp}_{user}_{counter}{ext}", 'wb')
            myfile.write(message)
            myfile.close()
            counter += 1
            last = 1

        # individual img
        elif (msg_to_come == "b"):
            user = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            ext = server.recv(
                int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(
                int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))

            file = open("logs.txt", "a")
            file.write(
                f"{usr} receivedImageFrom {user} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
            file.close()
            message = b''.join(msg)
            print(Fore.YELLOW + "<" + user + "> " + "Sent a file which is placed at " +
                  f"__received__{usr}__/{user}_{counter}{ext}")
            if not os.path.exists(f"__received__{usr}__"):
                os.makedirs(f"__received__{usr}__")
            myfile = open(f"__received__{usr}__/{user}_{counter}{ext}", 'wb')
            myfile.write(message)
            myfile.close()
            counter += 1
            last = 1

        elif (msg_to_come == "q"):
            print(Fore.GREEN+"Logged out successfully")
            return

        lock.release()


'''
    This is the main function
    Firstly, a socket connection is initiated between loadbalancer and client, when the user logs in, a server is alloted to it.
    Client disconnects its connection with the loadbalancer and a socket connection is initiated between the client and the server alloted to it
    All the messages received by the client while it was offline are displayed and receiving and sending threads are initiated.
'''
success = False
server.sendall("c".encode('utf-8'))
while not success:
    try:
        # showing the menu
        x = int(
            input(f"{Fore.MAGENTA}1. Login\n2. Sign Up\n3. Quit\n{Fore.YELLOW}"))
    except:
        print(f"{Fore.RED}Invalid option\n")
        continue

    # login
    if x == 1:
        usr = input(f"{Fore.CYAN}Enter user name: ")
        pwd = input(f"{Fore.CYAN}Enter your password: ")
        to_send = "{}:{}:{}".format(1, usr, pwd).encode('utf-8')
        if (len(to_send) > 512):
            print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
            continue
        server.sendall(to_send)
        user_found = server.recv(1).decode('utf-8')
        # if user exists
        if (user_found == "y"):
            encrypted_len = server.recv(4)
            password = server.recv(
                int(encrypted_len.decode('utf-8'))).decode('utf-8')
            # verify if the password is correct
            if (sha256_crypt.verify(pwd, password)):
                success = True
                server.sendall(bytes("y", 'utf-8'))
                private_key_str = server.recv(
                    int(server.recv(4).decode('utf-8'))).decode('utf-8')

                # encrypting the private key and sending to server
                private_key_str = cryptocode.decrypt(private_key_str, pwd)
                prvt_key = RSA.importKey(private_key_str.encode())
                prvt_key = PKCS1_OAEP.new(prvt_key)
                file = open("logs.txt", "a")
                file.write(
                    f"{usr} loggedIn {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
                file.close()
                # successful login
                print(f"{Fore.GREEN}Successfully logged in\n")
            else:
                server.sendall(bytes("n", 'utf-8'))
                print(f"{Fore.RED}Invalid username or password\n")
        elif user_found == "n":
            print(f"{Fore.RED}Invalid username or password\n")
        else:
            print(f"{Fore.RED}Already logged in at another screen\n")

    # signup of user
    elif x == 2:
        usr = input(f"{Fore.CYAN}Enter user name: ")
        pwd = input(f"{Fore.CYAN}Enter your password: ")
        to_send = "{}:{}:{}".format(
            2, usr, sha256_crypt.hash(pwd)).encode('utf-8')
        if (len(to_send) > 1024):
            print(f"{Fore.RED}Exceeded maximum length \nRetry\n")
            continue
        server.sendall(to_send)
        confirm = server.recv(1)
        confirm = confirm.decode('utf-8')
        if (confirm == "y"):
            # is user is signed up then keys are generated
            # private key is encrypted and
            # both keys are sent to server
            key = RSA.generate(1024)
            public_key_str = key.publickey().exportKey('PEM')
            priv_key = key.exportKey('PEM')
            encrypted_pvt_key = cryptocode.encrypt(priv_key.decode(), pwd)
            server.sendall(str(len(public_key_str)).zfill(4).encode('utf-8'))
            server.sendall(public_key_str)
            server.sendall(str(len(encrypted_pvt_key)
                               ).zfill(4).encode('utf-8'))
            server.sendall(encrypted_pvt_key.encode('utf-8'))

            file = open("logs.txt", "a")
            file.write(
                f"{usr} SignedUp {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
            file.close()
            print(f"{Fore.GREEN}Successfully signed up\nPlease login\n")
        else:
            print(f"{Fore.RED}Username already taken\n")

    elif x == 3:
        to_send = "quit".encode('utf-8')
        server.sendall(to_send)
        exit()

    else:
        print(f"{Fore.RED}Invalid option\n")
# user is now logged in
server_data = eval(server.recv(
    int(server.recv(3).decode('utf-8'))).decode('utf-8'))

# Closing the connection
server.close()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connected to new server, closed the previous connection
server.connect((server_data[0], server_data[1]))
server.sendall("c".encode('utf-8'))

server.sendall(str(len(usr)).zfill(3).encode('utf-8'))
server.sendall(usr.encode('utf-8'))

# Receiving all the messages here first
num_msgs = int(server.recv(4).decode('utf-8'))
if num_msgs > 0:
    print(Fore.GREEN + "Messages received by you while you were offline are:")
    default_length = 128
    for i in range(num_msgs):
        code = server.recv(2).decode('utf-8')

        # individual text message for offline users
        if code == "in":
            user = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            message = b''.join(msg)
            file = open("logs.txt", "a")
            file.write(
                f"{usr} receivedTextFrom {user} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
            file.close()
            print(Fore.YELLOW + "<" + user + "> " + message.decode('utf-8'))

        # receiving individual image for offline users
        elif code == "iy":
            user = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            ext = server.recv(
                int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(
                int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            message = b''.join(msg)
            file = open("logs.txt", "a")
            file.write(
                f"{usr} receivedImgFrom {user} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
            file.close()
            print(Fore.YELLOW + "<" + user + "> " + "Sent a file which is placed at " +
                  f"__received__{usr}__/{user}_{counter}{ext}")
            if not os.path.exists(f"__received__{usr}__"):
                os.makedirs(f"__received__{usr}__")
            myfile = open(f"__received__{usr}__/{user}_{counter}{ext}", 'wb')
            myfile.write(message)
            myfile.close()
            counter += 1

        # grp text for offline users
        elif code == "gn":
            g_pvt_key_str = server.recv(
                int(server.recv(4).decode('utf-8'))).decode('utf-8')
            g_pvt_key_str = cryptocode.decrypt(g_pvt_key_str, pwd)
            g_prvt_key = RSA.importKey(g_pvt_key_str.encode())
            g_prvt_key = PKCS1_OAEP.new(g_prvt_key)
            user = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            grp = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            message = b''.join(msg)
            file = open("logs.txt", "a")
            file.write(
                f"{usr} receivedTextFrom {user} group {grp} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
            file.close()
            print(Fore.YELLOW + "<Group: " + grp + "> " + "<User: " +
                  user + "> " + message.decode('utf-8'))

        # grp image for offline users
        elif code == "gy":
            g_pvt_key_str = server.recv(
                int(server.recv(4).decode('utf-8'))).decode('utf-8')
            g_pvt_key_str = cryptocode.decrypt(g_pvt_key_str, pwd)
            g_prvt_key = RSA.importKey(g_pvt_key_str.encode())
            g_prvt_key = PKCS1_OAEP.new(g_prvt_key)
            user = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            grp = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            ext = server.recv(
                int(server.recv(1).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(
                int(server.recv(2).decode('utf-8'))).decode('utf-8'))
            iter = size//86
            msg = []
            for i in range(iter):
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(g_prvt_key.decrypt(data))
            message = b''.join(msg)
            file = open("logs.txt", "a")
            file.write(
                f"{usr} receivedImgFrom {user} group {grp} {str(datetime.datetime.timestamp(datetime.datetime.now()))}\n")
            file.close()

            print(Fore.YELLOW + "<Group: " + grp + "> " + "<User: " + user + "> " +
                  "Sent a file which is placed at " + f"__received__{usr}__/{grp}_{user}_{counter}{ext}")
            if not os.path.exists(f"__received__{usr}__"):
                os.makedirs(f"__received__{usr}__")
            myfile = open(
                f"__received__{usr}__/{grp}_{user}_{counter}{ext}", 'wb')
            myfile.write(message)
            myfile.close()
            counter += 1

        # group key for offline users
        elif code == "gk":
            grp = server.recv(
                int(server.recv(3).decode('utf-8'))).decode('utf-8')
            size = int(server.recv(4).decode('utf-8'))
            iter = size//86
            msg = []
            # receiving group key
            for i in range(iter):
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            if not size % 86 == 0:
                data = server.recv(128)
                msg.append(prvt_key.decrypt(data))
            p_key = b''.join(msg)
            enc_grp_pvt_key = cryptocode.encrypt(p_key.decode(), pwd)
            to_send = "{}:{}:".format("gk", grp).ljust(
                512, '0').encode('utf-8')
            server.sendall(to_send)
            server.sendall(str(len(enc_grp_pvt_key)).zfill(4).encode('utf-8'))
            server.sendall(enc_grp_pvt_key.encode('utf-8'))
            print(Fore.GREEN + f"You were added to group: {grp}")

    print()

thread1 = threading.Thread(target=receiving_func, args=())
thread2 = threading.Thread(target=user_interface, args=())
# Starting thread 1
thread1.start()

# Starting thread 2
thread2.start()

# Wait until thread 1 is completely executed
thread1.join()

# Wait until thread 2 is completely executed
thread2.join()

server.close()
