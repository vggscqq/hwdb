import { Group, Text, Title, Stack } from "@mantine/core"
import React from "react"

type Props = {
    title: string
    value: React.ReactNode
}

export const PreviewField: React.FC<Props> = ({ title, value }) => {
    return (
        <Group gap={5} wrap="nowrap">
            <Title order={6}>{`${title}:`}</Title>
            <Text size="sm" c="dimmed" lineClamp={1}>
                {value}
            </Text>
        </Group>
    )
}

export const Field: React.FC<Props> = ({ title, value }) => {
    return (
        <Stack gap={0}>
            <Title order={5}>{title}:</Title>
            {React.isValidElement(value) ? value : (
                <Text size="md" lineClamp={20}>
                    {value}
                </Text>
            )}
        </Stack>
    )
}

export const SubField: React.FC<Props> = ({ title, value }) => {
    return (
        <Group gap={5}>
            <Title order={6}>{title}:</Title>
            <Text size="sm" lineClamp={1}>
                {value}
            </Text>
        </Group>
    )
}