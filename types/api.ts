// API Response types that match the backend response structure
export interface VulnerabilityApiResponse {
    blockTimestamp: string;
    id: string;
    pocHash: string;
    summary: string; // Backend returns 'summary', not 'pocSummary'
    pocType: string;
    target: string;
    metadataURI: string;
    severity: string;
}

// Extended vulnerability type that includes localStorage status
export interface VulnerabilityWithStatus extends Omit<VulnerabilityApiResponse, 'summary'> {
    status: 'new' | 'acknowledged' | 'resolved';
    serialNumber: number;
    // For UI compatibility, we'll add pocSummary as an alias to summary
    pocSummary: string;
    summary: string; // Keep original summary field
}

// Status storage for localStorage
export interface VulnerabilityStatus {
    [vulnerabilityId: string]: {
        status: 'new' | 'acknowledged' | 'resolved';
        updatedAt: Date;
    };
}

// API error response
export interface ApiError {
    error: string;
    message?: string;
    statusCode?: number;
}