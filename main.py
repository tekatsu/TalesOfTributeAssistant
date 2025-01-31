import asyncio
import decky_plugin
import decky.logger

class Plugin:
    def __init__(self):
        self.active = True
        self.last_suggestion = "AI Thinking..."
        decky.logger.info("Tales of Tribute Assistant Plugin Initialized")

    async def _main(self):
        """Main loop for the plugin."""
        while self.active:
            decky.logger.info("Plugin is running...")
            await asyncio.sleep(2)

    async def enable(self):
        """Enable the plugin."""
        self.active = True
        decky.logger.info("Plugin enabled.")
        return "Plugin Enabled"

    async def disable(self):
        """Disable the plugin."""
        self.active = False
        decky.logger.info("Plugin disabled.")
        return "Plugin Disabled"

    async def toggle(self):
        """Toggle plugin activity."""
        self.active = not self.active
        decky.logger.info(f"Plugin toggled. Active: {self.active}")
        return f"Toggled to {'enabled' if self.active else 'disabled'}"

    async def get_status(self):
        """Return the plugin's status."""
        return {"active": self.active}
