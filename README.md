# BUGWU Mutual Aid System

This repository contains the fully documented codebase for the BUGWU Mutual Aid system used in the BUGWU 2024 strike within the math and computer science departments. 

There are two main scripts, the first `run-distribution.py` which calculates the distribution of funds between senders and receivers and `send-email.py` which manages all of the email sending to provide some automation.

## Mutual Aid Distribution Algorithm

This script generates a randomized mutual aid distribution from a CSV of people who are either sending money or receiving support. It outputs a CSV-style list of transfers showing who should send money to whom and how much.

### Input Format

The script expects a CSV file with four columns:

```csv
name,email,contribution,amount
```

Where:

- `name` = person's name
- `email` = person's email address
- `contribution` = either `send` or `receive`
- `amount` = amount to send or receive, with or without a `$`

Example:

```csv
Alice,alice@example.com,send,100
Bob,bob@example.com,receive,250
Charlie,charlie@example.com,send,$75
```

### Overview

The algorithm:

1. Loads all senders and receivers from the input CSV.
2. Calculates total donations and total requested support.
3. Computes a donation scale factor so only the needed portion of each donor's listed contribution is used.
4. Randomizes the donor order for fairness.
5. Assigns donors to recipients until each recipient's requested amount is met.
6. Splits donor amounts across recipients when needed.
7. Outputs a CSV-style list of transfers.

Emails are stored for everyone so they can be included in the final output.

### Donation Scale

The script calculates how much of each sender's listed donation should actually be used.

First, it calculates the average amount needed per sender:

```python
needed_donation = round(total_need / n_send)
```

Then it calculates the scale factor:

```python
donation_scale = needed_donation / total_donation * n_send
```

This is equivalent to:

```python
donation_scale = total_amount_to_send / total_donation
```

For example, if donors collectively offered `$2,000`, but only `$1,000` is needed, then:

```python
donation_scale = 0.5
```

So each donor is asked to send approximately `50%` of their listed amount.

### Notes

- A donor may be matched with multiple recipients.
- A recipient may receive support from multiple donors.
- Donor order is randomized each time the script runs.
- Recipient order follows the order of the input CSV.
- The current version uses each recipient's individually requested amount.
- `TF_Base` is currently only used for printed diagnostics, not for determining allocations.

### Summary

In short, the script scales donor contributions to match total need, randomizes donors, then assigns donor amounts to recipients until every recipient has received their requested amount. Donor amounts can be split when necessary, and the final result is a CSV-style transfer list.
