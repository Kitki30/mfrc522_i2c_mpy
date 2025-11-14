#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Writes a specific datablock with random values
"""

__author__ = "Christoph Pranzl"
__version__ = "0.0.5"
__license__ = "GPLv3"

import machine
import time
import random
from mfrc522_i2c import MFRC522

continue_reading = True

i2cBus = machine.I2C(1, scl=machine.Pin(1), sda=machine.Pin(2))
i2cAddress = 0x28

def random_data(size=16):
    """ Create random data """
    data = []
    for i in range(size):
        data.append(random.randint(0, 255))
    return (data)

# Create an object of the class MFRC522
MFRC522Reader = MFRC522(i2cBus, i2cAddress)

version = MFRC522Reader.getReaderVersion()
print(f'MFRC522 Software Version: {version}')

while continue_reading:
    # Scan for cards
    (status, backData, tagType) = MFRC522Reader.scan()
    if status == MFRC522Reader.MIFARE_OK:
        print(f'Card detected, Type: {tagType}')

        # Get UID of the card
        (status, uid, backBits) = MFRC522Reader.identify()
        if status == MFRC522Reader.MIFARE_OK:
            print('Card identified, UID: ', end='')
            for i in range(0, len(uid) - 1):
                print(f'{uid[i]:02x}:', end='')
            print(f'{uid[len(uid) - 1]:02x}')

            # Select the scanned card
            (status, backData, backBits) = MFRC522Reader.select(uid)
            if status == MFRC522Reader.MIFARE_OK:
                print('Card selected')

                # TODO: Determine 1K or 4K

                # Authenticate
                blockAddr = 8
                (status, backData, backBits) = MFRC522Reader.authenticate(
                    MFRC522Reader.MIFARE_AUTHKEY2,
                    blockAddr,
                    MFRC522Reader.MIFARE_KEY,
                    uid)
                if (status == MFRC522Reader.MIFARE_OK):
                    print('Card authenticated')

                    # Read old data from card
                    (status, backData, backBits) = MFRC522Reader.read(
                        blockAddr)

                    if (status == MFRC522Reader.MIFARE_OK):
                        print(f'Block {blockAddr:02} : ', end='')
                        for i in range(0, len(backData)):
                            print(f'{backData[i]:02x} ', end='')
                        print('read')

                        time.sleep(0.5)  # Give it some time, or else data can corrupt in transport

                        # Write new data to card
                        data = random_data()

                        (status, backData, backBits) = MFRC522Reader.write(
                            blockAddr,
                            data)

                        if (status == MFRC522Reader.MIFARE_OK):
                            print(f'Block {blockAddr:02} : ', end='')
                            for i in range(0, len(data)):
                                print(f'{data[i]:02x} ', end='')
                            print('written')

                            time.sleep(0.5) # Give it some time, or else data can corrupt in transport

                            # Read new data from card
                            (status, backData, backBits) = MFRC522Reader.read(
                                blockAddr)

                            if (status == MFRC522Reader.MIFARE_OK):
                                print(f'Block {blockAddr:02} : ', end='')
                                for i in range(0, len(backData)):
                                    print(f'{backData[i]:02x} ', end='')
                                print('read')

                                continue_reading = False
                            else:
                                print('Error while reading new data')
                        else:
                            print('Error while writing new data')
                    else:
                        print('Error while reading old data')

                    # Deauthenticate
                    MFRC522Reader.deauthenticate()
                    print('Card deauthenticated')
                else:
                    print('Authentication error')
