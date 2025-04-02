import random
import time

# Initialize resources and users
num_resources = random.randint(1, 5)
print(f"Random Resources: {num_resources}")
# resources = [] 
# for i in range(num_resources):  # Loop from 0 to num_resources - 1
#     resource_name = f"Resource {i+1}"  # Format the string
#     resources.append(resource_name)  # Add the formatted string to the list
resources = [f"Resource {i+1}" for i in range(num_resources)]

num_users = random.randint(1, 10)
print(f"Random Users: {num_users}")
users = [f"User {i+1}" for i in range(num_users)]

# Assign random resources and usage times to each user
user_resource_time = {
    user: [(resource, random.randint(1, 15)) for resource in sorted(random.sample(resources, random.randint(1, len(resources))))] 
    for user in users
}

print(f"{user_resource_time}")

# Initialize tracking dictionaries
resource_status = {resource: [] for resource in resources}  # Active users on resource
resource_waiting = {resource: [] for resource in resources}  # Waiting queue

# Populate initial resource status
for user, assigned_resources in user_resource_time.items():
    for resource, time_left in assigned_resources:
        if len(resource_status[resource]) < 3:  # Limit 2 users per resource
            resource_status[resource].append((user, time_left))
        else:
            resource_waiting[resource].append((user, time_left))

# Simulation loop
current_time = 0
while any(resource_status.values()) or any(resource_waiting.values()):  # Run until all resources are free
    print(f"\n⏳ Time: {current_time} sec")

    # Decrement time for users currently using resources
    for resource, users_info in list(resource_status.items()):
        new_users_info = []
        for user, time_left in users_info:
            if time_left > 1:
                new_users_info.append((user, time_left - 1))
            else:
                print(f"✅ {user} finished using {resource}")
        
        resource_status[resource] = new_users_info  # Update resource status

    # Move waiting users to active users if space is available
    for resource, waiting_list in list(resource_waiting.items()):
        ongoing_users = sorted(resource_status[resource], key=lambda x: x[1])  # Sort by time left

        while len(resource_status[resource]) < 3 and waiting_list:
            next_user, usage_time = waiting_list.pop(0)
            if ongoing_users:   # Earliest free slot
              available_in = ongoing_users[0][1]  # Get the time of the first user
            else:
              available_in = 0  # If no users, set to 0

            print(f"➡️ {next_user} starts using {resource} in {usage_time} sec")
            
            # Add new user to the resource
            resource_status[resource].append((next_user, usage_time))
            # resource_status[resource].append((next_user, usage_time))

            # Keep the list sorted
            resource_status[resource].sort(key=lambda x: x[1])

    # Display resource status
    print("\n📌 Resource Status:")
    for resource, users_info in resource_status.items():
        if users_info:
            print(f"{resource}:")
            for user, time_left in users_info:
                print(f"  - Used by {user}, Time Left: {time_left} sec")

    # Display waiting users
    print("\n⏳ Users in Waiting:")
    for resource, waiting_list in resource_waiting.items():
        if waiting_list:
            print(f"{resource}:")

            # Get a sorted list of ongoing users based on their remaining time
            ongoing_users = sorted(resource_status[resource], key=lambda x: x[1])  # Sort by time left
            available_in = 0  # When the first waiting user will start

            # Process waiting users in order
            for user, usage_time in waiting_list:
                if ongoing_users:  # Check if any active user is finishing
                    finished_user, finished_time = ongoing_users.pop(0)  # Remove the first finishing user
                    available_in = finished_time  # This user starts when the slot becomes free

                print(f"- {user} is waiting, will start in {available_in} sec")

                # Add this user to the active list with their new time
                ongoing_users.append((user, available_in + usage_time))
                # ongoing_users.append((user, usage_time))

                # Keep the ongoing list sorted for the next iteration
                ongoing_users.sort(key=lambda x: x[1])  # Sort by new finish time


    # Calculate when resources will be free
    resource_free_time = {}
    for resource, users_info in resource_status.items():
        max_ongoing_time = max((time_left for _, time_left in users_info), default=0)
        max_waiting_time = max((wait_time for _, wait_time in resource_waiting.get(resource, [])), default=0)
        resource_free_time[resource] = max_ongoing_time + max_waiting_time

    # Display resource free times
    print("\n✅ Resource Free Time:")
    for resource, free_time in resource_free_time.items():
        print(f"{resource} will be free in {free_time} sec" if free_time else f"{resource} is free")

    # Pause for realism
    time.sleep(1)
    current_time += 1

print("\n🎉 All resources are now free!")
