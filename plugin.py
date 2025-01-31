import asyncio
import decky_plugin

class Plugin:
    def __init__(self):
        self.active = True

    async def _main(self):
        """Main loop for the plugin."""
        while self.active:
            print("Plugin is running...")
            await asyncio.sleep(2)

    async def enable(self):
        """Enable the plugin."""
        self.active = True
        print("Plugin enabled.")
        return "Plugin Enabled"

    async def disable(self):
        """Disable the plugin."""
        self.active = False
        print("Plugin disabled.")
        return "Plugin Disabled"

    async def toggle(self):
        """Toggle plugin activity."""
        self.active = not self.active
        print(f"Plugin toggled. Active: {self.active}")
        return f"Toggled to {'enabled' if self.active else 'disabled'}"

    async def get_status(self):
        """Return the plugin's status."""
        return {"active": self.active}
