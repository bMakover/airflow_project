import pandas as pd
import time
import random
import uuid

df = pd.read_csv('data/wine.csv')

min_rows = 10  # Minimum number of rows to extract
max_rows = 25  # Maximum number of rows to extract

while True:
    num_rows = random.randint(min_rows, max_rows)
    extracted_data = df.sample(num_rows)

    # Generate a unique filename using timestamp and UUID
    filename = f'/app/data/data_{time.time()}_{uuid.uuid4()}.csv'

    # Write the data to the new CSV file
    extracted_data.to_csv(filename, index=False)

    time.sleep(36)
