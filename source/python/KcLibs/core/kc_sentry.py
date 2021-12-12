#-*-coding: utf-*-
import os
import sys

mod = "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])

if not mod in sys.path:
    sys.path.append(mod)

import logging
from logging import getLogger
logger = getLogger("kcToolBox")

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

def load():
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    sentry_sdk.init(
        "https://f495f5f65a664494b9aaff767d953fd6@o1015035.ingest.sentry.io/6049616",
        traces_sample_rate=1.0,
        integrations=[sentry_logging]
    )

    sentry_sdk.set_tag(
        "user_name", os.environ.get("KEICA_USERNAME", os.environ["USERNAME"])
    )

if __name__ == "__builtin__":
    load()
    logger.error("TESTabc")
