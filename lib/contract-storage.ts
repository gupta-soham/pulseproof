import { ContractAddress, StoredData } from '@/types';

const STORAGE_KEY = 'pulseproof_data';

const DEFAULT_DATA: StoredData = {
    contracts: [],
    activeContract: null,
    userPreferences: {
        theme: 'light',
        notificationsEnabled: true,
        autoRefresh: true,
    },
    lastUpdated: new Date(),
};

export class ContractStorage {
    private static isClient(): boolean {
        return typeof window !== 'undefined';
    }

    private static isStorageAvailable(): boolean {
        if (!this.isClient()) return false;

        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch {
            return false;
        }
    }

    static getData(): StoredData {
        if (!this.isStorageAvailable()) {
            return DEFAULT_DATA;
        }

        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (!stored) return DEFAULT_DATA;

            const parsed = JSON.parse(stored);

            // Convert date strings back to Date objects
            return {
                ...parsed,
                contracts: parsed.contracts?.map((contract: ContractAddress) => ({
                    ...contract,
                    addedAt: new Date(contract.addedAt),
                })) || [],
                lastUpdated: new Date(parsed.lastUpdated),
            };
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            // Clear corrupted data
            if (typeof window !== 'undefined') {
                localStorage.removeItem(STORAGE_KEY);
            }
            return DEFAULT_DATA;
        }
    }

    static setData(data: StoredData): boolean {
        if (!this.isStorageAvailable()) {
            console.warn('localStorage not available');
            return false;
        }

        try {
            const dataToStore = {
                ...data,
                lastUpdated: new Date(),
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToStore));
            return true;
        } catch (error) {
            console.error('Error writing to localStorage:', error);
            return false;
        }
    }

    static addContract(contract: Omit<ContractAddress, 'addedAt' | 'isActive'>): boolean {
        const data = this.getData();

        // Check if contract already exists
        const exists = data.contracts.some(c => c.address.toLowerCase() === contract.address.toLowerCase());
        if (exists) {
            throw new Error('Contract already exists');
        }

        const newContract: ContractAddress = {
            ...contract,
            addedAt: new Date(),
            isActive: data.contracts.length === 0, // First contract is active by default
        };

        // If this is the first contract, make it active
        if (data.contracts.length === 0) {
            data.activeContract = newContract.address;
        }

        data.contracts.push(newContract);
        return this.setData(data);
    }

    static removeContract(address: string): boolean {
        const data = this.getData();
        const initialLength = data.contracts.length;

        data.contracts = data.contracts.filter(c => c.address !== address);

        // If we removed the active contract, set a new one or null
        if (data.activeContract === address) {
            data.activeContract = data.contracts.length > 0 ? data.contracts[0].address : null;

            // Update isActive flags
            data.contracts.forEach(contract => {
                contract.isActive = contract.address === data.activeContract;
            });
        }

        if (data.contracts.length !== initialLength) {
            return this.setData(data);
        }

        return false;
    }

    static setActiveContract(address: string): boolean {
        const data = this.getData();
        const contract = data.contracts.find(c => c.address === address);

        if (!contract) {
            throw new Error('Contract not found');
        }

        // Update active contract
        data.activeContract = address;

        // Update isActive flags
        data.contracts.forEach(contract => {
            contract.isActive = contract.address === address;
        });

        return this.setData(data);
    }

    static getActiveContract(): ContractAddress | null {
        const data = this.getData();
        if (!data.activeContract) return null;

        return data.contracts.find(c => c.address === data.activeContract) || null;
    }

    static getAllContracts(): ContractAddress[] {
        return this.getData().contracts;
    }

    static updateUserPreferences(preferences: Partial<StoredData['userPreferences']>): boolean {
        const data = this.getData();
        data.userPreferences = { ...data.userPreferences, ...preferences };
        return this.setData(data);
    }

    static clearAllData(): boolean {
        if (!this.isStorageAvailable()) return false;

        try {
            localStorage.removeItem(STORAGE_KEY);
            return true;
        } catch (error) {
            console.error('Error clearing localStorage:', error);
            return false;
        }
    }

    static validateContractAddress(address: string): boolean {
        // Basic Ethereum address validation
        const ethAddressRegex = /^0x[a-fA-F0-9]{40}$/;
        return ethAddressRegex.test(address);
    }
}