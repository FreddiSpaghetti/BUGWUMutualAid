# BUGWU Mutual Aid System

This repository contains the fully documented codebase for the BUGWU Mutual Aid system used in the BUGWU 2024 strike within the math and computer science departments. Code contributors include Eli, Debanuj, and Eric

There are two main scripts, the first `run-distribution.py` which calculates the distribution of funds between senders and receivers and `send-email.py` which manages all of the email sending to provide some automation.

## Mutual Aid Distribution Algorithm

This script generates a randomized mutual aid distribution from a CSV of people who are either sending money or receiving support. It outputs a CSV `distributions.csv` which list of transfers showing who should send money to whom and how much.

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
3. Computes a donation scale factor so only the needed portion of each donor's listed contribution is used. Critically, **each donor sends an equal amount of their giving contribution amount!**
4. Randomizes the donor order for fairness.
5. Assigns donors to recipients until each recipient's requested amount is met.
6. Splits donor amounts across recipients when needed.
7. Outputs a CSV-style list of transfers.

Emails are stored for everyone so they can be included in the final output.

### Notes

- A donor may be matched with multiple recipients.
- A recipient may receive support from multiple donors.
- Donor order is randomized each time the script runs.
- Recipient order follows the order of the input CSV.
- The current version uses each recipient's individually requested amount.
- `TF_Base` is currently only used for printed diagnostics, not for determining allocations.

### Output

The script writes the final distribution to a CSV file named `distributions.csv`.

Each row represents either:

1. A transfer from a donor to a recipient, or
2. The donor’s originally listed donation amount.

The CSV has the following columns:

```csv
from,email,action,to,amount
```

Where:

- `from` = the donor’s name
- `email` = the donor’s email address
- `action` = either `sends` or `listed`
- `to` = the recipient’s name, if this row is a transfer
- `amount` = the amount being sent, or the donor’s original listed amount

Example output:

```csv
from,email,action,to,amount
Alice,alice@example.com,sends,Bob,$75
Alice,alice@example.com,sends,Dana,$25
Charlie,charlie@example.com,sends,Bob,$50
```

## Email Sending Script

This script sends mutual aid emails using SMTP. Note that this needs to be configured before use! It can send either:

1. **Confirmation emails** asking contributors to confirm their pledged amount.
2. **Distribution emails** telling contributors who to send money to.

### SMTP

The script logs into any SMPT credentials stored in:

```text
data/smtp.conf
```

The config file should include:

```text
AuthUser=your-email@domain.com
AuthPass=your-password-or-app-password
```
which are used in the SMPT call, which you should also edit to match your provider:

```python
SMTP("TODO", PORTNUMBERTODO)
```

### TF Payment Information

Distribution emails use recipient payment information from:

```python
from examples.exampleTFs import tf_info
```

Each recipient listed in the distribution file must have a matching entry in `tf_info`.

For example, if the distribution includes:

```example from file
Person3,p3@email.com,sends,Bob,$113
```

then `tf_info` must contain information for `Bob`.


### Distribution Emails

The `distribution_emails(FILE)` function sends each contributor their assigned mutual aid transfers.

The input file is expected to be comma-separated and grouped by donor:

```text
from,email,action,to,amount
```

Example:

```text
Alice,alice@example.com,sends,Bob,$75
Alice,alice@example.com,sends,Dana,$25
```

Rows with `sends` are added to the donor’s email. When the script reaches a row with `listed`, it sends the completed email to that donor.

### Email Contents

Each distribution email includes:
- the senders’s name
- the recipient or recipients they should send money to
- the amount for each recipient
- the recipient’s payment information from `tf_info`
- instructions to send the money or contact the recipient if delayed

### Running the Script

Run the script with the input file in bash. Changing which email you want to send is done on line 13/14

```bash
python3 send-emails.py input-file.csv
```
