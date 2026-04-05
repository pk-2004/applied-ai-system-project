# DocuBot Model Card

This model card is a short reflection on your DocuBot system. Fill it out after you have implemented retrieval and experimented with all three modes:

1. Naive LLM over full docs  
2. Retrieval only  
3. RAG (retrieval plus LLM)

Use clear, honest descriptions. It is fine if your system is imperfect.

---

## 1. System Overview

**What is DocuBot trying to do?**  
Describe the overall goal in 2 to 3 sentences.

> DocuBot tries to look through the files and tokenize them. After tokenizing, assigns a score to tokens to show how good it aligns with the query asked. 

**What inputs does DocuBot take?**  
For example: user question, docs in folder, environment variables.

> A user query and uses the documents.
**What outputs does DocuBot produce?**

> A paragraph that attempts to answer the query. 

---

## 2. Retrieval Design

**How does your retrieval system work?**  
Describe your choices for indexing and scoring.

- How do you turn documents into an index?
- How do you score relevance for a query?
- How do you choose top snippets?

> The documents are turned in a dictionary. The key is a word and its associated value is a list of files where the word is located in. For scoring, the query is split into seperate words, and the frequency of the word as apperead in text that is segemented based on each paragraph becomes the score. The top 3 documents by their best score are ranked and returned. 

**What tradeoffs did you make?**  
For example: speed vs precision, simplicity vs accuracy.

> The scoring is based on exact word matches in a given text, thus might leave out words that are close like "generate" and "generation".

---

## 3. Use of the LLM (Gemini)

**When does DocuBot call the LLM and when does it not?**  
Briefly describe how each mode behaves.

- Naive LLM mode:
- Retrieval only mode:
- RAG mode:

> The Naive LLM model sends the query to Gemini AI without considering the docs in this file. Mode 2 simply tries to use the query and match words to excerpts and return the one with the highest match. The RAG mode gets the top 3 matched exceprts, and sends it to Gemini AI. 

**What instructions do you give the LLM to keep it grounded?**  
Summarize the rules from your prompt. For example: only use snippets, say "I do not know" when needed, cite files.

> If the given query does not give enough context, I told it to say "I don't know based on the given docs". In addition, I told it to cite the document name for the results. 

---

## 4. Experiments and Comparisons

Run the **same set of queries** in all three modes. Fill in the table with short notes.

You can reuse or adapt the queries from `dataset.py`.

| Query | Naive LLM: helpful or harmful? | Retrieval only: helpful or harmful? | RAG: helpful or harmful? | Notes |Responses are more generic and long.|Responses are shorter but not always straight to point| The responses are short yet precise with some additional information at times that is not always that useful.
        Also a bit slow
|------|---------------------------------|--------------------------------------|---------------------------|-------|
| Example: Where is the auth token generated? 
| Example: How do I connect to the database? | | | | |
| Example: Which endpoint lists all users? | | | | |
| Example: How does a client refresh an access token? | | | | |

**What patterns did you notice?**  

- When does naive LLM look impressive but untrustworthy?  
- When is retrieval only clearly better?  
- When is RAG clearly better than both?

> The naive LLM is great with providing a lot of detail. The retrieval is the best in terms of speed of responses. RAG is the best in terms of providing results that are short yet clear to the point. 

---

## 5. Failure Cases and Guardrails

**Describe at least two concrete failure cases you observed.**  
For each one, say:

- What was the question?  
- What did the system do?  
- What should have happened instead?

> Mode 2, ask Client's favorite color, expected I don't know but got unrelated responses. 
Question: What is the Client's favorite color?

Retrieved snippets:
[API_REFERENCE.md]
## User Data Endpoints

### GET /api/users/<user_id>       

Fetches profile data for a specific user.

Headers:

    ```plaintext
    Authorization: Bearer <token>  
    ```

Response Example:

    ```json
    {
    "user_id": 42,
    "email": "user@example.com",   
    "joined_at": "2024-01-15T10:22:00Z"
    }
    ```

Failure Cases:

* 401 if the token is missing or expired
* 403 if the user lacks permission to view this profile
* 404 if no user exists with the given ID

### GET /api/users

Returns a list of all users. Only accessible to admins.

Headers:

    ```plaintext
    Authorization: Bearer <token>  
    ```

Successful Response:

    ```json
    [
    {
        "user_id": 1,
        "email": "admin@example.com"
    },
    {
        "user_id": 2,
        "email": "guest@example.com"
    }
    ]
    ```

Notes:

* Returns 403 for non admin accounts.

---
[AUTH.md]
## Token Generation

Tokens are created by the `generate_access_token` function in the `auth_utils.py` module. The function takes a user ID and returns a signed JSON Web Token string.

Internally, the token is signed using the secret stored in the `AUTH_SECRET_KEY` environment variable. If the key is missing or empty, token creation will fail.

The token payload includes:        

- `user_id`
- `issued_at`
- `expires_at`
- `permissions` (optional)

---
[DATABASE.md]
## Connection Configuration        

The database connection is determined by the `DATABASE_URL` environment variable.

Examples:

- SQLite (default):

    ```plaintext
    sqlite:///app.db
    ```

- PostgreSQL:

    ```plaintext
    postgres://user:password@localhost:5432/appdb
    ```

If `DATABASE_URL` is not provided, the application creates a local SQLite database file named `app.db`
> Mode 1 asked what is the database type, expected SQL or Postgres, but got a generic response like database type is dependent on user application. 

**When should DocuBot say “I do not know based on the docs I have”?**  
Give at least two specific situations.

> When asking a question like "What is the weather tommorow?" and when a question is asked like why were ids assigned to user rather than name? 

**What guardrails did you implement?**  
Examples: refusal rules, thresholds, limits on snippets, safe defaults.

> If max score is 2, then the response is "I do not know based on the docs I have".

---

## 6. Limitations and Future Improvements

**Current limitations**  
List at least three limitations of your DocuBot system.

1. Can't reason on why a design choice was made. 
2. Not saying idk to unrelated questions with keywords like user.
3. Generalize words like treating "generate" and "generation" as the same. 

**Future improvements**  
List two or three changes that would most improve reliability or usefulness.

1. Increasing number of documents for more representation
2. Maybe use some sort of vector embedding technique to map similar words and context together
3. 
---

## 7. Responsible Use

**Where could this system cause real world harm if used carelessly?**  
Think about wrong answers, missing information, or over trusting the LLM.

> If a new hospital is working on creating a database to store patient information. Due to the limitations of Docubot, it is very much possible that the admins may be misguided and not properly store valuble information. 

**What instructions would you give real developers who want to use DocuBot safely?**  
Write 2 to 4 short bullet points.

- Try to not have any spelling mistakes
- Ask queries based on the contents of the document. 
- _Guideline 3 (optional)_

---
