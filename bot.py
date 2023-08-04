#!/usr/bin/env python3
from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException
from substrateinterface.base import KeypairType
from substrateinterface.utils.hasher import blake2_256
import logging, sys, json

with open('config.json', 'r') as f:
    config = json.load(f)

substrate = SubstrateInterface(url = config['endpoint'])
keypair = Keypair.create_from_mnemonic(config['proxy_seed'])
one_dot = 10**10

register_candidates_call = substrate.compose_call(
        call_module='CollatorSelection',
        call_function='register_as_candidate'
)

balance_call_test = substrate.compose_call(
    call_module='Balances',
    call_function='transfer',
    call_params={
        'dest': '12owmS8Sobqxfx6KK9vk9e67FqnGpZdmxCFCRFptzZdsoujC',
        'value': 1 * one_dot
    }
)

def call_extrinsic(extrinsic, tip):
    call = substrate.create_signed_extrinsic(extrinsic, keypair, tip=tip)
    try:
        receipt = substrate.submit_extrinsic(call, wait_for_inclusion=True)
        logging.info(f"Extrinsic {receipt.extrinsic_hash} included in a block {receipt.block_number}")
        if receipt.is_success:
            logging.info(f"Success")
        else:
            logging.error(f"Failed {receipt.error_message}")

    except SubstrateRequestException as e:
        logging.info(f"Failed to send {e}")


def subscription_handler(obj, update_nr, subscription_id):
    logging.info(f"New block {obj['header']['number']}")

    block = substrate.get_block(block_number=obj['header']['number'])

    for idx, extrinsic in enumerate(block['extrinsics']):
        if extrinsic['call']['call_module']['name'] == 'CollatorSelection':
            tip = one_dot ** -5 # 0.00001
            # call_extrinsic(register_candidates_call, tip)
            logging.info("System called")
        if idx > 1:
            logging.info(f"{idx}:  {extrinsic['call']['call_module']['name']}.{extrinsic['call']['call_function']['name']}")

if __name__ == "__main__":
  logging.basicConfig(stream=sys.stdout, level=logging.INFO)
  result = substrate.subscribe_block_headers(subscription_handler)
  print(result)
