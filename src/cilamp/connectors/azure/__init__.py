"""Azure Resource Manager connector implementations."""

from cilamp.connectors.azure.arm import AzureResourceManagerConnector
from cilamp.connectors.azure.base import AzureConnector, AzureConnectorError
from cilamp.connectors.azure.simulation import SimulationAzureConnector

__all__ = (
    "AzureConnector",
    "AzureConnectorError",
    "AzureResourceManagerConnector",
    "SimulationAzureConnector",
)
