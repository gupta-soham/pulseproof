"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ContractStorage } from "@/lib/contract-storage";
import { showToast } from "@/lib/toast";
import { Loader2 } from "lucide-react";
import { Logo } from "@/components/ui/logo";

interface RouteGuardProps {
  children: React.ReactNode;
  requireContract?: boolean;
  redirectTo?: string;
}

export function RouteGuard({
  children,
  requireContract = false,
  redirectTo = "/onboarding",
}: RouteGuardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkAccess = () => {
      try {
        const activeContract = ContractStorage.getActiveContract();

        if (requireContract) {
          // Route requires a contract
          if (!activeContract) {
            router.push(redirectTo);
            return;
          }
        } else {
          // Route doesn't require a contract (like onboarding)
          // Could add logic here if needed
        }

        setIsAuthorized(true);
      } catch (error) {
        console.error("Error checking route access:", error);
        showToast.error(
          "Access Error",
          "Unable to verify access permissions. Redirecting..."
        );
        if (requireContract) {
          router.push(redirectTo);
          return;
        }
        setIsAuthorized(true);
      } finally {
        setIsLoading(false);
      }
    };

    checkAccess();
  }, [requireContract, redirectTo, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted/20">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <Logo className="animate-pulse" width={48} height={48} />
          </div>
          <h1 className="text-2xl font-bold">PulseProof</h1>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Verifying access...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthorized) {
    return null; // Router will handle redirect
  }

  return <>{children}</>;
}
