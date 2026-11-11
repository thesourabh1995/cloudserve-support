# Hallucination review

59 generated replies from `evaluation/results/validation_01`. The Evaluation Framework asks for at least fifty.

## How to score this

For each reply, read the answer, then read the source article under it. Ask one question: **does every factual claim in the answer follow from the source text?** A claim the article does not make is unsupported, even if it happens to be true, and even if it sounds reasonable. Generic courtesy and offers to escalate are not factual claims.

Replace the word after `verdict:` with `supported`, `unsupported` or `unclear`, and write a short note when you mark anything other than supported. Then run:

```bash
.venv/bin/python -m analysis.hallucination_review --score docs/hallucination_review.md
```

Record who scored it and when. If only one person scored it, the report must say so: the framework asks for two independent assessors and an agreement rate, and one assessor cannot produce one.

- Assessor:
- Date:

---

## 1. VAL-0001

**Ticket.** Need to rotate an exposed key

One of our production keys started returning 401 at around yesterday morning without any
change on our side. Other keys against the same account are still working.

**Reply sent.**

The 401 error indicates that the key has been revoked, expired, or its scope no longer
allows access to the endpoint; you should rotate the key by generating a new one and
updating your application.

**Quoted as support.**

- `DOC-AUTH-004` — "- The key was revoked or reached its configured expiry"

**Source: DOC-AUTH-004 — API key rotation and scope management**

> # API key rotation and scope management  **Applies to:** All plans  ## Symptoms  - A
> previously working key returns 401 Unauthorized - A key works for some endpoints and
> not others - A key needs replacing after accidental exposure  ## Common causes  - The
> key was revoked or reached its configured expiry - The key was issued with a scope
> that excludes the endpoint being called - The key belongs to a deleted user and was
> removed with the account  ## Resolution  1. Check the API keys page for the key's
> status and expiry. Revoked and expired keys are listed with the date and the user who
> acted. 2. Review the scopes attached to the key. Read-only keys cannot write, and
> project-scoped keys cannot reach organisation endpoints. 3. To rotate without
> downtime, create the replacement key first, deploy it, confirm traffic has moved, then
> revoke the old key. 4. If a key has been exposed publicly, revoke it immediately
> rather than waiting for the rotation window.  ## Notes  Keys issued to individual
> users are removed when that user is deleted. Use service accounts for anything running
> in production.

verdict: UNSCORED

note:

---

## 2. VAL-0004

**Ticket.** MFA code keeps getting rejected

my authenticator app codes are being rejected every time. i am having tried generating
new ones several times.

**Reply sent.**

The most common reason for your authenticator codes being rejected is that your device’s
clock is out of sync by more than thirty seconds, which invalidates time‑based codes.

**Quoted as support.**

- `DOC-AUTH-002` — "Device clock drift of more than thirty seconds invalidates time-based codes"

**Source: DOC-AUTH-002 — Multi-factor authentication setup and recovery**

> # Multi-factor authentication setup and recovery  **Applies to:** All plans  ##
> Symptoms  - The authenticator code is rejected as invalid - A user has lost the device
> holding their authenticator - Recovery codes were never downloaded  ## Common causes
> - Device clock drift of more than thirty seconds invalidates time-based codes - The
> authenticator was enrolled against a different account - Recovery codes were
> regenerated, invalidating the older set  ## Resolution  1. Ask the user to check that
> automatic time synchronisation is enabled on the device generating the code. Drift is
> the most common cause by a wide margin. 2. If the device is lost, the user should sign
> in with one of their recovery codes and then re-enrol a new device from the security
> page. 3. Where no recovery codes are available, an account administrator can reset
> multi-factor authentication for that user from the team members page. 4. If the user
> is the sole administrator and has no recovery codes, identity verification through
> support is required and takes up to one business day.  ## Notes  Support cannot
> disable multi-factor authentication without identity verification, regardless of
> urgency.

verdict: UNSCORED

note:

---

## 3. VAL-0005

**Ticket.** (no subject)

Our cursor seems to stop working partway through a long iteration. Is there an expiry we
should be handling?

**Reply sent.**

Cursors expire after one hour, so you should handle expiry by restarting from a recorded
checkpoint during long iterations.

**Quoted as support.**

- `DOC-API-002` — "Cursors expire after one hour. Long-running iterations should handle expiry by restarting from a recorded checkpoint."

**Source: DOC-API-002 — Pagination and handling large result sets**

> # Pagination and handling large result sets  **Applies to:** All plans  ## Symptoms  -
> Only the first page of results is returned - Iterating through results misses or
> duplicates records - Large queries time out  ## Common causes  - The cursor from the
> previous response was not passed to the next request - Offset pagination was used
> against a changing collection - The page size requested exceeds the maximum  ##
> Resolution  1. Use cursor pagination for anything that may change while you iterate.
> Offset pagination will skip or repeat records when items are inserted mid-iteration.
> 2. Pass the next_cursor value from each response as the cursor parameter of the
> following request, and stop when it is null. 3. Keep page size at or below two
> hundred. Larger requests are rejected rather than truncated. 4. For very large
> extracts, use the export endpoint, which runs asynchronously and returns a download
> link.  ## Notes  Cursors expire after one hour. Long-running iterations should handle
> expiry by restarting from a recorded checkpoint.

verdict: UNSCORED

note:

---

## 4. VAL-0006

**Ticket.** MFA code keeps getting rejected

I have been trying to sign in for the last two hours and keep getting an invalid
credentials message. I am certain the password is correct because I use a password
manager. Nothing has changed at our end that I am aware of.

**Reply sent.**

The most common reasons for an MFA code being rejected are a device clock drift of more
than thirty seconds, enrolling the authenticator against a different account, or having
regenerated recovery codes that invalidate the older set.

**Quoted as support.**

- `DOC-AUTH-002` — "Device clock drift of more than thirty seconds invalidates time-based codes"
- `DOC-AUTH-002` — "The authenticator was enrolled against a different account"
- `DOC-AUTH-002` — "Recovery codes were regenerated, invalidating the older set"

**Source: DOC-AUTH-002 — Multi-factor authentication setup and recovery**

> # Multi-factor authentication setup and recovery  **Applies to:** All plans  ##
> Symptoms  - The authenticator code is rejected as invalid - A user has lost the device
> holding their authenticator - Recovery codes were never downloaded  ## Common causes
> - Device clock drift of more than thirty seconds invalidates time-based codes - The
> authenticator was enrolled against a different account - Recovery codes were
> regenerated, invalidating the older set  ## Resolution  1. Ask the user to check that
> automatic time synchronisation is enabled on the device generating the code. Drift is
> the most common cause by a wide margin. 2. If the device is lost, the user should sign
> in with one of their recovery codes and then re-enrol a new device from the security
> page. 3. Where no recovery codes are available, an account administrator can reset
> multi-factor authentication for that user from the team members page. 4. If the user
> is the sole administrator and has no recovery codes, identity verification through
> support is required and takes up to one business day.  ## Notes  Support cannot
> disable multi-factor authentication without identity verification, regardless of
> urgency.

verdict: UNSCORED

note:

---

## 5. VAL-0008

**Ticket.** (no subject)

We are tightening permissions after a review and I want to understand how group
membership interacts with directly assigned roles.

**Reply sent.**

Group membership can grant broader access than a directly assigned role, so when
tightening permissions you should review both group memberships and direct role
assignments.

**Quoted as support.**

- `DOC-ACCT-001` — "A group membership grants broader access than the direct role suggests"

**Source: DOC-ACCT-001 — Managing team members, roles and permissions**

> # Managing team members, roles and permissions  **Applies to:** All plans  ## Symptoms
> - A user cannot access a project they should be able to - A departing user needs
> removing - Permissions need narrowing after a review  ## Common causes  - The role was
> granted at project scope rather than organisation scope - The invitation was never
> accepted and the account does not exist - A group membership grants broader access
> than the direct role suggests  ## Resolution  1. Check the effective permissions view
> for the user, which resolves direct roles and group memberships together. 2. Confirm
> the invitation was accepted. Pending invitations appear in a separate section and
> expire after seven days. 3. Remove a departing user rather than only changing their
> password, and revoke any API keys they created. 4. Prefer group membership to direct
> role assignment, so that access can be reviewed in one place.  ## Notes  Removing the
> last account owner is not permitted. Transfer ownership before removing the account.

verdict: UNSCORED

note:

---

## 6. VAL-0010

**Ticket.** Invoice higher than expected

Our invoice this month is considerably higher than usual and I cannot see why from the
summary. Could you help me understand what has driven the increase?

**Reply sent.**

The higher invoice may be due to usage-based charges beyond the plan allowance, a
resource left running in a non-production environment, or the billing period starting
from the subscription date rather than the first of the month.

**Quoted as support.**

- `DOC-BILL-001` — "Usage-based charges accrued beyond the plan allowance"
- `DOC-BILL-001` — "A resource was left running in a non-production environment"
- `DOC-BILL-001` — "The billing period runs from the subscription date rather than the first of the month"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 7. VAL-0011

**Ticket.** How do I revert to the previous revision

We shipped a release yesterday morning that has broken checkout for a portion of our
customers. We need to get back to the previous version quickly. What is the fastest safe
route?

**Reply sent.**

To revert quickly, open the revisions page for the service, select the last healthy
revision, and click roll back; traffic will shift within roughly thirty seconds and no
rebuild is required.

**Quoted as support.**

- `DOC-DEPLOY-002` — "Open the revisions page for the service and identify the last revision that was healthy. Select roll back on that revision. Traffic moves within roughly thirty seconds and no rebuild takes place."

**Source: DOC-DEPLOY-002 — Rolling back a failed release**

> # Rolling back a failed release  **Applies to:** Container Service, Functions  ##
> Symptoms  - A release has introduced errors and must be reverted - The previous
> revision is needed while a fix is prepared  ## Common causes  - A defect reached
> production that testing did not catch - A configuration change had unintended effects
> ## Resolution  1. Open the revisions page for the service and identify the last
> revision that was healthy. 2. Select roll back on that revision. Traffic moves within
> roughly thirty seconds and no rebuild takes place. 3. If the release included a
> database migration, roll the migration back before the service, or the older code will
> encounter a schema it does not expect. 4. Record the incident and the reason for the
> rollback before deploying a fix, while the detail is still fresh.  ## Notes  Rollback
> restores the container image and its configuration together. It does not restore data.

verdict: UNSCORED

note:

---

## 8. VAL-0012

**Ticket.** Need to roll back the latest release

How do I revert to an earlier revision? The release we put out this morning is causing
errors and I would rather roll back than try to fix forward.

**Reply sent.**

To revert to an earlier revision, follow the steps outlined in the "Rolling back a
failed release" guide for Container Service or Functions.

**Quoted as support.**

- `DOC-DEPLOY-002` — "Rolling back a failed release"

**Source: DOC-DEPLOY-002 — Rolling back a failed release**

> # Rolling back a failed release  **Applies to:** Container Service, Functions  ##
> Symptoms  - A release has introduced errors and must be reverted - The previous
> revision is needed while a fix is prepared  ## Common causes  - A defect reached
> production that testing did not catch - A configuration change had unintended effects
> ## Resolution  1. Open the revisions page for the service and identify the last
> revision that was healthy. 2. Select roll back on that revision. Traffic moves within
> roughly thirty seconds and no rebuild takes place. 3. If the release included a
> database migration, roll the migration back before the service, or the older code will
> encounter a schema it does not expect. 4. Record the incident and the reason for the
> rollback before deploying a fix, while the detail is still fresh.  ## Notes  Rollback
> restores the container image and its configuration together. It does not restore data.

verdict: UNSCORED

note:

---

## 9. VAL-0013

**Ticket.** Question about this month's charges

There are charges on our invoice for a service I do not believe we use. Could you
explain what these relate to?

**Reply sent.**

The invoice may include charges for a service that was left running in a non‑production
environment, which can appear even if you believe the service is not in use.

**Quoted as support.**

- `DOC-BILL-001` — "Charges appear for a service that is not in use"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 10. VAL-0014

**Ticket.** Bad release in production

we shipped a release around 14:00 yesterday that has broken checkout for portion of our
customers. We need to get back to the previous version quickly. waiting for your reply.

**Reply sent.**

To revert the recent release and restore the previous version, follow the rollback
procedure described in the "Rolling back a failed release" guide.

**Quoted as support.**

- `DOC-DEPLOY-002` — "A release has introduced errors and must be reverted"

**Source: DOC-DEPLOY-002 — Rolling back a failed release**

> # Rolling back a failed release  **Applies to:** Container Service, Functions  ##
> Symptoms  - A release has introduced errors and must be reverted - The previous
> revision is needed while a fix is prepared  ## Common causes  - A defect reached
> production that testing did not catch - A configuration change had unintended effects
> ## Resolution  1. Open the revisions page for the service and identify the last
> revision that was healthy. 2. Select roll back on that revision. Traffic moves within
> roughly thirty seconds and no rebuild takes place. 3. If the release included a
> database migration, roll the migration back before the service, or the older code will
> encounter a schema it does not expect. 4. Record the incident and the reason for the
> rollback before deploying a fix, while the detail is still fresh.  ## Notes  Rollback
> restores the container image and its configuration together. It does not restore data.

verdict: UNSCORED

note:

---

## 11. VAL-0018

**Ticket.** How do I page through large results

Our cursor seems to stop working partway through a long iteration. Is there an expiry we
should be handling?

**Reply sent.**

Cursors expire after one hour, so you should handle expiry by restarting from a recorded
checkpoint.

**Quoted as support.**

- `DOC-API-002` — "Cursors expire after one hour. Long-running iterations should handle expiry by restarting from a recorded checkpoint."

**Source: DOC-API-002 — Pagination and handling large result sets**

> # Pagination and handling large result sets  **Applies to:** All plans  ## Symptoms  -
> Only the first page of results is returned - Iterating through results misses or
> duplicates records - Large queries time out  ## Common causes  - The cursor from the
> previous response was not passed to the next request - Offset pagination was used
> against a changing collection - The page size requested exceeds the maximum  ##
> Resolution  1. Use cursor pagination for anything that may change while you iterate.
> Offset pagination will skip or repeat records when items are inserted mid-iteration.
> 2. Pass the next_cursor value from each response as the cursor parameter of the
> following request, and stop when it is null. 3. Keep page size at or below two
> hundred. Larger requests are rejected rather than truncated. 4. For very large
> extracts, use the export endpoint, which runs asynchronously and returns a download
> link.  ## Notes  Cursors expire after one hour. Long-running iterations should handle
> expiry by restarting from a recorded checkpoint.

verdict: UNSCORED

note:

---

## 12. VAL-0021

**Ticket.** (no subject)

We shipped a release earlier today that has broken checkout for a portion of our
customers. We need to get back to the previous version quickly. What is the fastest safe
route?

**Reply sent.**

To quickly and safely revert to the previous healthy release, open the revisions page
for the service, select the last healthy revision, and click roll back; this restores
the container image and configuration within roughly thirty seconds without rebuilding,
and if a database migration was included, roll the migration back before the service so
the older code does not encounter an unexpected schema.

**Quoted as support.**

- `DOC-DEPLOY-002` — "Open the revisions page for the service and identify the last revision that was healthy."
- `DOC-DEPLOY-002` — "Select roll back on that revision. Traffic moves within roughly thirty seconds and no rebuild takes place."
- `DOC-DEPLOY-002` — "If the release included a database migration, roll the migration back before the service, or the older code will encounter a schema it does not expect."

**Source: DOC-DEPLOY-002 — Rolling back a failed release**

> # Rolling back a failed release  **Applies to:** Container Service, Functions  ##
> Symptoms  - A release has introduced errors and must be reverted - The previous
> revision is needed while a fix is prepared  ## Common causes  - A defect reached
> production that testing did not catch - A configuration change had unintended effects
> ## Resolution  1. Open the revisions page for the service and identify the last
> revision that was healthy. 2. Select roll back on that revision. Traffic moves within
> roughly thirty seconds and no rebuild takes place. 3. If the release included a
> database migration, roll the migration back before the service, or the older code will
> encounter a schema it does not expect. 4. Record the incident and the reason for the
> rollback before deploying a fix, while the detail is still fresh.  ## Notes  Rollback
> restores the container image and its configuration together. It does not restore data.

verdict: UNSCORED

note:

---

## 13. VAL-0023

**Ticket.** Migrating our app across

We have just signed up and I am not sure where to start. We have a containerised
application and would like to get it deployed.

**Reply sent.**

To get started, create a project and a service, connect your container image, set any
required environment variables before the first deployment, then deploy and monitor the
logs for the first sixty seconds.

**Quoted as support.**

- `DOC-ONB-001` — "Create a project, then a service within it. Resources belong to services and services belong to projects."
- `DOC-ONB-001` — "Connect a repository or push a container image. The build service detects common project layouts automatically."
- `DOC-ONB-001` — "Set any environment variables the application needs before the first deployment rather than after it."
- `DOC-ONB-001` — "Deploy, then watch the logs for the first sixty seconds. Most first-deployment problems are visible immediately in startup output."

**Source: DOC-ONB-001 — First deployment: a walkthrough**

> # First deployment: a walkthrough  **Applies to:** All plans  ## Symptoms  - A new
> user does not know where to begin - The first deployment fails for unclear reasons  ##
> Common causes  - Required configuration has not been set - The project structure does
> not match what the build expects  ## Resolution  1. Create a project, then a service
> within it. Resources belong to services and services belong to projects. 2. Connect a
> repository or push a container image. The build service detects common project layouts
> automatically. 3. Set any environment variables the application needs before the first
> deployment rather than after it. 4. Deploy, then watch the logs for the first sixty
> seconds. Most first-deployment problems are visible immediately in startup output.  ##
> Notes  The free tier includes one service and is sufficient for evaluating the
> platform.

verdict: UNSCORED

note:

---

## 14. VAL-0024

**Ticket.** (no subject)

A key can read fine but every write returns a permission error. I created it myself and
I thought I gave it full access.

**Reply sent.**

The key you created is likely missing write scopes; review the scopes attached to the
key and ensure it has the necessary write permissions.

**Quoted as support.**

- `DOC-AUTH-004` — "Read-only keys cannot write, and project-scoped keys cannot reach organisation endpoints."

**Source: DOC-AUTH-004 — API key rotation and scope management**

> # API key rotation and scope management  **Applies to:** All plans  ## Symptoms  - A
> previously working key returns 401 Unauthorized - A key works for some endpoints and
> not others - A key needs replacing after accidental exposure  ## Common causes  - The
> key was revoked or reached its configured expiry - The key was issued with a scope
> that excludes the endpoint being called - The key belongs to a deleted user and was
> removed with the account  ## Resolution  1. Check the API keys page for the key's
> status and expiry. Revoked and expired keys are listed with the date and the user who
> acted. 2. Review the scopes attached to the key. Read-only keys cannot write, and
> project-scoped keys cannot reach organisation endpoints. 3. To rotate without
> downtime, create the replacement key first, deploy it, confirm traffic has moved, then
> revoke the old key. 4. If a key has been exposed publicly, revoke it immediately
> rather than waiting for the rotation window.  ## Notes  Keys issued to individual
> users are removed when that user is deleted. Use service accounts for anything running
> in production.

verdict: UNSCORED

note:

---

## 15. VAL-0025

**Ticket.** (no subject)

every deployment fails at health check stage. i am having increase timeout twice already
and it makes no difference. kindly check and revert.

**Reply sent.**

The most common reasons for a deployment to fail during the health check phase are that
the health endpoint takes longer to respond than the configured timeout, the container
listens on a different port than the service declares, or a required environment
variable is absent in the deployed environment.

**Quoted as support.**

- `DOC-DEPLOY-001` — "- The health endpoint takes longer to respond than the configured timeout - The container listens on a different port than the service declares - A required environment variable is absent in the deployed environment"

**Source: DOC-DEPLOY-001 — Container deployments failing during the health check phase**

> # Container deployments failing during the health check phase  **Applies to:**
> Container Service  ## Symptoms  - The deployment reaches running and then rolls back -
> Logs show repeated health check timeouts - The service works locally but not when
> deployed  ## Common causes  - The health endpoint takes longer to respond than the
> configured timeout - The container listens on a different port than the service
> declares - A required environment variable is absent in the deployed environment  ##
> Resolution  1. Confirm the container is listening on the port declared in the service
> definition. A mismatch here produces a health check failure that looks like a timeout.
> 2. Increase the initial delay if the application needs time to warm up before it can
> answer. Thirty seconds is a reasonable starting point for services that load models or
> caches. 3. Compare the environment variables present in the deployment against those
> the application requires. Missing configuration frequently causes a silent startup
> failure. 4. Inspect the container logs from the failed revision rather than the
> running one; the rollback replaces the logs shown by default.  ## Notes  A health
> check must return within the timeout using only local state. Endpoints that call a
> database will fail during a database incident and take the service down with them.

verdict: UNSCORED

note:

---

## 16. VAL-0026

**Ticket.** Need data to stay in the EU

we need our data to remain within EU for contract we are signing. Our organisation
created some time ago and i not sure which region it is in. please do the needful.

**Reply sent.**

The documentation does not cover the request.

**Quoted as support.**


verdict: UNSCORED

note:

---

## 17. VAL-0027

**Ticket.** Usage allowance already consumed

Overage charges appeared on our invoice that we were not expecting. We thought we were
well inside our allowance.

**Reply sent.**

The overage charges appeared because the plan allowance was consumed before the end of
the period, and overage protection was disabled, allowing usage to continue beyond the
allowance.

**Quoted as support.**

- `DOC-BILL-003` — "Overage charges appeared unexpectedly"
- `DOC-BILL-003` — "Overage protection is disabled, so usage continued beyond the allowance"

**Source: DOC-BILL-003 — Usage limits, overage and spend controls**

> # Usage limits, overage and spend controls  **Applies to:** All plans  ## Symptoms  -
> Service was throttled after a traffic increase - Overage charges appeared unexpectedly
> - A spend cap stopped a production workload  ## Common causes  - Plan allowance was
> consumed before the end of the period - A spend cap was configured and reached -
> Overage protection is disabled, so usage continued beyond the allowance  ## Resolution
> 1. Check the current period usage against the plan allowance on the billing page. 2.
> Decide deliberately between a hard spend cap, which stops the service, and overage,
> which continues at the listed rate. Production workloads generally need the second. 3.
> Configure alerts at fifty, eighty and ninety-five per cent of allowance rather than
> relying on the cap as a warning. 4. Where a cap has stopped a production service, an
> account owner can raise it immediately from the billing page and service resumes
> within a minute.  ## Notes  Spend caps apply per organisation and cannot currently be
> set per project.

verdict: UNSCORED

note:

---

## 18. VAL-0028

**Ticket.** Deployment rolls back every time

builds that work last week are now fail during dependency resolution. we having not
change our code at all.

**Reply sent.**

The most likely cause is that an unpinned dependency released a new incompatible
version, which is causing the build to fail during dependency resolution; you should pin
the dependency versions or check the dependency cache, and if you need to roll back the
deployment, use the rollback procedure described in DOC-DEPLOY-002.

**Quoted as support.**

- `DOC-DEPLOY-003` — "An unpinned dependency released a new incompatible version"
- `DOC-DEPLOY-003` — "Dependency resolution takes far longer than usual"
- `DOC-DEPLOY-002` — "Open the revisions page for the service and identify the last revision that was healthy"
- `DOC-DEPLOY-002` — "Select roll back on that revision. Traffic moves within roughly thirty seconds and no rebuild takes place"

**Source: DOC-DEPLOY-003 — Build failures caused by dependency resolution**

> # Build failures caused by dependency resolution  **Applies to:** Build Service  ##
> Symptoms  - Builds that previously succeeded now fail without code changes - The build
> works locally but fails in the pipeline - Dependency resolution takes far longer than
> usual  ## Common causes  - An unpinned dependency released a new incompatible version
> - The build environment uses a different language runtime than the local machine - The
> dependency cache holds a partially written artefact  ## Resolution  1. Pin your
> dependencies with exact versions and commit the lock file. Unpinned dependencies are
> the cause in the large majority of cases of this kind. 2. Compare the runtime version
> declared in your build configuration against the version you use locally. 3. Clear the
> build cache from the settings page and trigger a fresh build to rule out a corrupted
> artefact. 4. If a specific dependency is failing to resolve, check whether its
> registry is reachable from the build network.  ## Notes  Build logs retain the full
> resolution output for thirty days, which is usually enough to identify which version
> changed.

**Source: DOC-DEPLOY-002 — Rolling back a failed release**

> # Rolling back a failed release  **Applies to:** Container Service, Functions  ##
> Symptoms  - A release has introduced errors and must be reverted - The previous
> revision is needed while a fix is prepared  ## Common causes  - A defect reached
> production that testing did not catch - A configuration change had unintended effects
> ## Resolution  1. Open the revisions page for the service and identify the last
> revision that was healthy. 2. Select roll back on that revision. Traffic moves within
> roughly thirty seconds and no rebuild takes place. 3. If the release included a
> database migration, roll the migration back before the service, or the older code will
> encounter a schema it does not expect. 4. Record the incident and the reason for the
> rollback before deploying a fix, while the detail is still fresh.  ## Notes  Rollback
> restores the container image and its configuration together. It does not restore data.

verdict: UNSCORED

note:

---

## 19. VAL-0031

**Ticket.** Bad release in production

We shipped a release yesterday morning that has broken checkout for a portion of our
customers. We need to get back to the previous version quickly. What is the fastest safe
route?

**Reply sent.**

To quickly and safely revert to the last healthy release, open the revisions page for
the service, select the last healthy revision, click roll back, and then record the
incident and reason for the rollback before deploying a fix.

**Quoted as support.**

- `DOC-DEPLOY-002` — "Open the revisions page for the service and identify the last revision that was healthy. Select roll back on that revision. Traffic moves within roughly thirty seconds and no rebuild takes place. Record the incident and the reason for the rollback before deploying a fix, while the detail is still fresh."

**Source: DOC-DEPLOY-002 — Rolling back a failed release**

> # Rolling back a failed release  **Applies to:** Container Service, Functions  ##
> Symptoms  - A release has introduced errors and must be reverted - The previous
> revision is needed while a fix is prepared  ## Common causes  - A defect reached
> production that testing did not catch - A configuration change had unintended effects
> ## Resolution  1. Open the revisions page for the service and identify the last
> revision that was healthy. 2. Select roll back on that revision. Traffic moves within
> roughly thirty seconds and no rebuild takes place. 3. If the release included a
> database migration, roll the migration back before the service, or the older code will
> encounter a schema it does not expect. 4. Record the incident and the reason for the
> rollback before deploying a fix, while the detail is still fresh.  ## Notes  Rollback
> restores the container image and its configuration together. It does not restore data.

verdict: UNSCORED

note:

---

## 20. VAL-0033

**Ticket.** Duplicate webhook deliveries

Signature verification fails for every delivery. We are computing the signature exactly
as the documentation describes, over the parsed body.

**Reply sent.**

Signature verification fails because the signature was computed over a parsed body
rather than the raw bytes.

**Quoted as support.**

- `DOC-API-003` — "The signature was computed over a parsed body rather than the raw bytes"

**Source: DOC-API-003 — Webhook delivery, retries and signature verification**

> # Webhook delivery, retries and signature verification  **Applies to:** All plans  ##
> Symptoms  - Webhooks are not arriving at the configured endpoint - The same event is
> delivered more than once - Signature verification fails  ## Common causes  - The
> endpoint returned a non-2xx status and delivery is being retried - The endpoint
> responded too slowly and the delivery timed out - The signature was computed over a
> parsed body rather than the raw bytes  ## Resolution  1. Check the webhook delivery
> log, which records every attempt with the response status and body for the last seven
> days. 2. Return 2xx as quickly as possible and process the event asynchronously.
> Deliveries time out after five seconds. 3. Compute the signature over the raw request
> body before any parsing. Re-serialising JSON changes the bytes and invalidates the
> signature. 4. Make your handler idempotent using the event identifier. At-least-once
> delivery means duplicates are expected rather than exceptional.  ## Notes  Failed
> deliveries are retried with backoff for twenty-four hours, after which the endpoint is
> disabled and the account is notified.

verdict: UNSCORED

note:

---

## 21. VAL-0034

**Ticket.** Need to roll back the latest release

How do I revert to an earlier revision? The release we put out this morning is causing
errors and I would rather roll back than try to fix forward.

**Reply sent.**

To revert to an earlier revision, follow the steps outlined in the "Rolling back a
failed release" guide for Container Service or Functions.

**Quoted as support.**

- `DOC-DEPLOY-002` — "Rolling back a failed release"

**Source: DOC-DEPLOY-002 — Rolling back a failed release**

> # Rolling back a failed release  **Applies to:** Container Service, Functions  ##
> Symptoms  - A release has introduced errors and must be reverted - The previous
> revision is needed while a fix is prepared  ## Common causes  - A defect reached
> production that testing did not catch - A configuration change had unintended effects
> ## Resolution  1. Open the revisions page for the service and identify the last
> revision that was healthy. 2. Select roll back on that revision. Traffic moves within
> roughly thirty seconds and no rebuild takes place. 3. If the release included a
> database migration, roll the migration back before the service, or the older code will
> encounter a schema it does not expect. 4. Record the incident and the reason for the
> rollback before deploying a fix, while the detail is still fresh.  ## Notes  Rollback
> restores the container image and its configuration together. It does not restore data.

verdict: UNSCORED

note:

---

## 22. VAL-0036

**Ticket.** Getting started with first deployment

Could you point me at the right starting place? I have created an account but the
console has more in it than I expected.

**Reply sent.**

To get started with your first deployment, create a project and then a service within
it, connect a repository or push a container image, set any required environment
variables before the first deployment, and then deploy while watching the logs for the
first sixty seconds.

**Quoted as support.**

- `DOC-ONB-001` — "Create a project, then a service within it. Resources belong to services and services belong to projects."
- `DOC-ONB-001` — "Connect a repository or push a container image. The build service detects common project layouts automatically."
- `DOC-ONB-001` — "Set any environment variables the application needs before the first deployment rather than after it."
- `DOC-ONB-001` — "Deploy, then watch the logs for the first sixty seconds. Most first-deployment problems are visible immediately in startup output."

**Source: DOC-ONB-001 — First deployment: a walkthrough**

> # First deployment: a walkthrough  **Applies to:** All plans  ## Symptoms  - A new
> user does not know where to begin - The first deployment fails for unclear reasons  ##
> Common causes  - Required configuration has not been set - The project structure does
> not match what the build expects  ## Resolution  1. Create a project, then a service
> within it. Resources belong to services and services belong to projects. 2. Connect a
> repository or push a container image. The build service detects common project layouts
> automatically. 3. Set any environment variables the application needs before the first
> deployment rather than after it. 4. Deploy, then watch the logs for the first sixty
> seconds. Most first-deployment problems are visible immediately in startup output.  ##
> Notes  The free tier includes one service and is sufficient for evaluating the
> platform.

verdict: UNSCORED

note:

---

## 23. VAL-0037

**Ticket.** Question about backup regions

Are backups replicated outside our primary region? A compliance review has raised this
and I need a definite answer.

**Reply sent.**

Yes, backups are replicated outside the primary region by default.

**Quoted as support.**

- `DOC-DATA-003` — "cross-region replication is enabled by default."

**Source: DOC-DATA-003 — Data residency and regional storage**

> # Data residency and regional storage  **Applies to:** Business and Enterprise plans
> ## Symptoms  - A customer requires data to remain in a specific region - Latency is
> high for users far from the primary region - A compliance review has asked where data
> is held  ## Common causes  - The organisation was created in a region that no longer
> suits the requirement - Read traffic is being served from the primary region only -
> Backups are replicated to a second region by default  ## Resolution  1. Check the
> region shown on the organisation settings page. This is fixed at creation and
> determines where primary data is stored. 2. Enable read replicas in additional regions
> to reduce latency for distant users without moving primary storage. 3. Review the
> backup replication setting if a single-region requirement applies, since cross-region
> replication is enabled by default. 4. Migrating an organisation between regions
> requires a planned migration with support and involves a maintenance window.  ## Notes
> Metadata such as account names and billing records is stored centrally regardless of
> the data region.

verdict: UNSCORED

note:

---

## 24. VAL-0039

**Ticket.** API key returning 401

One of our engineers pushed a key to a public repository by mistake. We need to replace
it without taking the service down. What is the correct order of operations?

**Reply sent.**

Create a replacement key, deploy it, confirm traffic has moved, then revoke the old key.

**Quoted as support.**

- `DOC-AUTH-004` — "To rotate without downtime, create the replacement key first, deploy it, confirm traffic has moved, then revoke the old key."

**Source: DOC-AUTH-004 — API key rotation and scope management**

> # API key rotation and scope management  **Applies to:** All plans  ## Symptoms  - A
> previously working key returns 401 Unauthorized - A key works for some endpoints and
> not others - A key needs replacing after accidental exposure  ## Common causes  - The
> key was revoked or reached its configured expiry - The key was issued with a scope
> that excludes the endpoint being called - The key belongs to a deleted user and was
> removed with the account  ## Resolution  1. Check the API keys page for the key's
> status and expiry. Revoked and expired keys are listed with the date and the user who
> acted. 2. Review the scopes attached to the key. Read-only keys cannot write, and
> project-scoped keys cannot reach organisation endpoints. 3. To rotate without
> downtime, create the replacement key first, deploy it, confirm traffic has moved, then
> revoke the old key. 4. If a key has been exposed publicly, revoke it immediately
> rather than waiting for the rotation window.  ## Notes  Keys issued to individual
> users are removed when that user is deleted. Use service accounts for anything running
> in production.

verdict: UNSCORED

note:

---

## 25. VAL-0040

**Ticket.** Question about this month's charges

There are charges on our invoice for a service I do not believe we use. Could you
explain what these relate to?

**Reply sent.**

The invoice may include charges for a service that was left running in a non‑production
environment, which can appear even if you believe the service is not in use.

**Quoted as support.**

- `DOC-BILL-001` — "Charges appear for a service that is not in use"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 26. VAL-0041

**Ticket.** Question about this month's charges

There are charges on our invoice for a service I do not believe we use. Could you
explain what these relate to?

**Reply sent.**

The invoice may include charges for a service that was left running in a non‑production
environment, which can appear even if you believe the service is not in use.

**Quoted as support.**

- `DOC-BILL-001` — "Charges appear for a service that is not in use"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 27. VAL-0042

**Ticket.** (no subject)

Our staging environment is picking up production configuration values. I cannot work out
where the override is coming from.

**Reply sent.**

The staging environment is likely picking up a configuration override that is not
visible on the main settings page.

**Quoted as support.**

- `DOC-DEPLOY-004` — "An environment override exists that is not visible on the main settings page"

**Source: DOC-DEPLOY-004 — Configuring environment variables and secrets**

> # Configuring environment variables and secrets  **Applies to:** All compute services
> ## Symptoms  - The application cannot read a variable that appears to be set - A
> secret value appears in plain text in the logs - Configuration differs between
> environments unexpectedly  ## Common causes  - The variable was set at project scope
> but read at service scope - The application logs its configuration at startup - An
> environment override exists that is not visible on the main settings page  ##
> Resolution  1. Check the scope at which the variable was defined. Service scope
> overrides project scope, and project scope overrides organisation defaults. 2. Store
> anything sensitive as a secret rather than a variable. Secrets are masked in logs and
> are not readable through the API after creation. 3. Review the environment overrides
> page, which lists values that differ from the defaults for each environment. 4.
> Redeploy after changing configuration. Running containers do not pick up new values
> without a restart.  ## Notes  A secret that has been printed to logs should be treated
> as exposed and rotated, even if the logs are private.

verdict: UNSCORED

note:

---

## 28. VAL-0044

**Ticket.** (no subject)

There are charges on our invoice for a service I do not believe we use. Could you
explain what these relate to?

**Reply sent.**

The invoice may include charges for a service that was left running in a non‑production
environment, which can appear even if you believe the service is not in use.

**Quoted as support.**

- `DOC-BILL-001` — "Charges appear for a service that is not in use"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 29. VAL-0045

**Ticket.** Export missing recent records

I started an export over the weekend and it is still showing as queued. It covers about
two million records. Should I cancel and try again?

**Reply sent.**

Large exports are queued and processed asynchronously, so you should wait for the job to
complete rather than canceling and retrying immediately.

**Quoted as support.**

- `DOC-DATA-001` — "Large exports are queued and processed asynchronously"

**Source: DOC-DATA-001 — Exporting account data and scheduled extracts**

> # Exporting account data and scheduled extracts  **Applies to:** All plans  ##
> Symptoms  - An export has not completed - The download link has expired - The export
> is missing recent records  ## Common causes  - Large exports are queued and processed
> asynchronously - Download links are valid for twenty-four hours - The export captured
> a snapshot taken when the job started  ## Resolution  1. Check the exports page for
> job status. Jobs covering more than a million records commonly take several minutes.
> 2. Request a fresh link from the exports page if the original has expired. The
> underlying file is retained for seven days. 3. Note that the export reflects the
> moment the job began, so records created during processing are not included. 4. For
> recurring needs, configure a scheduled export delivered to object storage rather than
> generating them manually.  ## Notes  Exports containing personal data are logged in
> the audit trail with the requesting user and the fields included.

verdict: UNSCORED

note:

---

## 30. VAL-0046

**Ticket.** How do I page through large results

when i do pagination some record coming two time and some missing. what is correct way?

**Reply sent.**

To avoid duplicate or missing records when paging large result sets, use cursor‑based
pagination, pass the cursor from the previous response to the next request, avoid offset
pagination on a changing collection, and keep the page size within the maximum allowed.

**Quoted as support.**

- `DOC-API-002` — "The cursor from the previous response was not passed to the next request"
- `DOC-API-002` — "Offset pagination was used against a changing collection"
- `DOC-API-002` — "The page size requested exceeds the maximum"

**Source: DOC-API-002 — Pagination and handling large result sets**

> # Pagination and handling large result sets  **Applies to:** All plans  ## Symptoms  -
> Only the first page of results is returned - Iterating through results misses or
> duplicates records - Large queries time out  ## Common causes  - The cursor from the
> previous response was not passed to the next request - Offset pagination was used
> against a changing collection - The page size requested exceeds the maximum  ##
> Resolution  1. Use cursor pagination for anything that may change while you iterate.
> Offset pagination will skip or repeat records when items are inserted mid-iteration.
> 2. Pass the next_cursor value from each response as the cursor parameter of the
> following request, and stop when it is null. 3. Keep page size at or below two
> hundred. Larger requests are rejected rather than truncated. 4. For very large
> extracts, use the export endpoint, which runs asynchronously and returns a download
> link.  ## Notes  Cursors expire after one hour. Long-running iterations should handle
> expiry by restarting from a recorded checkpoint.

verdict: UNSCORED

note:

---

## 31. VAL-0047

**Ticket.** (no subject)

Are the search endpoints limited differently from the rest? Our read traffic is fine but
search is being rejected constantly.

**Reply sent.**

Yes, the search endpoints can have a lower limit than the general API rate limits, which
may cause them to be rejected while other endpoints remain within limits.

**Quoted as support.**

- `DOC-API-001` — "The endpoint being called has a lower limit than the general one"

**Source: DOC-API-001 — Understanding API rate limits and quota tiers**

> # Understanding API rate limits and quota tiers  **Applies to:** All plans  ##
> Symptoms  - Requests return 429 Too Many Requests - Throughput drops sharply at a
> predictable point - Limits appear lower than the documented figure  ## Common causes
> - The limit applies per organisation rather than per key - Burst capacity was consumed
> and the sustained rate now applies - The endpoint being called has a lower limit than
> the general one  ## Resolution  1. Read the rate limit headers returned with every
> response. They give the limit, the remaining allowance and the reset time, which is
> more reliable than inferring the limit from behaviour. 2. Confirm whether the endpoint
> has a specific limit. Search and export endpoints are more expensive and are limited
> more tightly than reads. 3. Implement exponential backoff with jitter on 429 responses
> rather than retrying immediately, which prolongs the throttling. 4. Where sustained
> higher throughput is genuinely required, the limit can be raised on Business and
> Enterprise plans through an account request.  ## Notes  Limits are enforced per
> organisation. Issuing more keys does not increase the available quota.

verdict: UNSCORED

note:

---

## 32. VAL-0049

**Ticket.** Need to rotate an exposed key

key can read fine but every write returns permission error. I created it myself and I
thought I gave it full access. please help fast.

**Reply sent.**

The key you created is likely missing write scopes; review the scopes attached to the
key and ensure it has the necessary write permissions before attempting to rotate it.

**Quoted as support.**

- `DOC-AUTH-004` — "Review the scopes attached to the key. Read-only keys cannot write"

**Source: DOC-AUTH-004 — API key rotation and scope management**

> # API key rotation and scope management  **Applies to:** All plans  ## Symptoms  - A
> previously working key returns 401 Unauthorized - A key works for some endpoints and
> not others - A key needs replacing after accidental exposure  ## Common causes  - The
> key was revoked or reached its configured expiry - The key was issued with a scope
> that excludes the endpoint being called - The key belongs to a deleted user and was
> removed with the account  ## Resolution  1. Check the API keys page for the key's
> status and expiry. Revoked and expired keys are listed with the date and the user who
> acted. 2. Review the scopes attached to the key. Read-only keys cannot write, and
> project-scoped keys cannot reach organisation endpoints. 3. To rotate without
> downtime, create the replacement key first, deploy it, confirm traffic has moved, then
> revoke the old key. 4. If a key has been exposed publicly, revoke it immediately
> rather than waiting for the rotation window.  ## Notes  Keys issued to individual
> users are removed when that user is deleted. Use service accounts for anything running
> in production.

verdict: UNSCORED

note:

---

## 33. VAL-0050

**Ticket.** Getting started with first deployment

We have just signed up and I am not sure where to start. We have a containerised
application and would like to get it deployed.

**Reply sent.**

To get started with your first deployment, create a project and a service, connect your
container image, set any required environment variables before the first deployment,
then deploy and watch the logs for the first sixty seconds.

**Quoted as support.**

- `DOC-ONB-001` — "Create a project, then a service within it. Resources belong to services and services belong to projects."
- `DOC-ONB-001` — "Connect a repository or push a container image. The build service detects common project layouts automatically."
- `DOC-ONB-001` — "Set any environment variables the application needs before the first deployment rather than after it."
- `DOC-ONB-001` — "Deploy, then watch the logs for the first sixty seconds. Most first-deployment problems are visible immediately in startup output."

**Source: DOC-ONB-001 — First deployment: a walkthrough**

> # First deployment: a walkthrough  **Applies to:** All plans  ## Symptoms  - A new
> user does not know where to begin - The first deployment fails for unclear reasons  ##
> Common causes  - Required configuration has not been set - The project structure does
> not match what the build expects  ## Resolution  1. Create a project, then a service
> within it. Resources belong to services and services belong to projects. 2. Connect a
> repository or push a container image. The build service detects common project layouts
> automatically. 3. Set any environment variables the application needs before the first
> deployment rather than after it. 4. Deploy, then watch the logs for the first sixty
> seconds. Most first-deployment problems are visible immediately in startup output.  ##
> Notes  The free tier includes one service and is sufficient for evaluating the
> platform.

verdict: UNSCORED

note:

---

## 34. VAL-0051

**Ticket.** Log forwarding stopped working

log forwarding to our external system stop two days ago and not resumed by itself.
destination is healthy as we know. kindly check and revert.

**Reply sent.**

Log forwarding pauses after one hour of consecutive failures and must be resumed
manually once the destination is healthy.

**Quoted as support.**

- `DOC-INT-002` — "Forwarding pauses after one hour of consecutive failures and must be resumed manually once the destination is healthy."

**Source: DOC-INT-002 — Third party monitoring and log forwarding**

> # Third party monitoring and log forwarding  **Applies to:** Business and Enterprise
> plans  ## Symptoms  - Logs are not arriving at the external destination - Metrics are
> delayed compared with the console - Forwarded volume is higher than expected  ##
> Common causes  - The destination rejected the payload and forwarding paused -
> Aggregation introduces a delay before metrics are forwarded - Debug-level logs are
> being forwarded along with the rest  ## Resolution  1. Check the forwarding status
> page, which shows the last successful delivery and any error returned by the
> destination. 2. Expect a delay of up to two minutes on metrics, since they are
> aggregated before being sent. 3. Apply a level filter at source so that debug output
> is not forwarded, which is usually the reason volume is higher than expected. 4.
> Verify the destination credential separately if delivery has stopped entirely, as
> expired credentials are the most common cause.  ## Notes  Forwarding pauses after one
> hour of consecutive failures and must be resumed manually once the destination is
> healthy.

verdict: UNSCORED

note:

---

## 35. VAL-0052

**Ticket.** (no subject)

Since late last night I cannot get into the console at all. My colleague on the same
team signs in without any trouble, so it does not appear to be a general outage. Could
you check whether something is wrong with my account specifically?

**Reply sent.**

The console is likely returning an 'Invalid credentials' error because a stale session
cookie is being sent alongside new credentials or the account is locked after five
consecutive failed attempts. Please clear your browser cookies for the console, ensure
you are using the most recent password, and if the issue persists, try logging in from a
different browser or device.

**Quoted as support.**

- `DOC-AUTH-001` — "The console returns 'Invalid credentials' despite a correct password"
- `DOC-AUTH-001` — "A stale session cookie is being sent alongside new credentials"
- `DOC-AUTH-001` — "The account is locked after five consecutive failed attempts"

**Source: DOC-AUTH-001 — Resolving invalid credential errors on login**

> # Resolving invalid credential errors on login  **Applies to:** Console, CLI, SDK  ##
> Symptoms  - The console returns 'Invalid credentials' despite a correct password -
> Login succeeds in one browser but fails in another - The CLI reports authentication
> failure after a working period  ## Common causes  - The account is locked after five
> consecutive failed attempts - A stale session cookie is being sent alongside new
> credentials - The password was changed in another session and the client cached the
> old one  ## Resolution  1. Confirm whether the account is locked by checking the
> security page of the console. A locked account displays a red banner and unlocks
> automatically after thirty minutes. 2. Clear cookies for the CloudServe domain, or
> open a private browsing window, then attempt the login again. 3. If the CLI is
> failing, run `cloudserve auth logout` followed by `cloudserve auth login` to discard
> the cached token. 4. Where the account remains locked and the customer needs immediate
> access, an administrator on the account can release the lock from the team members
> page.  ## Notes  Repeated lockouts within a short period usually indicate an automated
> process still using an old password rather than a user error.

verdict: UNSCORED

note:

---

## 36. VAL-0053

**Ticket.** (no subject)

There are charges on our invoice for a service I do not believe we use. Could you
explain what these relate to?

**Reply sent.**

The invoice may include charges for a service that was left running in a non‑production
environment, which can appear even if you believe the service is not in use.

**Quoted as support.**

- `DOC-BILL-001` — "Charges appear for a service that is not in use"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 37. VAL-0054

**Ticket.** Where is our data stored

One of our customers has asked for written confirmation of where their data is
physically stored. Could you point me to something I can share with them?

**Reply sent.**

The data is stored in the region where your organisation was created, and backups are
replicated to a second region by default.

**Quoted as support.**

- `DOC-DATA-003` — "The organisation was created in a region that no longer suits the requirement"

**Source: DOC-DATA-003 — Data residency and regional storage**

> # Data residency and regional storage  **Applies to:** Business and Enterprise plans
> ## Symptoms  - A customer requires data to remain in a specific region - Latency is
> high for users far from the primary region - A compliance review has asked where data
> is held  ## Common causes  - The organisation was created in a region that no longer
> suits the requirement - Read traffic is being served from the primary region only -
> Backups are replicated to a second region by default  ## Resolution  1. Check the
> region shown on the organisation settings page. This is fixed at creation and
> determines where primary data is stored. 2. Enable read replicas in additional regions
> to reduce latency for distant users without moving primary storage. 3. Review the
> backup replication setting if a single-region requirement applies, since cross-region
> replication is enabled by default. 4. Migrating an organisation between regions
> requires a planned migration with support and involves a maintenance window.  ## Notes
> Metadata such as account names and billing records is stored centrally regardless of
> the data region.

verdict: UNSCORED

note:

---

## 38. VAL-0056

**Ticket.** Build fails in the pipeline

Every deployment fails at the health check stage. I have increased the timeout twice
already and it makes no difference.

**Reply sent.**

The deployment is rolling back because the health check is timing out; check that the
health endpoint responds quickly, that the container listens on the declared port, and
that all required environment variables are set in the deployed environment.

**Quoted as support.**

- `DOC-DEPLOY-001` — "The health endpoint takes longer to respond than the configured timeout"
- `DOC-DEPLOY-001` — "The container listens on a different port than the service declares"
- `DOC-DEPLOY-001` — "A required environment variable is absent in the deployed environment"

**Source: DOC-DEPLOY-001 — Container deployments failing during the health check phase**

> # Container deployments failing during the health check phase  **Applies to:**
> Container Service  ## Symptoms  - The deployment reaches running and then rolls back -
> Logs show repeated health check timeouts - The service works locally but not when
> deployed  ## Common causes  - The health endpoint takes longer to respond than the
> configured timeout - The container listens on a different port than the service
> declares - A required environment variable is absent in the deployed environment  ##
> Resolution  1. Confirm the container is listening on the port declared in the service
> definition. A mismatch here produces a health check failure that looks like a timeout.
> 2. Increase the initial delay if the application needs time to warm up before it can
> answer. Thirty seconds is a reasonable starting point for services that load models or
> caches. 3. Compare the environment variables present in the deployment against those
> the application requires. Missing configuration frequently causes a silent startup
> failure. 4. Inspect the container logs from the failed revision rather than the
> running one; the rollback replaces the logs shown by default.  ## Notes  A health
> check must return within the timeout using only local state. Endpoints that call a
> database will fail during a database incident and take the service down with them.

verdict: UNSCORED

note:

---

## 39. VAL-0057

**Ticket.** Deployment rolls back every time

Our deployment reaches running and then rolls back after about a minute. The logs
mention a health check timeout. It runs perfectly on my machine and in staging.

**Reply sent.**

The deployment is rolling back because the health check is timing out, likely due to the
health endpoint taking longer to respond than the configured timeout.

**Quoted as support.**

- `DOC-DEPLOY-001` — "Logs show repeated health check timeouts"

**Source: DOC-DEPLOY-001 — Container deployments failing during the health check phase**

> # Container deployments failing during the health check phase  **Applies to:**
> Container Service  ## Symptoms  - The deployment reaches running and then rolls back -
> Logs show repeated health check timeouts - The service works locally but not when
> deployed  ## Common causes  - The health endpoint takes longer to respond than the
> configured timeout - The container listens on a different port than the service
> declares - A required environment variable is absent in the deployed environment  ##
> Resolution  1. Confirm the container is listening on the port declared in the service
> definition. A mismatch here produces a health check failure that looks like a timeout.
> 2. Increase the initial delay if the application needs time to warm up before it can
> answer. Thirty seconds is a reasonable starting point for services that load models or
> caches. 3. Compare the environment variables present in the deployment against those
> the application requires. Missing configuration frequently causes a silent startup
> failure. 4. Inspect the container logs from the failed revision rather than the
> running one; the rollback replaces the logs shown by default.  ## Notes  A health
> check must return within the timeout using only local state. Endpoints that call a
> database will fail during a database incident and take the service down with them.

verdict: UNSCORED

note:

---

## 40. VAL-0058

**Ticket.** Need to rotate an exposed key

one of our production keys start returning 401 at around last Friday without any change
on our side. Other keys against same account still working. waiting for your reply.

**Reply sent.**

The key has likely been revoked or expired, so you should revoke all keys for the
account and issue a new key with the correct scope.

**Quoted as support.**

- `DOC-AUTH-004` — "The key was revoked or reached its configured expiry"

**Source: DOC-AUTH-004 — API key rotation and scope management**

> # API key rotation and scope management  **Applies to:** All plans  ## Symptoms  - A
> previously working key returns 401 Unauthorized - A key works for some endpoints and
> not others - A key needs replacing after accidental exposure  ## Common causes  - The
> key was revoked or reached its configured expiry - The key was issued with a scope
> that excludes the endpoint being called - The key belongs to a deleted user and was
> removed with the account  ## Resolution  1. Check the API keys page for the key's
> status and expiry. Revoked and expired keys are listed with the date and the user who
> acted. 2. Review the scopes attached to the key. Read-only keys cannot write, and
> project-scoped keys cannot reach organisation endpoints. 3. To rotate without
> downtime, create the replacement key first, deploy it, confirm traffic has moved, then
> revoke the old key. 4. If a key has been exposed publicly, revoke it immediately
> rather than waiting for the rotation window.  ## Notes  Keys issued to individual
> users are removed when that user is deleted. Use service accounts for anything running
> in production.

verdict: UNSCORED

note:

---

## 41. VAL-0059

**Ticket.** Config differs between environments

Where should secrets be stored so they do not appear in the logs? At the moment ours are
being printed at startup and I am not comfortable with that.

**Reply sent.**

Store sensitive values as secrets rather than environment variables so they are masked
in logs and not readable through the API after creation.

**Quoted as support.**

- `DOC-DEPLOY-004` — "Store anything sensitive as a secret rather than a variable. Secrets are masked in logs and are not readable through the API after creation."

**Source: DOC-DEPLOY-004 — Configuring environment variables and secrets**

> # Configuring environment variables and secrets  **Applies to:** All compute services
> ## Symptoms  - The application cannot read a variable that appears to be set - A
> secret value appears in plain text in the logs - Configuration differs between
> environments unexpectedly  ## Common causes  - The variable was set at project scope
> but read at service scope - The application logs its configuration at startup - An
> environment override exists that is not visible on the main settings page  ##
> Resolution  1. Check the scope at which the variable was defined. Service scope
> overrides project scope, and project scope overrides organisation defaults. 2. Store
> anything sensitive as a secret rather than a variable. Secrets are masked in logs and
> are not readable through the API after creation. 3. Review the environment overrides
> page, which lists values that differ from the defaults for each environment. 4.
> Redeploy after changing configuration. Running containers do not pick up new values
> without a restart.  ## Notes  A secret that has been printed to logs should be treated
> as exposed and rotated, even if the logs are private.

verdict: UNSCORED

note:

---

## 42. VAL-0060

**Ticket.** Webhooks not arriving

Signature verification fails for every delivery. We are computing the signature exactly
as the documentation describes, over the parsed body.

**Reply sent.**

Signature verification fails because the signature was computed over a parsed body
rather than the raw bytes.

**Quoted as support.**

- `DOC-API-003` — "The signature was computed over a parsed body rather than the raw bytes"

**Source: DOC-API-003 — Webhook delivery, retries and signature verification**

> # Webhook delivery, retries and signature verification  **Applies to:** All plans  ##
> Symptoms  - Webhooks are not arriving at the configured endpoint - The same event is
> delivered more than once - Signature verification fails  ## Common causes  - The
> endpoint returned a non-2xx status and delivery is being retried - The endpoint
> responded too slowly and the delivery timed out - The signature was computed over a
> parsed body rather than the raw bytes  ## Resolution  1. Check the webhook delivery
> log, which records every attempt with the response status and body for the last seven
> days. 2. Return 2xx as quickly as possible and process the event asynchronously.
> Deliveries time out after five seconds. 3. Compute the signature over the raw request
> body before any parsing. Re-serialising JSON changes the bytes and invalidates the
> signature. 4. Make your handler idempotent using the event identifier. At-least-once
> delivery means duplicates are expected rather than exceptional.  ## Notes  Failed
> deliveries are retried with backoff for twenty-four hours, after which the endpoint is
> disabled and the account is notified.

verdict: UNSCORED

note:

---

## 43. VAL-0061

**Ticket.** Webhooks not arriving

Signature verification fails for every delivery. We are computing the signature exactly
as the documentation describes, over the parsed body.

**Reply sent.**

Signature verification fails because the signature was computed over a parsed body
rather than the raw bytes.

**Quoted as support.**

- `DOC-API-003` — "The signature was computed over a parsed body rather than the raw bytes"

**Source: DOC-API-003 — Webhook delivery, retries and signature verification**

> # Webhook delivery, retries and signature verification  **Applies to:** All plans  ##
> Symptoms  - Webhooks are not arriving at the configured endpoint - The same event is
> delivered more than once - Signature verification fails  ## Common causes  - The
> endpoint returned a non-2xx status and delivery is being retried - The endpoint
> responded too slowly and the delivery timed out - The signature was computed over a
> parsed body rather than the raw bytes  ## Resolution  1. Check the webhook delivery
> log, which records every attempt with the response status and body for the last seven
> days. 2. Return 2xx as quickly as possible and process the event asynchronously.
> Deliveries time out after five seconds. 3. Compute the signature over the raw request
> body before any parsing. Re-serialising JSON changes the bytes and invalidates the
> signature. 4. Make your handler idempotent using the event identifier. At-least-once
> delivery means duplicates are expected rather than exceptional.  ## Notes  Failed
> deliveries are retried with backoff for twenty-four hours, after which the endpoint is
> disabled and the account is notified.

verdict: UNSCORED

note:

---

## 44. VAL-0062

**Ticket.** Connecting our CI pipeline

log forwarding to our external system stop over weekend and not resumed by itself.
destination healthy as we know.

**Reply sent.**

The log forwarding has paused after an hour of consecutive failures and must be resumed
manually once the destination is healthy.

**Quoted as support.**

- `DOC-INT-002` — "Forwarding pauses after one hour of consecutive failures and must be resumed manually once the destination is healthy."

**Source: DOC-INT-002 — Third party monitoring and log forwarding**

> # Third party monitoring and log forwarding  **Applies to:** Business and Enterprise
> plans  ## Symptoms  - Logs are not arriving at the external destination - Metrics are
> delayed compared with the console - Forwarded volume is higher than expected  ##
> Common causes  - The destination rejected the payload and forwarding paused -
> Aggregation introduces a delay before metrics are forwarded - Debug-level logs are
> being forwarded along with the rest  ## Resolution  1. Check the forwarding status
> page, which shows the last successful delivery and any error returned by the
> destination. 2. Expect a delay of up to two minutes on metrics, since they are
> aggregated before being sent. 3. Apply a level filter at source so that debug output
> is not forwarded, which is usually the reason volume is higher than expected. 4.
> Verify the destination credential separately if delivery has stopped entirely, as
> expired credentials are the most common cause.  ## Notes  Forwarding pauses after one
> hour of consecutive failures and must be resumed manually once the destination is
> healthy.

verdict: UNSCORED

note:

---

## 45. VAL-0063

**Ticket.** Permission changes not taking effect

One of our developers cannot see a project she should have access to. I have granted her
the role twice and it does not seem to take effect.

**Reply sent.**

The issue is likely because the role was granted at the project scope rather than the
organisation scope, which can prevent the user from accessing the project.

**Quoted as support.**

- `DOC-ACCT-001` — "The role was granted at project scope rather than organisation scope"

**Source: DOC-ACCT-001 — Managing team members, roles and permissions**

> # Managing team members, roles and permissions  **Applies to:** All plans  ## Symptoms
> - A user cannot access a project they should be able to - A departing user needs
> removing - Permissions need narrowing after a review  ## Common causes  - The role was
> granted at project scope rather than organisation scope - The invitation was never
> accepted and the account does not exist - A group membership grants broader access
> than the direct role suggests  ## Resolution  1. Check the effective permissions view
> for the user, which resolves direct roles and group memberships together. 2. Confirm
> the invitation was accepted. Pending invitations appear in a separate section and
> expire after seven days. 3. Remove a departing user rather than only changing their
> password, and revoke any API keys they created. 4. Prefer group membership to direct
> role assignment, so that access can be reviewed in one place.  ## Notes  Removing the
> last account owner is not permitted. Transfer ownership before removing the account.

verdict: UNSCORED

note:

---

## 46. VAL-0064

**Ticket.** (no subject)

What is the right way to pull a very large extract? Requesting a big page size gets
rejected and iterating page by page takes hours.

**Reply sent.**

Use the export endpoint, which runs asynchronously and returns a download link for very
large extracts.

**Quoted as support.**

- `DOC-API-002` — "For very large extracts, use the export endpoint, which runs asynchronously and returns a download link."
- `DOC-DATA-001` — "Large exports are queued and processed asynchronously"

**Source: DOC-API-002 — Pagination and handling large result sets**

> # Pagination and handling large result sets  **Applies to:** All plans  ## Symptoms  -
> Only the first page of results is returned - Iterating through results misses or
> duplicates records - Large queries time out  ## Common causes  - The cursor from the
> previous response was not passed to the next request - Offset pagination was used
> against a changing collection - The page size requested exceeds the maximum  ##
> Resolution  1. Use cursor pagination for anything that may change while you iterate.
> Offset pagination will skip or repeat records when items are inserted mid-iteration.
> 2. Pass the next_cursor value from each response as the cursor parameter of the
> following request, and stop when it is null. 3. Keep page size at or below two
> hundred. Larger requests are rejected rather than truncated. 4. For very large
> extracts, use the export endpoint, which runs asynchronously and returns a download
> link.  ## Notes  Cursors expire after one hour. Long-running iterations should handle
> expiry by restarting from a recorded checkpoint.

**Source: DOC-DATA-001 — Exporting account data and scheduled extracts**

> # Exporting account data and scheduled extracts  **Applies to:** All plans  ##
> Symptoms  - An export has not completed - The download link has expired - The export
> is missing recent records  ## Common causes  - Large exports are queued and processed
> asynchronously - Download links are valid for twenty-four hours - The export captured
> a snapshot taken when the job started  ## Resolution  1. Check the exports page for
> job status. Jobs covering more than a million records commonly take several minutes.
> 2. Request a fresh link from the exports page if the original has expired. The
> underlying file is retained for seven days. 3. Note that the export reflects the
> moment the job began, so records created during processing are not included. 4. For
> recurring needs, configure a scheduled export delivered to object storage rather than
> generating them manually.  ## Notes  Exports containing personal data are logged in
> the audit trail with the requesting user and the fields included.

verdict: UNSCORED

note:

---

## 47. VAL-0065

**Ticket.** Billing period dates unclear

There are charges on our invoice for a service I do not believe we use. Could you
explain what these relate to?

**Reply sent.**

The invoice shows charges for a service that may have been used beyond the plan
allowance or a resource left running in a non‑production environment, which are common
causes for unexpected charges.

**Quoted as support.**

- `DOC-BILL-001` — "Charges appear for a service that is not in use"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 48. VAL-0066

**Ticket.** Question about backup regions

one of our customers has asked for written confirmation of where their data is
physically stored. Can you please point me to something I can share with them? sorry for
my english.

**Reply sent.**

The primary data for an organisation is stored in the region shown on the organisation
settings page, which is fixed at creation.

**Quoted as support.**

- `DOC-DATA-003` — "Check the region shown on the organisation settings page. This is fixed at creation and determines where primary data is stored."

**Source: DOC-DATA-003 — Data residency and regional storage**

> # Data residency and regional storage  **Applies to:** Business and Enterprise plans
> ## Symptoms  - A customer requires data to remain in a specific region - Latency is
> high for users far from the primary region - A compliance review has asked where data
> is held  ## Common causes  - The organisation was created in a region that no longer
> suits the requirement - Read traffic is being served from the primary region only -
> Backups are replicated to a second region by default  ## Resolution  1. Check the
> region shown on the organisation settings page. This is fixed at creation and
> determines where primary data is stored. 2. Enable read replicas in additional regions
> to reduce latency for distant users without moving primary storage. 3. Review the
> backup replication setting if a single-region requirement applies, since cross-region
> replication is enabled by default. 4. Migrating an organisation between regions
> requires a planned migration with support and involves a maintenance window.  ## Notes
> Metadata such as account names and billing records is stored centrally regardless of
> the data region.

verdict: UNSCORED

note:

---

## 49. VAL-0069

**Ticket.** (no subject)

Our staging environment is picking up production configuration values. I cannot work out
where the override is coming from.

**Reply sent.**

The staging environment is likely picking up a configuration override that is not
visible on the main settings page.

**Quoted as support.**

- `DOC-DEPLOY-004` — "An environment override exists that is not visible on the main settings page"

**Source: DOC-DEPLOY-004 — Configuring environment variables and secrets**

> # Configuring environment variables and secrets  **Applies to:** All compute services
> ## Symptoms  - The application cannot read a variable that appears to be set - A
> secret value appears in plain text in the logs - Configuration differs between
> environments unexpectedly  ## Common causes  - The variable was set at project scope
> but read at service scope - The application logs its configuration at startup - An
> environment override exists that is not visible on the main settings page  ##
> Resolution  1. Check the scope at which the variable was defined. Service scope
> overrides project scope, and project scope overrides organisation defaults. 2. Store
> anything sensitive as a secret rather than a variable. Secrets are masked in logs and
> are not readable through the API after creation. 3. Review the environment overrides
> page, which lists values that differ from the defaults for each environment. 4.
> Redeploy after changing configuration. Running containers do not pick up new values
> without a restart.  ## Notes  A secret that has been printed to logs should be treated
> as exposed and rotated, even if the logs are private.

verdict: UNSCORED

note:

---

## 50. VAL-0070

**Ticket.** SSO works for some users only

Single sign-on works for our engineering group but the finance group gets an error. Both
are configured identically as far as we can tell. Any idea what differs?

**Reply sent.**

Check that the assertion consumer service URL and the NameID in the SAML assertion match
exactly for the finance group, and ensure just‑in‑time provisioning and default roles
are correctly set for new users.

**Quoted as support.**

- `DOC-AUTH-003` — "Compare the assertion consumer service URL in your identity provider against the value shown on the SSO settings page. They must match exactly, including the trailing path."
- `DOC-AUTH-003` — "Inspect a failing assertion and confirm the NameID is the user's email address in lower case."
- `DOC-AUTH-003` — "Enable just-in-time provisioning if new users should be created on first login, and set a default role for provisioned users."

**Source: DOC-AUTH-003 — Single sign-on configuration with SAML providers**

> # Single sign-on configuration with SAML providers  **Applies to:** Business and
> Enterprise plans  ## Symptoms  - Users are redirected to the identity provider and
> returned to an error page - SSO works for some users and not others - New users are
> not provisioned automatically  ## Common causes  - The assertion consumer service URL
> does not match the value registered with CloudServe - The email attribute in the
> assertion does not match the CloudServe account email - Just-in-time provisioning is
> disabled on the connection  ## Resolution  1. Compare the assertion consumer service
> URL in your identity provider against the value shown on the SSO settings page. They
> must match exactly, including the trailing path. 2. Inspect a failing assertion and
> confirm the NameID is the user's email address in lower case. 3. Enable just-in-time
> provisioning if new users should be created on first login, and set a default role for
> provisioned users. 4. Keep at least one administrator account with password access
> while testing, so a misconfiguration does not lock the whole organisation out.  ##
> Notes  SAML changes take effect immediately for new sessions but existing sessions
> remain valid until they expire.

verdict: UNSCORED

note:

---

## 51. VAL-0071

**Ticket.** Spend cap stopped our service

We were throttled over the weekend after a traffic increase and it took down part of our
product. We would rather pay overage than be stopped. How do we change that?

**Reply sent.**

To avoid the service being stopped, you can switch from a hard spend cap to overage on
the billing page, which will allow the service to continue at the listed rate during
traffic spikes.

**Quoted as support.**

- `DOC-BILL-003` — "Decide deliberately between a hard spend cap, which stops the service, and overage, which continues at the listed rate."

**Source: DOC-BILL-003 — Usage limits, overage and spend controls**

> # Usage limits, overage and spend controls  **Applies to:** All plans  ## Symptoms  -
> Service was throttled after a traffic increase - Overage charges appeared unexpectedly
> - A spend cap stopped a production workload  ## Common causes  - Plan allowance was
> consumed before the end of the period - A spend cap was configured and reached -
> Overage protection is disabled, so usage continued beyond the allowance  ## Resolution
> 1. Check the current period usage against the plan allowance on the billing page. 2.
> Decide deliberately between a hard spend cap, which stops the service, and overage,
> which continues at the listed rate. Production workloads generally need the second. 3.
> Configure alerts at fifty, eighty and ninety-five per cent of allowance rather than
> relying on the cap as a warning. 4. Where a cap has stopped a production service, an
> account owner can raise it immediately from the billing page and service resumes
> within a minute.  ## Notes  Spend caps apply per organisation and cannot currently be
> set per project.

verdict: UNSCORED

note:

---

## 52. VAL-0072

**Ticket.** Invoice higher than expected

There are charges on our invoice for a service I do not believe we use. Could you
explain what these relate to?

**Reply sent.**

The invoice may include usage-based charges for a service that was left running or for
usage beyond the plan allowance, which can appear as unexpected charges.

**Quoted as support.**

- `DOC-BILL-001` — "Charges appear for a service that is not in use"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 53. VAL-0073

**Ticket.** Invoice higher than expected

bill is very high this month. i not understand the charge. please explain what is this.

**Reply sent.**

The higher invoice may be due to usage-based charges beyond the plan allowance, a
resource left running in a non-production environment, or the billing period starting
from the subscription date rather than the first of the month.

**Quoted as support.**

- `DOC-BILL-001` — "Usage-based charges accrued beyond the plan allowance"
- `DOC-BILL-001` — "A resource was left running in a non-production environment"
- `DOC-BILL-001` — "The billing period runs from the subscription date rather than the first of the month"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 54. VAL-0074

**Ticket.** Remove a departing team member

We are tightening permissions after a review and I want to understand how group
membership interacts with directly assigned roles.

**Reply sent.**

Group membership is preferred over direct role assignment because it allows access to be
reviewed in one place, while direct roles are resolved together with group memberships
in the effective permissions view.

**Quoted as support.**

- `DOC-ACCT-001` — "Prefer group membership to direct role assignment, so that access can be reviewed in one place."

**Source: DOC-ACCT-001 — Managing team members, roles and permissions**

> # Managing team members, roles and permissions  **Applies to:** All plans  ## Symptoms
> - A user cannot access a project they should be able to - A departing user needs
> removing - Permissions need narrowing after a review  ## Common causes  - The role was
> granted at project scope rather than organisation scope - The invitation was never
> accepted and the account does not exist - A group membership grants broader access
> than the direct role suggests  ## Resolution  1. Check the effective permissions view
> for the user, which resolves direct roles and group memberships together. 2. Confirm
> the invitation was accepted. Pending invitations appear in a separate section and
> expire after seven days. 3. Remove a departing user rather than only changing their
> password, and revoke any API keys they created. 4. Prefer group membership to direct
> role assignment, so that access can be reviewed in one place.  ## Notes  Removing the
> last account owner is not permitted. Transfer ownership before removing the account.

verdict: UNSCORED

note:

---

## 55. VAL-0075

**Ticket.** API key returning 401

A key can read fine but every write returns a permission error. I created it myself and
I thought I gave it full access.

**Reply sent.**

The key was probably issued with a scope that excludes the write endpoint, so it can
read but not write.

**Quoted as support.**

- `DOC-AUTH-004` — "The key was issued with a scope that excludes the endpoint being called"

**Source: DOC-AUTH-004 — API key rotation and scope management**

> # API key rotation and scope management  **Applies to:** All plans  ## Symptoms  - A
> previously working key returns 401 Unauthorized - A key works for some endpoints and
> not others - A key needs replacing after accidental exposure  ## Common causes  - The
> key was revoked or reached its configured expiry - The key was issued with a scope
> that excludes the endpoint being called - The key belongs to a deleted user and was
> removed with the account  ## Resolution  1. Check the API keys page for the key's
> status and expiry. Revoked and expired keys are listed with the date and the user who
> acted. 2. Review the scopes attached to the key. Read-only keys cannot write, and
> project-scoped keys cannot reach organisation endpoints. 3. To rotate without
> downtime, create the replacement key first, deploy it, confirm traffic has moved, then
> revoke the old key. 4. If a key has been exposed publicly, revoke it immediately
> rather than waiting for the rotation window.  ## Notes  Keys issued to individual
> users are removed when that user is deleted. Use service accounts for anything running
> in production.

verdict: UNSCORED

note:

---

## 56. VAL-0076

**Ticket.** Need data to stay in the EU

We need our data to remain within the EU for a contract we are signing. Our organisation
was created some time ago and I am not sure which region it is in.

**Reply sent.**

To keep your data within the EU, you should verify the region in which your organisation
was created and, if necessary, move it to an EU region; the data residency guidance
notes that the organisation’s region may no longer suit the requirement and that backups
are replicated to a second region by default.

**Quoted as support.**

- `DOC-DATA-003` — "The organisation was created in a region that no longer suits the requirement"

**Source: DOC-DATA-003 — Data residency and regional storage**

> # Data residency and regional storage  **Applies to:** Business and Enterprise plans
> ## Symptoms  - A customer requires data to remain in a specific region - Latency is
> high for users far from the primary region - A compliance review has asked where data
> is held  ## Common causes  - The organisation was created in a region that no longer
> suits the requirement - Read traffic is being served from the primary region only -
> Backups are replicated to a second region by default  ## Resolution  1. Check the
> region shown on the organisation settings page. This is fixed at creation and
> determines where primary data is stored. 2. Enable read replicas in additional regions
> to reduce latency for distant users without moving primary storage. 3. Review the
> backup replication setting if a single-region requirement applies, since cross-region
> replication is enabled by default. 4. Migrating an organisation between regions
> requires a planned migration with support and involves a maintenance window.  ## Notes
> Metadata such as account names and billing records is stored centrally regardless of
> the data region.

verdict: UNSCORED

note:

---

## 57. VAL-0077

**Ticket.** (no subject)

Our billing period does not seem to match the calendar month, which is making
reconciliation difficult. Is that expected?

**Reply sent.**

Yes, the billing period starts from your subscription date rather than the first of the
month, which can cause a mismatch with the calendar month.

**Quoted as support.**

- `DOC-BILL-001` — "The billing period runs from the subscription date rather than the first of the month"

**Source: DOC-BILL-001 — Understanding your invoice and usage breakdown**

> # Understanding your invoice and usage breakdown  **Applies to:** All plans  ##
> Symptoms  - The invoice is higher than expected - Charges appear for a service that is
> not in use - The billing period does not align with the calendar month  ## Common
> causes  - Usage-based charges accrued beyond the plan allowance - A resource was left
> running in a non-production environment - The billing period runs from the
> subscription date rather than the first of the month  ## Resolution  1. Open the usage
> breakdown for the period, which itemises charges by service and by environment. 2.
> Look for resources in staging or development environments, which are billed at the
> same rate as production. 3. Check the billing period dates at the top of the invoice.
> The period runs from the anniversary of the subscription date. 4. Set a usage alert on
> the billing page so that unexpected accrual is noticed during the period rather than
> at the end of it.  ## Notes  Invoices are finalised three days after the period ends.
> Adjustments requested before finalisation appear on the same invoice.

verdict: UNSCORED

note:

---

## 58. VAL-0079

**Ticket.** Need data to stay in the EU

one of our customers has asked for written confirmation of where their data is
physically stored. Can you please point me to something I can share with them? kindly
check and revert.

**Reply sent.**

The documentation does not cover that request.

**Quoted as support.**


verdict: UNSCORED

note:

---

## 59. VAL-0080

**Ticket.** (no subject)

Builds that worked last week are now failing during dependency resolution. We have not
changed our code at all. This is blocking a release we had planned for yesterday
morning.

**Reply sent.**

The most common cause of builds that suddenly fail during dependency resolution is
unpinned dependencies that have changed, so pin your dependencies to exact versions and
commit the lock file.

**Quoted as support.**

- `DOC-DEPLOY-003` — "Pin your dependencies with exact versions and commit the lock file. Unpinned dependencies are the cause in the large majority of cases of this kind."

**Source: DOC-DEPLOY-003 — Build failures caused by dependency resolution**

> # Build failures caused by dependency resolution  **Applies to:** Build Service  ##
> Symptoms  - Builds that previously succeeded now fail without code changes - The build
> works locally but fails in the pipeline - Dependency resolution takes far longer than
> usual  ## Common causes  - An unpinned dependency released a new incompatible version
> - The build environment uses a different language runtime than the local machine - The
> dependency cache holds a partially written artefact  ## Resolution  1. Pin your
> dependencies with exact versions and commit the lock file. Unpinned dependencies are
> the cause in the large majority of cases of this kind. 2. Compare the runtime version
> declared in your build configuration against the version you use locally. 3. Clear the
> build cache from the settings page and trigger a fresh build to rule out a corrupted
> artefact. 4. If a specific dependency is failing to resolve, check whether its
> registry is reachable from the build network.  ## Notes  Build logs retain the full
> resolution output for thirty days, which is usually enough to identify which version
> changed.

verdict: UNSCORED

note:

---
