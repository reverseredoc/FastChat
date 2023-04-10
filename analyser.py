from pwn import process
import os
import datetime
import time
import random
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    '--c', type=int, help='Specify the number of clients', required=True)
parser.add_argument(
    '--m', type=str, help='Specify the messaging pattern, "a" for all, "s" for single, "r" for random, "g" mixture of group and direct message', default='r')
parser.add_argument(
    '--i', type=str, help='Specify whether you want to send images too', default='n')

args = parser.parse_args()

# For servers and loadbalancers
q = []
nq = 4

# For clients
p = []
np = args.c

# First lets sign up all the clients and then log them in
for i in range(np):
    p.append(process(['python3', 'client.py', '127.0.0.1', '7999']))
    print(p[i].recvuntil(b"t"))
    p[i].sendline(b'2')
    print(p[i].recvuntil(b":"))
    p[i].sendline(f"{i}".encode('utf-8'))
    print(p[i].recvuntil(b":"))
    p[i].sendline(f"{i}".encode('utf-8'))
    print(p[i].recvuntil(b"t"))
    p[i].sendline(b'1')
    print(p[i].recvuntil(b":"))
    p[i].sendline(f"{i}".encode('utf-8'))
    print(p[i].recvuntil(b":"))
    p[i].sendline(f"{i}".encode('utf-8'))
    print(p[i].recvuntil(b"out"))

if args.i == "n":
    if args.m == "r":
        for j in range(150):
            i = random.randint(0, np - 1)
            p[i].sendline("d".encode('utf-8'))
            print(p[i].recvuntil(b":"))
            p[i].sendline(f"{random.randint(0,np - 1)}".encode('utf-8'))
            for k in range(3):
                time.sleep(0.01)
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("t".encode('utf-8'))
                p[i].sendline(f"hiiiby{i}".encode('utf-8'))
                print(p[i].recvuntil(b"sent"))
            print(p[i].recvuntil(b"menu"))
            p[i].sendline("q".encode('utf-8'))
            print(p[i].recvuntil(b"out"))
    elif args.m == "s":
        # Sending a series of message to a single client by all members
        for i in range(np - 1):
            p[i].sendline("d".encode('utf-8'))
            print(p[i].recvuntil(b":"))
            p[i].sendline(f"{np-1}".encode('utf-8'))
            for k in range(15):
                time.sleep(0.01)
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("t".encode('utf-8'))
                p[i].sendline(f"hiiiby{i}".encode('utf-8'))
                print(p[i].recvuntil(b"sent"))
            print(p[i].recvuntil(b"menu"))
            p[i].sendline("q".encode('utf-8'))
            print(p[i].recvuntil(b"out"))
    elif args.m == "a":
        # Sending message by each client to each other client
        for i in range(np):
            for j in range(np):
                if i == j:
                    continue
                p[i].sendline("d".encode('utf-8'))
                print(p[i].recvuntil(b":"))
                p[i].sendline(f"{j}".encode('utf-8'))
                for k in range(10):
                    time.sleep(0.01)
                    print(p[i].recvuntil(b"menu"))
                    p[i].sendline("t".encode('utf-8'))
                    p[i].sendline(f"hiiiby{i}".encode('utf-8'))
                    print(p[i].recvuntil(b"sent"))
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("q".encode('utf-8'))
                print(p[i].recvuntil(b"out"))
    elif args.m == "g":
        # Sending group messages
        p[0].sendline("g".encode('utf-8'))
        print(p[0].recvuntil(b"menu"))
        p[0].sendline("n".encode('utf-8'))
        print(p[0].recvuntil(b":"))
        p[0].sendline("DEMOGRP".encode('utf-8'))
        print(p[0].recvuntil(b"menu"))
        p[0].sendline("m".encode('utf-8'))
        print(p[0].recvuntil(b":"))
        p[0].sendline("DEMOGRP".encode('utf-8'))

        # Adding members to the group
        for j in range(np-1):
            print(p[0].recvuntil(b"menu"))
            p[0].sendline("a".encode('utf-8'))
            print(p[0].recvuntil(b":"))
            p[0].sendline(f"{j+1}".encode('utf-8'))

        # Making sure admin too is at the main menu after group formation and addition
        print(p[0].recvuntil(b"menu"))
        p[0].sendline("q".encode('utf-8'))
        print(p[0].recvuntil(b"menu"))
        p[0].sendline("q".encode('utf-8'))
        print(p[0].recvuntil(b"out"))

        # Sending random messages from client to client or client to group
        for j in range(30):
            a = random.randint(0, 1)
            i = random.randint(0, np - 1)
            if a == 0:
                p[i].sendline("d".encode('utf-8'))
                print(p[i].recvuntil(b":"))
                p[i].sendline(f"{random.randint(0,np - 1)}".encode('utf-8'))
                for k in range(3):
                    time.sleep(0.02)
                    print(p[i].recvuntil(b"menu"))
                    p[i].sendline("t".encode('utf-8'))
                    p[i].sendline(f"hiiiby{i}".encode('utf-8'))
                    print(p[i].recvuntil(b"sent"))
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("q".encode('utf-8'))
                print(p[i].recvuntil(b"out"))
            else:
                p[i].sendline("b".encode('utf-8'))
                print(p[i].recvuntil(b":"))
                p[i].sendline("DEMOGRP".encode('utf-8'))
                for k in range(3):
                    time.sleep(0.02)
                    print(p[i].recvuntil(b"menu"))
                    p[i].sendline("t".encode('utf-8'))
                    p[i].sendline("hello".encode('utf-8'))
                    print(p[i].recvuntil(b"sent"))
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("q".encode('utf-8'))
                print(p[i].recvuntil(b"out"))
            time.sleep(0.02)
    else:
        print("Invalid messaging style")

elif args.i == "y":
    if args.m == "r":
        for j in range(30):
            i = random.randint(0, np - 1)
            p[i].sendline("d".encode('utf-8'))
            print(p[i].recvuntil(b":"))
            p[i].sendline(f"{random.randint(0,np - 1)}".encode('utf-8'))
            for k in range(2):
                time.sleep(0.05)
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("t".encode('utf-8'))
                p[i].sendline(f"hiiiby{i}".encode('utf-8'))
                print(p[i].recvuntil(b"sent"))
            time.sleep(0.05)
            print(p[i].recvuntil(b"menu"))
            p[i].sendline("i".encode('utf-8'))
            p[i].sendline("img.png".encode('utf-8'))
            print(p[i].recvuntil(b"sent"))
            print(p[i].recvuntil(b"menu"))
            p[i].sendline("q".encode('utf-8'))
            print(p[i].recvuntil(b"out"))
    elif args.m == "s":
        # Sending a series of message to a single client by all members
        for i in range(np - 1):
            p[i].sendline("d".encode('utf-8'))
            print(p[i].recvuntil(b":"))
            p[i].sendline(f"{np-1}".encode('utf-8'))
            for k in range(5):
                time.sleep(0.05)
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("t".encode('utf-8'))
                p[i].sendline(f"hiiiby{i}".encode('utf-8'))
                print(p[i].recvuntil(b"sent"))
            for k in range(2):
                time.sleep(0.05)
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("i".encode('utf-8'))
                p[i].sendline("img.png".encode('utf-8'))
                print(p[i].recvuntil(b"sent"))
            print(p[i].recvuntil(b"menu"))
            p[i].sendline("q".encode('utf-8'))
            print(p[i].recvuntil(b"out"))
    elif args.m == "a":
        # Sending message by each client to each other client
        for i in range(np):
            for j in range(np):
                if i == j:
                    continue
                p[i].sendline("d".encode('utf-8'))
                print(p[i].recvuntil(b":"))
                p[i].sendline(f"{j}".encode('utf-8'))
                for k in range(6):
                    time.sleep(0.05)
                    print(p[i].recvuntil(b"menu"))
                    p[i].sendline("t".encode('utf-8'))
                    p[i].sendline(f"hiiiby{i}".encode('utf-8'))
                    print(p[i].recvuntil(b"sent"))
                for k in range(2):
                    time.sleep(0.05)
                    print(p[i].recvuntil(b"menu"))
                    p[i].sendline("i".encode('utf-8'))
                    p[i].sendline("img.png".encode('utf-8'))
                    print(p[i].recvuntil(b"sent"))
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("q".encode('utf-8'))
                print(p[i].recvuntil(b"out"))
    elif args.m == "g":
        # Sending group messages
        p[0].sendline("g".encode('utf-8'))
        print(p[0].recvuntil(b"menu"))
        p[0].sendline("n".encode('utf-8'))
        print(p[0].recvuntil(b":"))
        p[0].sendline("DEMOGRP".encode('utf-8'))
        print(p[0].recvuntil(b"menu"))
        p[0].sendline("m".encode('utf-8'))
        print(p[0].recvuntil(b":"))
        p[0].sendline("DEMOGRP".encode('utf-8'))

        # Adding members to the group
        for j in range(np-1):
            print(p[0].recvuntil(b"menu"))
            p[0].sendline("a".encode('utf-8'))
            print(p[0].recvuntil(b":"))
            p[0].sendline(f"{j+1}".encode('utf-8'))

        # Making sure admin too is at the main menu after group formation and addition
        print(p[0].recvuntil(b"menu"))
        p[0].sendline("q".encode('utf-8'))
        print(p[0].recvuntil(b"menu"))
        p[0].sendline("q".encode('utf-8'))
        print(p[0].recvuntil(b"out"))

        # Sending random messages from client to client or client to group
        for j in range(15):
            a = random.randint(0, 1)
            i = random.randint(0, np - 1)
            if a == 0:
                p[i].sendline("d".encode('utf-8'))
                print(p[i].recvuntil(b":"))
                p[i].sendline(f"{random.randint(0,np - 1)}".encode('utf-8'))
                time.sleep(0.05)
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("t".encode('utf-8'))
                p[i].sendline(f"hiiiby{i}".encode('utf-8'))
                print(p[i].recvuntil(b"sent"))
                time.sleep(0.05)
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("i".encode('utf-8'))
                p[i].sendline("img.png".encode('utf-8'))
                print(p[i].recvuntil(b"sent"))
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("q".encode('utf-8'))
                print(p[i].recvuntil(b"out"))
            else:
                p[i].sendline("b".encode('utf-8'))
                print(p[i].recvuntil(b":"))
                p[i].sendline("DEMOGRP".encode('utf-8'))
                time.sleep(0.05)
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("t".encode('utf-8'))
                p[i].sendline("hello".encode('utf-8'))
                print(p[i].recvuntil(b"sent"))
                time.sleep(0.05)
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("i".encode('utf-8'))
                p[i].sendline("img.png".encode('utf-8'))
                print(p[i].recvuntil(b"sent"))
                print(p[i].recvuntil(b"menu"))
                p[i].sendline("q".encode('utf-8'))
                print(p[i].recvuntil(b"out"))
            time.sleep(0.05)
    else:
        print("Invalid messaging style")
time.sleep(40)
