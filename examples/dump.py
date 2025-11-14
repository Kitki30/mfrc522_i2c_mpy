#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Dumps datablocks
"""

__author__ = "Christoph Pranzl"
__version__ = "0.0.5"
__license__ = "GPLv3"

import time
import machine
from mfrc522_i2c import MFRC522

continue_reading = True

i2cBus = machine.I2C(1, scl=machine.Pin(1), sda=machine.Pin(2))
i2cAddress = 0x28

# Create an object of the class MFRC522
MFRC522Reader = MFRC522(i2cBus, i2cAddress)

version = MFRC522Reader.getReaderVersion()
print(f'MFRC522 Software Version: {version}')

while continue_reading:
    # Scan for cards
    (status, backData, tagType) = MFRC522Reader.scan()
    if status == MFRC522Reader.MIFARE_OK:
        start = time.ticks_ms()
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
                for blockAddr in MFRC522Reader.MIFARE_1K_DATABLOCK:
                    (status, backData, backBits) = MFRC522Reader.authenticate(
                        MFRC522Reader.MIFARE_AUTHKEY2,
                        blockAddr,
                        MFRC522Reader.MIFARE_KEY,
                        uid)
                    if (status == MFRC522Reader.MIFARE_OK):

                        (status, backData, backBits) = MFRC522Reader.read(
                            blockAddr)
                        if (status == MFRC522Reader.MIFARE_OK):
                            print(f'Block {blockAddr:02d} : ', end='')
                            for i in range(0, len(backData)):
                                print(f'{backData[i]:02x} ', end='')
                            print('read')

                        else:
                            print('Error while reading')

                        continue_reading = False

                    else:
                        print('Authentication error')
                time.sleep_ms(1) # Give some time for it, so data is not corrupted

                # Deauthenticate
                MFRC522Reader.deauthenticate()
                print('Card deauthenticated')
end = time.ticks_ms()
print("Time to read: " + str(end - start))