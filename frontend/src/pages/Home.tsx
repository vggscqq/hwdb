import {
    ActionIcon,
    AppShell,
    GridColProps,
    GridProps,
    Group,
    Title,
    useMantineTheme,
} from "@mantine/core"
import { useToggle } from "@mantine/hooks"
import { IconLayoutGrid, IconLayoutList } from "@tabler/icons-react"
import React from "react"

import { Main } from "../components/Main"
import { FilterSortControls } from "../components/FilterSortControls"
import { TagManager } from "../components/TagManager"
import { useFetchAllTags, useCreateTag, useDeleteTag } from "../hooks/useService"

type ViewType = "grid" | "list"

type View = {
    [key in ViewType]: {
        gutter: GridProps["gutter"]
        icon: React.ReactNode
        span: GridColProps["span"]
    }
}

const view: View = {
    grid: {
        gutter: { base: "xs", md: "sm" },
        icon: <IconLayoutList size={24} />,
        span: { base: 12, sm: 6, lg: 4, xl: 3 },
    },
    list: {
        gutter: { base: "xs", md: "sm" },
        icon: <IconLayoutGrid size={24} />,
        span: { base: 12 },
    },
}

export const Home: React.FC = () => {
    const theme = useMantineTheme()
    const [viewType, toggleView] = useToggle<ViewType>(["grid", "list"])
    const [sortBy, setSortBy] = React.useState<string>('submitted_at')
    const [sortOrder, setSortOrder] = React.useState<'asc' | 'desc'>('desc')
    const [selectedTag, setSelectedTag] = React.useState<string | null>(null)

    // Fetch tags from API
    const tagsQuery = useFetchAllTags()
    const createTagMutation = useCreateTag({
        onSuccess: () => {
            // Tags will be refetched automatically due to query invalidation
        }
    })
    const deleteTagMutation = useDeleteTag({
        onSuccess: () => {
            // Tags will be refetched automatically due to query invalidation
        }
    })

    const handleSortChange = (newSortBy: string, newSortOrder: 'asc' | 'desc') => {
        setSortBy(newSortBy)
        setSortOrder(newSortOrder)
    }

    const handleTagFilter = (tagName: string | null) => {
        setSelectedTag(tagName)
    }

    const handleTagCreate = async (name: string, color: string) => {
        await createTagMutation.mutateAsync({ name, color })
    }

    const handleTagDelete = async (tagId: number) => {
        await deleteTagMutation.mutateAsync({ tagId })
    }

    return (
        <AppShell header={{ height: { base: 60, md: 70 } }} padding="md">
            <AppShell.Header>
                <Group h="100%" px="lg">
                    <Title c={theme.primaryColor} order={2}>
                        PCDB
                    </Title>
                    <div style={{ flex: 1 }} />
                    {tagsQuery.data && (
                        <TagManager 
                            onCreateTag={handleTagCreate} 
                            onDeleteTag={handleTagDelete} 
                            tags={tagsQuery.data} 
                        />
                    )}
                    <ActionIcon visibleFrom="sm" size="xl" variant="subtle" onClick={() => toggleView()}>
                        {view[viewType].icon}
                    </ActionIcon>
                </Group>
            </AppShell.Header>
            <AppShell.Main>
                <FilterSortControls
                    availableTags={tagsQuery.data || []}
                    onSortChange={handleSortChange}
                    onTagFilter={handleTagFilter}
                    selectedTag={selectedTag}
                    sortBy={sortBy}
                    sortOrder={sortOrder}
                />
                <Main 
                    colSpan={view[viewType].span} 
                    gutter={view[viewType].gutter}
                    sortBy={sortBy}
                    sortOrder={sortOrder}
                    selectedTag={selectedTag}
                />
            </AppShell.Main>
        </AppShell>
    )
}
