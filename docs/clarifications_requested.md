# Clarification questions for the course provider

Drafted 11 November 2026. Each question cites where the pack says conflicting or unclear things, and states the assumption being worked to in the meantime, so that a late answer does not invalidate the build.

---

**Subject: CloudServe capstone — five clarifications before submission**

Hello,

I am working through the CloudServe Solutions capstone and have hit five points where the pack is either internally inconsistent or where I would rather confirm an interpretation than assume one. Each has my working assumption attached, so none of these is blocking me — but three of them affect how I write the evaluation section, so an answer before the 15th would help.

**1. Size of the hidden evaluation set.** The README, Project Instructions §05 and Build Specification §04 say 120 tickets. Start Here, Project Instructions §10, Build Specification §08 and the Evaluation Framework say 100. Which is correct?

*Working assumption:* neither, operationally — the harness takes `--input` and `--output` as arguments, counts whatever it is given and reports against that, so it runs correctly on either. I am asking because the report has to state a figure.

**2. Whether the validation set may be used during development.** The Project Brief says of the 80 validation tickets "do not look at these while building, do not tune against them". The README, the Build Specification and the Dataset Guide say the opposite: the Dataset Guide states "check yourself against the 80 validation tickets as often as you want... there is no penalty for repeated use" and "report your validation figures in your report".

*Working assumption:* the Dataset Guide governs, since it is the document specific to the datasets. I have run the validation set once, end to end, and reported the figures as validation figures. I did not adjust any threshold, rule or prompt afterwards, so nothing has been tuned against it even on the stricter reading. If the Project Brief's reading is the correct one, I would like to know whether that single run is a problem and how to declare it.

**3. Hallucination rate with one assessor.** The Evaluation Framework asks for at least fifty generated responses assessed independently by two people, with an inter-rater agreement rate reported. This is an individual project, so a second independent assessor is not available to me.

*Working assumption:* I will score a sample myself against the published rubric, state the sample size, state that there was one assessor, and state that no agreement rate can be computed. Confirming that a declared single-assessor sample is acceptable — rather than leaving the metric as "not measured" — would change what I report.

**4. Free-tier token limits and the unattended run.** The gate runs the harness on an assessor's machine, presumably with an assessor's own free-tier key. My measured cost is about 1,470 tokens per ticket, so a 120-ticket run needs roughly 177,000 tokens. On Groq's free tier the account exposes 1,000 requests per day and a refilling 8,000 tokens per minute, and the published per-day token allowance for the model is close to that 177,000 figure. Two questions follow:

   - Is a free-tier key expected to be sufficient for the gate run, or will the assessor use a paid key?
   - My repository contains a response cache that makes repeated runs cheap. Is committing cached responses acceptable, or would that be treated as avoiding genuine execution?

*Working assumption:* the cache is not committed, and the run is expected to make real calls. I have reduced per-ticket cost by 55% to fit, and the README states the expected wall clock, which the per-minute limit puts at roughly 25 minutes for 120 tickets.

**5. Submission packaging.** The Submission Guide specifies an archive named `FirstnameLastname_Capstone_Submission.zip` with exactly four top-level folders. The course announcement mentions only "complete project files plus a 20-minute video".

*Working assumption:* the Submission Guide applies and I will follow its four-folder layout.

Thank you,
Sourabh

---

## Notes to self

Not part of the message. The extension request mentioned in the delivery plan is a separate conversation and should be sent on its own rather than bundled with these, since it needs a reason and a proposed date rather than a yes or no.

Question 2 is the one with real consequence. If the Project Brief's reading turns out to govern, the validation figures in the report need reframing and the run needs declaring, which is a writing change rather than a build change — but it is better found now than in a marker's comments.
