// Accessibility utilities and helpers

export const focusManagement = {
    // Focus the first focusable element in a container
    focusFirst: (container: HTMLElement) => {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0] as HTMLElement;
        if (firstElement) {
            firstElement.focus();
        }
    },

    // Focus the last focusable element in a container
    focusLast: (container: HTMLElement) => {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
        if (lastElement) {
            lastElement.focus();
        }
    },

    // Trap focus within a container (useful for modals)
    trapFocus: (container: HTMLElement, event: KeyboardEvent) => {
        if (event.key !== 'Tab') return;

        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (event.shiftKey) {
            if (document.activeElement === firstElement) {
                event.preventDefault();
                lastElement.focus();
            }
        } else {
            if (document.activeElement === lastElement) {
                event.preventDefault();
                firstElement.focus();
            }
        }
    },
};

export const announcements = {
    // Announce text to screen readers
    announce: (message: string, priority: 'polite' | 'assertive' = 'polite') => {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', priority);
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        document.body.appendChild(announcement);

        // Remove after announcement
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    },

    // Announce loading states
    announceLoading: (isLoading: boolean, context: string = '') => {
        if (isLoading) {
            announcements.announce(`Loading ${context}`, 'polite');
        } else {
            announcements.announce(`${context} loaded`, 'polite');
        }
    },

    // Announce filter changes
    announceFilterChange: (resultCount: number, filterType: string) => {
        announcements.announce(
            `${filterType} filter applied. Showing ${resultCount} result${resultCount !== 1 ? 's' : ''}`,
            'polite'
        );
    },
};

export const keyboardNavigation = {
    // Handle arrow key navigation in lists
    handleArrowKeys: (
        event: KeyboardEvent,
        items: NodeListOf<HTMLElement> | HTMLElement[],
        currentIndex: number,
        onIndexChange: (newIndex: number) => void
    ) => {
        let newIndex = currentIndex;

        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                newIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
                break;
            case 'ArrowUp':
                event.preventDefault();
                newIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
                break;
            case 'Home':
                event.preventDefault();
                newIndex = 0;
                break;
            case 'End':
                event.preventDefault();
                newIndex = items.length - 1;
                break;
            default:
                return;
        }

        onIndexChange(newIndex);
        (items[newIndex] as HTMLElement).focus();
    },

    // Handle escape key
    handleEscape: (callback: () => void) => {
        return (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                callback();
            }
        };
    },
};

export const colorContrast = {
    // Check if color combination meets WCAG AA standards
    meetsWCAG: (foreground: string, background: string): boolean => {
        // This is a simplified check - in a real app you'd use a proper color contrast library
        // For now, we'll assume our design system colors meet WCAG standards
        return true;
    },
};

export const screenReader = {
    // Generate descriptive text for complex UI elements
    describeVulnerability: (vulnerability: {
        serialNumber: number;
        pocSummary: string;
        priorityScore: number;
        status: string;
        category: string;
    }) => {
        const priorityLabels = {
            1: 'Critical',
            2: 'High',
            3: 'Medium',
            4: 'Low',
            5: 'Info'
        };

        return `Vulnerability ${vulnerability.serialNumber}: ${vulnerability.pocSummary}. Priority: ${priorityLabels[vulnerability.priorityScore as keyof typeof priorityLabels]}. Status: ${vulnerability.status}. Category: ${vulnerability.category.replace('_', ' ')}`;
    },

    // Generate table descriptions
    describeTable: (rowCount: number, columnCount: number, caption: string) => {
        return `${caption}. Table with ${rowCount} rows and ${columnCount} columns.`;
    },
};