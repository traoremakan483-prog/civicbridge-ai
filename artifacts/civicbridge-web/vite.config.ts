import { defineConfig } from "vite";
import path from "path";

const rawPort = process.env.PORT;

if (!rawPort) {
  throw new Error(
    "PORT environment variable is required but was not provided.",
  );
}

const port = Number(rawPort);

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

const basePath = process.env.BASE_PATH ?? "/";

const STREAMLIT_PORT = 5000;
const STREAMLIT_TARGET = `http://localhost:${STREAMLIT_PORT}`;

export default defineConfig({
  base: basePath,
  plugins: [],
  server: {
    port,
    host: "0.0.0.0",
    allowedHosts: true,
    proxy: {
      "/": {
        target: STREAMLIT_TARGET,
        changeOrigin: true,
        ws: true,
        bypass(req) {
          if (req.url?.startsWith("/@") || req.url?.startsWith("/__vite")) {
            return req.url;
          }
          return null;
        },
      },
    },
  },
  preview: {
    port,
    host: "0.0.0.0",
    allowedHosts: true,
  },
});
