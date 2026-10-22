import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { defineConfig, mergeConfig } from "vite";
import base from "./vite.config.ts";

/**
 * Spec 004 E5 (US9-AS5, automated): the dev server over HTTPS, as Vercel serves the page, so the
 * Secure renewal cookie is handled as in production. `/api` is forwarded to the API on the page's
 * own origin, as `frontend/vercel.json` does after the switch. Throwaway self-signed certificate.
 */
const dir = join(tmpdir(), "oulad-session-cert");
const key = join(dir, "key.pem");
const cert = join(dir, "cert.pem");
if (!existsSync(cert)) {
  mkdirSync(dir, { recursive: true });
  execFileSync("openssl", [
    "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2",
    "-keyout", key, "-out", cert, "-subj", "/CN=localhost",
  ], { stdio: "ignore" });
}

export default mergeConfig(
  base,
  defineConfig({
    server: { port: 5174, strictPort: true, https: { key: readFileSync(key), cert: readFileSync(cert) } },
  }),
);
