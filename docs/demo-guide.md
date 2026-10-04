# Three-minute hackathon walkthrough

1. Open the dashboard at `http://localhost:3000`. Point out the live PostgreSQL status, local semantic model, and visible six-part formula. With `NEXT_PUBLIC_DEMO_MODE=true`, the **Hackathon Demo** badge and recommended selector group are visible.
2. Open **1-to-1 Match** and compare the default AI engineer with the product manager. Show both **Professional Affinity** and **Collaboration Potential** cards. The affinity is low while complementarity is exceptional: “They are not highly similar profiles, but they may create strong professional value together.” Read the deterministic **Professional Connection Insight** below the cards.
3. Select Avery Quinn and Casey Lin from **Recommended demo profiles**. Affinity is very high, confidence is 100%, and similarity dimensions agree. Complementarity is lower, supporting peer collaboration rather than implying exceptional cross-functional value. See [all nine recommended pairs](demo-cases.md) for an unrelated control and a moderate match.
4. Switch one profile to **Enter manually** and clear its interests. Show the unavailable component and reduced confidence; the remaining weights are renormalized.
5. Open **1-to-N Ranking**, select **Stored PostgreSQL profiles**, and click **Find Best Matches**. Display measured execution time, affinity, complementarity, and evidence tags. Filter minimum complementarity or industry; explain that filters narrow the returned results without recalculating scores. Expand a result: its evidence is already in the ranking response.
6. Open **Engine Explanation**. Follow the flow from profiles and normalization through structured, semantic and complementarity evidence to the deterministic decision. End with the explicit statement: **“The AI language model does not calculate the score.”**

Useful language: “The model provides embeddings. Our engine decides the score. The explanation provider only describes that result.”

For reproducible demonstrations, leave `OPENAI_API_KEY` empty. Warm the model with one comparison before presenting. Keep the backend running to retain its concept cache.

Use **Demo professionals** for the regular 100-profile walkthrough. The [50,000-profile presentation case](large-network-demo.md) uses **Stored PostgreSQL profiles** and the expandable **Engine metrics** panel. See the [current scalability report](scalability-report.md) for measured latency, retrieval recall and actual HNSW verification.
