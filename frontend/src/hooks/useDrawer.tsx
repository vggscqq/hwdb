import { Drawer as MDrawer } from "@mantine/core"
import { useDisclosure } from "@mantine/hooks"
import React from "react"

type DrawerContent = {
    body: React.ReactNode
    title?: React.ReactNode
}

type DrawerRef = {
    close: () => void
    open: (content: DrawerContent) => void
}

const DrawerContext = React.createContext<DrawerRef>(null!)

export const useDrawer = () => {
    return React.useContext(DrawerContext)
}

export const Drawer = React.forwardRef<DrawerRef>((_, ref) => {
    const [opened, { open, close }] = useDisclosure(false)
    const [content, setContent] = React.useState<DrawerContent | null>(null)

    React.useImperativeHandle(ref, () => ({
        close: () => {
            close()
            setContent(null)
        },
        open: (content: DrawerContent) => {
            setContent(content)
            open()
        },
    }))

    return (
        <MDrawer opened={opened} onClose={close} position="right" size="xl" title={content?.title}>
            {content?.body}
        </MDrawer>
    )
})

export const DrawerProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
    const drawerRef = React.useRef<DrawerRef>(null)
    const controller: DrawerRef = {
        close: () => {
            drawerRef.current?.close()
        },
        open: (content: DrawerContent) => {
            drawerRef.current?.open(content)
        },
    }

    const drawer = React.useMemo(() => <Drawer ref={drawerRef} />, [])

    return (
        <DrawerContext.Provider value={controller}>
            {drawer}
            {children}
        </DrawerContext.Provider>
    )
}
