# MHT-CET 2026 (All India / JEE) Data Extraction & Distribution Engine

An automated data pipeline that parses, validates, and visualizes candidate distribution data from the Maharashtra State CET Cell's All India (JEE-based) engineering merit list.

The pipeline transforms an unformatted 7,278-page government PDF into a verified dataset of 98,360 candidate records, calculating empirical rank spans and outputting publication-grade analytical PDF reports.

---

## Engineering Pipeline

1. **Document Slicing (\pikepdf\):** Segmented the 7,278-page PDF without running into memory buffer overflow.
2. **Text Conversion & Buffered Reading:** Streamed raw text to disk (6A.txt\) and processed lines in chunks to prevent system freezing.
3. **Regex Pattern Stripping:** Filtered out repeating multi-line government headers and page footers (\Published on 27/07/2026...\).
4. **Token Alignment & Gap Detection:** 
   - Dual-exam candidates had 16 score tokens (4 JEE + 4 CET + 4 HSC + 4 SSC).
   - JEE-only candidates had 12 score tokens (missing the 4 intermediate CET columns).
   - Dynamically injected empty placeholder columns to maintain a rigid 20-column schema across all rows.
5. **Cross-Verification:** Verified all 98,360 rows across three validation passes, reaching 0 mismatched columns.
6. **Regulatory Clarification:** Confirmed that Maharashtra CAP All India quota seats (15%) operate under 100% General/Open merit without category reservations.
7. **Empirical Density Calculation:** Derived rank boundaries directly from candidate distributions, eliminating off-by-one gaps and manual typos.
8. **PDF Report Generation (eportlab\):** Generated a vector-rendered, paginated distribution table with running headers and dynamic footers (\Page X of Y\).

---

## Percentile vs Rank Density Matrix

| Percentile Tier | Merit Rank Range | Candidates Count |
| :--- | :---: | :---: |
| **99.75 — 100.00** | 1 — 144 | 144 |
| **99.50 — 99.75** | 145 — 289 | 145 |
| **99.25 — 99.50** | 290 — 441 | 152 |
| **99.00 — 99.25** | 442 — 592 | 151 |
| **98.00 — 99.00** | 593 — 1,691 | 1,099 |
| **97.00 — 98.00** | 1,692 — 2,872 | 1,181 |
| **96.00 — 97.00** | 2,873 — 4,095 | 1,223 |
| **95.00 — 96.00** | 4,096 — 5,380 | 1,285 |
| **92.50 — 95.00** | 5,381 — 8,469 | 3,089 |
| **90.00 — 92.50** | 8,470 — 11,650 | 3,181 |
| **85.00 — 90.00** | 11,651 — 18,069 | 6,419 |
| **80.00 — 85.00** | 18,070 — 25,052 | 6,983 |
| **75.00 — 80.00** | 25,053 — 32,124 | 7,072 |
| **70.00 — 75.00** | 32,125 — 39,415 | 7,291 |
| **60.00 — 70.00** | 39,416 — 53,006 | 13,591 |
| **50.00 — 60.00** | 53,007 — 65,314 | 12,308 |
| **40.00 — 50.00** | 65,315 — 75,895 | 10,581 |
| **Below 40.00** | 75,896 — 98,360 | 22,465 |
| **Total** | **1 — 98,360** | **98,360** |

---

## Setup & Execution

### Prerequisites
\\ash
pip install pandas reportlab pikepdf
\
### Run Pipeline
1. Place raw extracted text 6A.txt\ in the root directory.
2. Execute the parser and PDF generator:
\\ash
python gen_pdf_2.py
\3. The output CSV (\mht_cet_all_india_clean.csv\) and PDF report (\All_India_Percentile_Distribution.pdf\) will be generated automatically.

---

## Author
**Malhar Kshirsagar**  
*MHT-CET 2026[JEE] Ranks v/s Percentile Analysis*
