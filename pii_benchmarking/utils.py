import socket
import time


MASK_CHAR = '*'
NAME_ENT_LABEL = 'PERSON_NAME'


def get_standardized_result(engine_name, text, entities):
    return {'service': engine_name, 'input': text, 'masked_input': mask_text(text, entities), 'results': entities}


def mask_text(text, entities):
    for ent in entities:
        text = text[:ent['start_char']] + MASK_CHAR*(ent['end_char'] - ent['start_char']) + text[ent['end_char']:]
    return text


def standardized_person_ent(entity):
    if entity['entity_label'].lower() in ['name', 'person', 'person_name']:
        entity['entity_label'] = NAME_ENT_LABEL
    return entity


def poll_api(success_status, api_get_status, *args, tries=15, initial_delay=10, delay=1, backoff=2):
    print('Polling for PII job...')
    time.sleep(initial_delay)
    for n in range(tries):
        try:
            status = api_get_status(*args)
            print(f"Attempt {n}: {status}", flush=True)
            if status != success_status:
                time.sleep(delay)
                delay *= backoff
            else:
                return status
        except socket.error as e:
            print(f"Connection dropped with error code {e.errno}")
    raise TimeoutError(f"Failed to poll within {tries}")
