import socket
import os, os.path
import time
import base64
#from Crypto.Cipher import AES
#from Crypto.PublicKey import RSA
#from Crypto.Hash import SHA256
from pyecc import ECC
import tempfile
import hashlib
import binascii
import random
 
class MyNode:
    def __init__(self, address):
        self.ecc = ECC.generate()
        self.publicKey = self.ecc._public
        self.privateKey = self.ecc._private
        self.curve = self.ecc._curve
        self.node_id = hashlib.sha1(publicKey).digest()
        self.node_id_hex = binascii.b2a_hex(self.node_id_b)
        self.socket_path = os.path.join("nodes", node_id)
        self.address = address
    def bootstrap(self, bootstrap_nodes):
        closest_nodes = set()
        seen_nodes = set()
        while len(bootstrap_nodes) != 0:
            node_id = bootstrap_nodes.pop() 
            seen_nodes.add(node_id)
            node = Node.factory(node_id)
            rsp = new NLOOKUP(self).do(node, self.node_id)
            for n in rsp:
                if n.node_id not in seen_nodes:
                    bootstrap_nodes.add(n.node_id)
                if n.node_id == node_id:
                    closest_nodes.add(node_id)
        closest_nodes = sorted(closest_nodes, key= lambda x : xor_str(x, self.node_id))
        self.known_nodes = [Node.factory(x) for x in closest_nodes]
            

class Node:
    nodes = {}
    def factory(node_id, address = None, publicKey = None):
        if node_id not in nodes:
            nodes[node_id] = new Node(node_id, address, publicKey)
        return nodes[node_id] 
    def __init__(self, node_id, address, public_key):
        self.address = address
        self.publicKey = public_key
        self.node_id = node_id
    def send_message(self, message):
        client = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
        datagram = None
        try:
            client.connect(bootstrap_nodes[node])
            client.send(message)
            datagram = client.recv(1024)
        finally:
            client.close()
        return datagram

class DIST:
    def __init__(self, node):
        self.node = node
    def do(self, node, val):
        rsp = node.send_message(self.generate_request(val))
        rsp = self.parse_response(rsp)
        return rsp
    def generate_request(self, val):
        val = hashlib.sha1(publicKey).hexdigest()
        return "DIST " + val
    def parse_response(self, val):
        return binascii.a2b_hex(val)
    def generate_response(self, val):
        val = binascii.a2b_hex(val)
        xor = xor_str(self.node.node_id, val)
        return binascii.b2a_hex(xor)

class NLOOKUP:
    def __init__(self, node):
        self.node = node
    def generate_request(self, val):
        val = binascii.b2a_hex(val)
        return "NLOOKUP " + val
    def parse_response(self, val):
        return [ Node.factory(y[0], y[1]) for y in [ x.split(':') for x in val.split(' ') ] ]
    def generate_response(self, val):
        val = binascii.a2b_hex(val)
        closeness = [(binascii.b2a_hex(xor_str(val, self.node.node_id)), node) for node in known_nodes]
        closeness = sorted(closeness, key=lambda x: x[0])
        nodelist = (' '.join(["%s:%s" % (x[1], known_nodes[x[1]]) for x in closeness]))
        return nodelist

class AUTH:
    def __init__(self, node):
        self.node = node
    def do(self, node):
        

# Should research how good this is
ecc = ECC.generate()
 
publicKey = ecc._public
privateKey = ecc._private
curve = ecc._curve
print("Priv",privateKey)
print("Pub",publicKey)
print("Curve:",curve)

# maybe sha512?
node_id = hashlib.sha1(publicKey).hexdigest()
print("Node ID:", node_id)
socket_path = os.path.join("nodes", node_id)
print("Socket:", socket_path)
def not_str(s):
    return ''.join(chr(0xFF & ~ord(a)) for a in s)
def xor_str(s,t):
    return ''.join(chr(ord(a)^ord(b)) for a,b in zip(s,t))
try:
    server = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
    server.bind(socket_path)
    server.listen(5)

     
    print("Listening...")


    # Bootstrap

    possible_nodes = {}

    # These 2 line would normally be hard-coded or found in irc
    bootstrap_nodes = { x: os.path.join("nodes", x) for x in os.listdir("nodes") }
    del bootstrap_nodes[node_id]

    # No known nodes, so we'll just carry on and be calm
    if 0 != len(bootstrap_nodes):
        bootstrap_node = random.choice(bootstrap_nodes.keys())
        bootstrap_nodes = {bootstrap_node: bootstrap_nodes[bootstrap_node]}

        print(bootstrap_node)
        while len(bootstrap_nodes) != 0:
            node = bootstrap_nodes.keys().pop()
            client = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
            try:
                possible_nodes[node] = bootstrap_nodes[node]
                print(node)
                client.connect(bootstrap_nodes[node])
                
                client.send("NODE_LOOKUP " + node_id)
                datagram = client.recv(1024)
                nodes = set(datagram.split(' ')) - set(possible_nodes)
                for node in nodes:
                    node = node.split(':')
                    bootstrap_nodes[node[0]] = node[1] 
                    for k in possible_nodes:
                        del bootstrap_nodes[k]
                    print(bootstrap_node)
            finally:
                client.close()
        possible_nodes = sorted(possible_nodes, key=lambda x : xor_str(x[0], node_id))[0:4]
        for node in possible_nodes:
            client = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
            try:
                client.connect(possible_nodes[node])
                nonce = random.getrandbits(32)
                nonce_enc = ecc.encrypt(str(nonce))
                print(nonce_enc)
                client.send("AUTH " + binascii.b2a_hex(publicKey) + " " + binascii.b2a_hex(nonce_enc))
                datagram = client.recv(1024)
                nodes = set(datagram.split(' ')) - set(possible_nodes)
                for node in nodes:
                    node = node.split(':')
                    bootstrap_nodes[node[0]] = node[1] 
                    for k in possible_nodes:
                        del bootstrap_nodes[k]
                    print(bootstrap_node)
            finally:
                client.close()
        print possible_nodes
    known_nodes = possible_nodes
    known_nodes[node_id] = socket_path
    while True:
      client, address = server.accept()
      datagram = client.recv( 1024 )
      if not datagram:
        break
      else:
        cmd, rest = datagram.split(' ', 1)
        print("-" * 20)
        print(cmd)
        if "DONE" == cmd:
          break
        elif "DIST" == cmd:
            H1 = hashlib.sha1(rest).digest()
            H2 = not_str(H1)
            xor1 = xor_str(node_id, H1)
            xor2 = xor_str(node_id, H2)
            print("H1 ",binascii.b2a_hex(H1))
            print("H2 ",binascii.b2a_hex(H2))
            print("x1 ",binascii.b2a_hex(xor1))
            print("x2 ",binascii.b2a_hex(xor2))
            print("df ",cmp(xor1, xor2))
        elif "NODE_LOOKUP":
            val = binascii.a2b_hex(rest)
            closeness = [(binascii.b2a_hex(xor_str(val, binascii.a2b_hex(node))), node) for node in known_nodes]
            closeness = sorted(closeness, key=lambda x: x[0])
            print(closeness)
            nodelist = (' '.join(["%s:%s" % (x[1], os.path.join("nodes",x[1])) for x in closeness]))
            print(nodelist)
            client.send(nodelist)
finally:
    print("-" * 20)
    print("Shutting down...")
    server.close()
    os.remove(socket_path)
    print("Done")
