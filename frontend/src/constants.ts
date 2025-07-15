import { DiskKeyTranslates, PcKeyTranslates, RamStickKeyTranslates } from "./types"

export const pcKeyTranslates: PcKeyTranslates = {
    cpu: "CPU",
    disks: "Disks",
    gpus: "GPUs",
    host: "Hostname",
    id: "ID",
    mainboard: "Mainboard",
    notes: "Notes",
    ram_slots: "Ram slots",
    ram_sticks: "Ram sticks",
    ram_total_gb: "Ram total (GB)",
    resolution: "Resolution",
    serial: "Serial",
    submitted_at: "Submitted at",
}

export const diskKeyTranslates: DiskKeyTranslates = {
    model: "Model",
    path: "Path",
    serial: "Serial",
    size_gb: "Size (GB)",
}

export const ramStickKeyTranslates: RamStickKeyTranslates = {
    model: "Model",
    size_gb: "Size (GB)",
    type: "Type",
}
