// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract PoCRegistry {
    event VerifiedPoC(
        bytes32 indexed pocHash,     // hash of PoC metadata (sha256)
        string pocType,              // "REENTRANCY","FLASH_LOAN",...
        address indexed target,      // exploited contract (if applicable)
        string metadataURI,          // optional offchain metadata (IPFS/HTTP)
        string hederaTx              // optional Hedera tx id anchor
    );

    function registerPoC(
        bytes32 pocHash,
        string calldata pocType,
        address target,
        string calldata metadataURI,
        string calldata hederaTx
    ) external {
        emit VerifiedPoC(pocHash, pocType, target, metadataURI, hederaTx);
    }
}