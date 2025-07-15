import { Button, Group, Select } from "@mantine/core"
import { IconSearch, IconSortAscending, IconSortDescending, IconX } from "@tabler/icons-react"
import React from "react"

import { Tag } from "../types"

type Props = {
    availableTags: Tag[]
    onSortChange: (sortBy: string, sortOrder: 'asc' | 'desc') => void
    onTagFilter: (tagName: string | null) => void
    selectedTag: string | null
    sortBy: string
    sortOrder: 'asc' | 'desc'
}

export const FilterSortControls: React.FC<Props> = ({
    availableTags,
    onSortChange,
    onTagFilter,
    selectedTag,
    sortBy,
    sortOrder,
}) => {
    const sortOptions = [
        { value: 'submitted_at', label: 'Date Added' },
        { value: 'host', label: 'Hostname' },
        { value: 'cpu', label: 'CPU' },
    ]

    const tagOptions = availableTags.map(tag => ({
        value: tag.name,
        label: tag.name,
    }))

    const handleSortByChange = (value: string | null) => {
        if (value) {
            onSortChange(value, sortOrder)
        }
    }

    const handleSortOrderToggle = () => {
        const newOrder = sortOrder === 'asc' ? 'desc' : 'asc'
        onSortChange(sortBy, newOrder)
    }

    const handleTagFilter = (value: string | null) => {
        onTagFilter(value)
    }

    const clearTagFilter = () => {
        onTagFilter(null)
    }

    return (
        <Group mb="md" gap="sm">
            <Select
                label="Sort by"
                data={sortOptions}
                value={sortBy}
                onChange={handleSortByChange}
                w={150}
                clearable={false}
            />
            <Button
                variant="light"
                onClick={handleSortOrderToggle}
                leftSection={sortOrder === 'asc' ? <IconSortAscending size={16} /> : <IconSortDescending size={16} />}
            >
                {sortOrder === 'asc' ? 'Ascending' : 'Descending'}
            </Button>
            <Select
                label="Filter by tag"
                placeholder="Select tag..."
                data={tagOptions}
                value={selectedTag}
                onChange={handleTagFilter}
                w={200}
                clearable
                leftSection={<IconSearch size={16} />}
            />
            {selectedTag && (
                <Button
                    variant="light"
                    color="red"
                    onClick={clearTagFilter}
                    leftSection={<IconX size={16} />}
                >
                    Clear Filter
                </Button>
            )}
        </Group>
    )
}
