"use client";

import { useState } from "react";
import { motion, type Transition } from "motion/react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { VulnerabilityAlert } from "@/types";
import { VulnerabilityDataService } from "@/lib/vulnerability-data";
import { PocDialog } from "@/components/ui/poc-dialog";
import {
  AlertTriangle,
  X,
  ExternalLink,
  Clock,
  ArrowUpRight,
} from "lucide-react";
import { Logo } from "@/components/ui/logo";

interface CriticalNotificationsProps {
  alerts: VulnerabilityAlert[];
  onDismiss?: (alertId: string) => void;
  onAcknowledge?: (alertId: string) => void;
}

const transition: Transition = {
  type: "spring",
  stiffness: 300,
  damping: 26,
};

const getCardVariants = (i: number) => ({
  collapsed: {
    marginTop: i === 0 ? 0 : -92, // Much closer stacking
    scaleX: 1 - i * 0.02, // Even less scaling for tighter stack
  },
  expanded: {
    marginTop: i === 0 ? 0 : 2, // Almost no gap when expanded
    scaleX: 1,
  },
});

const textSwitchTransition: Transition = {
  duration: 0.22,
  ease: "easeInOut",
};

const notificationTextVariants = {
  collapsed: { opacity: 1, y: 0, pointerEvents: "auto" as const },
  expanded: { opacity: 0, y: -16, pointerEvents: "none" as const },
};

const viewAllTextVariants = {
  collapsed: { opacity: 0, y: 16, pointerEvents: "none" as const },
  expanded: { opacity: 1, y: 0, pointerEvents: "auto" as const },
};

export function CriticalNotifications({
  alerts,
  onDismiss,
  onAcknowledge,
}: CriticalNotificationsProps) {
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(
    new Set()
  );

  const visibleAlerts = alerts.filter(
    (alert) => !dismissedAlerts.has(alert.id) && alert.priorityScore === 1
  );

  const handleDismiss = (alertId: string) => {
    setDismissedAlerts((prev) => new Set([...prev, alertId]));
    onDismiss?.(alertId);
  };

  const handleAcknowledge = (alertId: string) => {
    onAcknowledge?.(alertId);
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60)
    );

    if (diffInMinutes < 1) return "just now";
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  if (visibleAlerts.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col lg:flex-row gap-4 w-full">
      {/* Main notification stack */}
      <motion.div
        className="bg-red-50 dark:bg-red-950/20 p-3 sm:p-4 rounded-2xl w-full lg:flex-1 space-y-3 shadow-lg border border-red-200 dark:border-red-800"
        initial="collapsed"
        whileHover="expanded"
        whileTap="expanded"
      >
        <div className="space-y-0">
          {visibleAlerts.slice(0, 5).map((alert, i) => (
            <motion.div
              key={alert.id}
              className="bg-white dark:bg-neutral-800 rounded-xl px-3 sm:px-4 py-3 sm:py-4 shadow-sm hover:shadow-md transition-shadow duration-200 relative border border-red-100 dark:border-red-800/50"
              variants={getCardVariants(i)}
              transition={transition}
              style={{
                zIndex: visibleAlerts.length - i,
              }}
            >
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
                <div className="flex-1 space-y-2 sm:space-y-3">
                  {/* Header with badges - responsive layout */}
                  <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-500 flex-shrink-0" />
                    <Badge variant="destructive" className="text-xs">
                      Critical
                    </Badge>
                    <Badge
                      variant="outline"
                      className="text-xs font-mono truncate max-w-[120px] sm:max-w-none"
                    >
                      {VulnerabilityDataService.getHashBadge(
                        alert.contractHash
                      )}
                    </Badge>
                  </div>

                  {/* Content */}
                  <div className="space-y-1.5">
                    <h3 className="text-sm sm:text-base font-medium leading-tight">
                      {alert.pocSummary}
                    </h3>

                    {/* Meta info - stack on mobile, inline on desktop */}
                    <div className="text-xs text-muted-foreground">
                      <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2">
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3 flex-shrink-0" />
                          <span>{formatTimeAgo(alert.detectedAt)}</span>
                        </div>
                        <span className="hidden sm:inline">•</span>
                        <span className="capitalize">
                          {alert.category.replace("_", " ")}
                        </span>
                        <span className="hidden sm:inline">•</span>
                        <span>SN #{alert.serialNumber}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions - better mobile layout */}
                  <div className="flex items-center gap-2 pt-1">
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-7 sm:h-8 text-xs px-2 sm:px-3"
                      onClick={() => handleAcknowledge(alert.id)}
                    >
                      Acknowledge
                    </Button>
                    <PocDialog
                      vulnerability={alert}
                      trigger={
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-7 sm:h-8 text-xs px-2 sm:px-3"
                        >
                          View PoC
                        </Button>
                      }
                    />
                  </div>
                </div>

                {/* Dismiss button - better positioning */}
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 w-7 sm:h-8 sm:w-8 p-0 text-muted-foreground hover:text-foreground self-start sm:self-auto flex-shrink-0"
                  onClick={() => handleDismiss(alert.id)}
                >
                  <X className="h-3 w-3 sm:h-4 sm:w-4" />
                </Button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Footer - responsive layout */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 pt-2 border-t border-red-200 dark:border-red-800">
          <div className="flex items-center gap-3">
            <div className="size-6 sm:size-7 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-medium flex-shrink-0">
              {visibleAlerts.length}
            </div>
            <span className="grid flex-1 sm:flex-none">
              <motion.span
                className="text-sm font-medium text-red-700 dark:text-red-300 row-start-1 col-start-1 flex items-center gap-2"
                variants={notificationTextVariants}
                transition={textSwitchTransition}
              >
                <Logo className="flex-shrink-0" width={16} height={16} />
                <span className="truncate">Critical Security Alerts</span>
              </motion.span>
              <motion.span
                className="text-sm font-medium text-red-700 dark:text-red-300 flex items-center gap-1 cursor-pointer select-none row-start-1 col-start-1"
                variants={viewAllTextVariants}
                transition={textSwitchTransition}
              >
                <span className="truncate">View all alerts</span>
                <ArrowUpRight className="size-4 flex-shrink-0" />
              </motion.span>
            </span>
          </div>

          {visibleAlerts.length > 1 && (
            <Button
              variant="ghost"
              size="sm"
              className="text-xs text-red-600 hover:text-red-700 self-start sm:self-auto"
              onClick={() => {
                visibleAlerts.forEach((alert) => handleDismiss(alert.id));
              }}
            >
              Dismiss All
            </Button>
          )}
        </div>
      </motion.div>

      {/* Right sidebar with additional info */}
      <div className="w-full lg:w-80 space-y-4">
        {/* Quick Stats */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-4 shadow-sm border border-red-100 dark:border-red-800/50">
          <h4 className="text-sm font-semibold text-red-700 dark:text-red-300 mb-3 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Alert Summary
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">
                Total Critical
              </span>
              <Badge variant="destructive" className="text-xs">
                {visibleAlerts.length}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">Last 24h</span>
              <span className="text-xs font-medium">
                {
                  visibleAlerts.filter(
                    (alert) =>
                      new Date().getTime() - alert.detectedAt.getTime() <
                      24 * 60 * 60 * 1000
                  ).length
                }
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">
                Unacknowledged
              </span>
              <span className="text-xs font-medium">
                {visibleAlerts.filter((alert) => alert.status === "new").length}
              </span>
            </div>
          </div>
        </div>

        {/* Categories Breakdown */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-4 shadow-sm border border-red-100 dark:border-red-800/50">
          <h4 className="text-sm font-semibold text-red-700 dark:text-red-300 mb-3">
            Alert Categories
          </h4>
          <div className="space-y-2">
            {Object.entries(
              visibleAlerts.reduce(
                (acc, alert) => {
                  const category = alert.category.replace("_", " ");
                  acc[category] = (acc[category] || 0) + 1;
                  return acc;
                },
                {} as Record<string, number>
              )
            ).map(([category, count]) => (
              <div key={category} className="flex justify-between items-center">
                <span className="text-xs text-muted-foreground capitalize">
                  {category}
                </span>
                <span className="text-xs font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl p-4 shadow-sm border border-red-100 dark:border-red-800/50">
          <h4 className="text-sm font-semibold text-red-700 dark:text-red-300 mb-3">
            Quick Actions
          </h4>
          <div className="space-y-2">
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start text-xs"
              onClick={() => {
                visibleAlerts.forEach((alert) => handleAcknowledge(alert.id));
              }}
            >
              <Logo className="mr-2" width={12} height={12} />
              Acknowledge All
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start text-xs"
            >
              <ExternalLink className="h-3 w-3 mr-2" />
              View Full Report
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start text-xs"
            >
              <Clock className="h-3 w-3 mr-2" />
              Alert History
            </Button>
          </div>
        </div>

        {/* Recent Activity */}
        {visibleAlerts.length > 5 && (
          <div className="bg-white dark:bg-neutral-800 rounded-xl p-4 shadow-sm border border-red-100 dark:border-red-800/50">
            <h4 className="text-sm font-semibold text-red-700 dark:text-red-300 mb-3">
              More Alerts
            </h4>
            <div className="space-y-2">
              {visibleAlerts.slice(5, 8).map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center gap-2 p-2 rounded-lg bg-red-50 dark:bg-red-950/20"
                >
                  <AlertTriangle className="h-3 w-3 text-red-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium truncate">
                      {alert.pocSummary}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatTimeAgo(alert.detectedAt)}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0"
                    onClick={() => handleDismiss(alert.id)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ))}
              {visibleAlerts.length > 8 && (
                <div className="text-center pt-2">
                  <Button variant="ghost" size="sm" className="text-xs">
                    +{visibleAlerts.length - 8} more alerts
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
