# Recommended hackathon demo cases

All 100 profiles pass schema validation, have unique IDs, and contain all five confidence fields. Twelve profiles (IDs 81–92) are hand-authored synthetic examples; the remaining 88 retain the seeded generator output. The generator preserves these cases at all supported dataset sizes.

Use the following relationship expectations, not memorized percentages. Actual MiniLM observations are captured separately in `demo-audit.json`; they are not hardcoded into scoring. High means ≥80 for the deterministic insight. Good (70–79.9) is not classified as high.

| Case | Profile A | Profile B | Expected relationship | Presentation value |
| --- | --- | --- | --- | --- |
| Nearly identical peers | Avery Quinn — AI Engineer (`usr_00081`) | Casey Lin — AI Engineer (`usr_00082`) | Very high affinity; lower complementarity | Same professional evidence, different people. Demonstrates peer collaboration without a cross-functional bonus. |
| Related AI specialties | Avery Quinn — AI Engineer (`usr_00081`) | Rowan Patel — Machine Learning Engineer (`usr_00083`) | High affinity; lower complementarity | Related titles and shared skills remain similar even when one framework differs. |
| AI meets product | Taylor Okafor — AI Engineer (`usr_00004`) | Cameron Santos — Product Manager (`usr_00008`) | Lower affinity; exceptional complementarity | The original default pair: different industries and skills can coexist with valuable role and domain relationships. |
| Marketing meets sales | Maya Costa — Marketing Manager (`usr_00085`) | Noah Bennett — Sales Manager (`usr_00086`) | Lower affinity; strong or exceptional complementarity | Demonstrates business collaboration without needing identical skills. |
| Design meets product | Sofia Park — UX Designer (`usr_00087`) | Jordan Reyes — Product Manager (`usr_00084`) | Good or stronger affinity and high complementarity | Shared product research and analytics support affinity; design and product strengths support collaboration. |
| Security meets DevOps | Omar Vega — Cybersecurity Engineer (`usr_00088`) | Elena Singh — DevOps Engineer (`usr_00089`) | Lower affinity; strong complementarity | Security plus infrastructure is professionally useful. Shared Linux and interests are separate evidence. |
| Different professional worlds | Avery Quinn — AI Engineer (`usr_00081`) | Mateo Santos — Restaurant Operations Manager (`usr_00090`) | Low affinity and low complementarity | An intentional negative control: AI engineering and restaurant operations are not automatically complementary. |
| Backend across toolsets | Priya Chen — Backend Developer (`usr_00091`) | Leo Rivera — Backend Developer (`usr_00092`) | Moderate affinity; lower complementarity | Shared role, industry and API design provide alignment, while tools, experience and interests differ. |
| AI meets backend engineering | Avery Quinn — AI Engineer (`usr_00081`) | Priya Chen — Backend Developer (`usr_00091`) | Good affinity and strong complementarity | Shows shared Python/FastAPI expertise alongside useful AI and software engineering relationships. |

## Presentation notes

Enable `NEXT_PUBLIC_DEMO_MODE=true` to surface these profiles in a Recommended demo profiles selector group. The badge and ordering are presentation conveniences; every comparison still calls the backend.

Start with AI meets product to show Affinity ≠ Complementarity. Next compare the near-identical pair, then the unrelated pair. The moderate case helps explain that the six dimensions can pull in different directions.

Restaurant-specific skills and Hospitality are intentionally outside the initial taxonomy. The engine uses semantic evidence and does not infer useful complementarity just from unfamiliar terms.
