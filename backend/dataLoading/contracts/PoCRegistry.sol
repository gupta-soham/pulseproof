// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract PoCRegistry {
    event VerifiedPoC(
        bytes32 indexed pocHash,     // hash of PoC metadata (sha256)
        address indexed target,      // exploited contract (if applicable)
        uint256 indexed attackedVictimBlockNumber,
        string pocType ,              // "REENTRANCY","FLASH_LOAN",...
        string metadataURI ,          // optional offchain metadata (IPFS/HTTP)
        string severity,
        string summary
    );

    function registerPoC(
        bytes32 pocHash,
        address target,
        uint256 attackedVictimBlockNumber,
        string calldata pocType,
        string calldata metadataURI,
        string calldata severity,
        string calldata summary
    ) external {
        emit VerifiedPoC(
            pocHash,
            target,
            attackedVictimBlockNumber,
            pocType,
            metadataURI,
            severity,
            summary
        );
    }
}