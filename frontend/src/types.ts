type Disk = {
    model: string
    path: string
    serial: string
    size_gb: number
}

type RamStick = {
    model: string
    size_gb: number
    type: string
}

export type Id = string

type Gpu = string

export type Tag = {
    id: number
    name: string
    color: string
}

export type Pc = {
    cpu: string
    disks: Disk[]
    gpus: Gpu[]
    host: string
    id: Id
    mainboard: string
    notes: string
    ram_slots: string
    ram_sticks: RamStick[]
    ram_total_gb: number
    resolution: string
    serial: string
    submitted_at: string
    tags?: Tag[]
}

export type PcKeyTranslates = { [K in keyof Pc]: string }
export type DiskKeyTranslates = { [K in keyof Disk]: string }
export type RamStickKeyTranslates = { [K in keyof RamStick]: string }
