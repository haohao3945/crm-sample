import os
import subprocess
import time

# Set the path to your Git repository
repo_path = r'D:\crm'

# Estimate average network speed in megabits per second (Mbps)
average_network_speed_mbps = 10  # Adjust this value based on your network speed

# Get the list of files that would be pushed
status_output = subprocess.check_output(['git', '-C', repo_path, 'status', '-s'], text=True)
files_to_push = [line.split()[1] for line in status_output.splitlines() if line.startswith('A') or line.startswith('M')]

# Calculate total size of files in bytes
total_size_bytes = sum(os.path.getsize(os.path.join(repo_path, file)) for file in files_to_push)
print("Total_size_bytes : ", total_size_bytes)

# Convert total size to megabits
total_size_mbps = total_size_bytes * 8 / 1024 / 1024
print("total_size_mbps : ", total_size_mbps)


# Calculate estimated time in seconds
estimated_time_seconds = total_size_mbps / average_network_speed_mbps

print("Estimated time to push:", estimated_time_seconds, "seconds")

# You can then decide whether to proceed with the push based on this estimation
proceed = input("Do you want to proceed with the push? (yes/no): ").lower()
if proceed == 'yes':
    subprocess.run(['git', '-C', repo_path, 'push', 'origin', 'master'])
    print("Push completed!")
else:
    print("Push canceled.")
