"use client";

import { useState } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Copy, ExternalLink, AlertTriangle } from "lucide-react";
import { showToast } from "@/lib/toast";

interface PocDialogProps {
  trigger: React.ReactNode;
  vulnerability: {
    serialNumber: number;
    pocSummary: string;
    category: string;
    priorityScore: number;
    pocCodeLink: string;
  };
}

// Sample PoC code for demonstration
const getSamplePocCode = (category: string) => {
  const samples = {
    reentrancy: `// Reentrancy Attack Example
contract VulnerableContract {
    mapping(address => uint256) public balances;
    
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "Insufficient balance");
        
        // Vulnerable: External call before state update
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] = 0; // State update after external call
    }
}

// Attack Contract
contract ReentrancyAttack {
    VulnerableContract public target;
    
    constructor(address _target) {
        target = VulnerableContract(_target);
    }
    
    function attack() external payable {
        target.withdraw();
    }
    
    receive() external payable {
        if (address(target).balance >= 1 ether) {
            target.withdraw(); // Reentrant call
        }
    }
}`,
    integer_overflow: `// Integer Overflow Attack Example
contract VulnerableToken {
    mapping(address => uint256) public balances;
    
    function transfer(address to, uint256 amount) public {
        // Vulnerable: No overflow check
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}

// Attack: Transfer more than balance to cause underflow
// balances[attacker] = 100
// transfer(victim, 101) causes underflow
// balances[attacker] becomes 2^256 - 1`,
    access_control: `// Access Control Vulnerability Example
contract VulnerableContract {
    address public owner;
    uint256 public funds;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Vulnerable: Missing access control
    function withdraw(uint256 amount) public {
        require(funds >= amount, "Insufficient funds");
        funds -= amount;
        payable(msg.sender).transfer(amount);
    }
    
    // Should be: onlyOwner modifier
    function setOwner(address newOwner) public {
        owner = newOwner;
    }
}`,
    default: `// Generic Smart Contract Vulnerability
contract VulnerableContract {
    // This is a sample PoC demonstrating
    // the vulnerability pattern found in your contract
    
    function vulnerableFunction() public {
        // Vulnerable code pattern here
        // Specific details would be shown
        // based on the actual vulnerability
    }
}`,
  };

  return samples[category as keyof typeof samples] || samples.default;
};

export function PocDialog({ trigger, vulnerability }: PocDialogProps) {
  const [copied, setCopied] = useState(false);

  const sampleCode = getSamplePocCode(vulnerability.category);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sampleCode);
      setCopied(true);
      showToast.success("PoC code copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      showToast.error("Failed to copy code");
    }
  };

  const handleViewExternal = () => {
    window.open(vulnerability.pocCodeLink, "_blank");
  };

  const getPriorityColor = (score: number) => {
    switch (score) {
      case 1:
        return "destructive";
      case 2:
        return "destructive";
      case 3:
        return "default";
      default:
        return "secondary";
    }
  };

  const getPriorityLabel = (score: number) => {
    switch (score) {
      case 1:
        return "Critical";
      case 2:
        return "High";
      case 3:
        return "Medium";
      default:
        return "Low";
    }
  };

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>{trigger}</AlertDialogTrigger>
      <AlertDialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
        <AlertDialogHeader>
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <Badge variant={getPriorityColor(vulnerability.priorityScore)}>
              {getPriorityLabel(vulnerability.priorityScore)}
            </Badge>
            <Badge variant="outline" className="font-mono">
              #{vulnerability.serialNumber}
            </Badge>
          </div>
          <AlertDialogTitle className="text-left">
            Proof of Concept: {vulnerability.pocSummary}
          </AlertDialogTitle>
          <AlertDialogDescription className="text-left">
            <span className="capitalize">
              {vulnerability.category.replace("_", " ")} vulnerability
            </span>
            {" - "}
            This is a sample demonstration of how this vulnerability could be
            exploited.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="flex-1 overflow-hidden">
          <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4 h-full overflow-auto">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium">Sample PoC Code</h4>
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopy}
                className="h-8"
              >
                <Copy className="h-4 w-4 mr-2" />
                {copied ? "Copied!" : "Copy"}
              </Button>
            </div>
            <pre className="text-xs overflow-auto bg-white dark:bg-slate-800 p-3 rounded border">
              <code>{sampleCode}</code>
            </pre>
          </div>
        </div>

        <AlertDialogFooter className="flex-col sm:flex-row gap-2">
          <AlertDialogCancel>Close</AlertDialogCancel>
          <AlertDialogAction onClick={handleViewExternal}>
            <ExternalLink className="h-4 w-4 mr-2" />
            View Full Report
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
