# run-distribution.py
#
# Given a CSV formatted as in example-everyone.csv, output a CSV file which provides a mutual aid distribution
# This CSV can then be turned back into a spreadsheet and/or used to send emails with SMTP configured!

from collections import defaultdict
import random
import math
import sys

# TF expected payment per week. Calculated for BUGWU by net pay - strike pay
TF_Base = 550

# Decide how to distribute the money, based on individual report need (True) or done equally given the base missing pay (False)
distribute_need = True

donations = {}
receive_support = {}

emails = {}

if len(sys.argv) != 2:
    print("Please provide an input file")

with open(sys.argv[1]) as f:
    for line in f:
        # expects CSV and inputs data into script, see example-everyone
        name, email, contribution, amount = line.split(',')
        # optionally remove $ sign
        if amount.startswith('$'):
            amount = int(amount[1:])
        else:
            amount = int(amount)

        if contribution == 'send':
            if amount == 0:
                continue
            
            donations[name] = amount
        if contribution == 'receive':
            receive_support[name] = amount
        emails[name] = email


# Calculating basic stats and outputting them
n_send = len(donations)
n_receive = len(receive_support)

total_donation = sum(donations.values())
total_need = sum(receive_support.values())
print(f"Loaded {n_send} senders and {n_receive} Receivers.")
print(f"  Total donations: ${total_donation}")
print(f"  Avg donation: ${round(total_donation/n_send)}")


# Calculating the needed donation from each sender to fulfil all needs.
needed_donation = round(total_need / n_send)
# Calculating average need for all receivers.
receive_avg_each = round(total_need / n_receive)
#Calculating total amount of money sent
totalSent = needed_donation * n_send

# Calculating how much each senders donation will be used. That is, if donation_scale is 0.6, we will be using
# 60% of each sender's donation.
donation_scale = needed_donation/total_donation*n_send

# Printing out diagnostics for the distribution
print(f"Required joint avg donation: ${needed_donation}")
print(f"  Sending a total amount of ${totalSent}")
print(f"  TFs recv total of ${totalSent}, or ${receive_avg_each} each, avg")
print(f"  TF avg income lost = ${TF_Base} - ${receive_avg_each} = ${TF_Base - receive_avg_each}")
print(f"  Scale factor: {donation_scale:.2}")

# Create list of remaining donor amounts
remaining_donor_amounts = []

for k, v in donations.items():
    old_v = v
    # This needs to be `ceil`, because otherwise we could round down too often 
    # and run out of money.
    remaining_donor_amounts.append((k, min(v, math.ceil(v * donation_scale))))

output = defaultdict(list)
num_transfers = 0

# Randomize distribution so it's fair.
random.shuffle(remaining_donor_amounts)

for t, amt in receive_support.items():
    print(f"**** {t} (${amt}) ****")
    recv = 0

    tf_need = amt
    if distribute_need == False:
        tf_need = TF_Base

    while recv < tf_need:
        next_donor, amount = remaining_donor_amounts.pop(0) # pop_next_closest(support - recv)

        if recv + amount > tf_need:
            leftover = recv + amount - tf_need
            recv = tf_need
            amount -= leftover
            remaining_donor_amounts.append((next_donor, leftover))
        else:
            recv += amount
        
        print(f"{next_donor}, ${amount}, ${recv}")
        num_transfers += 1

        output[next_donor].append(f"{next_donor}, {emails[next_donor]}, sends, {t}, ${amount}")
    print()

    assert recv == tf_need


print(f"{num_transfers} transfers")

print("-------")
print("from,,,to,amount")

for d, s in output.items():
    for l in s:
        print(l)
    print(f"{d},, listed,, ${donations[d]}")
    print()

