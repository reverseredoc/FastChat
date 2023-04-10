# FastChat by Thrice as Nice

# Members
| Name | Roll number |
| ----------- | ----------- |
| Guramrit Singh | 210050061 |
| Isha Arora | 210050070 |
| Karan Godara | 210050082 |

# Description about repository
- This repository contains the course project of CS 251 : Software Systems Lab 
- Code files and sphinx generated pdf are contained within the repository

## Implementation

### Postgresql
Database Fastchat is created which contains these tables: 
- credentials : User name, password, public key, private key
- groups : Group name, admin, public key, private keys, member count and member names in group
- msg : Stored messages for offline users which can be textual or image messages

## Signup and login
  A client firstly connects to load balancer where a user gets a chance to either signup or login. When signing up, loadbalancer firstly check if a successful signup can be made or not by making sure that the username is unique, it then updates database and its dictionary containing every user's public/private key to add a new user. 
  Whereas on a successful login the loadbalancer sends the user its stored private key as well as the address of the server to which it needs to be connected to and closing the existing socket connection between client and load balancer.
  
### Menu options
- Main menu
- Group Settings
- Group Message
- Direct Message

### Textual and image/text files
At the core of every chatting program lies its numerous feature of conecting to other fellow users and the mutual give and take of information between them. So for that our program have the ability to allow texts/images from one user to other either in dm or in a group message. Key things in the program for this purpose being:
- Text sent through terminal limited to size
  Our chatting program as based on terminals allows user to type in their messages in their terminal window and popping these messages to the receiver's terminal at the same time or when they come online whichever the case be. The max limit of text size we allow is roughly 2048 bytes. These texts are end-to-end encrypted and hence making the chat safe and secure. This communication encrytpion is dicussed below in the encryption section.
 
- Image (.png, .jpeg, .jpg) and Text (.txt) are supported
  A picture speaks a thousand work and so our program allows them to do so. Our chatting program rather than being just restricted to the texts messages allows user to share between each other images of type png, jpeg and jpg. These images too following the footsteps of text messages are sent safely and securely using the same encyrption methods as for texts.
  As image are nothing more than a text file with unique extensions, after the successful addition of image transfer feature we extended our program to also send files having .txt extension too between the users so that one may not have to write everything in the terminal.
  
- Threading and Locking
  One server, many clents. The condition on the one hand provides smoothly monitored conversation while on other a challenge of maintaining how everyone can simultaneously uses the same program at once without causing breakdown of server.
  So to overcome this challenge, we used the concept of threading. These threading allows the successful hadling of large number of clients efficiently without any concurrency clashes. 
  Also in inevitable cases where concurrency of variables posed as the necessary devil, we used locking to make sure only one part of the program can access/modify these variables at any particular time.

### Groups
Our fastchat program allows users to create groups with max limit of 20. The addition and removal of members can be done by the admin/creator of the group. Each group name is unique to ease the storage/implementation of the feature.
A textual or image message sent in group is broadcasted to every other member of the group and delivered to them later if they are offline at the moment.

### Encryption
For encryption we use SHA(Secure Hashing Algorithm) and RSA (Rivest, Shamir, Adleman) algorithms using the libraries:
- cryptocode
- Crypto
- passlib

Password storage and encrypting/decrypting messages
- Password is stored as an hashed version of itelf using passlib library in the database credentials. It makes it non-decryptabe but only verifiable. RSA library Crypto allows us to create public/private keys for each user and group which is used to send and receive messages/images across the network. This public/private key itself is stored in the database in an encrypted fashion using cryptocode which encrypts it using the user's password. This can only be decrypted only using the user's password and hence making it impossible for the server to crack it even though it has access to it.
- A person who wants to send group/direct message gets the public key from the server and encrypts the message and sends it to the server for delivery. In case of person receiving a direct message, he has his private key stored while it logged in and hence decrypts the message whereas for group, the server before sending message also sends the private key which user decrypts with his password and with this decrypted private key decrypts the message.
- This system is highly secure and protected for messages being sent between client-server or server-server.  


### Server Load Balancing
- We have three strategies of load balancer which are random, round robin and least connected which allocates server after a successful verification of a user. This verification of user is done by sendng the encrypted password of a user to the client program where it is verified with the input password. 
The load balancer aims to reduce the load of each server by making sure each gets almost equal number of clients. The load balancer also stores in it public/private keys associated with every username, public keys for all groups and a dictionary which maintains which all users are online and are connected which server.
- A user on successful login receives its private key from loadbalancer.
This strategy works as each server is also connected to every other server of the network and whenever load balancer want to direct a message to some other server it is done by using those intra-server sockets.

## Performance Analysis
We implemented three different startegies to balance the load across the servers in the load balancer. Those being,
- Round Robin Method : In a cyclic order assign each new client to the next server in the cycle.
- Random Method : Randomly assign one server out of all the existing servers to the new client.
- Least connection Method : Assign the server with the the least connections to the new incoming client.

Apart from this load balancing method we also experimented with the type of messages that were being sent in the network. Those being,
- Single client receiving messages from all the other clients.
- Each client getting a message from every other client.
- Randomly sending messages between the existing clients.
- Randomly switching between direct and group messaging between users that are online.
- Sending Images combined with messages in all the above techniques.

While using any of the above strategy, we created log files containing timestamps for all the messages sent and received by the clients. Using those log files we computed latency and throughput and plotted the same on the graph.

To automate the above process we used "pwn" library that allows us to run multiple processes from a single python file.

## Running the code files
1. We have 3 servers and 1 loadbalancer in the code files available here
2. Start loadbalancer in a terminal using `python3 loadbalancer.py 127.0.0.1 7999`
3. In ascending order of ports start all the servers first using `python3 server.py 127.0.0.1 <port>` where port ranges from 8000 to 8002.
4. Finally to start any client use `python3 client.py 127.0.0.1 7999`

Apart from these file for performance analysis we created two other files, first being analyser.py and the other called calculator.py. analyser.py is used to create log files automatically using above mentioned strategies whereas calculator.py is used to find the latency and throughput from the log files produced earlier. 

To run the analyser.py file write `python3 analyser.py --c <number of clients> --m <messaging style> --i <y or n whether we want image or not>`
To run the calculator.py file write `python3 calculator.py --c <number of clients> --g <y or n whether group message involved or not> --i <y or n whether image involved or not>`

## Team members' contributions
**All the design techniques and coding strategies were discussed in group as a whole.**
The coding and documentation was done piecewise by all three.

The following parts were written by Guramrit:
- User interface with coloured terminal display
- Database management
- Sending of encrypted textual/image messages
- Storing undelivered encrypted message for offline users for a limited period of time
- Receiving, decrypting and displaying message to user
- Group creation, member addition, member removal
- Group public key and private keys generation
- Least connected load balancer strategy
- calculater.py file for calculating latency and throughput
- README

The following parts were written by Karan:
- Threading and locking
- User login/signup verification
- Sending small textual encrypted direct messages
- Loadbalancer for distributing server load
- Two load balancer startegies of random and round robin
- analyser.py for generating logs.txt
- Presentation
- README

The following parts were written by Isha:
- Threading and locking
- User login/signup verification
- Encryption libraries, public and private key generation
- Sending small textual encrypted direct messages
- Loadbalancer for distributing server load
- Two load balancer startegies of random and round robin
- Documentation using sphinx
- Presentation
- README
