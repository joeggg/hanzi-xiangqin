import Image from "next/image";

import { isMobile } from "@/app/tools/misc";
import SettingsMenu from "./menu";

export default async function Footer() {
  const isMb = await isMobile();
  const justify = isMb ? "between" : "center";

  return (
    <footer
      className={`row-start-3 flex gap-6 flex-wrap items-center justify-${justify}`}
    >
      {isMb ? (
        <div className="flex-1 p-2">
          <SettingsMenu />
        </div>
      ) : null}
      <a
        className="flex items-center gap-2 hover:underline hover:underline-offset-4"
        href="https://github.com/joeggg/hanzi-xiangqin"
        target="_blank"
        rel="noopener noreferrer"
      >
        <Image
          aria-hidden
          src="/file.svg"
          alt="File icon"
          width={16}
          height={16}
        />
        View Source
      </a>
      {isMb ? <div className="flex-1 p-2" /> : null}
    </footer>
  );
}
