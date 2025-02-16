import random

#random number of resources
num_resources = random.randint(1, 30)
print(f"Random Resources: {num_resources}")
resources = []
for i in range(num_resources):
  resources.append(f"Resources {i+1}")
  # print(resources)

#random number of users
num_users = random.randint(1, 30)
print(f"Random Users: {num_users}")
users = []
for i in range(num_users):
  users.append(f"Users {i+1}")
  # print(users)

#random resource and usage time to each user
user_resource_time = {
    user: [(resource, random.randint(1, 30)) for resource in sorted(random.sample(resources, random.randint(1, len(resources))))]
    for user in users
}

print(f"{user_resource_time}")

#dictionary to tracker which users are using each resource and who is waiting
resource_status =  {resource: [] for resource in resources}
resource_waiting = {resource: [] for resource in resources}

# Populate resource status with users and their respective time left
for user, assigned_resources in user_resource_time.items(): #this will get the key(user) and the values (resoure, time)
    for resource, time_left in assigned_resources:  
        if len(resource_status[resource]) < 2:  # Limit concurrent users per resource
            resource_status[resource].append((user, time_left))
        else:
            # If the resource is full, put the user in the waiting list
            max_time = max(time for _, time in resource_status[resource])
            resource_waiting[resource].append((user, max_time + random.randint(1, 10)))  # Random start time

# Find out when resources will be completely free
resource_free_time = {}

for resource, users_info in resource_status.items():
    # Step 1: Find the max time left for the current (ongoing) users
    max_ongoing_time = max((time_left for _, time_left in users_info), default=0)

    # Step 2: Find the max time required by the waiting users (if any)
    max_waiting_time = max((wait_time for _, wait_time in resource_waiting.get(resource, [])), default=0)

    # Step 3: The total free time is when the last waiting user finishes
    resource_free_time[resource] = max_ongoing_time + max_waiting_time



# Display resource status
print("\n📌 Resource Status:")
for resource, users_info in resource_status.items():
    print(f"{resource}:")
    for user, time_left in users_info:
        print(f"  - Used by {user}, Time Left: {time_left} sec")

# Display waiting users
print("\n⏳ Users in Waiting:")
for resource, waiting_list in resource_waiting.items():
    if waiting_list:
        print(f"{resource}:")
        for user, start_time in waiting_list:
            print(f"  - {user} will start in {start_time} sec")

# Display when each resource is free
print("\n✅ Resource Free Time:")
for resource, free_time in resource_free_time.items():
    print(f"{resource} will be free in {free_time} sec")