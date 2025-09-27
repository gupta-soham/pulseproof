#!/usr/bin/env python3
import os, json, hashlib, tempfile
from pathlib import Path
from typing import Union
from lighthouseweb3 import Lighthouse
from web3 import Web3
from eth_account import Account
from hexbytes import HexBytes

# Load environment variables from .env file

from dotenv import load_dotenv
# Look for .env file in the eth-global directory (parent of agents)
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
else:
    print(f"No .env file found at: {env_path}")
    load_dotenv()

LH_KEY = os.getenv("LIGHTHOUSE_API_KEY")
RPC = os.getenv("ALCHEMY_API_KEY")
PK = os.getenv("PRIVATE_KEY") or os.getenv("PK")  # Try both variable names
CONTRACT = os.getenv("CONTRACT_ADDRESS")

# Debug output
print(f"LIGHTHOUSE_API_KEY: {'✓' if LH_KEY else '✗'}")
print(f"ALCHEMY_API_KEY: {'✓' if RPC else '✗'}")
print(f"PRIVATE_KEY/PK: {'✓' if PK else '✗'}")
print(f"CONTRACT_ADDRESS: {'✓' if CONTRACT else '✗'}")

assert LH_KEY and RPC and PK and CONTRACT, "Set LIGHTHOUSE_API_KEY, ALCHEMY_API_KEY, PRIVATE_KEY (or PK), CONTRACT_ADDRESS"
RPC=f"https://eth-sepolia.g.alchemy.com/v2/{RPC}"
lh = Lighthouse(token=LH_KEY)
w3 = Web3(Web3.HTTPProvider(RPC))
acct = Account.from_key(PK)
contract = w3.eth.contract(address=w3.to_checksum_address(CONTRACT), abi=[
    {
      "name": "registerPoC",
      "type": "function",
      "stateMutability": "nonpayable",
      "inputs": [
        {"name": "pocHash", "type": "bytes32"},
        {"name": "target", "type": "address"},
        {"name": "attackedVictimBlockNumber", "type": "uint256"},
        {"name": "pocType", "type": "string"},
        {"name": "metadataURI", "type": "string"},
        {"name": "severity", "type": "string"},
        {"name": "summary", "type": "string"}
      ],
      "outputs": []
    }
])

def _tmp_file_from_bytes(b: bytes, suffix: str):
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tf.write(b); tf.flush(); tf.close()
    return tf.name

def upload_to_lighthouse(source: Union[str, bytes], tag: str = "poc"):
    if isinstance(source, (bytes, bytearray)):
        path = _tmp_file_from_bytes(bytes(source), suffix=".bin")
        try:
            res = lh.upload(source=path, tag=tag)
        finally:
            try: Path(path).unlink()
            except: pass
    else:
        res = lh.upload(source=source, tag=tag)
    # Lighthouse response usually in res["data"]["Hash"]
    cid = None
    if isinstance(res, dict):
        cid = res.get("data", {}).get("Hash") or res.get("cid") or res.get("Hash")
    if not cid:
        raise RuntimeError(f"Upload failed: {res}")
    return cid

def sha256_hex(b: bytes) -> str:
    return "0x" + hashlib.sha256(b).hexdigest()

def register_poc(poc_source: Union[str, bytes], poc_filename: str, poc_id: str,
                         poc_type: str, target: str, block_number: int, severity: str, summary: str):
    # upload PoC file
    poc_cid = upload_to_lighthouse(poc_source, tag=f"poc-{poc_type}")
    poc_uri = f"ipfs://{poc_cid}/{poc_filename}"

    # metadata (canonical)
    meta = {"poc_id": poc_id, "poc_file": poc_uri, "vulnerability": poc_type, "target": target, "block_number": int(block_number)}
    meta_bytes = json.dumps(meta, sort_keys=True, separators=(",", ":")).encode()
    meta_cid = upload_to_lighthouse(meta_bytes, tag=f"meta-{poc_type}")
    metadata_uri = f"ipfs://{meta_cid}/metadata.json"

    poc_hash = sha256_hex(meta_bytes)  # bytes32 hex

    # build tx
    func = contract.functions.registerPoC(
    w3.to_bytes(hexstr=poc_hash),            # bytes32
    w3.to_checksum_address(target),          # address
    int(block_number),                       # uint256 attackedVictimBlockNumber
    poc_type,                            # string pocType
    metadata_uri,                        # string metadataURI
    severity,                            # string severity
    summary                              # string summary
)
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = func.build_transaction({"from": acct.address, "nonce": nonce, "gas": 300000, "gasPrice": w3.eth.gas_price})
    signed = acct.sign_transaction(tx)
    raw = HexBytes(signed.raw_transaction).hex()

    out = {"poc_cid": poc_cid, "meta_cid": meta_cid, "metadata_uri": metadata_uri, "metadata_sha256": poc_hash, "signed_raw_tx": raw}

    txh = w3.eth.send_raw_transaction(signed.raw_transaction)
    out["tx_hash"] = HexBytes(txh).hex()
    return out

if __name__ == "__main__":
    # quick example
    poc_code = "// PoC example\npragma solidity ^0.8.19;"

    r = register_poc(poc_source=poc_code.encode(), poc_filename="exploit.sol", poc_id="poc_demo",
                             poc_type="REENTRANCY", severity="high", summary="Reentrancy attack", target="0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
                             block_number=65535)  # Use max uint16 value
    print(json.dumps(r, indent=2))
