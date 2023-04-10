import os
import argparse

parser = argparse.ArgumentParser()

# Arguments
parser.add_argument(
'--c', type=int, help='Specify the number of clients', required=True)
parser.add_argument(
'--g', type=str, help='Specify if group is used "y" for yes, "n" for no', default='n')
parser.add_argument(
'--i', type=str, help='Specify whether you want to send images too, "y" for yes, "n" for no', default='n')

args = parser.parse_args()

# Required lists to store lines in log file
sent_id_tx = []
received_id_tx = []
sent_id_im = []
received_id_im = []
sent_grp_tx = []
received_grp_tx = []
sent_grp_im = []
received_grp_im = []
# Number of messages and total difference between sent and received message
number_tx = 0
number_im = 0
total_tx = 0
total_im = 0

# NO GROUP
if args.g == 'n':

    # NO IMAGE
    if args.i == 'n':
        # Open logs file, ignore login/signup messages and add entry to corresponding list
        with open("logs.txt", "r") as file:
            for line in file.readlines():
                words = line.split(" ")
                if len(words) == 3:
                    continue
                elif len(words) == 4:
                    words[3] = words[3][:-1]
                    if words[1] == "receivedTextFrom":
                        received_id_tx.append(words)
                    elif words[1] == "sentTextTo":
                        sent_id_tx.append(words)
                    else:
                        print("Incorrect Input")
                        exit(1)
                else:
                    print("Incorrect Input")
                    exit(1)

        # Sort the lists according to time
        sent_id_tx.sort(key = lambda x: x[3])
        received_id_tx.sort(key = lambda x: x[3])

        # Make a copy so that we can remove found messages from the copy
        cp_sent_id_tx = sent_id_tx.copy()
        cp_received_id_tx = received_id_tx.copy()

        # Find first matching sender and receiver and vice-versa and remove the entry from copied list

        for elem in cp_received_id_tx:
            for sen in cp_sent_id_tx:
                if elem[0] == sen[2] and elem[2] == sen [0]:
                    number_tx += 1
                    total_tx += float(elem[3]) - float(sen[3])
                    cp_sent_id_tx.remove(sen)
                    break
        
        # Latency calculation
        latency = total_tx/number_tx
        print("Latency: ", latency, "seconds")

        # We take 3rd of the 5 intervals for calculating throughput
        number_intervals = 5
        
        # We divide total timeline between first message sent and last message received into 5 intervals
        interval_len = (float(received_id_tx[-1][3]) - float(sent_id_tx[0][3]))/5

        # Variables for throughputs
        in_th=0
        out_th=0

        # Calculate messages sent in the given time interval
        for elem in sent_id_tx:
            to_increase = int((float(elem[3]) - float(sent_id_tx[0][3]))/interval_len)
            if to_increase == 2:
                in_th += 1

        # Calculate messages received in the given time interval
        for elem in received_id_tx:
            to_increase = int((float(elem[3]) - float(sent_id_tx[0][3]))/interval_len)
            if to_increase == 2:
                out_th +=1

        print("Input throughput: ", in_th/interval_len, "messages per second")
        print("Output throughput: ", out_th/interval_len, "messages per second")

    # IMAGE
    elif args.i == 'y':

        # Open logs file, ignore login/signup messages and add entry to corresponding list
        with open("logs.txt", "r") as file:
            for line in file.readlines():
                words = line.split(" ")
                if len(words) == 3:
                    continue
                elif len(words) == 4:
                    words[3] = words[3][:-1]
                    if words[1] == "receivedTextFrom":
                        received_id_tx.append(words)
                    elif words[1] == "sentTextTo":
                        sent_id_tx.append(words)
                    elif words[1] == "receivedImageFrom":
                        received_id_im.append(words)
                    elif words[1] == "sentImageTo":
                        sent_id_im.append(words)
                    else:
                        print("Incorrect Input")
                        exit(1)

        # Sort the lists according to time
        sent_id_tx.sort(key = lambda x: x[3])
        received_id_tx.sort(key = lambda x: x[3])
        sent_id_im.sort(key = lambda x: x[3])
        received_id_im.sort(key = lambda x: x[3])
        
        # Make a copy so that we can remove found messages from the copy
        cp_sent_id_tx = sent_id_tx.copy()
        cp_received_id_tx = received_id_tx.copy()
        cp_sent_id_im = sent_id_im.copy()
        cp_received_id_im = received_id_im.copy()

        # Find first matching sender and receiver and vice-versa and remove the entry from copied list

        for elem in cp_received_id_tx:
            for sen in cp_sent_id_tx:
                if elem[0] == sen[2] and elem[2] == sen [0]:
                    number_tx += 1
                    total_tx += float(elem[3]) - float(sen[3])
                    cp_sent_id_tx.remove(sen)
                    break

        for elem in cp_received_id_im:
            for sen in cp_sent_id_im:
                if elem[0] == sen[2] and elem[2] == sen [0]:
                    number_im += 1
                    total_im += float(elem[3]) - float(sen[3])
                    cp_sent_id_im.remove(sen)
                    break

        # No images were sent        
        if total_im ==0:
            print("Incorrect Input")
            exit(1)

        # Latency calculation for text, messages and overall
        latency_tx = total_tx/number_tx
        latency_im = total_im/number_im
        latency = (total_im + total_tx)/(number_tx + number_im) 
        print("Latency(overall): ", latency, "seconds")
        print("Latency(text messages): ", latency_tx, "seconds")
        print("Latency(images): ", latency_im, "seconds")

        # We take 3rd of the 5 intervals for calculating throughput
        number_intervals = 5
        min_time = min(float(sent_id_tx[0][3]), float(sent_id_im[0][3]))
        max_time = max(float(received_id_tx[-1][3]), float(received_id_im[-1][3]))
        
        # We divide total timeline between first message sent and last message received into 5 intervals
        interval_len = (max_time - min_time)/5
       
        # Variables for throughputs
        in_th_tx=0
        in_th_im=0
        out_th_tx=0
        out_th_im=0

        # Calculate messages sent in the given time interval
        for elem in sent_id_tx:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                in_th_tx += 1

        # Calculate messages received in the given time interval
        for elem in received_id_tx:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                out_th_tx +=1
        
        # Calculate messages sent in the given time interval
        for elem in sent_id_im:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                in_th_im += 1

        # Calculate messages received in the given time interval
        for elem in received_id_im:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                out_th_im +=1
        
        # Variables for throughputs
        in_th=in_th_tx+in_th_im
        out_th=out_th_tx+out_th_im

        print("Input throughput(overall): ", in_th/interval_len, "messages per second")
        print("Output throughput(overall): ", out_th/interval_len, "messages per second")
        print("Input throughput(text messages): ", in_th_tx/interval_len, "messages per second")
        print("Output throughput(text messages)): ", out_th_tx/interval_len, "messages per second")
        print("Input throughput(images): ", in_th_im/interval_len, "messages per second")
        print("Output throughput(images): ", out_th_im/interval_len, "messages per second")

# GROUP
elif args.g == 'y':

    # NO IMAGE
    if args.i == 'n':

        # Open logs file, ignore login/signup messages and add entry to corresponding list
        with open("logs.txt", "r") as file:
            for line in file.readlines():
                words = line.split(" ")
                if len(words) == 3:
                    continue
                elif len(words) == 4:
                    words[3] = words[3][:-1]
                    if words[1] == "receivedTextFrom":
                        received_id_tx.append(words)
                    elif words[1] == "sentTextTo":
                        sent_id_tx.append(words)
                    else:
                        print("Incorrect Input")
                        exit(1)
                elif len(words) == 5:
                    words[4] = words[4][:-1]
                    if words[1] == "sentTextTo":
                        sent_grp_tx.append(words)
                    else:
                        print("Incorrect Input")
                        exit(1)
                elif len(words) == 6:
                    words[5] = words[5][:-1]
                    if words[1] == "receivedTextFrom":
                        received_grp_tx.append(words)
                    else:
                        print("Incorrect Input")
                        exit(1)
                else:
                    print("Incorrect Input")
                    exit(1)
        
        # No group messages were sent
        if len(sent_grp_tx)==0:
            print("Incorrect Input")
            exit(1)

        # Sort the lists according to time
        sent_id_tx.sort(key = lambda x: x[3])
        received_id_tx.sort(key = lambda x: x[3])
        sent_grp_tx.sort(key = lambda x: x[4])
        received_grp_tx.sort(key = lambda x: x[5])

        # Make a copy so that we can remove found messages from the copy
        cp_sent_id_tx = sent_id_tx.copy()
        cp_received_id_tx = received_id_tx.copy()
        cp_sent_grp_tx = sent_grp_tx.copy()
        cp_received_grp_tx = received_grp_tx.copy()

        # Find first matching sender and receiver and vice-versa and remove the entry from copied list

        for elem in cp_received_id_tx:
            for sen in cp_sent_id_tx:
                if elem[2] == sen [0]:
                    number_tx += 1
                    total_tx += float(elem[3]) - float(sen[3])
                    cp_sent_id_tx.remove(sen)
                    break

        for sen in cp_sent_grp_tx:
            found=[0]*args.c
            found[int(sen[0])] = 1
            for elem in cp_received_grp_tx:
                if elem[2] == sen[0] and found[int(elem[0])] == 0:
                    total_tx += float(elem[5]) - float(sen[4])
                    number_tx += 1
                    found[int(elem[0])] = 1
                    cp_received_grp_tx.remove(elem)
                    if not 0 in found:
                        break

        # Latency calculation
        latency = total_tx/number_tx
        print("Latency: ", latency, "seconds")
        

        # We take 3rd of the 5 intervals for calculating throughput
        number_intervals = 5
        min_time = min(float(sent_id_tx[0][3]), float(sent_grp_tx[0][4]))
        max_time = max(float(received_id_tx[-1][3]), float(received_grp_tx[-1][5]))
        
        # We divide total timeline between first message sent and last message received into 5 intervals
        interval_len = (max_time - min_time)/5
        
        # Variables for throughputs
        in_th=0
        out_th=0

        # Calculate messages sent in the given time interval
        for elem in sent_id_tx:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                in_th += 1

        # Calculate messages received in the given time interval
        for elem in received_id_tx:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                out_th +=1

        # Calculate messages sent in the given time interval
        for elem in sent_grp_tx:
            to_increase = int((float(elem[4]) - min_time)/interval_len)
            if to_increase == 2:
                in_th += 1

        # Calculate messages received in the given time interval
        for elem in received_grp_tx:
            to_increase = int((float(elem[5]) - min_time)/interval_len)
            if to_increase == 2:
                out_th +=1
    

        print("Input throughput: ", in_th/interval_len, "messages per second")
        print("Output throughput: ", out_th/interval_len, "messages per second")
        
    # IMAGE
    elif args.i == "y":
        
        # Open logs file, ignore login/signup messages and add entry to corresponding list
        with open("logs.txt", "r") as file:
            for line in file.readlines():
                words = line.split(" ")
                if len(words) == 3:
                    continue
                elif len(words) == 4:
                    words[3] = words[3][:-1]
                    if words[1] == "receivedTextFrom":
                        received_id_tx.append(words)
                    elif words[1] == "sentTextTo":
                        sent_id_tx.append(words)
                    elif words[1] == "receivedImageFrom":
                        received_id_im.append(words)
                    elif words[1] == "sentImageTo":
                        sent_id_im.append(words)
                    else:
                        print("Incorrect Input")
                        exit(1)
                elif len(words) == 5:
                    words[4] = words[4][:-1]
                    if words[1] == "sentTextTo":
                        sent_grp_tx.append(words)
                    elif words[1] == "sentImageTo":
                        sent_grp_im.append(words)
                    else:
                        print("Incorrect Input")
                        exit(1)
                elif len(words) == 6:
                    words[5] = words[5][:-1]
                    if words[1] == "receivedTextFrom":
                        received_grp_tx.append(words)
                    elif words[1] == "receivedImageFrom":
                        received_grp_im.append(words)
                    else:
                        print("Incorrect Input")
                        exit(1)
                else:
                    print("Incorrect Input")
                    exit(1)

        # No group messages were sent
        if len(sent_grp_tx)==0 and len(sent_grp_im)==0:
            print("Incorrect Input")
            exit(1)

        # Sort the lists according to time
        sent_id_tx.sort(key = lambda x: x[3])
        received_id_tx.sort(key = lambda x: x[3])
        sent_id_im.sort(key = lambda x: x[3])
        received_id_im.sort(key = lambda x: x[3])
        sent_grp_tx.sort(key = lambda x: x[4])
        received_grp_tx.sort(key = lambda x: x[5])
        sent_grp_im.sort(key = lambda x: x[4])
        received_grp_im.sort(key = lambda x: x[5])

        # Make a copy so that we can remove found messages from the copy
        cp_sent_id_tx = sent_id_tx.copy()
        cp_received_id_tx = received_id_tx.copy()
        cp_sent_id_im = sent_id_im.copy()
        cp_received_id_im = received_id_im.copy()
        cp_sent_grp_tx = sent_grp_tx.copy()
        cp_received_grp_tx = received_grp_tx.copy()
        cp_sent_grp_im = sent_grp_im.copy()
        cp_received_grp_im = received_grp_im.copy()

        # Find first matching sender and receiver and vice-versa and remove the entry from copied list

        for elem in cp_received_id_tx:
            for sen in cp_sent_id_tx:
                if elem[0] == sen[2] and elem[2] == sen [0]:
                    number_tx += 1
                    total_tx += float(elem[3]) - float(sen[3])
                    cp_sent_id_tx.remove(sen)
                    break

        for elem in cp_received_id_im:
            for sen in cp_sent_id_im:
                if elem[0] == sen[2] and elem[2] == sen [0]:
                    number_im += 1
                    total_im += float(elem[3]) - float(sen[3])
                    cp_sent_id_im.remove(sen)
                    break

        for sen in cp_sent_grp_tx:
            found=[0]*args.c
            found[int(sen[0])] = 1
            for elem in cp_received_grp_tx:
                if elem[2] == sen[0] and found[int(elem[0])] == 0:
                    total_tx += float(elem[5]) - float(sen[4])
                    number_tx +=1
                    found[int(elem[0])] = 1
                    cp_received_grp_tx.remove(elem)
                    if not 0 in found:
                        break

        for sen in cp_sent_grp_im:
            found=[0]*args.c
            found[int(sen[0])] = 1
            for elem in cp_received_grp_im:
                if elem[2] == sen[0] and found[int(elem[0])] == 0:
                    total_im += float(elem[5]) - float(sen[4])
                    number_im +=1
                    found[int(elem[0])] = 1
                    cp_received_grp_im.remove(elem)
                    if not 0 in found:
                        break

        # No images were sent        
        if total_im ==0:
            print("Incorrect Input")
            exit(1)

        # Latency calculation for text, messages and overall
        latency_tx = total_tx/number_tx
        latency_im = total_im/number_im
        latency = (total_im + total_tx)/(number_tx + number_im) 
        print("Latency(overall): ", latency, "seconds")
        print("Latency(text messages): ", latency_tx, "seconds")
        print("Latency(images): ", latency_im, "seconds")

        # We take 3rd of the 5 intervals for calculating throughput
        number_intervals = 5
        min_time = min(float(sent_id_tx[0][3]), float(sent_grp_tx[0][4]), float(sent_id_im[0][3]), float(sent_grp_im[0][4]))
        max_time = max(float(received_id_tx[-1][3]), float(received_grp_tx[-1][5]), float(received_id_im[-1][3]), float(received_grp_im[-1][5]))
        
        # We divide total timeline between first message sent and last message received into 5 intervals
        interval_len = (max_time - min_time)/5
        
        # Variables for throughputs
        in_th_tx=0
        in_th_im=0
        out_th_tx=0
        out_th_im=0

        # Calculate messages sent in the given time interval
        for elem in sent_id_tx:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                in_th_tx += 1

        # Calculate messages received in the given time interval
        for elem in received_id_tx:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                out_th_tx +=1
        
        # Calculate messages sent in the given time interval
        for elem in sent_id_im:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                in_th_im += 1

        # Calculate messages received in the given time interval
        for elem in received_id_im:
            to_increase = int((float(elem[3]) - min_time)/interval_len)
            if to_increase == 2:
                out_th_im +=1

        # Calculate messages sent in the given time interval
        for elem in sent_grp_tx:
            to_increase = int((float(elem[4]) - min_time)/interval_len)
            if to_increase == 2:
                in_th_tx += 1

        # Calculate messages received in the given time interval
        for elem in received_grp_tx:
            to_increase = int((float(elem[5]) - min_time)/interval_len)
            if to_increase == 2:
                out_th_tx +=1
        
        # Calculate messages sent in the given time interval
        for elem in sent_grp_im:
            to_increase = int((float(elem[4]) - min_time)/interval_len)
            if to_increase == 2:
                in_th_im += 1

        # Calculate messages received in the given time interval
        for elem in received_grp_im:
            to_increase = int((float(elem[5]) - min_time)/interval_len)
            if to_increase == 2:
                out_th_im +=1
        
        # Variables for throughputs 
        in_th=in_th_tx+in_th_im
        out_th=out_th_tx+out_th_im

        print("Input throughput(overall): ", in_th/interval_len, "messages per second")
        print("Output throughput(overall): ", out_th/interval_len, "messages per second")
        print("Input throughput(text messages): ", in_th_tx/interval_len, "messages per second")
        print("Output throughput(text messages)): ", out_th_tx/interval_len, "messages per second")
        print("Input throughput(images): ", in_th_im/interval_len, "messages per second")
        print("Output throughput(images): ", out_th_im/interval_len, "messages per second")
