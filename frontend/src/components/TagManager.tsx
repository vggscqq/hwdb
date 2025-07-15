import { ActionIcon, Badge, Button, ColorInput, Group, Modal, Stack, TextInput } from "@mantine/core"
import { useForm } from "@mantine/form"
import { useDisclosure } from "@mantine/hooks"
import { notifications } from "@mantine/notifications"
import { IconPlus, IconTrash } from "@tabler/icons-react"
import React from "react"

import { Tag } from "../types"

type Props = {
    onCreateTag: (name: string, color: string) => Promise<void>
    onDeleteTag: (tagId: number) => Promise<void>
    tags: Tag[]
}

export const TagManager: React.FC<Props> = ({ onCreateTag, onDeleteTag, tags }) => {
    const [opened, { open, close }] = useDisclosure(false)
    const [isCreating, setIsCreating] = React.useState(false)

    const form = useForm({
        initialValues: {
            name: '',
            color: '#228BE6',
        },
        validate: {
            name: (value) => (value.trim().length < 1 ? 'Tag name is required' : null),
        },
    })

    const handleSubmit = async (values: typeof form.values) => {
        setIsCreating(true)
        try {
            await onCreateTag(values.name.trim(), values.color)
            form.reset()
            close()
            notifications.show({
                title: 'Success',
                message: 'Tag created successfully',
                color: 'green',
            })
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to create tag',
                color: 'red',
            })
        } finally {
            setIsCreating(false)
        }
    }

    const handleDeleteTag = async (tagId: number, tagName: string) => {
        if (!window.confirm(`Are you sure you want to delete the tag "${tagName}"?`)) {
            return
        }

        try {
            await onDeleteTag(tagId)
            notifications.show({
                title: 'Success',
                message: 'Tag deleted successfully',
                color: 'green',
            })
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to delete tag',
                color: 'red',
            })
        }
    }

    return (
        <>
            <Button
                variant="light"
                leftSection={<IconPlus size={16} />}
                onClick={open}
            >
                Manage Tags
            </Button>

            <Modal opened={opened} onClose={close} title="Tag Management" size="md">
                <Stack>
                    <form onSubmit={form.onSubmit(handleSubmit)}>
                        <Stack gap="sm">
                            <TextInput
                                label="Tag name"
                                placeholder="Enter tag name"
                                {...form.getInputProps('name')}
                            />
                            <ColorInput
                                label="Tag color"
                                {...form.getInputProps('color')}
                            />
                            <Button type="submit" loading={isCreating}>
                                Create Tag
                            </Button>
                        </Stack>
                    </form>

                    {tags.length > 0 && (
                        <Stack gap="xs">
                            <h4>Existing Tags:</h4>
                            {tags.map((tag) => (
                                <Group key={tag.id} justify="space-between">
                                    <Badge color={tag.color} variant="filled">
                                        {tag.name}
                                    </Badge>
                                    <ActionIcon
                                        color="red"
                                        variant="light"
                                        onClick={() => handleDeleteTag(tag.id, tag.name)}
                                    >
                                        <IconTrash size={16} />
                                    </ActionIcon>
                                </Group>
                            ))}
                        </Stack>
                    )}
                </Stack>
            </Modal>
        </>
    )
}
