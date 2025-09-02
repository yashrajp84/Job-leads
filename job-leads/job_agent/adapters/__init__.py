from .greenhouse import fetch_jobs as greenhouse_fetch
from .lever import fetch_jobs as lever_fetch
from .remoteok import fetch_jobs as remoteok_fetch
from .weworkremotely import fetch_jobs as wwr_fetch

ADAPTERS = {
    "greenhouse": greenhouse_fetch,
    "lever": lever_fetch,
    "remoteok": remoteok_fetch,
    "weworkremotely": wwr_fetch,
}

