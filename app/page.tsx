"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ContractStorage } from "@/lib/contract-storage";
import { Loader2 } from "lucide-react";
import { Logo } from "@/components/ui/logo";

export default function Home() {
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user has an active contract
    const checkActiveContract = () => {
      try {
        const activeContract = ContractStorage.getActiveContract();

        if (activeContract) {
          // User has a contract, redirect to dashboard
          router.push("/dashboard");
        } else {
          // No contract found, redirect to onboarding
          router.push("/onboarding");
        }
      } catch (error) {
        console.error("Error checking active contract:", error);
        // On error, default to onboarding
        router.push("/onboarding");
      } finally {
        setIsLoading(false);
      }
    };

    // Small delay to prevent flash
    const timer = setTimeout(checkActiveContract, 100);
    return () => clearTimeout(timer);
  }, [router]);

  // Show loading state while determining route
  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center bg-gradient-to-br from-background to-muted/20">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <Logo className="animate-pulse" width={48} height={48} />
          </div>
          <h1 className="text-2xl font-bold">PulseProof</h1>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  // This should not be reached due to redirects, but provide fallback
  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center">
      <div className="text-center">
        <Logo className="mx-auto mb-4" width={48} height={48} />
        <h1 className="text-2xl font-bold mb-2">PulseProof</h1>
        <p className="text-muted-foreground">Redirecting...</p>
      </div>
    </div>
  );
}
