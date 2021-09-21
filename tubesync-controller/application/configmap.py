import kubernetes
import kopf
import pathlib
from datetime import datetime, timezone
from kubernetes.client.rest import ApiException
from ..labels import Labels
from yaml import load, Loader
from jinja2 import Environment, FileSystemLoader, select_autoescape
from os.path import join
from more_itertools import one

PREFIX = "controllers.illallangi.enterprises"
COMPONENT = "application"
CRD_GROUP = "controllers.illallangi.enterprises"
CRD_VERSION = "v1"
CRD_SINGULAR = "tubesync"
CRD_PLURAL = "tubesyncs"
LABEL_COMPONENT = "app.kubernetes.io/component"
LABEL_CONTROLLER = "app.kubernetes.io/controller"
LABEL_INSTANCE = "app.kubernetes.io/instance"
LABEL_NAME = "app.kubernetes.io/name"

CONTROLLER="application-configmap"

env = Environment(
    loader=FileSystemLoader(pathlib.Path(__file__).parent.absolute()),
    autoescape=select_autoescape(),
)
env.filters["path_join"] = lambda paths: join(*paths)


@kopf.index(
    "configmap",
    labels={
        LABEL_CONTROLLER: CONTROLLER,
        LABEL_NAME: CRD_SINGULAR,
    },
)
async def application_configmap_idx(
    namespace,
    body,
    **_,
):
    return {
        namespace: {k: body[k] for k in body},
    }


@kopf.on.probe(
    id=application_configmap_idx.__name__,
)
async def application_configmap_probe(
    application_configmap_idx: kopf.Index,
    **_,
):
    return {
        namespace: {
            o["metadata"]["name"]: o for o in application_configmap_idx[namespace]
        }
        for namespace in application_configmap_idx
    }


@kopf.on.create(CRD_GROUP, CRD_VERSION, CRD_SINGULAR)
@kopf.on.update(CRD_GROUP, CRD_VERSION, CRD_SINGULAR)
@kopf.on.resume(CRD_GROUP, CRD_VERSION, CRD_SINGULAR)
async def application_configmap(
    namespace,
    body,
    patch,
    **kwargs,
):
    api = kubernetes.client.CoreV1Api()

    # Define the object label
    label = Labels(
        **{
            LABEL_NAME: CRD_SINGULAR,
            LABEL_INSTANCE: body["metadata"]["name"],
            LABEL_COMPONENT: COMPONENT,
            LABEL_CONTROLLER: CONTROLLER,
        }
    )

    # Check if required objects are created yet
    for kind in []:
        try:
            kwargs["_".join(kind)] = one(
                [
                    o
                    for o in kwargs[f"{kind[0]}_{kind[1]}_idx"][namespace]
                    if o["metadata"]["name"]
                    == body["status"][f"{kind[0]}-{kind[1]}"]["name"]
                ]
            )
        except KeyError:
            # Save status
            patch.status[CONTROLLER] = {
                "name": None,
                "processed": datetime.now(timezone.utc).isoformat(),
                "status": f"Waiting for {kind[0]} {kind[1]} creation",
            }
            # raise temporary error
            raise kopf.TemporaryError(f"{kind[0]} {kind[1]} not created yet", delay=15)

    # Define the object
    body = (
        load(
            env.get_template("configmap.yaml.j2").render(
                namespace=namespace,
                selector=label.but(
                    LABEL_CONTROLLER,
                ).asdict,
                **kwargs,
            ),
            Loader=Loader,
        )
        or {}
    )
    kopf.adopt(body)

    # Ugly hack to disable controller
    body["metadata"]["ownerReferences"][0]["controller"] = False

    kopf.label(
        body,
        label.but(),
        forced=True,
    )
    kopf.harmonize_naming(
        body,
        label.but(
            LABEL_CONTROLLER,
        ).asname,
        forced=True,
        strict=True,
    )

    # Patch existing object
    obj = None
    try:
        obj = api.patch_namespaced_config_map(
            namespace=namespace,
            name=body["metadata"]["name"],
            body=body,
        )
    except ApiException as ex:
        if ex.status != 404:
            raise

    # Create new object
    if obj is None:
        try:
            obj = api.create_namespaced_config_map(
                namespace=namespace,
                body=body,
            )
        except ApiException as ex:
            if ex.status != 409:
                raise
            # Save status
            patch.status[CONTROLLER] = {
                "name": None,
                "processed": datetime.now(timezone.utc).isoformat(),
                "status": "HTTP 409 Conflict; retrying in 15 seconds.",
            }
            # raise temporary error
            raise kopf.TemporaryError(
                "HTTP 409 Conflict; retrying in 15 seconds.", delay=15
            )

    # Save status
    patch.status[CONTROLLER] = {
        "name": obj.metadata.name,
        "processed": datetime.now(timezone.utc).isoformat(),
        "status": "OK",
    }
