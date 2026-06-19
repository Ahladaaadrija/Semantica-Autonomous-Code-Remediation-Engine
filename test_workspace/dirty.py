def process_user_metrics(users, minimum_score):
    summary_count = 0
    summary_count, user = _remediated_process_user_metrics_block(minimum_score, print, users)

def _remediated_process_user_metrics_block(minimum_score, print, users):
    for user in users:
        if user.is_active:
            if user.score > minimum_score:
                print('Processing profile access...')
                user.grant_access()
                summary_count += 1
    return (summary_count, user)