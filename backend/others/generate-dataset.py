import pandas as pd
import numpy as np
from sklearn.utils import shuffle

def generate_random_dataset(base_data, noise_factor=0.2):
    """
    Generate new dataset with randomized moisture values while preserving the pattern
    """
    # Create a copy of the original data
    new_data = base_data.copy()
    
    # Separate data by pump status
    pump_on = new_data[new_data['pump'] == 1]
    pump_off = new_data[new_data['pump'] == 0]
    
    # Calculate mean and std for each group
    mean_on = pump_on['moisture'].mean()
    std_on = pump_on['moisture'].std()
    
    mean_off = pump_off['moisture'].mean()
    std_off = pump_off['moisture'].std()
    
    # Generate new moisture values
    new_moisture_on = np.random.normal(mean_on, std_on * (1 + noise_factor), size=len(pump_on))
    new_moisture_off = np.random.normal(mean_off, std_off * (1 + noise_factor), size=len(pump_off))
    
    # Update moisture values
    pump_on.loc[:, 'moisture'] = new_moisture_on
    pump_off.loc[:, 'moisture'] = new_moisture_off
    
    # Combine and shuffle the data
    new_dataset = pd.concat([pump_on, pump_off])
    new_dataset = shuffle(new_dataset, random_state=42)
    
    # Ensure moisture values are positive and rounded
    new_dataset['moisture'] = np.maximum(0, new_dataset['moisture']).round()
    
    return new_dataset

# Load original data
original_data = pd.read_csv('data.csv')

# Generate two new datasets with different random patterns
dataset2 = generate_random_dataset(original_data, noise_factor=0.2)
dataset3 = generate_random_dataset(original_data, noise_factor=0.3)

# Save the new datasets
dataset2.to_csv('data2.csv', index=False)
dataset3.to_csv('data3.csv', index=False)

# Print summary statistics for comparison
def print_dataset_stats(data, name):
    print(f"\n{name} Statistics:")
    print("Pump ON  - Moisture Mean: {:.2f}, Std: {:.2f}".format(
        data[data['pump'] == 1]['moisture'].mean(),
        data[data['pump'] == 1]['moisture'].std()
    ))
    print("Pump OFF - Moisture Mean: {:.2f}, Std: {:.2f}".format(
        data[data['pump'] == 0]['moisture'].mean(),
        data[data['pump'] == 0]['moisture'].std()
    ))

print_dataset_stats(original_data, "Original Dataset")
print_dataset_stats(dataset2, "Dataset 2")
print_dataset_stats(dataset3, "Dataset 3")