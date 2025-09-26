"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ContractInputForm } from "@/components/contract/contract-input-form";
import { MonitoringConfigDisplay } from "@/components/contract/monitoring-config";
import { ContractStorage } from "@/lib/contract-storage";
import { Logo } from "@/components/ui/logo";

export default function OnboardingPage() {
  const [contractAddress, setContractAddress] = useState("");
  const [network, setNetwork] = useState("");
  const [showConfig, setShowConfig] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check if user already has contracts
    const activeContract = ContractStorage.getActiveContract();
    if (activeContract) {
      router.push("/dashboard");
    }
  }, [router]);

  const handleFormSuccess = () => {
    // This will be called when the form is successfully submitted
    // The form component handles navigation to dashboard
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] bg-gradient-to-br from-background to-muted/20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="flex items-center gap-3">
              <Logo width={40} height={40} />
              <h1 className="text-4xl font-bold tracking-tight">PulseProof</h1>
            </div>
          </div>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Advanced Web3 security monitoring for smart contracts. Detect
            vulnerabilities, suspicious activities, and malicious attacks in
            real-time.
          </p>
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 items-start">
            {/* Left Column - Form */}
            <div className="space-y-6">
              <ContractInputForm onSuccess={handleFormSuccess} />

              {/* Features List */}
              <div className="bg-card rounded-lg p-6 border">
                <h3 className="text-lg font-semibold mb-4">What We Monitor</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-destructive rounded-full"></div>
                    <span>Reentrancy and flash loan attacks</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-destructive rounded-full"></div>
                    <span>Suspicious transaction patterns</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-secondary rounded-full"></div>
                    <span>Excessive gas usage and MEV activity</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-destructive rounded-full"></div>
                    <span>Liquidity manipulation attempts</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-secondary rounded-full"></div>
                    <span>Price oracle and governance attacks</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column - Configuration Preview */}
            <div className="space-y-6">
              <MonitoringConfigDisplay
                contractAddress={contractAddress}
                network={network}
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-16 text-sm text-muted-foreground">
          <p>
            Secure your smart contracts with real-time monitoring and instant
            alerts
          </p>
        </div>
      </div>
    </div>
  );
}
