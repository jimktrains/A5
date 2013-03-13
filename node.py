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
server = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
server.bind(socket_path)
server.listen(5)

 
print("Listening...")

def not_str(s):
    return ''.join(chr(0xFF & ~ord(a)) for a in s)
def xor_str(s,t):
    return ''.join(chr(ord(a)^ord(b)) for a,b in zip(s,t))

# Bootstrap
bootstrap_node = set([random.choice(os.listdir("nodes"))])
bootstrap_node = bootstrap_node.difference(set([node_id]))
while len(bootstrap_node) != 0:
    node = bootstrap_node.pop()
    try:
        print node
        client = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
        client.connect(node)
        
        client.send("NODE_LOOKUP " + node_id)
        datagram = server.recv( 1024 )
        print(datagram)
    finally:
        client.close()



known_nodes = []
try:
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
            closeness.append( (binascii.b2a_hex(xor_str(val, binascii.a2b_hex(node_id))), node_id) )
            closeness = sorted(closeness, key=lambda x: x[0])
            print(closeness)
            
            
finally:
    print("-" * 20)
    print("Shutting down...")
    server.close()
    os.remove(socket_path)
    print("Done")
