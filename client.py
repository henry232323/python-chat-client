from sys import exit, stdout, stdin
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from os.path import isfile
import tkinter as tk
import json

class Gui(tk.Tk):
    """GUI for chat client. Two labels and exit button at the top,
    then single-line text entry and Send button for user, finally
    multiple-line text box and Clear button to receive messages
    from chat server."""
    
    def __init__(self, parent, user):
        """Gui constructor"""
        tk.Tk.__init__(self)
        self.parent = parent
        self.client = Client(user)
        self.user = user
        self.initialize()
        self.receive()
           
    def onPressEnter(self, event): 
        """Handle Enter button press the same as Send button click"""
        self.send()
    
    def send(self):
        """Send user input from client to server, then clear Entry"""
        msg = self.mytext.get()
        self.client.send(msg)
        self.mytext.set('')
        self.receive()
    
    def receive(self):
        """Check server for any messages; append them to Text"""
        data = self.client.run()
        if data:
            self.text1.insert(tk.END, '\n' + data.strip())
        while self.text1.count(1.0, tk.END, 
                               "displaylines")[0] > self.maxlines:
            self.text1.delete(1.0, 2.0)
        self.after(100, self.receive)  # try again in 100 msec
            
    def initialize(self):
        """Initialize the GUI components"""
        self.title('Chat')
        self.minsize(350,300)
        self.maxsize(350,300)
        self.maxlines = 10  # number of lines in receive Text
      
        frame1 = tk.Frame(self)
        frame1.pack()
        handle = tk.StringVar()
        label1 = tk.Label(frame1, textvariable=handle)
        handle.set(self.user)
        button1 = tk.Button(frame1, text="Exit", command=self.destroy)
        label1.pack(side=tk.LEFT)
        button1.pack(side=tk.LEFT, padx=20)
    
        frame2 = tk.Frame(self)
        frame2.pack()
        lb2 = tk.StringVar()
        label2 = tk.Label(frame2, textvariable=lb2)
        lb2.set(self.client.host)  #IP:port
        label2.pack()
    
        frame3 = tk.Frame(self)
        frame3.pack()
        self.mytext = tk.StringVar()
        entry1 = tk.Entry(frame3, width=40, textvariable=self.mytext)
        entry1.bind("<Return>", self.onPressEnter)  # same as Send button
        button2 = tk.Button(frame3, text="Send", command=self.send)
        entry1.pack()
        button2.pack()
    
        frame4 = tk.Frame(self)
        frame4.pack()
        spacer1 = tk.Label(frame4)
        self.text1 = tk.Text(frame4, width=50, height=self.maxlines)
        #self.text1.insert(tk.END, "This is a test")
        button3 = tk.Button(frame4, text="Clear",
                            command=lambda: self.text1.delete(1.0, tk.END))
        spacer2 = tk.Label(frame4)
        spacer1.pack()
        self.text1.pack()
        spacer2.pack()
        button3.pack()                    

        
class Client(object):
    """Client networking class to connect to chat server. Handle initial
    handshake with server. Send messages to and receive them from server.""" 
    def __init__(self, user, host="localhost", port=50000):
        """Construct a Client to connect to server specified by myfile, 
        with handle specified by myname."""
        self.host = host
        self.port = port
        self.user = user
        self.server = socket(AF_INET, SOCK_STREAM)
        # connect to remote host
        self.server.connect((host, port))
        
    def send(self, message):
        """Send user's message to server"""
        msg = dict(message=message, name=self.user)
        self.server.send(json.dumps(msg).encode())
                         
    def run(self):
        """Check once for message (assumed to be server) and return it."""
        read_sockets, write_sockets, error_sockets = select([self.server], [], [], 0)
        result = []
        for asocket in read_sockets: 
            data = asocket.recv(4096)   # parameter, not magic number?
            if data:
                result.append("{name}: {message}".format(**json.loads(data.decode())))
        return "\n".join(result)


if __name__ == "__main__":
    main = Gui(None, "henry232323")
    main.mainloop()
    print("Thank you for using our chat client.")
