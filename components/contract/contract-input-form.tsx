"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ContractStorage } from "@/lib/contract-storage";
import { Loader2 } from "lucide-react";
import { Logo } from "@/components/ui/logo";

interface ContractInputFormProps {
  onSuccess?: () => void;
}

const NETWORKS = [
  { value: "ethereum", label: "Ethereum Mainnet" },
  { value: "polygon", label: "Polygon" },
  { value: "bsc", label: "Binance Smart Chain" },
  { value: "arbitrum", label: "Arbitrum" },
  { value: "optimism", label: "Optimism" },
];

export function ContractInputForm({ onSuccess }: ContractInputFormProps) {
  const [address, setAddress] = useState("");
  const [network, setNetwork] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const validateAddress = (addr: string): boolean => {
    return ContractStorage.validateContractAddress(addr);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!address.trim()) {
      setError("Contract address is required");
      return;
    }

    if (!validateAddress(address)) {
      setError("Invalid Ethereum address format");
      return;
    }

    if (!network) {
      setError("Please select a network");
      return;
    }

    setIsLoading(true);

    try {
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const success = ContractStorage.addContract({
        address: address.trim(),
        network,
      });

      if (success) {
        onSuccess?.();
        router.push("/dashboard");
      } else {
        setError("Failed to save contract. Please try again.");
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const isAddressValid = address ? validateAddress(address) : null;

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <Logo width={48} height={48} />
        </div>
        <CardTitle className="text-2xl">Add Contract to Monitor</CardTitle>
        <CardDescription>
          Enter your smart contract address to start monitoring for security
          vulnerabilities
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="address">Contract Address</Label>
            <Input
              id="address"
              type="text"
              placeholder="0x..."
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className={
                isAddressValid === false
                  ? "border-destructive focus-visible:ring-destructive"
                  : isAddressValid === true
                    ? "border-green-500 focus-visible:ring-green-500"
                    : ""
              }
              disabled={isLoading}
            />
            {isAddressValid === false && (
              <p className="text-sm text-destructive">
                Invalid Ethereum address format
              </p>
            )}
            {isAddressValid === true && (
              <p className="text-sm text-green-600">Valid Ethereum address</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="network">Network</Label>
            <Select
              value={network}
              onValueChange={setNetwork}
              disabled={isLoading}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select network" />
              </SelectTrigger>
              <SelectContent>
                {NETWORKS.map((net) => (
                  <SelectItem key={net.value} value={net.value}>
                    {net.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {error && (
            <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              {error}
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading || !isAddressValid || !network}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Adding Contract...
              </>
            ) : (
              "Start Monitoring"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
