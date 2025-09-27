"use client";

import { useState, useEffect, useMemo } from "react";
import { VulnerabilityTable } from "@/components/dashboard/vulnerability-table";
import { VulnerabilityFilters } from "@/components/dashboard/vulnerability-filters";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { CriticalNotifications } from "@/components/dashboard/critical-notifications";
import { RouteGuard } from "@/components/auth/route-guard";
import { LoadingSkeleton } from "@/components/ui/loading-skeleton";
import { PerformanceMonitor } from "@/components/ui/performance-monitor";
import { FilterState, PaginationState, VulnerabilityAlert } from "@/types";
import { showToast, vulnerabilityToasts } from "@/lib/toast";
import { analytics, trackingEvents } from "@/lib/analytics";
import { VulnerabilityDataService } from "@/lib/vulnerability-data";
import { VulnerabilityApiService } from "@/lib/vulnerability-api";
import { ContractStorage } from "@/lib/contract-storage";

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
  const [vulnerabilityData, setVulnerabilityData] = useState<
    VulnerabilityAlert[]
  >([]);
  const [activeContractAddress, setActiveContractAddress] = useState<
    string | null
  >(null);

  // Function to refresh data
  const refreshData = async () => {
    if (!activeContractAddress) return;

    try {
      setIsLoading(true);
      const apiData = await VulnerabilityApiService.queryVulnerabilities(
        activeContractAddress
      );
      const transformedData =
        VulnerabilityApiService.transformToVulnerabilityAlert(apiData);
      setVulnerabilityData(transformedData);
      setIsLoading(false);
    } catch (error) {
      console.error("Error refreshing data:", error);
      setIsLoading(false);
    }
  };

  // Handle status changes from the vulnerability table
  const handleStatusChange = (
    vulnerabilityId: string,
    newStatus: "new" | "acknowledged" | "resolved"
  ) => {
    // Update the local state to reflect the change immediately
    setVulnerabilityData((prev) =>
      prev.map((vuln) =>
        vuln.id === vulnerabilityId ? { ...vuln, status: newStatus } : vuln
      )
    );
  };

  // Load vulnerability data from API
  useEffect(() => {
    const loadData = async () => {
      const startTime = performance.now();

      try {
        setIsLoading(true);
        setError(null);

        // Track page view
        analytics.trackPageView("/dashboard");

        // Get active contract from storage
        const activeContract = ContractStorage.getActiveContract();
        if (!activeContract) {
          throw new Error(
            "No active contract found. Please add a contract to monitor."
          );
        }

        setActiveContractAddress(activeContract.address);

        // Fetch vulnerability data from API
        const apiData = await VulnerabilityApiService.queryVulnerabilities(
          activeContract.address
        );
        const transformedData =
          VulnerabilityApiService.transformToVulnerabilityAlert(apiData);

        setVulnerabilityData(transformedData);

        const loadTime = performance.now() - startTime;
        analytics.trackPerformance({ loadTime });

        setIsLoading(false);

        // Show success toast if vulnerabilities found
        if (transformedData.length > 0) {
          showToast.success(
            "Data Loaded",
            `Found ${transformedData.length} vulnerability alert${transformedData.length === 1 ? "" : "s"}`
          );
        }
      } catch (err) {
        console.error("Error loading dashboard data:", err);
        const error = err instanceof Error ? err : new Error("Unknown error");
        trackingEvents.errorOccurred(error, "dashboard_load");

        let errorMessage =
          "Failed to load vulnerability data. Please try again.";
        if (error.message.includes("No active contract")) {
          errorMessage =
            "No active contract found. Please add a contract to monitor.";
        } else if (
          error.message.includes("fetch") ||
          error.message.includes("API Error")
        ) {
          errorMessage =
            "Unable to connect to the vulnerability scanning service. Please check if the service is running.";
        }

        setError(errorMessage);
        setIsLoading(false);
        showToast.error("Loading Error", errorMessage);
      }
    };

    loadData();
  }, []);

  // Apply filters and get filtered data
  const filteredData = useMemo(() => {
    return VulnerabilityDataService.filterData(vulnerabilityData, filters);
  }, [vulnerabilityData, filters]);

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
          vulnerabilityData,
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
              onStatusChange={handleStatusChange}
              isLoading={false}
            />
          </div>
        </div>
        <PerformanceMonitor />
      </div>
    </RouteGuard>
  );
}
