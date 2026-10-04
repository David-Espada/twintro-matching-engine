import type { Metadata } from "next";
import { Shell } from "@/components/shell";
import "./globals.css";
export const metadata: Metadata = { title: "Twintro — Professional Matching", description: "Discover professional affinity and complementary strengths with the Twintro Hybrid Decision Engine." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><Shell>{children}</Shell></body></html>;
}
