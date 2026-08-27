export type EndpointStatus = {
  url: string;
  ok: boolean;
  latencyMs: number;
};

export function summarize(statuses: EndpointStatus[]): string {
  return statuses
    .map(({ url, ok, latencyMs }) => `${ok ? "UP" : "DOWN"} ${url} ${latencyMs}ms`)
    .join("\n");
}
