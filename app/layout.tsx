import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { NavigationBar } from "@/components/navigation/navigation-bar";
import { ErrorBoundary } from "@/components/error/error-boundary";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "PulseProof - Smart Contract Security Monitoring",
  description:
    "Advanced Web3 security monitoring for smart contracts. Detect vulnerabilities, suspicious activities, and malicious attacks in real-time.",
  keywords: [
    "Web3",
    "Smart Contract",
    "Security",
    "Monitoring",
    "Blockchain",
    "Ethereum",
    "DeFi",
  ],
  authors: [{ name: "PulseProof Team" }],
  creator: "PulseProof",
  publisher: "PulseProof",
  robots: "index, follow",
  viewport: "width=device-width, initial-scale=1",
  themeColor: "#0f172a",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://pulseproof.com",
    title: "PulseProof - Smart Contract Security Monitoring",
    description:
      "Advanced Web3 security monitoring for smart contracts. Detect vulnerabilities, suspicious activities, and malicious attacks in real-time.",
    siteName: "PulseProof",
  },
  twitter: {
    card: "summary_large_image",
    title: "PulseProof - Smart Contract Security Monitoring",
    description:
      "Advanced Web3 security monitoring for smart contracts. Detect vulnerabilities, suspicious activities, and malicious attacks in real-time.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="theme-color" content="#0f172a" />
      </head>
      <body
        className={`${inter.variable} font-sans antialiased min-h-screen bg-background`}
      >
        <div className="relative flex min-h-screen flex-col">
          <NavigationBar />
          <main className="flex-1">
            <ErrorBoundary>{children}</ErrorBoundary>
          </main>
          <footer className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container mx-auto px-4 py-6">
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span>© 2025 PulseProof. All rights reserved.</span>
                </div>
                <div className="flex items-center gap-6 text-sm text-muted-foreground">
                  <a
                    href="#"
                    className="hover:text-foreground transition-colors"
                  >
                    Privacy Policy
                  </a>
                  <a
                    href="#"
                    className="hover:text-foreground transition-colors"
                  >
                    Terms of Service
                  </a>
                  <a
                    href="#"
                    className="hover:text-foreground transition-colors"
                  >
                    Documentation
                  </a>
                  <a
                    href="#"
                    className="hover:text-foreground transition-colors"
                  >
                    Support
                  </a>
                </div>
              </div>
            </div>
          </footer>
        </div>
        <Toaster />
      </body>
    </html>
  );
}
