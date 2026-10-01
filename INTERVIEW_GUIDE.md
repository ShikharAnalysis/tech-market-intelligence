# Interview preparation — explain it, do not memorize it

## A three-minute walkthrough

**First 30 seconds:** State the decision: prioritize technology-service segments for a hypothetical consulting firm's further market research. Explain that time and business-development capacity are limited.

**Next 45 seconds:** State source, scope and grain. Real USAspending data; four selected awarding agencies; three IT service categories; FY2023–FY2025. The cleaned snapshot contains 7,704 recipient-year observations, not contracts. Explain retained negative values.

**Next 45 seconds:** Explain the score: market size, historical growth and supplier fragmentation. Mention that weights are business assumptions. Open the dashboard and change a scenario so the interviewer can see the trade-off.

**Next 30 seconds:** Show the actual top segment and its values from the current memo. Explain why it warrants investigation and what could disqualify it.

**Last 30 seconds:** Explain one validation and one limitation. For example, SQL/Python metrics reconcile, but historical obligations cannot identify obtainable future revenue. End with the next evidence you would collect.

## Questions you should be able to answer

### Why this project?

It connects data processing to a resource-allocation decision. The useful output is a prioritized research agenda, not merely a chart of the largest spenders.

### Why this dataset if you are applying in India?

It is a public, reproducible source for demonstrating analytical methods. The case concerns US procurement; it does not imply the same market structure or procurement eligibility in India. The skills—SQL, data quality, grouping, measurement and communicating trade-offs—are transferable.

### Why only four agencies?

A bounded educational scope keeps the analysis interpretable and auditable. The sample is deliberate, not statistically representative. You cannot claim the highest-ranked segment is the best across all government agencies.

### What is one observation?

A recipient entity's net obligations for one fiscal year, one awarding agency and one NAICS category. Multiple contracts can contribute to that observation.

### Why obligations instead of revenue?

That is what the source measures. Obligations represent commitments; neither company revenue nor cash outlays can be inferred directly from them.

### Why keep negative values?

Removing them inflates the market total. But a negative recipient net amount cannot be used as a market share, so concentration uses a separately defined positive-recipient denominator.

### What does HHI tell you?

How concentrated the measured positive recipient-net shares are. It says nothing directly about bid eligibility, incumbent relationships or the number of potential entrants.

### Why use log size?

A large size gap could dominate a linear normalized score. Log size moderates that influence while preserving order. It is a modeling choice and should be tested, not treated as a universal rule.

### Why these weights?

They represent a balanced starting preference for this case, not a data-estimated truth. The alternative scenarios reveal how the recommendation depends on those preferences. If a real client has clear priorities, elicit weights and decision gates from them.

### How did you validate it?

Check source hashes, pagination, expected query coverage, duplicate grain, exact monetary sums and SQL/Python metrics. Latest-year sums are also compared with the API's agency aggregates. Discrepancies of up to four cents are disclosed and within a defined rounding bound.

### Why no machine learning?

The task is transparent prioritization, and there are only three annual observations per segment. There is no label for a successful market entry. An ML model would need a different dataset and a defensible validation target.

### Is a low HHI automatically attractive?

No. It may indicate multiple suppliers, but those suppliers can still be hard to displace. Some may share a corporate parent. The score is a first screening stage; procurement access and delivery capability are separate gates.

### How would you improve it?

Consolidate corporate parents; inspect actual upcoming solicitations and procurement vehicles; assess delivery fit; distinguish subcontracting routes; and validate recommendations with a domain expert. State which improvement you have actually implemented versus proposed.

### What did you do personally?

Answer honestly. This starter repository was developed with AI assistance. Before using it as a completed portfolio project, reproduce it, understand its calculations and make your own documented contribution. A good contribution can be a well-supported interpretation or sensitivity extension, not necessarily a complex algorithm.

## Claims to avoid

- “Analyzed 7,704 contracts.” They are recipient-year groups.
- “Improved revenue by X%.” No business intervention was measured.
- “Predicted the best market with 95% accuracy.” No predictive evaluation exists.
- “Built it for Gartner.” It is an independent case study.
- “Used Power BI.” Only say this after building the optional Power BI version.
- “The score proves easy entry.” Eligibility and access remain unmeasured.

## Readiness check

You should be able to run the project, explain one raw record, reproduce a SQL total, calculate a small HHI example, change weights, interpret a rank change and explain why the recommendation could be wrong. If you cannot yet do that, describe it as a project you are learning and developing rather than claiming full independent mastery.
