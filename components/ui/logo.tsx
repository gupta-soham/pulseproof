import Image from "next/image";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  width?: number;
  height?: number;
}

export function Logo({ className, width = 24, height = 24 }: LogoProps) {
  return (
    <Image
      src="/logo.svg"
      alt="PulseProof Logo"
      width={width}
      height={height}
      className={cn("", className)}
      priority
    />
  );
}
