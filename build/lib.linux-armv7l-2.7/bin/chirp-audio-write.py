#!/usr/bin/env python

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
import wave

from chirp import (
    ChirpConnect,
    CHIRP_CONNECT_STATE, CHIRP_CONNECT_STATE_SENDING,
    CHIRP_CONNECT_BUFFER_SIZE
)


def main(args):
    # Initialise the Chirp Connect SDK
    sdk = ChirpConnect(args.app_key, args.app_secret, args.app_licence)
    print(str(sdk))

    # Disable audio playback
    sdk.audio = None
    sdk.start(send=True, receive=False)

    # Encode an ASCII string as a payload
    if args.ascii:
        message = args.ascii.encode('ascii')
        payload = sdk.new_payload(message)
    elif args.hex:
        message = bytearray.fromhex(args.hex)
        payload = sdk.new_payload(message)
    else:
        payload = sdk.random_payload()

    # Process output
    output_file = args.output_file if args.output_file else '%s.wav' % payload
    w = wave.open(output_file, 'w')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sdk.sample_rate)

    sdk.send(payload)

    while sdk.state == CHIRP_CONNECT_STATE_SENDING:
        data = '\x00' * CHIRP_CONNECT_BUFFER_SIZE
        sdk.process_shorts_output(data)
        w.writeframes(data.encode() if sys.version[0] == '3' else data)

    print('Wrote audio to output: %s' % output_file)
    w.close()

    sdk.stop()
    sdk.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Chirp Connect Audio Writer',
        epilog='Generates a .wav file containing a Chirp payload, either user-specified or random payload'
    )
    parser.add_argument('app_key', help='Chirp Connect application key')
    parser.add_argument('app_secret', help='Chirp Connect application secret')
    parser.add_argument('app_licence', help='Chirp Connect application licence', nargs='?')
    parser.add_argument('-o', '--output-file', type=str, help='Output filename to write .wav data to')
    parser.add_argument('-A', '--ascii', type=str, help='ASCII string used to generate payload')
    parser.add_argument('-H', '--hex', type=str, help='Hex string used to generate payload')
    args = parser.parse_args()

    main(args)
