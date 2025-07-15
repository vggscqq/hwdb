import { Grid, GridColProps, GridProps } from "@mantine/core"
import React from "react"

import { useFetchAllPcs } from "../hooks/useService"
import { Card } from "./Card"

type Props = React.PropsWithChildren<{
    colSpan: GridColProps["span"]
    gutter: GridProps["gutter"]
    selectedTag?: string | null
    sortBy?: string
    sortOrder?: 'asc' | 'desc'
}>

export const Main: React.FC<Props> = ({ 
    colSpan, 
    gutter, 
    selectedTag = null, 
    sortBy = 'submitted_at', 
    sortOrder = 'desc' 
}) => {
    const { data, isLoading, error } = useFetchAllPcs(sortBy, sortOrder, selectedTag || undefined)

    if (isLoading) {
        return <div>Loading...</div>
    }

    if (error) {
        return <div>Error: {error.message}</div>
    }

    // Backend handles sorting and filtering, so use data as-is
    const pcs = data || []

    return (
        <Grid gutter={gutter} justify="center">
            {pcs.map(({ id }) => (
                <Grid.Col span={colSpan} key={id}>
                    <Card pcId={id} />
                </Grid.Col>
            ))}
        </Grid>
    )
}
