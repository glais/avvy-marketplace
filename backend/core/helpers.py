from avvy import AvvyClient
from web3.middleware import geth_poa_middleware
from web3 import Web3
from . import contracts


# We're not actually pulling data from the chain
# Instead we're pulling from the centralized
# avvy indexer for simplicity. In the future
# data could be pulled directly from RPC.
def get_w3(network_id=None):
	if network_id is None: network_id = 43114
	rpc_url = {
		43113: 'https://api.avax-test.network/ext/bc/C/rpc',
		43114: 'https://api.avax.network/ext/bc/C/rpc',
	}[network_id]
	provider = Web3.HTTPProvider(rpc_url)
	w3 = Web3(provider)
	w3.middleware_onion.inject(geth_poa_middleware, layer=0)
	return w3


def get_avvy():
	return AvvyClient(get_w3())


def get_hash(name):
	avvy = get_avvy()
	return avvy.utils.name_hash(name)
