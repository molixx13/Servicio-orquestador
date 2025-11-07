import xmlrpc.client
import json
from datetime import datetime

server = xmlrpc.client.ServerProxy('http://192.168.100.233:8083/rpc', allow_none=True) 
data = {'origen': 'Inventario', 'productos': [{'nombre': 'Mesa', 'cantidad': 10}], 'motivo': 'Bajo stock'} 
resp = server.procesarRequerimiento(json.dumps(data)) 
print(resp)