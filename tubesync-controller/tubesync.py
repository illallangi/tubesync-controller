import kopf

CRD_GROUP = "controllers.illallangi.enterprises"
CRD_VERSION = "v1"
CRD_SINGULAR = "tubesync"


@kopf.index(
    group=CRD_GROUP,
    version=CRD_VERSION,
    singular=CRD_SINGULAR,
)
async def tubesync_idx(
    namespace,
    body,
    **_,
):
    return {
        namespace: {k: body[k] for k in body},
    }


@kopf.on.probe(
    id=tubesync_idx.__name__,
)
async def tubesync_probe(
    tubesync_idx: kopf.Index,
    **_,
):
    return {
        namespace: [o for o in tubesync_idx[namespace]]
        for namespace in tubesync_idx
    }
