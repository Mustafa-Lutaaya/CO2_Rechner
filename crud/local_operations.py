class LocalCRUD:
    # Update counts and CO2 value of an item from the local in-memory list.
    @staticmethod
    def update_item_count(items, item_name, action):
        for category in items:  # Loops through each item within the current category
            for item in category['items']: 
                if item['name'] == item_name: # If the item's name macthes submitted form value
                    # Updates item's count based on the action
                    if action == 'increment':
                        item['count'] += 1
                    elif action == 'decrement':
                        item['count'] = max(0, item['count'] - 1)
    
                    # Recalculates the total CO2 savings for the item using base_co2 as the fixed value and co2 as the updated total
                    item['co2'] = item['count'] * item['base_co2']
                    return # Stops after the item is updated

    # Resets locally displayed items
    @staticmethod
    def reset_items(items):
        for category in items:
            for item in category['items']:
                item['count'] = 0 # Resets local count to 0
                item['co2'] = 0  # Resets local CO2 to 0   