"use client";

import { useRouter, usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ContractStorage } from "@/lib/contract-storage";
import { Home, Plus } from "lucide-react";
import { Logo } from "@/components/ui/logo";

export function NavigationBar() {
  const router = useRouter();
  const pathname = usePathname();

  const handleNavigation = (path: string) => {
    router.push(path);
  };

  const handleAddContract = () => {
    router.push("/onboarding");
  };

  const hasActiveContract = () => {
    try {
      return !!ContractStorage.getActiveContract();
    } catch {
      return false;
    }
  };

  const isActive = (path: string) => {
    return pathname === path;
  };

  return (
    <nav
      className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Logo width={24} height={24} />
            <span className="text-xl font-bold">PulseProof</span>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-2 sm:gap-4">
            {hasActiveContract() && (
              <>
                <Button
                  variant={isActive("/dashboard") ? "default" : "ghost"}
                  size="sm"
                  onClick={() => handleNavigation("/dashboard")}
                  className="flex items-center gap-2"
                  aria-current={isActive("/dashboard") ? "page" : undefined}
                >
                  <Home className="h-4 w-4" aria-hidden="true" />
                  <span className="hidden sm:inline">Dashboard</span>
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAddContract}
                  className="flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" aria-hidden="true" />
                  <span className="hidden sm:inline">Add Contract</span>
                  <span className="sm:hidden">Add</span>
                </Button>
              </>
            )}

            {!hasActiveContract() && pathname !== "/onboarding" && (
              <Button
                variant="default"
                size="sm"
                onClick={() => handleNavigation("/onboarding")}
                className="flex items-center gap-2"
              >
                <Plus className="h-4 w-4" aria-hidden="true" />
                <span className="hidden sm:inline">Get Started</span>
                <span className="sm:hidden">Start</span>
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
