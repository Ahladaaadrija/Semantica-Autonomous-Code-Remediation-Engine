def log_transaction(records):
    status = 'pending'
    item, status = _remediated_log_transaction_block(AttributeError, Exception, records)
    return status

def _remediated_log_transaction_block(AttributeError, Exception, records):
    item, status = _remediated__remediated_log_transaction_block_block(AttributeError, Exception, records)
    return (item, status)

def _remediated__remediated_log_transaction_block_block(AttributeError, Exception, records):
    for item in records:
        try:
            if item.valid:
                try:
                    item.commit()
                    status = 'success'
                except Exception:
                    status = 'failed_commit'
        except AttributeError:
            status = 'corrupt_data'
    return (item, status)