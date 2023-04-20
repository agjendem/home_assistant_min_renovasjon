from datetime import timedelta, datetime, date
import logging

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from ..min_renovasjon import DATA_MIN_RENOVASJON

_LOGGER = logging.getLogger(__name__)

CONF_FRACTION_ID = "fraction_id"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_FRACTION_ID): vol.All(cv.ensure_list),
    }
)

SCAN_INTERVAL = timedelta(minutes=30)


def setup_platform(hass, config, add_entities, discovery_info=None):
    fraction_ids = config.get(CONF_FRACTION_ID)
    min_renovasjon = hass.data[DATA_MIN_RENOVASJON]

    add_entities(
        MinRenovasjonSensor(min_renovasjon, fraction_id) for fraction_id in fraction_ids
    )
    add_entities(
        MinRenovasjonWasteCollectionDaySensor(min_renovasjon, fraction_id) for fraction_id in fraction_ids
    )
    add_entities(
        MinRenovasjonWasteCollectionDayTomorrowSensor(min_renovasjon, fraction_id) for fraction_id in fraction_ids
    )


class MinRenovasjonSensor(Entity):
    def __init__(self, min_renovasjon, fraction_id):
        """Initialize with API object, device id."""
        self._min_renovasjon = min_renovasjon
        self._fraction_id = fraction_id

    @property
    def name(self):
        """Return the name of the fraction if any."""
        fraction = self._min_renovasjon.get_calender_for_fraction(self._fraction_id)
        if fraction is not None:
            return fraction[1]

    @property
    def state(self):
        """Return the state/date of the fraction."""
        fraction = self._min_renovasjon.get_calender_for_fraction(self._fraction_id)
        if fraction is not None:
            return self._min_renovasjon.format_date(fraction[3])

    @property
    def entity_picture(self):
        """Symbol."""
        fraction = self._min_renovasjon.get_calender_for_fraction(self._fraction_id)
        if fraction is not None:
            return fraction[2]

    def update(self):
        """Update calendar."""
        self._min_renovasjon.refresh_calendar()


class MinRenovasjonWasteCollectionDaySensor(BinarySensorEntity):
    """Representation of a BinarySensor for waste collection day."""
    _attr_has_entity_name = True

    def __init__(self, min_renovasjon, fraction_id):
        """Initialize with API object, device id."""
        self._min_renovasjon = min_renovasjon
        self._fraction_id = fraction_id

    @property
    def name(self):
        """Return the name of the fraction if any."""
        fraction = self._min_renovasjon.get_calender_for_fraction(self._fraction_id)
        if fraction is not None:
            return f'{fraction[1]}_waste_collection_day_today'

    @property
    def is_on(self) -> bool | None:
        fraction = self._min_renovasjon.get_calender_for_fraction(self._fraction_id)
        if fraction is not None:
            first_waste_collection_day = fraction[3]
            second_waste_collection_day = fraction[4]
            trigger_date = self._get_trigger_date()

            return self._is_same_date(trigger_date, first_waste_collection_day) \
                or self._is_same_date(trigger_date, second_waste_collection_day)

    @staticmethod
    def _is_same_date(as_date: date, waste_collection_date: datetime | None) -> bool | None:
        if waste_collection_date:
            return waste_collection_date.date() == as_date

    @staticmethod
    def _get_trigger_date() -> date:
        return datetime.today().date()

    @property
    def entity_picture(self):
        """Symbol."""
        fraction = self._min_renovasjon.get_calender_for_fraction(self._fraction_id)
        if fraction is not None:
            return fraction[2]

    def update(self):
        """Update calendar."""
        self._min_renovasjon.refresh_calendar()


class MinRenovasjonWasteCollectionDayTomorrowSensor(MinRenovasjonWasteCollectionDaySensor):

    @property
    def name(self):
        """Return the name of the fraction if any."""
        fraction = self._min_renovasjon.get_calender_for_fraction(self._fraction_id)
        if fraction is not None:
            return f'{fraction[1]}_waste_collection_day_tomorrow'

    @staticmethod
    def _get_trigger_date() -> date:
        tomorrow = datetime.today() + timedelta(days=1)
        return tomorrow.date()
