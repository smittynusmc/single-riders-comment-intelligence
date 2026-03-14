import path from "node:path";

const nextConfig = {
  experimental: {
    typedRoutes: true,
  },
  output: "standalone",
  outputFileTracingRoot: path.join(process.cwd(), "../.."),
  transpilePackages: ["@single-riders/shared-types"],
};

export default nextConfig;
