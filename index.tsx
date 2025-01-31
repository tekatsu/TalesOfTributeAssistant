import { useState } from "react";
import {
  PanelSection,
  PanelSectionRow,
  ButtonItem
} from "@decky/ui";
import { definePlugin } from "@decky/api";

function AssistantControl() {
  const [active, setActive] = useState<boolean>(true);

  const togglePlugin = async () => {
    setActive(!active);
    await fetch(`/api/toggle_plugin`);
  };

  return (
    <PanelSection>
      <PanelSectionRow>
        <ButtonItem layout="below" onClick={togglePlugin}>
          {active ? "Disable Assistant" : "Enable Assistant"}
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
}

export default definePlugin(() => ({
  name: "Tales of Tribute Assistant",
  content: <AssistantControl />,
}));
