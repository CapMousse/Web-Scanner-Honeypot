from multiprocessing import Process
from datetime import datetime
from time import sleep
import socket
import re
import os

class Honeypot():
  """
  Web Scanner Honeypot
  """

  def __init__(self, address="0.0.0.0", port="8080"):
    """
    Honeypot(address, port) -> Honeypot
    """

    self.address = address
    self.port = port
    self.__pid = os.getpid()
    self.__server_socket = None
    self.__process_pool = []

  def run(self):
    """
    run() -> None

    Launch socket to given address and port
    """

    self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) # initiate an IPV4 two way stream socket using TCP
    self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # prevent error when wildcard is used
    self.__server_socket.bind((self.address, int(self.port)))
    self.__server_socket.listen()

    print(f'Starting honeypot on {self.address}:{self.port}')

    while self.__server_socket:
      connection, connection_address = self.__server_socket.accept()
      process = Process(target=self.__handle_request, args=(connection, connection_address))
      process.start()
      self.__process_pool.append(process)

  def __handle_request(self, connection, address):
    """
    __handle_request(socket object, address info) -> None

    Read chunck from request to get headers and find http verb
    Flood response with chuncked not found
    """

    client_query = ""

    try:
      while True:
        chunck = connection.recv(1024).decode()
        client_query += chunck

        if len(chunck) <= 1024:
          break
    except Exception as e:
      print(f"{datetime.now()} - [{address[0]}] - {e}") #prevent error while reading client request

    matchs = re.findall(r"GET (.+) HTTP\/[0-9.]+", client_query, re.DOTALL) #match only GET query

    if len(matchs) == 0:
      connection.close()
      return

    print(f'{datetime.now()} - [{address[0]}] - GET {matchs[0]}')

    connection.sendall("HTTP/1.1 404 Not Found\r\n".encode()) # Use http/1.1 to enable chunked encoding
    connection.sendall("Content-Type: text/plain\r\n".encode()) # Send text content type to prevent encoding error
    connection.sendall("Transfer-Encoding: chunked\r\n\r\n".encode()) # Force chunked response to force client to wait for end bytes

    chunk = "Not found\r\n"
    chunk_length = len(chunk.encode("utf-8"))
    
    try:
      while True:
        connection.sendall(f"{chunk_length:X}\r\n{chunk}\r\n".encode('utf-8'))
        sleep(5)
    except Exception as e:
      print(f'{datetime.now()} - [{address[0]}] - GET {matchs[0]} - {e}') # Prevent error when client force disconnection

  def stop(self):
    """
    stop() -> None

    Stop all runing subprocess and socket
    """

    if os.getpid() != self.__pid: #prevent execution on subprocess
      return

    print("Stopping server")
    for process in self.__process_pool:
      process.kill()

    self.__server_socket.close()
    self.__server_socket = None
    self.__process_pool = []