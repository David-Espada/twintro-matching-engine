import type { Match, Profile, Ranking } from "./types";
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function request<T>(path: string, body?: unknown): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 180000);
  try {
    const response = await fetch(`${API_URL}/api/v1${path}`, {
      method: body === undefined ? "GET" : "POST", signal: controller.signal,
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const detail = typeof data?.detail === "string" ? data.detail :
        Array.isArray(data?.detail) ? data.detail.map((e: {msg: string}) => e.msg).join(". ") :
        `Matching service returned HTTP ${response.status}. Check that the backend is available and retry.`;
      throw new Error(detail);
    }
    if (data === null) throw new Error("The matching engine returned an unreadable response. Please retry.");
    return data;
  } catch (error) {
    if (error instanceof TypeError) throw new Error("Cannot reach the matching engine. Check that the backend is running on port 8000.");
    if (error instanceof Error && error.name === "AbortError") throw new Error("The request timed out. The first analysis may need time to download the local model. Try again shortly.");
    throw error;
  } finally { clearTimeout(timeout); }
}
export const getProfiles = () => request<Profile[]>("/profiles/demo");
export const compare = (a: Profile, b: Profile) => request<Match>("/match/1-to-1", { profile_a: a, profile_b: b });
export const rank = (source: Profile, pool: Profile[] | null, limit: number) => request<Ranking>("/match/1-to-n", {
  source_profile: source, ...(pool === null ? {} : { candidate_pool: pool }), limit, justify_top: 5,
});
