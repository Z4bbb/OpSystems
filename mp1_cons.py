import random
import time

# Step 1: Generate a random number of resources (1-30)
num_resources = random.randint(1, 5)
resources = [f"Resource {i+1}" for i in range(num_resources)]
print(f"Random Resources: {num_resources}")
print(f"Resources: {resources}")

# Step 2: Generate a random number of users (1-30)
num_users = random.randint(1, 10)
users = [f"User {i+1}" for i in range(num_users)]
print(f"Random Users: {num_users}")
print(f"Users: {users}")

# Step 3: Assign random resources and usage times to each user
# Each user will request a random subset of resources in chronological order
user_resource_time = {
    user: [(resource, random.randint(1, 15)) for resource in sorted(random.sample(resources, random.randint(1, len(resources))))] 
    for user in users
}


# Print the generated user-resource-time assignments
print("\nUser Resource Requests:")
for user, requests in user_resource_time.items():
    print(f"{user}: {requests}")

# Initialize tracking dictionaries
resource_status = {resource: None for resource in resources}  # Active user on resource (user, time_left)
resource_waiting = {resource: [] for resource in resources}  # Waiting queue for each resource

# Populate the waiting queues for each resource
for user, requests in user_resource_time.items():
    for resource, time_needed in requests:
        resource_waiting[resource].append((user, time_needed))

# Simulation loop
current_time = 0
while any(resource_status.values()) or any(resource_waiting.values()):  # Run until all resources are free
    print(f"\n⏳ Time: {current_time} sec")

    # Step 4: Decrement time for users currently using resources
    for resource, user_info in list(resource_status.items()):
        if user_info:
            user, time_left = user_info
            if time_left > 1:
                resource_status[resource] = (user, time_left - 1)
            else:
                print(f"✅ {user} finished using {resource}")
                resource_status[resource] = None

    # Step 5: Move waiting users to active users if space is available
    for resource, waiting_list in list(resource_waiting.items()):
        if not resource_status[resource] and waiting_list:
            next_user, usage_time = waiting_list.pop(0)
            print(f"➡️ {next_user} starts using {resource} for {usage_time} sec")
            resource_status[resource] = (next_user, usage_time)

    # Display resource status
    print("\n📌 Resource Status:")
    for resource, user_info in resource_status.items():
        if user_info:
            user, time_left = user_info
            print(f"{resource}: Used by {user}, Time Left: {time_left} sec")
        else:
            print(f"{resource}: Free")

    # Display waiting users
    print("\n⏳ Users in Waiting:")
    for resource, waiting_list in resource_waiting.items():
        if waiting_list:
            print(f"{resource}:")
            for user, usage_time in waiting_list:
                # Calculate when the user will start using the resource
                if resource_status[resource]:
                    start_time = resource_status[resource][1]  # Time left for the current user
                else:
                    start_time = 0  # Resource is free
                print(f"- {user} is waiting, will start in {start_time} sec")

    # Step 6: Calculate when resources will be free
    resource_free_time = {}
    for resource, user_info in resource_status.items():
        if user_info:
            # Time left for the current user
            time_left = user_info[1]
            # Sum of usage times for all waiting users
            waiting_time = sum(time for _, time in resource_waiting[resource])
            # Total time until the resource is free
            resource_free_time[resource] = time_left + waiting_time
        else:
            resource_free_time[resource] = 0  # Resource is already free

    # Display resource free times
    print("\n✅ Resource Free Time:")
    for resource, free_time in resource_free_time.items():
        if free_time > 0:
            print(f"{resource} will be free in {free_time} sec")
        else:
            print(f"{resource} is free")

    # Pause for realism
    time.sleep(1)
    current_time += 1

print("\n🎉 All resources are now free!")