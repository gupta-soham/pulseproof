import { toast } from "sonner";

export const showToast = {
    success: (message: string, description?: string) => {
        toast.success(message, {
            description,
            duration: 4000,
        });
    },

    error: (message: string, description?: string) => {
        toast.error(message, {
            description,
            duration: 6000,
        });
    },

    warning: (message: string, description?: string) => {
        toast.warning(message, {
            description,
            duration: 5000,
        });
    },

    info: (message: string, description?: string) => {
        toast.info(message, {
            description,
            duration: 4000,
        });
    },

    loading: (message: string) => {
        return toast.loading(message);
    },

    dismiss: (toastId?: string | number) => {
        toast.dismiss(toastId);
    },

    promise: <T>(
        promise: Promise<T>,
        {
            loading,
            success,
            error,
        }: {
            loading: string;
            success: string | ((data: T) => string);
            error: string | ((error: Error) => string);
        }
    ) => {
        return toast.promise(promise, {
            loading,
            success,
            error,
        });
    },
};

// Specific toast messages for common scenarios
export const contractToasts = {
    added: (address: string) =>
        showToast.success(
            "Contract Added Successfully",
            `Now monitoring ${address.slice(0, 6)}...${address.slice(-4)}`
        ),

    addError: (error: string) =>
        showToast.error(
            "Failed to Add Contract",
            error || "Please check the address and try again"
        ),

    switched: (address: string) =>
        showToast.info(
            "Contract Switched",
            `Now viewing ${address.slice(0, 6)}...${address.slice(-4)}`
        ),

    removed: (address: string) =>
        showToast.success(
            "Contract Removed",
            `Stopped monitoring ${address.slice(0, 6)}...${address.slice(-4)}`
        ),

    validationError: (field: string) =>
        showToast.error("Validation Error", `Please check the ${field} field`),

    networkError: () =>
        showToast.error(
            "Network Error",
            "Please check your connection and try again"
        ),

    storageError: () =>
        showToast.error(
            "Storage Error",
            "Unable to save data. Please try again"
        ),
};

export const vulnerabilityToasts = {
    acknowledged: (id: string) =>
        showToast.success("Alert Acknowledged", `Vulnerability ${id} marked as acknowledged`),

    dismissed: (count: number) =>
        showToast.info(
            "Alerts Dismissed",
            `${count} alert${count > 1 ? "s" : ""} dismissed`
        ),

    filterApplied: (count: number) =>
        showToast.info(
            "Filters Applied",
            `Showing ${count} result${count !== 1 ? "s" : ""}`
        ),

    exportSuccess: () =>
        showToast.success("Export Complete", "Vulnerability data exported successfully"),

    exportError: () =>
        showToast.error("Export Failed", "Unable to export data. Please try again"),
};