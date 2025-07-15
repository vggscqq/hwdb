/**
 * Format a date string to local timezone with a consistent format
 * @param dateStr ISO date string
 * @returns Formatted date string with timezone based on user's browser locale
 */
export const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleString(undefined, {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZoneName: 'short'
    });
};
