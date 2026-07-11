"""Button entities for SamsungAC-PRO."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SamsungClimateCoordinator

RESET_FILTER_OPERATION = "reset_filter"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SamsungAC-PRO button entities."""
    coordinator_data = hass.data[DOMAIN][entry.entry_id]
    coordinators = (
        list(coordinator_data.values())
        if isinstance(coordinator_data, dict)
        else [coordinator_data]
    )

    entities = []
    for coordinator in coordinators:
        operation = coordinator.controller.get_property_object(
            RESET_FILTER_OPERATION
        )
        if operation is not None:
            entities.append(SamsungResetFilterButton(coordinator))

    if entities:
        async_add_entities(entities)


class SamsungResetFilterButton(CoordinatorEntity, ButtonEntity):
    """Reset the legacy Samsung AC filter-cleaning timer."""

    _attr_has_entity_name = True
    _attr_name = "Reset filter timer"
    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator: SamsungClimateCoordinator) -> None:
        """Initialize the reset-filter button."""
        super().__init__(coordinator)
        self._controller = coordinator.controller
        self._attr_unique_id = f"{coordinator.unique_id}_reset_filter"
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Return whether the device is available."""
        return (
            self.coordinator.last_update_success
            and self._controller.available
        )

    async def async_press(self) -> None:
        """Send the momentary filter-reset command."""
        await self._controller.async_set_property(
            RESET_FILTER_OPERATION,
            "press",
        )
        await self.coordinator.async_request_refresh()
