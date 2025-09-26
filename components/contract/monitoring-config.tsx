"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { MonitoringConfig } from "@/types";
import { Eye, AlertTriangle, Zap, DollarSign, Activity } from "lucide-react";

interface MonitoringConfigDisplayProps {
  contractAddress?: string;
  network?: string;
}

const DEFAULT_MONITORING_CONFIG: MonitoringConfig = {
  contractAddress: "",
  monitoringEvents: [
    "Reentrancy Attack Detection",
    "Suspicious Transaction Patterns",
    "High Gas Usage Alerts",
    "Liquidity Pool Manipulation",
    "Flash Loan Attack Patterns",
    "Price Oracle Manipulation",
    "MEV Bot Activity",
    "Governance Token Manipulation",
    "Timestamp Manipulation",
    "Integer Overflow/Underflow",
  ],
  thresholds: {
    gasLimit: 500000,
    transactionAmount: 1000000, // in wei equivalent
    liquidityRatio: 0.1, // 10% of pool
  },
};

const EVENT_ICONS = {
  "Reentrancy Attack Detection": AlertTriangle,
  "Suspicious Transaction Patterns": Eye,
  "High Gas Usage Alerts": Zap,
  "Liquidity Pool Manipulation": DollarSign,
  "Flash Loan Attack Patterns": Activity,
  "Price Oracle Manipulation": DollarSign,
  "MEV Bot Activity": Activity,
  "Governance Token Manipulation": AlertTriangle,
  "Timestamp Manipulation": Eye,
  "Integer Overflow/Underflow": AlertTriangle,
};

const EVENT_COLORS = {
  "Reentrancy Attack Detection": "destructive",
  "Suspicious Transaction Patterns": "default",
  "High Gas Usage Alerts": "secondary",
  "Liquidity Pool Manipulation": "destructive",
  "Flash Loan Attack Patterns": "default",
  "Price Oracle Manipulation": "destructive",
  "MEV Bot Activity": "secondary",
  "Governance Token Manipulation": "destructive",
  "Timestamp Manipulation": "default",
  "Integer Overflow/Underflow": "destructive",
} as const;

export function MonitoringConfigDisplay({
  contractAddress,
  network,
}: MonitoringConfigDisplayProps) {
  const config: MonitoringConfig = {
    ...DEFAULT_MONITORING_CONFIG,
    contractAddress: contractAddress || "",
  };

  const configJson = {
    contract: {
      address: contractAddress || "Not specified",
      network: network || "Not specified",
    },
    monitoring: {
      events: config.monitoringEvents,
      thresholds: {
        maxGasLimit: config.thresholds.gasLimit.toLocaleString(),
        maxTransactionAmount: `${(config.thresholds.transactionAmount / 1e18).toFixed(2)} ETH`,
        liquidityRatioAlert: `${config.thresholds.liquidityRatio * 100}%`,
      },
    },
    alerting: {
      realTimeNotifications: true,
      criticalAlertThreshold: "Priority 1-2",
      notificationChannels: ["Dashboard", "Browser Notifications"],
    },
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Monitoring Configuration
          </CardTitle>
          <CardDescription>
            Events and patterns that will be monitored for your contract
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-3">Security Events</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {config.monitoringEvents.map((event) => {
                const Icon =
                  EVENT_ICONS[event as keyof typeof EVENT_ICONS] ||
                  AlertTriangle;
                const color =
                  EVENT_COLORS[event as keyof typeof EVENT_COLORS] || "default";

                return (
                  <Badge
                    key={event}
                    variant={color}
                    className="flex items-center gap-1 justify-start p-2 h-auto"
                  >
                    <Icon className="h-3 w-3" />
                    <span className="text-xs">{event}</span>
                  </Badge>
                );
              })}
            </div>
          </div>

          <Separator />

          <div>
            <h4 className="text-sm font-medium mb-3">Alert Thresholds</h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
              <div className="space-y-1">
                <div className="text-muted-foreground">Gas Limit</div>
                <div className="font-medium">
                  {config.thresholds.gasLimit.toLocaleString()}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-muted-foreground">Transaction Amount</div>
                <div className="font-medium">
                  {(config.thresholds.transactionAmount / 1e18).toFixed(2)} ETH
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-muted-foreground">Liquidity Ratio</div>
                <div className="font-medium">
                  {config.thresholds.liquidityRatio * 100}%
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Configuration JSON</CardTitle>
          <CardDescription>
            Complete monitoring configuration for frontend mapping
          </CardDescription>
        </CardHeader>
        <CardContent>
          <pre className="text-xs bg-muted p-4 rounded-md overflow-x-auto">
            {JSON.stringify(configJson, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
