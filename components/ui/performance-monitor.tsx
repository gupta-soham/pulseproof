"use client";

import { useEffect, useState } from "react";

interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage?: number;
}

export function usePerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);

  useEffect(() => {
    // Measure page load time
    const loadTime = performance.now();

    // Measure render time
    const renderStart = performance.now();

    // Use requestAnimationFrame to measure after render
    requestAnimationFrame(() => {
      const renderEnd = performance.now();
      const renderTime = renderEnd - renderStart;

      // Get memory usage if available
      const memoryUsage = (
        performance as unknown as { memory?: { usedJSHeapSize: number } }
      ).memory?.usedJSHeapSize;

      setMetrics({
        loadTime,
        renderTime,
        memoryUsage,
      });

      // Log performance metrics in development
      if (process.env.NODE_ENV === "development") {
        console.log("Performance Metrics:", {
          loadTime: `${loadTime.toFixed(2)}ms`,
          renderTime: `${renderTime.toFixed(2)}ms`,
          memoryUsage: memoryUsage
            ? `${(memoryUsage / 1024 / 1024).toFixed(2)}MB`
            : "N/A",
        });
      }
    });
  }, []);

  return metrics;
}

// Component to display performance metrics in development
export function PerformanceMonitor() {
  const metrics = usePerformanceMonitor();

  if (process.env.NODE_ENV !== "development" || !metrics) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 bg-background border rounded-lg p-3 text-xs font-mono shadow-lg z-50">
      <div className="text-muted-foreground mb-1">Performance</div>
      <div>Load: {metrics.loadTime.toFixed(2)}ms</div>
      <div>Render: {metrics.renderTime.toFixed(2)}ms</div>
      {metrics.memoryUsage && (
        <div>Memory: {(metrics.memoryUsage / 1024 / 1024).toFixed(2)}MB</div>
      )}
    </div>
  );
}
