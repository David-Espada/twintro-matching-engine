import type { Profile } from "./types";

export const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";
export const RECOMMENDED_IDS = ["usr_00004", "usr_00008", ...Array.from({length: 12}, (_, i) => `usr_${String(81 + i).padStart(5, "0")}`)];

export function groupDemoProfiles(profiles: Profile[], enabled: boolean = DEMO_MODE) {
  const indexed = new Map(profiles.map(p => [p.user_id, p]));
  const recommended = enabled ? RECOMMENDED_IDS.flatMap(id => indexed.has(id) ? [indexed.get(id)!] : []) : [];
  const selected = new Set(recommended.map(p => p.user_id));
  return { recommended, remaining: profiles.filter(p => !selected.has(p.user_id)) };
}
