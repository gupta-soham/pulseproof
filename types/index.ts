export interface ContractAddress {
    address: string;
    network: string;
    addedAt: Date;
    isActive: boolean;
}

export interface VulnerabilityAlert {
    id: string;
    serialNumber: number;
    pocSummary: string;
    pocCodeLink: string;
    priorityScore: 1 | 2 | 3 | 4 | 5; // 1 = Critical, 5 = Low
    contractHash: string;
    detectedAt: Date;
    status: 'new' | 'acknowledged' | 'resolved';
    category: 'suspicious_transaction' | 'high_gas' | 'liquidity_exceeded' | 'pattern_match';
}

export interface MonitoringConfig {
    contractAddress: string;
    monitoringEvents: string[];
    thresholds: {
        gasLimit: number;
        transactionAmount: number;
        liquidityRatio: number;
    };
}

export interface StoredData {
    contracts: ContractAddress[];
    activeContract: string | null;
    userPreferences: {
        theme: 'light' | 'dark';
        notificationsEnabled: boolean;
        autoRefresh: boolean;
    };
    lastUpdated: Date;
}

// Export API types for use in components
export type { VulnerabilityApiResponse, VulnerabilityWithStatus, VulnerabilityStatus, ApiError } from './api';

export interface FilterState {
    priorityScore?: number[];
    category?: string[];
    hashSearch?: string;
    dateRange?: {
        from?: Date;
        to?: Date;
    };
}

export interface PaginationState {
    currentPage: number;
    itemsPerPage: number;
    totalItems: number;
    totalPages: number;
}