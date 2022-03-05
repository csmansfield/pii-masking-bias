from pii_benchmarking import pii_engine

test_string = "Lindsey was very kind and helpful!"
masked_test_string = "******* was very kind and helpful!"

test_list = ["Courtney is writing some test cases", "That's Leanne she's cool", "Lindsey was very kind and helpful!"]


def test_pii(engine_name):
    masker = pii_engine.Masker(engine_name)
    masked_string = masker.mask_text(test_string)
    return masked_string


def test_batch(engine_name):
    masker = pii_engine.Masker(engine_name)
    masked_list = masker.batch_mask(test_list)
    return masked_list


print(test_batch('aws'))
print(test_batch('gcp'))
print(test_batch('presidio'))

