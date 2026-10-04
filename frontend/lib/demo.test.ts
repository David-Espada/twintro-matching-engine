import { expect, it } from "vitest";
import { groupDemoProfiles } from "./demo";
import type { Profile } from "./types";

it("demo mode only reorders real profiles and does not duplicate or invent entries", () => {
  const profiles = [{user_id: "ordinary"}, {user_id: "usr_00081"}, {user_id: "usr_00004"}] as Profile[];
  const grouped = groupDemoProfiles(profiles, true);
  expect(grouped.recommended.map(p => p.user_id)).toEqual(["usr_00004", "usr_00081"]);
  expect(grouped.remaining).toEqual([profiles[0]]);
  expect(grouped.recommended[0]).toBe(profiles[2]);
  expect(groupDemoProfiles(profiles, false)).toEqual({recommended: [], remaining: profiles});
});
