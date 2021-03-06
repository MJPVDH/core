"""Support for Tile device trackers."""
import logging

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SOURCE_TYPE_GPS
from homeassistant.core import callback

from . import DATA_COORDINATOR, DOMAIN, TileEntity

_LOGGER = logging.getLogger(__name__)

ATTR_ALTITUDE = "altitude"
ATTR_CONNECTION_STATE = "connection_state"
ATTR_IS_DEAD = "is_dead"
ATTR_IS_LOST = "is_lost"
ATTR_RING_STATE = "ring_state"
ATTR_VOIP_STATE = "voip_state"
ATTR_TILE_NAME = "tile_name"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Tile device trackers."""
    coordinator = hass.data[DOMAIN][DATA_COORDINATOR][config_entry.entry_id]

    async_add_entities(
        [
            TileDeviceTracker(coordinator, tile_uuid, tile)
            for tile_uuid, tile in coordinator.data.items()
        ]
    )


class TileDeviceTracker(TileEntity, TrackerEntity):
    """Representation of a network infrastructure device."""

    def __init__(self, coordinator, tile_uuid, tile):
        """Initialize."""
        super().__init__(coordinator)
        self._name = tile["name"]
        self._tile = tile
        self._tile_uuid = tile_uuid
        self._unique_id = f"tile_{tile_uuid}"

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success and not self._tile["is_dead"]

    @property
    def battery_level(self):
        """Return the battery level of the device.

        Percentage from 0-100.
        """
        return None

    @property
    def location_accuracy(self):
        """Return the location accuracy of the device.

        Value in meters.
        """
        state = self._tile["last_tile_state"]
        h_accuracy = state.get("h_accuracy")
        v_accuracy = state.get("v_accuracy")

        if h_accuracy is not None and v_accuracy is not None:
            return round(
                (
                    self._tile["last_tile_state"]["h_accuracy"]
                    + self._tile["last_tile_state"]["v_accuracy"]
                )
                / 2
            )

        if h_accuracy is not None:
            return h_accuracy

        if v_accuracy is not None:
            return v_accuracy

        return None

    @property
    def latitude(self) -> float:
        """Return latitude value of the device."""
        return self._tile["last_tile_state"]["latitude"]

    @property
    def longitude(self) -> float:
        """Return longitude value of the device."""
        return self._tile["last_tile_state"]["longitude"]

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    @callback
    def _update_from_latest_data(self):
        """Update the entity from the latest data."""
        self._tile = self.coordinator.data[self._tile_uuid]
        self._attrs[ATTR_ALTITUDE] = self._tile["last_tile_state"]["altitude"]
        self._attrs[ATTR_IS_LOST] = self._tile["last_tile_state"]["is_lost"]
        self._attrs[ATTR_RING_STATE] = self._tile["last_tile_state"]["ring_state"]
        self._attrs[ATTR_VOIP_STATE] = self._tile["last_tile_state"]["voip_state"]
