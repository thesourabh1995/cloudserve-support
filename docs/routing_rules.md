# How a ticket is routed

The decision is made in `src/route.py`. It is a pure function: the same
ticket, classification, passages and threshold always produce the same
action and the same reason. That is what A5 checks.

## The tree

Checked in this order. The first match wins, so the reason a manager reads is
the most specific one rather than whichever happened to be tested last.

| Rule | Action | Why it is here |
|---|---|---|
| `empty_ticket` | escalate | Nothing to answer. |
| `classification_unusable` | escalate | The classifier degraded. Answering on a guess is the failure mode the brief warns about. |
| `protected_category` | escalate | `security_incident`, `compliance_request`, `feature_request`, `unclear_request`. All 87 such tickets in the development set are labelled escalate. |
| `below_threshold` | escalate | Confidence is under the configured threshold. |
| `no_supporting_passage` | escalate | Retrieval returned nothing above the relevance floor, so an answer would have nothing to cite. The 87 development tickets that are not answerable from the docs are all labelled escalate. |
| `live_incident` | escalate | High-urgency `database_issue` or `performance_degradation`. All 15 of these in the development set are labelled escalate even though the docs cover them. |
| `confident_and_grounded` | auto_respond | Everything else. 311 of 500 development tickets. |

A high-urgency `deployment_failure` is answered when it is grounded. The
labels do not treat urgency on its own as a reason to escalate, and widening
the live-incident rule to every high-urgency ticket would escalate work the
development set expects to be answered.

## The threshold is still 0.80, and that is a gap

The brief prints 0.80 and says the number is illustrative. The right value is
the one where the cost of a wrong automatic answer balances the cost of an
unnecessary escalation, read off a real confidence distribution.

That distribution does not exist yet. Classification has been measured for
accuracy on 18 tickets, not for how confidence spreads across 500. Moving the
threshold before that pass would be choosing a number because it looks
reasonable, which is the failure the brief names.

Until the full classification pass, 0.80 stays, and it is read from
`CONFIDENCE_THRESHOLD` so the calibration changes one line and can be re-run.

## What an escalation carries

The route decision itself carries the reason. The decision log
(`src/logging_store.py`) stores, for every ticket, the input, the predicted
intent and urgency, the alternatives considered, the confidence, the passages
retrieved, the action and the reason. The drafted summary is added when
generation exists; the column set is append-only so that addition does not
rewrite history.
