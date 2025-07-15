import "@mantine/core/styles.css"
import "@mantine/notifications/styles.css"
import { MantineProvider } from "@mantine/core"
import { Notifications } from "@mantine/notifications"
import { QueryClientProvider } from "@tanstack/react-query"

import { DrawerProvider } from "./hooks/useDrawer"
import { queryClient } from "./hooks/useService"
import { Home } from "./pages/Home"
import { theme } from "./theme"

export default function App() {
    return (
        <MantineProvider theme={theme}>
            <Notifications />
            <QueryClientProvider client={queryClient}>
                <DrawerProvider>
                    <Home />
                </DrawerProvider>
            </QueryClientProvider>
        </MantineProvider>
    )
}
