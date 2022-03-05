from pii_benchmarking.interfaces import presidio, aws, gcp


class Masker:
    def __init__(self, engine='presidio'):
        self.engine = self._get_masker(engine)

    def mask_text(self, text):
        return self.engine.mask_text(text)

    def batch_mask(self, list_of_text):
        return self.engine.batch_mask(list_of_text)

    @staticmethod
    def _get_masker(engine_name):
        engine_name = engine_name.lower()
        try:
            if engine_name == 'presidio':
                return presidio.Masker()
            elif engine_name == 'aws':
                return aws.Masker()
            elif engine_name == 'gcp':
                return gcp.Masker()
            elif engine_name == 'lp':
                return lp.Masker()
            else:
                raise ValueError("Engine name not found.  Select engine: presidio, aws, gcp, lp")
        except NameError:
            raise NameError(f"Could not find {engine_name} library module.")


