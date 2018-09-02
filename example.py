# ------------------------------------------------------------------------
#
#  This file is part of the Chirp Connect Python SDK.
#  For full information on usage and licensing, see https://chirp.io/
#
#  Copyright (c) 2011-2018, Asio Ltd.
#  All rights reserved.
#
# ------------------------------------------------------------------------

import argparse
import sys
import time
import json
import web3
import Date
import hashlib
import RPi.GPIO as GPIO

from web3.contract import ConciseContract
from chirp import ChirpConnect, CallbackSet, CHIRP_CONNECT_STATE
from datetime import datetime


class MyCallbacks(CallbackSet):
    
    def open(){
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(14, GPIO.OUT)
            GPIO.output(14, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(14, GPIO.LOW)
        }
    def on_state_changed(self, previous_state, current_state):
        """ Called when the SDKs state has changed """
        print("State changed from {} to {}".format(
            CHIRP_CONNECT_STATE.get(previous_state),
            CHIRP_CONNECT_STATE.get(current_state)))

    def on_sending(self, payload):
        """ Called when a chirp has started to be transmitted """
        print('Sending: ' + str(payload))

    def on_sent(self, payload):
        """ Called when the entire chirp has been sent """
        print('Sent data')

    def on_receiving(self):
        """ Called when a chirp frontdoor is detected """
        print('Receiving data')

    def on_received(self, payload):
        """
        Called when an entire chirp has been received.
        Note: A length of 0 indicates a failed decode.
        """
        uid_py = "01"
        if len(payload) == 0:
            print('Decode failed!')
        else:
            print('Received:' + str(payload))            
            
            cryptokey = payload[0,10] + uid_py
            hash = payload[0,-1]    
            tx_receipt = w3.eth.getTransactionReceipt(hash)
            
            # Contract instance in concise mode
            abi = contract_interface['abi']
            contract_instance = w3.eth.contract(address=contract_address, abi=abi,ContractFactoryClass=ConciseContract)

            # Getters + Setters for web3.eth.contract object
            print('Contract value: {}'.format(contract_instance.getCredencials()))
            if (contract_instance['criptokey'] == hashlib.md5().update(crypotokey)) && datetime.strptime(contract_instance['data_i'], '%b %d %Y %I:%M%p') <= datetime.now() && datetime.strptime(contract_instance['data_f'],  '%b %d %Y %I:%M%p') >= datetime.now():
                open()


def main(licence_file,
         input_device, output_device,
         block_size, sample_rate):

    app_key = "AF7ccbc7F3CCfAcdddcF2"
    app_secret = "19FDf94E1Dca7FDc45A8beAFB58BAEd2DB00C6f4dFEae6cAE3"
   
    # Initialise ConnectSDK
    sdk = ChirpConnect(app_key, app_secret, licence_file)
    print(str(sdk))
    print(sdk.audio.query_devices())

    # Configure audio
    sdk.audio.input_device = input_device
    sdk.audio.output_device = output_device
    sdk.audio.block_size = block_size
    sdk.sample_rate = sample_rate

    # Set callback functions
    sdk.set_callbacks(MyCallbacks())

    # Generate random payload and send
    payload = sdk.random_payload()
    sdk.start(send=True, receive=True)
    sdk.send(payload)

    try:
        # Process audio streams
        while True:
            time.sleep(0.1)
            sys.stdout.write('.')
            sys.stdout.flush()
    except KeyboardInterrupt:
        print('Exiting')

    sdk.stop()
    sdk.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Chirp Connect SDK Example',
        epilog='Sends a random chirp payload, then continuously listens for chirps'
    )
    parser.add_argument('key', help='Chirp application key')
    parser.add_argument('secret', help='Chirp application secret')
    parser.add_argument('-l', help='Path to licence file (optional)')
    parser.add_argument('-i', type=int, default=None, help='Input device index (optional)')
    parser.add_argument('-o', type=int, default=None, help='Output device index (optional)')
    parser.add_argument('-b', type=int, default=0, help='Block size (optional)')
    parser.add_argument('-s', type=int, default=44100, help='Sample rate (optional)')
    args = parser.parse_args()

    main(args.key, args.secret, args.l, args.i, args.o, args.b, args.s)
