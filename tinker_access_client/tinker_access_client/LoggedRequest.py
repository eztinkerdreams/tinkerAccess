import requests
from retry import retry
from ClientLogger import ClientLogger

_retry = -1

# TODO: add retry logic and automatically increase timeout on retries see:https://pypi.python.org/pypi/retrying
class LoggedRequest(object):

    @staticmethod
    def get(url, params=None, **kwargs):
        logger = ClientLogger.setup()

        try:
            response = LoggedRequest.__get(url,  params, **kwargs)

        except Exception as e:
            logger.debug('API request failed\n\turl: %s\n\tparams: %s\n\tkwargs: %s.', url, params, kwargs)
            logger.exception(e)
            raise e

        return response

    #TODO: refactor the logger.setup call which is breaking unit tests...

    @staticmethod
    @retry(tries=4, delay=1, backoff=2) #logger=ClientLogger.setup())
    def __get(url, params=None, **kwargs):
        # global _retry
        # _retry += 1
        # if _retry < 3:
        #     raise ZeroDivisionError
        # _retry = -1

        response = requests.get(url, params, timeout=5, **kwargs)
        response.raise_for_status()
        return response

