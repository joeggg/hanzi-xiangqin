"use client";

import { getCookie, setCookie } from "cookies-next";
import { useRouter } from "next/navigation";
import { DropdownMenu, Button } from "@radix-ui/themes";

export default function SettingsMenu() {
  const router = useRouter();

  const toggleTheme = () => {
    const theme = getCookie("theme") || "light";
    const newTheme = theme === "light" ? "dark" : "light";
    setCookie("theme", newTheme);
    router.refresh();
  };

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        <Button variant="soft">
          Options
          <DropdownMenu.TriggerIcon />
        </Button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Content>
        <DropdownMenu.Item onClick={toggleTheme}>
          Toggle theme
        </DropdownMenu.Item>
        <DropdownMenu.Separator />
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  );
}
