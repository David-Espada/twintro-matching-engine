"use client";
import { useEffect, useState } from "react";
import { getProfiles } from "./api";
import type { Profile } from "./types";

export function useProfiles() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    getProfiles().then(p => { if (active) setProfiles(p); }).catch(e => { if (active) setError(e.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  return { profiles, error, loading };
}
