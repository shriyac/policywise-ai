# Evaluation provenance

The original Replit run (not reproduced by this reference repository) reported:

- 15 questions: 5 factual, 4 cross-document, 3 ambiguous, 3 unanswerable.
- Hit@5: 9/9 answerable questions.
- Faithfulness of *released* claims: 13/13.
- Citation validity and support: 13/13 released citations.
- Unanswerable abstention: 3/3.
- Answer availability: 7/9 answerable questions.
- C3: exhausted model-provider rate-limit retries.
- C4: generated answer failed citation validation and was withheld.
- 75 tests passed **in the user's original Replit project** (not asserted for this reference implementation).
- Cold initialization: 31.71 s. Warm final completed calls mean: 1.66 s; elapsed including backoff mean: 26.26 s.

**This repo is a reconstructed/reference codebase, not an export of the Replit implementation.**
Scores above are historical observations supplied in the user's evaluation export; do not present them as results from running this repository. The source corpus consisted of eight *independently written GitLab policy briefs*, not original complete GitLab policy PDFs. Copy the actual permitted PDFs into `data/policies/` to reproduce ingestion.
