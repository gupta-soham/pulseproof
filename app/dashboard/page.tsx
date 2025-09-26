"use client";

import { useState, useEffect, useMemo } from "react";
import { VulnerabilityTable } from "@/components/dashboard/vulnerability-table";
import { VulnerabilityFilters } from "@/components/dashboard/vulnerability-filters";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { CriticalNotifications } from "@/components/dashboard/critical-notifications";
import { RouteGuard } from "@/components/auth/route-guard";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PerformanceMonitor } from "@/components/ui/performance-monitor";
import { FilterState, PaginationState } from "@/types";
import { showToast, vulnerabilityToasts } from "@/lib/toast";
import { analytics, trackingEvents } from "@/lib/analytics";
import {
  DUMMY_VULNERABILITIES,
  VulnerabilityDataService,
} from "@/lib/vulnerability-data";

export default function DashboardPage() {
  const [filters, setFilters] = useState<FilterState>({});
  const [pagination, setPagination] = useState<PaginationState>({
    currentPage: 1,
    itemsPerPage: 10,
    totalItems: 0,
    totalPages: 0,
  });
  const [isFiltersCollapsed, setIsFiltersCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Simulate loading state with error handling
  useEffect(() => {
    const loadData = async () => {
      const startTime = performance.now();

      try {
        setIsLoading(true);
        setError(null);

        // Track page view
        analytics.trackPageView("/dashboard");

        // Simulate API call delay
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // In a real app, you'd fetch data here
        // const data = await fetchVulnerabilityData();

        const loadTime = performance.now() - startTime;
        analytics.trackPerformance({ loadTime });

        setIsLoading(false);
      } catch (err) {
        console.error("Error loading dashboard data:", err);
        const error = err instanceof Error ? err : new Error("Unknown error");
        trackingEvents.errorOccurred(error, "dashboard_load");
        setError("Failed to load vulnerability data. Please try again.");
        setIsLoading(false);
        showToast.error(
          "Loading Error",
          "Unable to load vulnerability data. Please refresh the page."
        );
      }
    };

    loadData();
  }, []);

  // Apply filters and get filtered data
  const filteredData = useMemo(() => {
    return VulnerabilityDataService.filterData(DUMMY_VULNERABILITIES, filters);
  }, [filters]);

  // Get paginated data
  const paginatedResult = useMemo(() => {
    return VulnerabilityDataService.paginateData(filteredData, pagination);
  }, [filteredData, pagination]);

  // Get critical alerts for notifications
  const criticalAlerts = useMemo(() => {
    return VulnerabilityDataService.getCriticalAlerts(filteredData);
  }, [filteredData]);

  // Update pagination when filters change
  useEffect(() => {
    setPagination((prev) => ({
      ...prev,
      currentPage: 1,
      totalItems: filteredData.length,
      totalPages: Math.ceil(filteredData.length / prev.itemsPerPage),
    }));
  }, [filteredData]);

  const handleFiltersChange = (newFilters: FilterState) => {
    try {
      setFilters(newFilters);

      // Show toast for filter changes
      const hasFilters = Object.values(newFilters).some((value) =>
        Array.isArray(value) ? value.length > 0 : !!value
      );

      if (hasFilters) {
        const filteredCount = VulnerabilityDataService.filterData(
          DUMMY_VULNERABILITIES,
          newFilters
        ).length;
        vulnerabilityToasts.filterApplied(filteredCount);
      }
    } catch (error) {
      console.error("Error applying filters:", error);
      showToast.error(
        "Filter Error",
        "Unable to apply filters. Please try again."
      );
    }
  };

  const handlePageChange = (page: number) => {
    setPagination((prev) => ({
      ...prev,
      currentPage: page,
    }));
  };

  const handleItemsPerPageChange = (itemsPerPage: number) => {
    setPagination((prev) => ({
      ...prev,
      itemsPerPage,
      currentPage: 1,
      totalPages: Math.ceil(filteredData.length / itemsPerPage),
    }));
  };

  const toggleFiltersCollapse = () => {
    setIsFiltersCollapsed(!isFiltersCollapsed);
  };

  if (isLoading) {
    return (
      <RouteGuard requireContract={true} redirectTo="/onboarding">
        <div className="container mx-auto p-6">
          <LoadingSkeleton variant="dashboard" />
        </div>
      </RouteGuard>
    );
  }

  if (error) {
    return (
      <RouteGuard requireContract={true} redirectTo="/onboarding">
        <div className="container mx-auto p-6 space-y-6 min-h-[calc(100vh-8rem)]">
          <DashboardHeader />
          <div className="text-center py-12">
            <div className="text-destructive mb-2">Error Loading Dashboard</div>
            <div className="text-sm text-muted-foreground mb-4">{error}</div>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </div>
      </RouteGuard>
    );
  }

  return (
    <RouteGuard requireContract={true} redirectTo="/onboarding">
      <div className="container mx-auto p-6 space-y-6 min-h-[calc(100vh-8rem)]">
        {/* Dashboard Header */}
        <DashboardHeader />

        {/* Critical Notifications */}
        {criticalAlerts.length > 0 && (
          <CriticalNotifications alerts={criticalAlerts} />
        )}

        {/* Main Content Grid */}
        <div className="flex flex-col lg:grid lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div
            className={`${
              isFiltersCollapsed
                ? "lg:col-span-4"
                : "lg:col-span-1 order-2 lg:order-1"
            }`}
          >
            <VulnerabilityFilters
              filters={filters}
              onFiltersChange={handleFiltersChange}
              totalResults={filteredData.length}
              isCollapsed={isFiltersCollapsed}
              onToggleCollapse={toggleFiltersCollapse}
            />
          </div>

          {/* Vulnerability Table */}
          <div
            className={`${
              isFiltersCollapsed
                ? "lg:col-span-4"
                : "lg:col-span-3 order-1 lg:order-2"
            }`}
          >
            <VulnerabilityTable
              data={paginatedResult.items}
              pagination={paginatedResult.pagination}
              onPageChange={handlePageChange}
              onItemsPerPageChange={handleItemsPerPageChange}
              isLoading={false}
            />
          </div>
        </div>
        <PerformanceMonitor />
      </div>
    </RouteGuard>
  );
}
