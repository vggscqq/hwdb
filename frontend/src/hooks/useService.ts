import { QueryClient, useMutation, useQuery } from "@tanstack/react-query"

import { Id, Pc, Tag } from "../types"

const API_URL = ""
const headers: HeadersInit = {
    "Content-Type": "application/json",
}

export const queryClient = new QueryClient()

export const useFetchAllPcs = (sortBy?: string, sortOrder?: string, tagFilter?: string) => {
    return useQuery({
        queryFn: async () => {
            const params = new URLSearchParams()
            if (sortBy) params.append('sort_by', sortBy)
            if (sortOrder) params.append('sort_order', sortOrder)
            if (tagFilter) params.append('tag', tagFilter)
            
            const url = `${API_URL}/pcs${params.toString() ? '?' + params.toString() : ''}`
            const response = await fetch(url, { headers })
            if (!response.ok) {
                throw new Error("Failed to fetch data")
            }
            try {
                const data: Pc[] = await response.json()
                return data
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        queryKey: ["pcs", { sortBy, sortOrder, tagFilter }],
    })
}

export const useFetchPc = (id: Id) => {
    return useQuery({
        queryFn: async () => {
            const response = await fetch(`${API_URL}/pc/${id}`, { headers })
            if (!response.ok) {
                throw new Error("Failed to fetch data")
            }
            try {
                const data: Pc = await response.json()
                return data
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        queryKey: ["pc", { id }],
    })
}

type UseUpdateNoteParams = {
    onError?: () => void
    onFinish?: () => void
    onSuccess?: (notes: string) => void
}

export const useUpdateNote = ({ onError, onFinish, onSuccess, }: UseUpdateNoteParams) => {
    return useMutation({
        mutationFn: async (data: { pc_id: Id; notes: string }) => {
            const response = await fetch(`${API_URL}/update_notes`, {
                body: JSON.stringify(data),
                headers,
                method: 'POST',
            })
            if (!response.ok) {
                throw new Error("Failed to update data")
            }
            try {
                const data: { pc_id: Id } = await response.json()
                return data
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        onSuccess: (_data, vars) => {
            queryClient.invalidateQueries({ queryKey: ["pc", vars.pc_id] })
            queryClient.setQueryData(["pc", { id: vars.pc_id }], old => old ? ({ ...old, notes: vars.notes }) : old)
            onSuccess?.(vars.notes)
        },
        onSettled: onFinish,
        onError,
    })
}

type UseDeletePcParams = {
    onError?: () => void
    onFinish?: () => void
    onSuccess?: () => void
}

export const useDeletePc = ({ onError, onFinish, onSuccess }: UseDeletePcParams) => {
    return useMutation({
        mutationFn: async (data: { pcId: Id }) => {
            const response = await fetch(`${API_URL}/pc/${data.pcId}/delete`, {
                headers,
                method: 'DELETE',
            })
            if (!response.ok) {
                throw new Error("Failed to update data")
            }
            try {
                const data: { pc_id: Id } = await response.json()
                return data
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        onSuccess,
        onSettled: onFinish,
        onError,
    })
}

// Tag management hooks
export const useFetchAllTags = () => {
    return useQuery({
        queryFn: async () => {
            const response = await fetch(`${API_URL}/tags`, { headers })
            if (!response.ok) {
                throw new Error("Failed to fetch tags")
            }
            try {
                const data: Tag[] = await response.json()
                return data
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        queryKey: ["tags"],
    })
}

type UseCreateTagParams = {
    onError?: () => void
    onFinish?: () => void
    onSuccess?: (tag: Tag) => void
}

export const useCreateTag = ({ onError, onFinish, onSuccess }: UseCreateTagParams) => {
    return useMutation({
        mutationFn: async (data: { name: string; color: string }) => {
            const response = await fetch(`${API_URL}/tags`, {
                body: JSON.stringify(data),
                headers,
                method: 'POST',
            })
            if (!response.ok) {
                throw new Error("Failed to create tag")
            }
            try {
                const tag: Tag = await response.json()
                return tag
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        onSuccess: (tag) => {
            queryClient.invalidateQueries({ queryKey: ["tags"] })
            onSuccess?.(tag)
        },
        onSettled: onFinish,
        onError,
    })
}

type UseDeleteTagParams = {
    onError?: () => void
    onFinish?: () => void
    onSuccess?: () => void
}

export const useDeleteTag = ({ onError, onFinish, onSuccess }: UseDeleteTagParams) => {
    return useMutation({
        mutationFn: async (data: { tagId: number }) => {
            const response = await fetch(`${API_URL}/tags/${data.tagId}`, {
                headers,
                method: 'DELETE',
            })
            if (!response.ok) {
                throw new Error("Failed to delete tag")
            }
            try {
                const result = await response.json()
                return result
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["tags"] })
            queryClient.invalidateQueries({ queryKey: ["pcs"] })
            onSuccess?.()
        },
        onSettled: onFinish,
        onError,
    })
}

// PC Tag management hooks
type UseAddTagToPcParams = {
    onError?: () => void
    onFinish?: () => void
    onSuccess?: () => void
}

export const useAddTagToPc = ({ onError, onFinish, onSuccess }: UseAddTagToPcParams) => {
    return useMutation({
        mutationFn: async (data: { pcId: Id; tagId: number }) => {
            const response = await fetch(`${API_URL}/pc/${data.pcId}/tags`, {
                body: JSON.stringify({ tag_id: data.tagId }),
                headers,
                method: 'POST',
            })
            if (!response.ok) {
                throw new Error("Failed to add tag to PC")
            }
            try {
                const result = await response.json()
                return result
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["pcs"] })
            queryClient.invalidateQueries({ queryKey: ["pc"] })
            onSuccess?.()
        },
        onSettled: onFinish,
        onError,
    })
}

type UseRemoveTagFromPcParams = {
    onError?: () => void
    onFinish?: () => void
    onSuccess?: () => void
}

export const useRemoveTagFromPc = ({ onError, onFinish, onSuccess }: UseRemoveTagFromPcParams) => {
    return useMutation({
        mutationFn: async (data: { pcId: Id; tagId: number }) => {
            const response = await fetch(`${API_URL}/pc/${data.pcId}/tags/${data.tagId}`, {
                headers,
                method: 'DELETE',
            })
            if (!response.ok) {
                throw new Error("Failed to remove tag from PC")
            }
            try {
                const result = await response.json()
                return result
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["pcs"] })
            queryClient.invalidateQueries({ queryKey: ["pc"] })
            onSuccess?.()
        },
        onSettled: onFinish,
        onError,
    })
}

export const useFetchPcTags = (pcId: Id) => {
    return useQuery({
        queryFn: async () => {
            const response = await fetch(`${API_URL}/pc/${pcId}/tags`, { headers })
            if (!response.ok) {
                throw new Error("Failed to fetch PC tags")
            }
            try {
                const data: Tag[] = await response.json()
                return data
            } catch {
                throw new Error("Failed to parse response")
            }
        },
        queryKey: ["pc-tags", { pcId }],
    })
}
