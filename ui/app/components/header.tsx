import Link from "next/link";

import { isMobile } from "@/app/tools/misc";
import { yrdzst } from "@/app/fonts";
import SettingsMenu from "./menu";

export default async function Header() {
  const isMb = await isMobile();
  const justify = isMb ? "center" : "between";

  return (
    <header
      className={`row-start-1 flex justify-${justify} items-center ${yrdzst.className} text-4xl 
font-bold w-full`}
    >
      {!isMb ? (
        <div className="flex-1 flex justify-start">
          <SettingsMenu />
        </div>
      ) : null}
      <div className="flex gap-16">
        <h1 className="">
          <Link href="/">hanzi</Link>
          <br />
          <Link href="/">xiangqin</Link>
        </h1>
        <h1 className="text-justify">
          <Link href="/">汉字</Link>
          <br />
          <Link href="/">相亲</Link>
        </h1>
      </div>
      {!isMb ? <div className="flex-1" /> : null}
    </header>
  );
}
