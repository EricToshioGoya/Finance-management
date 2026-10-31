import { defineConfig } from '@playwright/test';
import { createHash, X509Certificate } from 'node:crypto';
import { readFileSync } from 'node:fs';

// Trust only the generated local certificate's public key, not arbitrary TLS errors.
// The backend smoke check separately verifies the certificate chain/hostname.
const certificate = new X509Certificate(readFileSync('../.local/localhost.crt'));
const pin = createHash('sha256').update(certificate.publicKey.export({ type: 'spki', format: 'der' })).digest('base64');

export default defineConfig({
  testDir: './tests', fullyParallel: false, workers: 1,
  use: {
    baseURL: 'https://localhost:8443',
    launchOptions: { executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium',
      args: [`--ignore-certificate-errors-spki-list=${pin}`] },
  },
});
