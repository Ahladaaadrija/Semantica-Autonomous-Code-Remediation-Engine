def process_user_metrics(users, minimum_score):
    summary_count = 0
    
    # Layer 1 Nesting: A loop running through users
    for user in users: 
        
        # Layer 2 Nesting: An IF statement checking if active
        if user.is_active: 
            
            # Layer 3 Nesting: Another IF statement checking the score
            if user.score > minimum_score: 
                print("Processing profile access...")
                user.grant_access()
                summary_count += 1  # <-- Deeply nested mutation