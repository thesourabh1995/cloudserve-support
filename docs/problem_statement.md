# The problem statement

**Draft for review.** You have to present this on camera and answer questions about it. Read it as a proposal, change anything you would not say in your own words, and keep the reasoning only if you agree with it. The evidence it rests on is real; the framing is a judgement, and the judgement has to be yours.

---

## The statement

> CloudServe's support team is not short of answers. It is short of a reliable path from what a customer wrote to the article that already answers them.
>
> Seven in ten tickets are answerable from twenty-nine knowledge base articles that are accurate and currently reviewed. Yet agents reconstruct those answers from memory, because the internal search matches article titles and customers do not describe problems in the words the titles use. The cost of that broken path is paid twice: once as an eight-to-twelve-hour first response while known answers are rewritten by hand, and again as an escalation rate of 56%, of which roughly half is not difficulty at all but an agent who could not find the page and would not send an answer they were not confident about.
>
> The organisation cannot see this, because each person can only see their own part of it. The Head of Support sees the escalation rate but not what is inside the escalations. The technical writer sees her articles going unused and understood it as a complaint about their quality. The tier one agent who identified the search as the problem raised it once and was misheard. The tier two engineer knows that half his queue was resolvable, and his manager does not.
>
> What CloudServe needs is therefore not a new place for customers to ask questions. It is a system that closes the distance between a customer's words and the correct existing article — answering directly where it can do so with a citation, and handing a human the ticket, the likely category, the relevant documentation and an explicit statement of what it was unsure about where it cannot.

## Why this is the problem, and not the one we were asked to solve

Marcus asked for a chatbot. Asked what he pictured it doing, he said: *"answering the easy ones so my people can do the hard ones"*, and added, *"I do not have a strong view about how it works."* The request names a technology; the need behind it is a number.

A chatbot would not meet that need, and the evidence says why. The failure is not that customers have nowhere to ask — they already have four channels, and 42% of volume arrives by email alone. The failure is that the route from a question to its existing answer is broken by vocabulary. Ines put it precisely: someone writes *"my deployment keeps dying"* and her article is called *"resolving container health check failures"*, and *"there is no path between those two phrases in a keyword search."* A conversational front end adds a fifth place to ask without repairing that path. It would reproduce the existing failure at higher volume while appearing modern.

The same evidence also rules out the obvious shortcut. Daniel warned that answers circulating in agents' private files *"were correct two years ago and have not been right since"*, and that a system learning from them *"will scale up a mistake."* The data agrees that the corpus is the trustworthy source: all 29 articles were reviewed within the current cycle, so the staleness Daniel describes lives in the private files, not the knowledge base. Grounding answers in the reviewed articles rather than in past agent replies is an evidenced decision, not a convenience.

## What the evidence settles, including where it corrected us

Two claims from the interviews do not survive the ticket data, and both change the brief.

Sofia believed tickets in non-fluent English *"have our worst satisfaction scores and I do not think anyone has noticed."* They do not: those tickets score 3.04 against 2.95 for fluent English, and resolve marginally faster. What she is describing accurately is her own effort — she has to work out the question before answering it — but that effort is not reaching the customer as a worse outcome. The problem she identified is real and is a workload problem, not a fairness outcome.

Ravi, a business-plan customer, believed enterprise customers *"get answers in about an hour"* and warned that widening that gap *"will come up at renewal."* The opposite is true. Enterprise is the worst-served tier in the company: 369 minutes median resolution against business's 141, the lowest first contact resolution at 37.3%, and only 37% of enterprise tickets resolved inside an hour. Ravi is already receiving the fastest service CloudServe provides and does not know it.

That finding also inverts Marcus's main anxiety. He worried that enterprise customers *"will notice immediately if they get worse service than they were getting."* They are already bottom of the table, and nobody in the five conversations knew. Protecting the status quo for enterprise is protecting the worst outcome in the business.

## What success looks like

Marcus named the measure himself, and it is not the one in the service agreement: *"First contact resolution, if I am being honest, more than response time."* His reasoning is economic — an escalated ticket costs roughly four times a resolved one and *"makes the customer angrier than waiting would have."*

He also named the two ways this fails, and both are constraints rather than preferences:

- **Sending something wrong.** *"I would rather it said nothing than said something wrong."* CloudServe's customers are engineers who *"will screenshot a confidently incorrect answer and put it on the internet within the hour."* Abstention must be cheaper than error, which is why answers are blocked rather than warned about when a claim is not traceable to a retrieved passage.
- **Making more work for agents than it saves.** The canned-response library failed because *"finding the right one took longer than writing the answer."* An escalation that arrives as a bare forwarded ticket repeats that mistake. Daniel was explicit about the remedy: *"I do not need it to be right. I need it to show its working."*

Ravi set the condition for the customer side: an automated first response is acceptable *"provided it is honest"* — what it thinks, the page it came from, and that a person will confirm. He would also want to know it was automated, *"because I calibrate how much I trust it."* That last point is a requirement this build does not satisfy, and it is recorded as FR-15 rather than quietly dropped.

## The sentence behind the sentence

The five people interviewed describe one situation from five positions, and none of them states it whole. Marcus has the cost, Sofia has the mechanism, Daniel has the consequence, Ines has the cause, Ravi has the experience. Assembled, they say that CloudServe has already written the answers to most of its support volume and has no working way to deliver them — and that the gap has persisted not because it is technically hard but because no single person in the operation could see it from where they stood.
