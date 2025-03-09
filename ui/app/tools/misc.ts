import { headers } from "next/headers";
import { UAParser } from "ua-parser-js";

export const isMobile = async (): Promise<boolean> => {
  const { get } = await headers();
  const ua = get("user-agent");

  const device = new UAParser(ua || "").getDevice();
  return device.type === "mobile";
};
