"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ContractStorage } from "@/lib/contract-storage";
import { ContractAddress } from "@/types";
import { ExternalLink, Settings, Plus, Activity } from "lucide-react";
import { Logo } from "@/components/ui/logo";

interface DashboardHeaderProps {
  onContractChange?: (contract: ContractAddress | null) => void;
}

const NETWORK_COLORS = {
  ethereum: "default",
  polygon: "secondary",
  bsc: "outline",
  arbitrum: "destructive",
  optimism: "default",
} as const;

export function DashboardHeader({ onContractChange }: DashboardHeaderProps) {
  const [activeContract, setActiveContract] = useState<ContractAddress | null>(
    null
  );
  const [allContracts, setAllContracts] = useState<ContractAddress[]>([]);
  const [isOnline, setIsOnline] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadContracts();

    // Simulate connection status
    const interval = setInterval(() => {
      setIsOnline(Math.random() > 0.1); // 90% uptime simulation
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const loadContracts = () => {
    const active = ContractStorage.getActiveContract();
    const all = ContractStorage.getAllContracts();

    setActiveContract(active);
    setAllContracts(all);
    onContractChange?.(active);
  };

  const handleAddContract = () => {
    router.push("/onboarding");
  };

  const handleSwitchContract = (address: string) => {
    try {
      ContractStorage.setActiveContract(address);
      loadContracts();
    } catch (error) {
      console.error("Failed to switch contract:", error);
    }
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const getExplorerUrl = (address: string, network: string) => {
    const explorers = {
      ethereum: "https://etherscan.io/address/",
      polygon: "https://polygonscan.com/address/",
      bsc: "https://bscscan.com/address/",
      arbitrum: "https://arbiscan.io/address/",
      optimism: "https://optimistic.etherscan.io/address/",
    };

    return explorers[network as keyof typeof explorers] + address;
  };

  if (!activeContract) {
    return (
      <Card>
        <CardContent className="flex items-center justify-between p-6">
          <div className="flex items-center gap-4">
            <Logo className="opacity-60" width={32} height={32} />
            <div>
              <h1 className="text-2xl font-bold">PulseProof Dashboard</h1>
              <p className="text-muted-foreground">
                No contracts being monitored
              </p>
            </div>
          </div>
          <Button onClick={handleAddContract}>
            <Plus className="mr-2 h-4 w-4" />
            Add Contract
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Logo width={32} height={32} />
              <div>
                <h1 className="text-2xl font-bold">PulseProof Dashboard</h1>
                <div className="flex items-center gap-2 mt-1">
                  <Activity
                    className={`h-3 w-3 ${isOnline ? "text-green-500" : "text-red-500"}`}
                  />
                  <span className="text-sm text-muted-foreground">
                    {isOnline ? "Monitoring Active" : "Connection Lost"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm" onClick={handleAddContract}>
              <Plus className="mr-2 h-4 w-4" />
              Add Contract
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
          </div>
        </div>

        <div className="mt-6 p-4 bg-muted/50 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Active Contract:</span>
                <code className="text-sm bg-background px-2 py-1 rounded border">
                  {formatAddress(activeContract.address)}
                </code>
                <Badge
                  variant={
                    NETWORK_COLORS[
                      activeContract.network as keyof typeof NETWORK_COLORS
                    ] || "default"
                  }
                  className="text-xs"
                >
                  {activeContract.network}
                </Badge>
              </div>
              <div className="text-xs text-muted-foreground">
                Added on {new Date(activeContract.addedAt).toLocaleDateString()}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  window.open(
                    getExplorerUrl(
                      activeContract.address,
                      activeContract.network
                    ),
                    "_blank"
                  )
                }
              >
                <ExternalLink className="mr-2 h-3 w-3" />
                View on Explorer
              </Button>

              {allContracts.length > 1 && (
                <select
                  className="text-sm border rounded px-2 py-1 bg-background"
                  value={activeContract.address}
                  onChange={(e) => handleSwitchContract(e.target.value)}
                >
                  {allContracts.map((contract) => (
                    <option key={contract.address} value={contract.address}>
                      {formatAddress(contract.address)} ({contract.network})
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
