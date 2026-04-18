"""Config flow for Weishaupt Heat Pump integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import callback

from .const import (
    CONF_CONNECTION_TYPE,
    CONF_EBUSD_CIRCUIT,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_EBUSD_PORT,
    DEFAULT_HOST,
    DEFAULT_HTTP_PORT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    ConnectionType,
)

_LOGGER = logging.getLogger(__name__)

# Step 1: Choose connection type
STEP_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONNECTION_TYPE, default=ConnectionType.EBUSD): vol.In(
            {
                ConnectionType.EBUSD: "ebusd (eBUS Adapter — Gas-Brennwert / WTC)",
                ConnectionType.WCM_HTTP: "WCM-COM HTTP (Gas-Brennwert / WTC)",
                ConnectionType.MODBUS_TCP: "Modbus TCP (Wärmepumpe / WBB)",
            }
        ),
    }
)

# Step 2a: Modbus TCP connection details
STEP_MODBUS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.Coerce(int),
    }
)

# Step 2b: WCM-COM HTTP connection details
STEP_WCM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_HTTP_PORT): vol.Coerce(int),
        vol.Required(CONF_USERNAME, default="admin"): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

# Step 2c: ebusd TCP connection details
STEP_EBUSD_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="localhost"): str,
        vol.Required(CONF_PORT, default=DEFAULT_EBUSD_PORT): vol.Coerce(int),
        vol.Optional(CONF_EBUSD_CIRCUIT, default=""): str,
    }
)


class WeishauptConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Weishaupt Heat Pump."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._connection_type: ConnectionType | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle step 1 — choose connection type."""
        if user_input is not None:
            self._connection_type = ConnectionType(user_input[CONF_CONNECTION_TYPE])
            if self._connection_type == ConnectionType.MODBUS_TCP:
                return await self.async_step_modbus()
            if self._connection_type == ConnectionType.EBUSD:
                return await self.async_step_ebusd()
            return await self.async_step_wcm()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_TYPE_SCHEMA,
        )

    async def async_step_modbus(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle Modbus TCP connection setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            slave_id = user_input[CONF_SLAVE_ID]

            from weishaupt_modbus import WeishauptModbusClient
            from weishaupt_modbus.exceptions import WeishauptConnectionError

            client = WeishauptModbusClient(host=host, port=port, slave_id=slave_id)
            try:
                await client.async_identify_device()
                await client.disconnect()
            except WeishauptConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during Modbus connection test")
                errors["base"] = "unknown"
            else:
                unique_id = f"weishaupt_{host}_{port}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Weishaupt WP ({host})",
                    data={
                        **user_input,
                        CONF_CONNECTION_TYPE: ConnectionType.MODBUS_TCP,
                    },
                )

        return self.async_show_form(
            step_id="modbus",
            data_schema=STEP_MODBUS_SCHEMA,
            errors=errors,
        )

    async def async_step_wcm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle WCM-COM HTTP connection setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            from weishaupt_modbus import WeishauptWCMClient
            from weishaupt_modbus.exceptions import WeishauptConnectionError

            client = WeishauptWCMClient(
                host=host, port=port, username=username, password=password
            )
            try:
                success = await client.async_test_connection()
                if not success:
                    errors["base"] = "cannot_connect"
                else:
                    device_info = await client.async_identify_device()
                    await client.disconnect()
            except WeishauptConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during WCM-COM connection test")
                errors["base"] = "unknown"

            if not errors:
                unique_id = f"weishaupt_wcm_{host}_{port}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                title = device_info.device_name or f"Weishaupt WTC ({host})"
                return self.async_create_entry(
                    title=title,
                    data={
                        **user_input,
                        CONF_CONNECTION_TYPE: ConnectionType.WCM_HTTP,
                    },
                )

        return self.async_show_form(
            step_id="wcm",
            data_schema=STEP_WCM_SCHEMA,
            errors=errors,
        )

    async def async_step_ebusd(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle ebusd TCP connection setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            circuit = user_input.get(CONF_EBUSD_CIRCUIT, "")

            from weishaupt_modbus import WeishauptEbusdClient
            from weishaupt_modbus.exceptions import WeishauptConnectionError

            client = WeishauptEbusdClient(host=host, port=port, circuit=circuit)
            try:
                success = await client.async_test_connection()
                if not success:
                    errors["base"] = "cannot_connect"
                else:
                    device_info = await client.async_identify_device()
                    await client.disconnect()
            except WeishauptConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during ebusd connection test")
                errors["base"] = "unknown"

            if not errors:
                unique_id = f"weishaupt_ebusd_{host}_{port}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                title = device_info.device_name or f"Weishaupt WTC ({host})"
                return self.async_create_entry(
                    title=title,
                    data={
                        **user_input,
                        CONF_CONNECTION_TYPE: ConnectionType.EBUSD,
                    },
                )

        return self.async_show_form(
            step_id="ebusd",
            data_schema=STEP_EBUSD_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return WeishauptOptionsFlow()


class WeishauptOptionsFlow(OptionsFlow):
    """Handle options for Weishaupt Heat Pump."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current_interval
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                }
            ),
        )
