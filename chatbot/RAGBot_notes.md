# RAG Chatbot Notes

## What is the RAG chatbot?

My first chatbot ([chatbot.py](chatbot.py)) sends all the bank policies to the LLM with every question. That works for three short files, but a real bank has hundreds of documents, far too many to send each time.

The RAG chatbot ([ragchatbot.py](ragchatbot.py)) works differently. It first **searches** the policies for the parts that match the question, then sends only those parts to the LLM. RAG stands for Retrieval-Augmented Generation: find the right information first, then answer.

How my version searches:

1. Each policy file is cut into sections, one per heading (for example "Home Loan" or "Fees"). That gives 10 sections.
2. For each question, it counts how many words the question shares with each section. Small words like "what", "is" and "the" are ignored.
3. The 2 sections with the most shared words are sent to the LLM.

## Retrieval investigation

I asked the RAG bot 14 questions from my golden dataset, and for each one I checked two things: which sections it found, and whether the answer was right.

| # | Question | Sections it found | Answer correct? |
|---|---|---|---|
| TS01 | Home loan interest rate | Home Loan, Personal Loan | Yes: 8.5% per year |
| TS02 | Personal loan rate for self-employed | Personal Loan, Home Loan | Yes: 12% per year |
| TS03 | FD rate for a senior citizen for 4 years | Personal Loan, Home Loan | **No.** It said "I don't have that information" (should be 7.75%) |
| TS04 | Do I always pay the credit card annual fee? | Fees, Eligibility | Yes: ₹500, waived if you spend ₹50,000 or more |
| TS07 | "wat is late fee on credit card" (spelling mistakes) | Fees, Eligibility | Yes: ₹750 |
| TS10 | Hi | (none needed) | Yes: a polite greeting |
| TS11 | Minimum amount for a fixed deposit | Deposit Amount, Personal Loan | Yes: ₹10,000 |
| TS14 | I'm 20, can I get a credit card? | Eligibility, Home Loan | Yes: you must be at least 21 |
| TS16 | Fee for withdrawing ₹4,000 cash on a credit card | Fees, Eligibility | Yes: 2.5% = ₹100 |
| TS18 | ₹20,000 EMI, one month late: what's the penalty? | Late EMI Payment, Fees | Yes: 2% = ₹400 |
| TS19 | Can I withdraw my FD on the 3rd day? | ATM withdrawal limit | **No.** It said "I don't have that information" (should be: not allowed in the first 7 days) |
| TS25 | (after asking about the home loan) And what is the maximum tenure? | Home Loan, Personal Loan | Yes: 30 years |
| TS28 | "FD ka minimum amount kitna hai?" (Hinglish) | Personal Loan, Deposit Amount | Yes: ₹10,000 |
| TS05 | Car loan rate (not a bank product) | Personal Loan, Home Loan | Yes: it correctly said it doesn't know |

**Result: 12 out of 14 correct.**

The two wrong answers were not the LLM's fault. The search never found the right section, so the LLM never saw the answer, and it was right to say "I don't have that information". My first chatbot gets both questions right, because it always sees every policy.

## Problems I found with the search

**1. It doesn't know that "FD" means "Fixed Deposit".** Customers write "FD", but the policy file says "Fixed Deposit". The search only matches exact words, so "FD" never matches anything. This broke both TS03 and TS19.

**2. It doesn't understand plurals or similar words.** "withdraw" and "withdrawal" count as different words, and so do "day" and "days", "rate" and "rates", "citizen" and "citizens". In TS19, the Early Withdrawal section, which had the answer, scored zero. The only match was the word "day" in the credit card ATM section ("₹40,000 per day"), which has nothing to do with FDs.

**3. When sections tie, loans always win.** In TS03, three sections had the same score: Personal Loan, Home Loan, and the FD Interest Rates section that had the answer. The code breaks ties by sorting the section text, and because of how the file titles sort, loan sections always come first. The FD section was pushed out of the top 2.

**4. Some right answers were just luck.** In TS28, the Personal Loan and Deposit Amount sections tied. The answer was right only because the bot takes 2 sections. If it took only 1, it would have picked Personal Loan and got it wrong.

**5. It forgets the conversation when searching.** The search only looks at the latest question, not the earlier messages. TS25 worked because "maximum tenure" happens to match the Home Loan section. A follow-up like "And what about for self-employed?" would be searched without the words "personal loan", and could find the wrong section.

**6. An unrelated section almost always comes along.** Because it always takes 2 sections, most answers also got one that had nothing to do with the question, like Home Loan for a credit card question. The LLM ignored it this time, but extra unrelated text gives it more chances to mix up facts.

## What I learned

- **In a RAG bot, a wrong answer can come from the search, not the LLM.** If the right information is never found, even a perfect LLM can't answer.
- **Always look at what was retrieved.** Printing the sections it found told me straight away whether the bot didn't know the answer or was never shown it.
- **Matching exact words is fragile.** Customers use short forms, plurals, spelling mistakes and other languages, and all of these can break a word-matching search.
- **A passing answer can still hide a weak spot.** TS28 passed only because of a lucky tie.

Ideas to try next: teach the search that "FD" means "fixed deposit", match word roots (so "withdraw" matches "withdrawal"), or use embeddings, which search by meaning instead of exact words.
