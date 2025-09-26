// Analytics and user behavior tracking utilities

interface AnalyticsEvent {
    name: string;
    properties?: Record<string, unknown>;
    timestamp: Date;
}

class Analytics {
    private events: AnalyticsEvent[] = [];
    private isEnabled: boolean;

    constructor() {
        this.isEnabled = process.env.NODE_ENV === 'production';
    }

    // Track user events
    track(name: string, properties?: Record<string, unknown>) {
        if (!this.isEnabled) return;

        const event: AnalyticsEvent = {
            name,
            properties,
            timestamp: new Date(),
        };

        this.events.push(event);

        // In a real app, you'd send this to your analytics service
        console.log('Analytics Event:', event);
    }

    // Track page views
    trackPageView(page: string, properties?: Record<string, unknown>) {
        this.track('page_view', {
            page,
            ...properties,
        });
    }

    // Track user interactions
    trackInteraction(element: string, action: string, properties?: Record<string, unknown>) {
        this.track('user_interaction', {
            element,
            action,
            ...properties,
        });
    }

    // Track errors
    trackError(error: Error, context?: string) {
        this.track('error', {
            message: error.message,
            stack: error.stack,
            context,
        });
    }

    // Track performance metrics
    trackPerformance(metrics: {
        loadTime?: number;
        renderTime?: number;
        memoryUsage?: number;
    }) {
        this.track('performance', metrics);
    }

    // Get all events (for debugging)
    getEvents() {
        return this.events;
    }

    // Clear events
    clearEvents() {
        this.events = [];
    }
}

export const analytics = new Analytics();

// Specific tracking functions for common events
export const trackingEvents = {
    // Contract management
    contractAdded: (address: string, network: string) =>
        analytics.track('contract_added', { address, network }),

    contractSwitched: (address: string) =>
        analytics.track('contract_switched', { address }),

    contractRemoved: (address: string) =>
        analytics.track('contract_removed', { address }),

    // Vulnerability interactions
    vulnerabilityViewed: (vulnerabilityId: string, priority: number) =>
        analytics.track('vulnerability_viewed', { vulnerabilityId, priority }),

    vulnerabilityAcknowledged: (vulnerabilityId: string) =>
        analytics.track('vulnerability_acknowledged', { vulnerabilityId }),

    vulnerabilityDismissed: (vulnerabilityId: string) =>
        analytics.track('vulnerability_dismissed', { vulnerabilityId }),

    // Filter usage
    filtersApplied: (filters: Record<string, unknown>, resultCount: number) =>
        analytics.track('filters_applied', { filters, resultCount }),

    filtersCleared: () =>
        analytics.track('filters_cleared'),

    // Pagination
    pageChanged: (page: number, itemsPerPage: number) =>
        analytics.track('page_changed', { page, itemsPerPage }),

    // Search
    searchPerformed: (query: string, resultCount: number) =>
        analytics.track('search_performed', { query, resultCount }),

    // Navigation
    navigationUsed: (from: string, to: string) =>
        analytics.track('navigation_used', { from, to }),

    // Errors
    errorOccurred: (error: Error, context: string) =>
        analytics.trackError(error, context),
};