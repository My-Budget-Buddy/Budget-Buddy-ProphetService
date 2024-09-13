from faker import Faker # faker to generate fake data
import random # random for random values and weights
import pandas as pd #need pandas for data manipulation/create dataframe
from datetime import timedelta # timedelta to move between dates

# create a faker instance
fake = Faker()

# define categories for transactions with varying weights based on real-world spending patterns
categories = [
    ('Groceries', 0.25),  
    ('Dining', 0.15),      
    ('Entertainment', 0.10), 
    ('Shopping', 0.20),   
    ('Transportation', 0.10), 
    ('Healthcare', 0.05),  
    ('Living Expenses', 0.10), 
    ('Misc', 0.05),        
]

# ranges to keep values realistic
# to fix: why were the values so big
category_ranges = {
    'Groceries': (10, 100),
    'Dining': (10, 100),
    'Entertainment': (10, 150),
    'Shopping': (10, 300),
    'Transportation': (5, 50),
    'Healthcare': (20, 300),
    'Living Expenses': (1000, 1500), 
    'Misc': (5, 100),
}



# set a cap for how much a person might spend in a month, used to control how much synthetic data generates
MONTHLY_SPENDING_CAP = 3000

def generate_synthetic_data(start_date, end_date):
    # list to store all the transactions generated for each day
    transactions = []
    monthly_living_expense_added = set()  # track months where living expenses have been added

    # total monthly spending 
    monthly_spending = 0
    current_month = start_date.month
    
    # loop through each day from start to end
    current_date = start_date
    while current_date <= end_date:
        # get the year and month to simulate different trends for each year
        year = current_date.year
        month = current_date.month

        # reset the monthly spending tracker if move into a new month
        if month != current_month:
            monthly_spending = 0  
            current_month = month
        
        # increase spending for holidays and summer vacation
        holiday_spending_multiplier = 1.5 if month in [11, 12] else 1 
        vacation_spending_multiplier = 1.3 if month in [6, 7, 8] else 1  

        # adjust the category weights to reflect trends for specific years
        if year == 2022:
            #  higher spending on groceries due to inflation
            category_weights = [0.30, 0.10, 0.05, 0.20, 0.10, 0.05, 0.05, 0.15]
        elif year == 2023:
            # post pandemic more spending on dining and entertainment
            category_weights = [0.25, 0.20, 0.12, 0.20, 0.10, 0.05, 0.05, 0.10]
        else:
            # default spending pattern for 2024 and beyond
            category_weights = [c[1] for c in categories]  


        # add living expenses like rent once per month
        if (year, month) not in monthly_living_expense_added:
            # generate a random rent or utility transaction for this month
            living_expense_amount = round(random.uniform(800, 1500), 2)  
            living_expense_transaction = {
                'transactionId': random.randint(1000, 9999), # assign a random transaction id
                'userId': 1,
                'accountId': random.randint(1, 3), # random account id
                'vendorName': fake.company(),
                'amount': living_expense_amount, # generated rent or utility amount
                'description': 'Monthly rent or utilities',
                'category': 'Living Expenses',
                'date': current_date.strftime('%Y-%m-%d') # format the date to 'YYYY-MM-DD'
            }
            # add to list of transactions 
            transactions.append(living_expense_transaction)

            # mark the expense as added for this month
            monthly_living_expense_added.add((year, month))  


        # number of days left in the month to distribute spending
        days_remaining_in_month = max(1, 30 - current_date.day)  # ensure at least one day remains so you dont divide by zero

        # daily spending cap that adjusts based on the remaining monthly budget
        DAILY_SPENDING_CAP = min(200, (MONTHLY_SPENDING_CAP - monthly_spending) / days_remaining_in_month)


        # generate between 1 to 2 transactions per day
        num_transactions = random.randint(1, 2)
        daily_transactions = []  #today's transaction
        daily_total_spending = 0  
        
        for _ in range(num_transactions):
            # randomly choose a vendor name and category based on weighted categories
            vendor_name = fake.company()
            category, category_weight = random.choices(categories, weights=[c[1] for c in categories])[0]
            
             # random transaction amount within the category's range
            min_amount, max_amount = category_ranges[category]
            transaction_amount = round(random.uniform(min_amount, max_amount), 2)

             # apply spending multipliers during holiday or vacation periods for certain categories
            if category in ['Groceries', 'Dining', 'Shopping', 'Entertainment']:
                transaction_amount = round(transaction_amount * holiday_spending_multiplier, 2)

            if category in ['Transportation', 'Dining', 'Entertainment']:
                transaction_amount = round(transaction_amount * vacation_spending_multiplier, 2)


          # only add the transaction if it doesn't exceed the daily spending cap
            if daily_total_spending + transaction_amount <= DAILY_SPENDING_CAP:
                daily_total_spending += transaction_amount

                # create a transaction record with the generated data
                daily_transactions.append({
                    'transactionId': random.randint(1000, 9999),
                    'userId': 1,
                    'accountId': random.randint(1, 3),
                    'vendorName': vendor_name,
                    'amount': transaction_amount,
                    'description': fake.text(max_nb_chars=50), # generates a random description
                    'category': category,
                    'date': current_date.strftime('%Y-%m-%d')
                })
            else:
                break  # stop if daily cap is reached
           

        # add today's transactions to the main list of transactions
        transactions.extend(daily_transactions)
        
        # move to the next day
        current_date += timedelta(days=1)
    
    # convert the transactions list to a pandas dataframe
    transactions_df = pd.DataFrame(transactions)
    
    return transactions_df


