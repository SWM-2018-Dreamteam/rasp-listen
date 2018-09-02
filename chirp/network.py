# ------------------------------------------------------------------------
#
#  This file is part of the Chirp Connect Python SDK.
#  For full information on usage and licensing, see https://chirp.io/
#
#  Copyright (c) 2011-2018, Asio Ltd.
#  All rights reserved.
#
# ------------------------------------------------------------------------
from datetime import datetime

import requests
from requests_futures.sessions import FuturesSession

from . import __version__
from .exceptions import ConnectNetworkError

session = FuturesSession()
licence_url = 'https://licence.chirp.io'
analytics_url = 'https://analytics.chirp.io'


def get_licence_data(key, secret, name=None):
    """
    Retrieve a licence for an application.
    If name is specified then this licence is returned, otherwise
    the default is used.

    Args:
        name (str): Licence name, default is used if not set

    Returns: (str) licence string

    Raises:
        ConnectNetworkError: If licence request fails
        ValueError: If an invalid licence name is requested
    """
    try:
        url = licence_url + '/v3/connect'
        r = requests.get(url, auth=(key, secret))
        if r.status_code != 200:
            err = r.json()
            raise ConnectNetworkError(err.get('message', 'Failed to retrieve licence'))
        data = r.json()
        licences = [l['name'] for l in data['data']]
        if name and name not in licences:
            raise ValueError('Invalid licence name')
        return data['data'][licences.index(name)] if name else data['data'][0]['licence']
    except requests.exceptions.ConnectionError:
        raise ConnectNetworkError('No internet connection')
    except requests.exceptions.Timeout:
        raise ConnectNetworkError('Timeout')
    except requests.exceptions.RequestException as err:
        raise ConnectNetworkError(str(err))


def async_request(url, auth, data):
    """ Asynschronous request with no consequences """
    try:
        session.post(url, auth=auth, json=data)
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.RequestException as err:
        pass


def create_instantiate(key, secret, uid):
    """ Instantiated the SDK """
    url = analytics_url + '/v3/connect/instantiate'
    async_request(url, (key, secret), {
        'client_id': uid,
        'timestamp': datetime.now().isoformat(),
        'platform': 'python',
        'sdk_version': __version__
    })


def create_send(key, secret, uid, length, protocol_name, protocol_version):
    """ Sent a payload """
    url = analytics_url + '/v3/connect/send'
    async_request(url, (key, secret), {
        'client_id': uid,
        'timestamp': datetime.now().isoformat(),
        'payload_length': length,
        'protocol_name': protocol_name,
        'protocol_version': protocol_version,
        'platform': 'python',
        'sdk_version': __version__
    })


def create_receive(key, secret, uid, length, protocol_name, protocol_version):
    """ Received a payload """
    url = analytics_url + '/v3/connect/receive'
    async_request(url, (key, secret), {
        'client_id': uid,
        'timestamp': datetime.now().isoformat(),
        'success': length != 0,
        'payload_length': length,
        'protocol_name': protocol_name,
        'protocol_version': protocol_version,
        'platform': 'python',
        'sdk_version': __version__
    })
