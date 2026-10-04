import { afterEach, describe, expect, it, vi } from "vitest";
import { compare, rank, request } from "./api";
import type { Profile } from "./types";
const profile: Profile = { user_id: "x", name: "Test", role: null, industry: null, skills: [], interests: [], experience_years: 0 };
afterEach(() => vi.unstubAllGlobals());
describe("backend contract", () => {
  it("sends profiles without manufacturing an affinity score", async () => {
    const fetcher = vi.fn().mockResolvedValue({ok: true, json: async () => ({affinity_percentage: 81.7})});
    vi.stubGlobal("fetch", fetcher);
    expect((await compare(profile, profile)).affinity_percentage).toBe(81.7);
    expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({profile_a: profile, profile_b: profile});
  });
  it("omits the pool to request PostgreSQL candidates", async () => {
    const fetcher = vi.fn().mockResolvedValue({ok: true, json: async () => ({results: []})});
    vi.stubGlobal("fetch", fetcher);
    await rank(profile, null, 20);
    expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({source_profile: profile, limit: 20, justify_top: 5});
  });
  it("preserves an explicit empty pool", async () => {
    const fetcher = vi.fn().mockResolvedValue({ok: true, json: async () => ({results: []})});
    vi.stubGlobal("fetch", fetcher);
    await rank(profile, [], 5);
    expect(JSON.parse(fetcher.mock.calls[0][1].body).candidate_pool).toEqual([]);
  });
  it("shows validation errors to the user", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ok: false, json: async () => ({detail: [{msg: "Invalid experience"}]})}));
    await expect(request("/test")).rejects.toThrow("Invalid experience");
  });
  it("explains connection failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("fetch failed")));
    await expect(request("/test")).rejects.toThrow("Cannot reach the matching engine");
  });
  it("explains non-JSON service failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ok: false, status: 503, json: async () => { throw new SyntaxError("HTML error page"); }}));
    await expect(request("/test")).rejects.toThrow("HTTP 503");
  });
  it("explains timeouts", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new DOMException("Aborted", "AbortError")));
    await expect(request("/test")).rejects.toThrow("The request timed out");
  });
});
