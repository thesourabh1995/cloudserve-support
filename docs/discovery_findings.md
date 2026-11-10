# Stage 1 — Discovery findings

Generated from 500 development tickets and 29 knowledge base articles by `analysis/discovery_analysis.py`.

## 1. Where the volume comes from

| Channel | Tickets | Share |
|---|---:|---:|
| email | 212 | 42.4% |
| chat | 155 | 31.0% |
| docs_comment | 78 | 15.6% |
| forum | 55 | 11.0% |

## 2. How much of it is already answered in the documentation

| Channel | Tickets | Answerable from docs | Share |
|---|---:|---:|---:|
| email | 212 | 153 | 72.2% |
| chat | 155 | 119 | 76.8% |
| docs_comment | 78 | 48 | 61.5% |
| forum | 55 | 37 | 67.3% |
| **All channels** | **500** | **357** | **71.4%** |

## 3. What the tickets are about

| Intent | Tickets | Share | Answerable | Expected escalation | Never auto-respond |
|---|---:|---:|---:|---:|:---:|
| data_export | 29 | 5.8% | 93% | 7% |  |
| data_residency | 29 | 5.8% | 72% | 28% |  |
| rollback_request | 28 | 5.6% | 75% | 25% |  |
| deployment_failure | 27 | 5.4% | 70% | 30% |  |
| compliance_request | 26 | 5.2% | 65% | 100% | yes |
| sso_configuration | 26 | 5.2% | 85% | 15% |  |
| security_incident | 26 | 5.2% | 54% | 100% | yes |
| database_issue | 26 | 5.2% | 69% | 62% |  |
| api_usage_question | 24 | 4.8% | 96% | 4% |  |
| billing_query | 24 | 4.8% | 88% | 12% |  |
| performance_degradation | 23 | 4.6% | 74% | 57% |  |
| quota_or_overage | 23 | 4.6% | 87% | 13% |  |
| account_access | 22 | 4.4% | 77% | 23% |  |
| onboarding | 22 | 4.4% | 91% | 9% |  |
| integration_help | 21 | 4.2% | 76% | 24% |  |
| webhook_issue | 21 | 4.2% | 76% | 24% |  |
| feature_request | 20 | 4.0% | 0% | 100% | yes |
| authentication_failure | 20 | 4.0% | 70% | 30% |  |
| api_key_issue | 18 | 3.6% | 67% | 33% |  |
| configuration_help | 17 | 3.4% | 59% | 41% |  |
| unclear_request | 15 | 3.0% | 0% | 100% | yes |
| rate_limit | 13 | 2.6% | 92% | 8% |  |

Intents that must never be answered automatically: compliance_request, feature_request, security_incident, unclear_request.

## 4. The human baseline

| Measure | Value |
|---|---:|
| Tickets in set | 500 |
| First contact resolution | 43.8% |
| Escalation rate | 56.2% |
| Repeat contact rate | 21.6% |
| Mean resolution time | 422 min |
| Median resolution time | 214 min |
| Mean CSAT | 2.97 / 5 |

## 5. Outcomes by customer group

| Customer tier | Tickets | FCR | Mean CSAT | Median resolution |
|---|---:|---:|---:|---:|
| standard | 253 | 43.1% | 2.98 | 266 min |
| business | 164 | 48.2% | 2.91 | 141 min |
| enterprise | 83 | 37.3% | 3.05 | 369 min |

Spread between best and worst group: **10.8 percentage points**.

| Language fluency | Tickets | FCR | Mean CSAT | Median resolution |
|---|---:|---:|---:|---:|
| fluent | 380 | 43.2% | 2.95 | 216 min |
| non_fluent | 120 | 45.8% | 3.04 | 198 min |

Spread between best and worst group: **2.7 percentage points**.

| Region | Tickets | FCR | Mean CSAT | Median resolution |
|---|---:|---:|---:|---:|
| north_america | 170 | 48.8% | 3.05 | 110 min |
| europe | 151 | 43.7% | 3.01 | 198 min |
| asia_pacific | 119 | 39.5% | 2.94 | 292 min |
| latin_america | 60 | 38.3% | 2.73 | 235 min |

Spread between best and worst group: **10.5 percentage points**.

## 6. Interview claims checked against the data

| Claim | What the data shows | Verdict |
|---|---|---|
| Sofia: 'seven out of ten I could answer without looking anything up' | 71.4% of tickets are answerable from the knowledge base (357 of 500) | supported |
| Daniel: 'about half of what reaches me tier one could have resolved' | 49.1% of escalated tickets (138 of 281) were answerable from the docs | check against the figure above |
| Marcus: 'we are at forty-two per cent' first contact resolution | 43.8% in this sample | check |
| Sofia: non-fluent English tickets 'have our worst satisfaction scores' | fluent: 2.95; non_fluent: 3.04 | check |
| Ravi: enterprise customers 'get answers in about an hour' | business: 141 min median; enterprise: 369 min median; standard: 266 min median | check |

## 7. Documentation coverage

| Article | Title | Tickets needing it |
|---|---|---:|
| DOC-DATA-001 | Exporting account data and scheduled extracts | 27 |
| DOC-API-003 | Webhook delivery, retries and signature verification | 26 |
| DOC-API-001 | Understanding API rate limits and quota tiers | 24 |
| DOC-API-002 | Pagination and handling large result sets | 23 |
| DOC-AUTH-003 | Single sign-on configuration with SAML providers | 22 |
| DOC-DEPLOY-002 | Rolling back a failed release | 21 |
| DOC-BILL-001 | Understanding your invoice and usage breakdown | 21 |
| DOC-DATA-003 | Data residency and regional storage | 21 |
| DOC-BILL-003 | Usage limits, overage and spend controls | 20 |
| DOC-ONB-001 | First deployment: a walkthrough | 20 |

Knowledge base holds **29 articles**. **29** are the expected source for at least one ticket.
Every article was reviewed within the current cycle, so the knowledge base itself is not stale. Daniel's warning about answers that were correct two years ago therefore applies to the agents' unreviewed private snippet files, not to these articles — evidence for retrieving from the knowledge base rather than learning from past agent replies.
