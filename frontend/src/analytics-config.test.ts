import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

describe('production analytics configuration', () => {
  it('uses the configured GA4 measurement ID', () => {
    const environmentPath = resolve(process.cwd(), '.env.production')
    const productionEnvironment = readFileSync(environmentPath, 'utf8')

    expect(productionEnvironment).toMatch(/^VITE_GA_MEASUREMENT_ID=G-ZTGCCK8R1T$/m)
  })
})
