import { Card as MCard, Divider, Text, Title, Stack, Blockquote, Textarea, Button, ActionIcon, Group, Box, Modal, Badge, Select } from "@mantine/core"
import React from "react"

import { DiskKeyTranslates, Id, Pc, RamStickKeyTranslates } from "../types"
import { useDrawer } from "../hooks/useDrawer"
import { useDeletePc, useFetchAllPcs, useFetchPc, useUpdateNote, useFetchAllTags, useAddTagToPc, useRemoveTagFromPc } from "../hooks/useService"
import { IconEdit, IconTrash } from "@tabler/icons-react"
import { Field, PreviewField, SubField } from "./Field"
import { diskKeyTranslates, pcKeyTranslates, ramStickKeyTranslates } from "../constants"
import { formatDate } from "../utils/dateUtils"

type Props = {
    pcId: Id
}

export const Card: React.FC<Props> = ({ pcId }) => {
    const drawer = useDrawer()
    const { data: pc, error, isPending, isError, refetch } = useFetchPc(pcId)
    const { refetch: refetchAllPcs } = useFetchAllPcs()
    const { mutate: deletePc } = useDeletePc({
        onFinish: () => {
            drawer.close()
            refetchAllPcs()
        }
    })

    if (isPending) {
        return <div>Loading...</div>
    }

    if (isError) {
        return <Blockquote color="red">{error.message}</Blockquote>
    }

    if (!pc) {
        return <Blockquote color="red">No data</Blockquote>
    }

    const title = (
        <Title order={4} lineClamp={1}>
            {pc.host}
        </Title>
    )


    // Check if PC was added within the 15 minutes in user's local time
    const isRecentlyAdded = () => {
        const submittedAt = new Date(pc.submitted_at);
        const now = new Date();

        const diffInMs = now.getTime() - submittedAt.getTime();
        const diffInMinutes = diffInMs / (1000 * 60);

        return diffInMinutes < 15;
    };
    return (
        <MCard
            p="md"
            radius="md"
            style={{ 
                cursor: "pointer",
                borderColor: isRecentlyAdded() ? '#228BE6' : undefined,
                borderWidth: isRecentlyAdded() ? '2px' : '1px',
                backgroundColor: isRecentlyAdded() ? 'rgba(34, 139, 230, 0.1)' : undefined,
                transition: 'all 0.3s ease'
            }}
            onClick={() => {
                drawer.open({
                    body: <DrawerCard pc={pc} refetch={refetch} onDelete={() => void deletePc({ pcId })} />,
                    title: <div>{title}</div>, // Needs to be wrapped in `div`. Otherwise cause console error. 
                })
            }}
            withBorder
        >
            {title}

            <MCard.Section>
                <Divider my="xs" />
            </MCard.Section>

            <PreviewField
                title="CPU"
                value={pc.cpu}
            />
            <PreviewField
                title="RAM"
                value={`${pc.ram_total_gb} GB`}
            />
            <PreviewField
                title="Resolution"
                value={pc.resolution}
            />
            <PreviewField
                title="Notes"
                value={pc.notes}
            />
            {pc.tags && pc.tags.length > 0 && (
                <Group gap="xs" mt="xs">
                    {pc.tags.map((tag) => (
                        <Badge key={tag.id} color={tag.color} variant="light" size="sm">
                            {tag.name}
                        </Badge>
                    ))}
                </Group>
            )}
            <Box mt="xs" style={{ textAlign: 'right' }}>
                <Text size="sm" c="dimmed">
                    {formatDate(pc.submitted_at)}
                </Text>
            </Box>
        </MCard>
    )
}

const DrawerCard: React.FC<{ pc: Pc, refetch: () => void, onDelete: () => void }> = ({ pc, refetch, onDelete }) => {
    const [data, setData] = React.useState(pc)
    const [notes, setNotes] = React.useState(data.notes)
    const [isEditing, setIsEditing] = React.useState(false)
    const [isEditingTags, setIsEditingTags] = React.useState(false)
    const [isDeleteModalOpen, setIsDeleteModalOpen] = React.useState(false)
    
    // Tags state and hooks
    const { data: allTags } = useFetchAllTags()
    const { mutate: addTagToPc, isPending: isAddingTag } = useAddTagToPc({
        onSuccess: () => {
            refetch()
            setIsEditingTags(false)
        }
    })
    const { mutate: removeTagFromPc, isPending: isRemovingTag } = useRemoveTagFromPc({
        onSuccess: () => {
            refetch()
        }
    })
    
    const { mutate: updateNote, isPending } = useUpdateNote({
        onFinish: () => {
            setIsEditing(false)
        },
        onSuccess: notes => {
            setData(value => ({ ...value, notes }))
            refetch()
        },
    })
    
    // Update local data when pc prop changes
    React.useEffect(() => {
        setData(pc)
        setNotes(pc.notes)
    }, [pc])
    
    const availableTagsForSelect = allTags?.filter(
        tag => !data.tags?.some(pcTag => pcTag.id === tag.id)
    ) || []
    
    const handleAddTag = (tagId: string | null) => {
        if (tagId) {
            addTagToPc({ pcId: data.id, tagId: parseInt(tagId) })
        }
    }
    
    const handleRemoveTag = (tagId: number) => {
        removeTagFromPc({ pcId: data.id, tagId })
    }

    return (
        <Stack>
            <Field title={pcKeyTranslates.cpu} value={data.cpu} />
            <Field
                title={pcKeyTranslates.disks}
                value={(
                    <>
                        {data.disks.map((disk, index) => {
                            return (
                                // TODO: Use id as key
                                <Stack key={index} gap={0} ml={"lg"}>
                                    {Object.entries(disk).map(([key, value], index) => (
                                        <SubField
                                            // TODO: Use id as key
                                            key={index}
                                            title={diskKeyTranslates[key as keyof DiskKeyTranslates]}
                                            value={value}
                                        />
                                    ))}
                                    {index !== data.disks.length - 1 && <Divider my="xs" />}
                                </Stack>
                            )
                        })}
                    </>
                )}
            />
            <Field
                title={pcKeyTranslates.gpus}
                value={(
                    <>
                        {data.gpus.map((gpu, index) => (
                            // TODO: Use id as key
                            <Text key={index} size="sm" lineClamp={1}>
                                {gpu}
                            </Text>
                        ))}
                    </>
                )}
            />
            <Field title={pcKeyTranslates.host} value={data.host} />
            <Field title={pcKeyTranslates.id} value={data.id} />
            <Field title={pcKeyTranslates.mainboard} value={data.mainboard} />
            <Field title={pcKeyTranslates.ram_slots} value={data.ram_slots} />
            <Field
                title={pcKeyTranslates.ram_sticks}
                value={(
                    <>
                        {data.ram_sticks.map((ramStick, index) => {
                            return (
                                // TODO: Use id as key
                                <Stack key={index} gap={0} ml={"lg"}>
                                    {Object.entries(ramStick).map(([key, value], index) => (
                                        <SubField
                                            // TODO: Use id as key
                                            key={index}
                                            title={ramStickKeyTranslates[key as keyof RamStickKeyTranslates]}
                                            value={value}
                                        />
                                    ))}
                                    {index !== data.ram_sticks.length - 1 && <Divider my="xs" />}
                                </Stack>
                            )
                        })}
                    </>
                )}
            />
            <Field title={pcKeyTranslates.ram_total_gb} value={`${data.ram_total_gb}`} />
            <Field title={pcKeyTranslates.resolution} value={data.resolution} />
            <Field title={pcKeyTranslates.serial} value={data.serial} />
            <Field title={pcKeyTranslates.submitted_at} value={formatDate(data.submitted_at)} />
            <Stack gap={0}>
                <Group gap="sm">
                    <Title order={5}>{pcKeyTranslates.notes}:</Title>
                    {!isEditing && (
                        <ActionIcon
                            onClick={() => void setIsEditing(true)}
                            variant="light"
                            size="sm"
                        >
                            <IconEdit />
                        </ActionIcon>
                    )}
                </Group>
                {isEditing ? (
                    <Stack>
                        <Textarea
                            placeholder="Add notes about this PC..."
                            value={notes}
                            onChange={(event) => setNotes(event.currentTarget.value)}
                            minRows={3}
                            maxRows={8}
                            autosize
                            mt="md"
                            disabled={isPending}
                        />
                        <Group>
                            <Button
                                onClick={() => void setIsEditing(false)}
                                disabled={isPending}
                                loading={isPending}
                                variant="outline"
                            >
                                {'Cancel'}
                            </Button>
                            <Button
                                onClick={() => {
                                    updateNote({ notes: notes, pc_id: data.id })
                                }}
                                disabled={isPending}
                                loading={isPending}
                            >
                                {'Save'}
                            </Button>
                        </Group>
                    </Stack>
                ) : (
                    <Text size="md" lineClamp={20}>
                        {data.notes}
                    </Text>
                )}
            </Stack>
            
            {/* Tag Management Section */}
            <Stack gap={0}>
                <Group gap="sm">
                    <Title order={5}>Tags:</Title>
                    {!isEditingTags && (
                        <ActionIcon
                            onClick={() => setIsEditingTags(true)}
                            variant="light"
                            size="sm"
                        >
                            <IconEdit />
                        </ActionIcon>
                    )}
                </Group>
                
                {/* Display current tags */}
                {data.tags && data.tags.length > 0 && (
                    <Group gap="xs" mt="sm">
                        {data.tags.map((tag) => (
                            <Badge 
                                key={tag.id} 
                                color={tag.color} 
                                variant="filled" 
                                size="sm"
                                rightSection={
                                    isEditingTags ? (
                                        <ActionIcon 
                                            size="xs" 
                                            color="red"
                                            variant="transparent"
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                handleRemoveTag(tag.id)
                                            }}
                                            disabled={isRemovingTag}
                                        >
                                            ×
                                        </ActionIcon>
                                    ) : undefined
                                }
                            >
                                {tag.name}
                            </Badge>
                        ))}
                    </Group>
                )}
                
                {isEditingTags && (
                    <Stack mt="sm">
                        <Select
                            placeholder="Add a tag..."
                            data={availableTagsForSelect.map(tag => ({
                                value: tag.id.toString(),
                                label: tag.name
                            }))}
                            onChange={handleAddTag}
                            disabled={isAddingTag || availableTagsForSelect.length === 0}
                            clearable
                        />
                        <Group>
                            <Button
                                onClick={() => setIsEditingTags(false)}
                                variant="outline"
                                size="sm"
                            >
                                Done
                            </Button>
                        </Group>
                    </Stack>
                )}
                
                {!data.tags || data.tags.length === 0 ? (
                    <Text size="sm" c="dimmed" mt="sm">
                        {isEditingTags ? "Select tags to add to this PC" : "No tags assigned"}
                    </Text>
                ) : null}
            </Stack>
            
            <Button
                color="red"
                leftSection={<IconTrash size={18} />}
                onClick={() => setIsDeleteModalOpen(true)}
            >
                {"Delete pc"}
            </Button>

            <Modal
                opened={isDeleteModalOpen}
                onClose={() => setIsDeleteModalOpen(false)}
                title="Confirm Deletion"
                centered
            >
                <Stack>
                    <Text>Are you sure you want to delete this PC ({data.host})? This action cannot be undone.</Text>
                    <Group justify="flex-end">
                        <Button variant="outline" onClick={() => setIsDeleteModalOpen(false)}>
                            Cancel
                        </Button>
                        <Button 
                            color="red"
                            onClick={() => {
                                onDelete();
                                setIsDeleteModalOpen(false);
                            }}
                        >
                            Delete
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </Stack>
    )
}
