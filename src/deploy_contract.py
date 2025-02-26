from web3 import Web3
import json
import os
from solcx import compile_standard, install_solc

# Load configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file)

INFURA_URL = f"https://mainnet.infura.io/v3/{config['API_KEYS']['infura']}"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS")

# Solidity Smart Contract Code
CONTRACT_SOURCE = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ArbitrageBot {
    address public owner;

    event TradeExecuted(address indexed tokenA, address indexed tokenB, uint256 amountA, uint256 amountB);

    constructor() {
        owner = msg.sender;
    }

    function executeTrade(address tokenA, address tokenB, uint256 amountA, uint256 amountB) public {
        require(msg.sender == owner, "Only owner can execute trades");
        emit TradeExecuted(tokenA, tokenB, amountA, amountB);
    }
}
"""

# Install Solidity Compiler
install_solc("0.8.0")

# Compile Contract
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ArbitrageBot.sol": {"content": CONTRACT_SOURCE}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode", "evm.deployedBytecode"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

# Extract ABI & Bytecode
contract_interface = compiled_sol["contracts"]["ArbitrageBot.sol"]
contract_name = list(contract_interface.keys())[0]  # Get actual contract name
bytecode = contract_interface[contract_name]["evm"]["bytecode"]["object"]
abi = contract_interface[contract_name]["abi"]

# Web3 Connection
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not web3.is_connected():
    print("[ERROR] Failed to connect to Ethereum network")
    exit()

def deploy_contract():
    print("[INFO] Deploying smart contract...")

    # Deploy contract
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    tx = contract.constructor().build_transaction({
        "from": ACCOUNT_ADDRESS,
        "nonce": web3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        "gas": 3000000,
        "gasPrice": web3.to_wei("20", "gwei"),
    })

    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt.contractAddress
    print(f"[SUCCESS] Contract deployed at: {contract_address}")

    # Save contract address in config.json
    config["CONTRACT_ADDRESS"] = contract_address
    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=2)

    return contract_address

if __name__ == "__main__":
    deploy_contract()
