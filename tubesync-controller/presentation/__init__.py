from .service import (
    presentation_service,
    presentation_service_probe,
    presentation_service_idx,
)

from .configmap import (
    presentation_configmap,
    presentation_configmap_probe,
    presentation_configmap_idx,
)

from .serviceaccount import (
    presentation_serviceaccount,
    presentation_serviceaccount_probe,
    presentation_serviceaccount_idx,
)

from .deployment import (
    presentation_deployment,
    presentation_deployment_probe,
    presentation_deployment_idx,
)

from .dnsrpzrecord import (
    presentation_dnsrpzrecord,
    presentation_dnsrpzrecord_probe,
    presentation_dnsrpzrecord_idx,
)

__all__ = [
    "presentation_service",
    "presentation_service_probe",
    "presentation_service_idx",
    "presentation_configmap",
    "presentation_configmap_probe",
    "presentation_configmap_idx",
    "presentation_serviceaccount",
    "presentation_serviceaccount_probe",
    "presentation_serviceaccount_idx",
    "presentation_deployment",
    "presentation_deployment_probe",
    "presentation_deployment_idx",
    "presentation_dnsrpzrecord",
    "presentation_dnsrpzrecord_probe",
    "presentation_dnsrpzrecord_idx",
]
