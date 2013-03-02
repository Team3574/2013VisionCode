#! /usr/bin/env python

"""
Simple implementation of the NetworkTables2 protocol for client

"""

import socket
import sys
import select
import struct
import time
import thread

class EntryValue:
    def __init__(self, name, entryId, seqId, value):
        self.name = name
        self.entryId = entryId
        self.seqId = seqId
        self.value = value
        self.watch = None

    def update(self, value, seqId):
        self.value = value
        self.seqId = seqId

    def getType(self):
        return type(self.value)

    def __repr__(self):
        return str((self.name, self.entryId, self.seqId, self.value))

class NetworkTableClient(object):
    def __init__(self, team):
        teamPad = team.rjust(5, '0')
        c1 = int(teamPad[0:3])
        c2 = int(teamPad[3:5])
        self.port = 1735
        self.host = "10.{0}.{1}.2".format(c1, c2)
        self.tableValues = dict()
        self.entryIdByName = dict()
        self.watches = dict()

        # Create a lock for sending data on the socket, so we don't send a keep alive in the middle of an entry
        self.sendLock = thread.allocate_lock()

        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print 'Connected to NetworkTables server@%d' % self.port

            # Hello message
            self.sayHello()
            time.sleep(0.1)
            thread.start_new_thread(self.valueReciever, ())
            thread.start_new_thread(self.keepAlive, ())
            # Hacky way to give the initial value load time to process
            time.sleep(0.5)

        except socket.error, e:
            print e
            print 'Could not connect to chat server @%d' % self.port
            sys.exit(1)

    def getNumFromBytes(self, b):
        return (b[0] * 2**8) + b[1]

    def interpretEntry(self, data):
        nameLen = self.getNumFromBytes(data[0:2])
        name = str(data[2:nameLen+2])
        data = data[(nameLen + 2):]

        t = data[0]

        entryId = self.getNumFromBytes(data[1:3])
        seq = self.getNumFromBytes(data[3:5])

        data = data[5:]

        if t == 0:
            """Boolean"""
            self.tableValues[entryId] = EntryValue(name, entryId, seq, data[0] == 0x01)
            self.entryIdByName[name] = entryId
            return data[1:]
        elif t == 1:
            """Double"""
            d = struct.unpack('!d', str(data[0:8]))[0]
            self.tableValues[entryId] = EntryValue(name, entryId, seq, d)
            self.entryIdByName[name] = entryId
            return data[8:]
        elif t == 2:
            """String"""
            strLen = self.getNumFromBytes(data[0:2])
            strValue = str(data[2:strLen+2])
            self.tableValues[entryId] = EntryValue(name, entryId, seq, strValue)
            self.entryIdByName[name] = entryId
            return data[strLen + 2:]

    def watch(self, name, func):
        self.watches[name] = func

    def setValue(self, name, value):

        if not self.entryIdByName.has_key(name):
            entry = EntryValue(name, 0xFFFF, 0x0, value)
            if entry.getType() == bool:
                updateMessage = "\x10" + struct.pack("!H" + str(len(name)) + "sBHH?", len(name), name, 0x00, entry.entryId, entry.seqId, entry.value);

            elif entry.getType() == float:
                updateMessage = "\x10" + struct.pack("!H" + str(len(name)) + "sBHHd", len(name), name, 0x01, entry.entryId, entry.seqId, entry.value);

            elif entry.getType() == str:
                strLen = len(value)
                updateMessage = "\x10" + struct.pack("!H" + str(len(name)) + "sBHHH" + str(strLen) + "s", len(name), name, 0x02, entry.entryId, entry.seqId, strLen, entry.value);
            else:
                updateMessage = ""

        else:
            entryId = self.entryIdByName[name]
            entry = self.tableValues[entryId]

            if type(value) != entry.getType():
                raise TypeError('Wrong type for ' + name + ' Got:' + str(type(value)) + ' Need:' + str(entry.getType()))

            if entry.getType() == bool:
                entry.update(value, entry.seqId + 1)
                updateMessage = "\x11" + struct.pack("!HH?", entry.entryId, entry.seqId, entry.value);

            elif entry.getType() == float:
                entry.update(value, entry.seqId + 1)
                updateMessage = "\x11" + struct.pack("!HHd", entry.entryId, entry.seqId, entry.value);

            elif entry.getType() == str:
                strLen = len(value)
                entry.update(value, entry.seqId + 1)
                updateMessage = "\x11" + struct.pack("!HHH" + str(strLen) + "s", entry.entryId, entry.seqId, strLen, entry.value);

        self.sendLock.acquire()
        self.sock.send(updateMessage)
        self.sendLock.release()

    def getValue(self, name):
        if not self.entryIdByName.has_key(name):
            return None
        entryId = self.entryIdByName[name]
        entry = self.tableValues[entryId]

        return entry.value

    def updateEntry(self, data):
        entryId = self.getNumFromBytes(data[0:2])
        seq = self.getNumFromBytes(data[2:4])

        data = data[4:]

        entry = self.tableValues[entryId]

        if entry.getType() == bool:
            """Boolean"""
            entry.update(data[0] == 0x01, seq)
            return data[1:]
        elif entry.getType() == float:
            """Double"""
            entry.update(struct.unpack('!d', str(data[0:8]))[0], seq)
            return data[8:]
        elif entry.getType() == str:
            """String"""
            strLen = self.getNumFromBytes(data[0:2])
            entry.update(str(data[2:strLen+2]), seq)
            return data[strLen + 2:]

    def sayHello(self):
        self.sock.send("\x01\x02\x00")

    def keepAlive(self):
        while True:
            time.sleep(5.0)
            self.sendLock.acquire()
            self.sock.send('\x00')
            self.sendLock.release()


    def valueReciever(self):
        while True:
            d = bytearray(self.sock.recv(4096 * 1024))

            # while d != None and len(d) > 0:
            while d != None and len(d) > 1:
                msgType = d[0]

                if msgType == 0x10:
                    d = self.interpretEntry(d[1:])

                elif msgType == 0x11:
                    """ Entry update """
                    d = self.updateEntry(d[1:])
                elif msgType == 0x03:
                    """ Hello Complete """
                    d = d[1:]
                elif msgType == 0x02:
                    """ Unsuported protocol """
                    d = d[1:]
                elif msgType == 0x00:
                    """ Keep Alive """
                    d = d[1:]

            # Give some time to make sure we get all the message from the server
            time.sleep(0.05)

if __name__ == "__main__":
    import sys

    if len(sys.argv)<1:
        sys.exit('Usage: %s team number' % sys.argv[0])

    client = NetworkTableClient(sys.argv[1])


    client.setValue("howdy", 2000.0)
    client.setValue("/what/is/up", "Cool!")
    client.setValue("/what/is/down", True)
    client.setValue("/what/is/left", 1234.0)
    client.setValue("/what/is/right", 1337.0)

    print client.getValue("/SmartDashboard/PizzaBoxTilt/i")
