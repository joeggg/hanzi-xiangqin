"use client";

import { Box, Flex, RadioCards, Text } from "@radix-ui/themes";
import { getCookie, setCookie } from "cookies-next";
import { NextFont } from "next/dist/compiled/@next/font";
import { useMemo } from "react";

import { ebas, fontquan, geistMono, tegakizatsu, yrdzst } from ".";

const fonts = [yrdzst, tegakizatsu, ebas, fontquan, geistMono];

export default function Fonts() {
  const changeFont = (font: NextFont) => {
    setCookie("font", font.className);
  };

  const currentFont = useMemo(
    () => (getCookie("font") as string) || yrdzst.className,
    [],
  );

  return (
    <Box>
      <Text weight={"medium"} size={"4"} align={"center"}>
        Please select a font:
      </Text>
      <Box maxWidth="600px">
        <RadioCards.Root
          defaultValue={currentFont}
          columns={{ initial: "1", sm: "3" }}
        >
          {fonts.map((font, index) => (
            <RadioCards.Item
              key={index}
              value={font.className}
              onClick={() => changeFont(font)}
            >
              <Flex direction="column" width="100%">
                <Text size={"8"} className={font.className}>
                  汉字相亲
                </Text>
                <Text size={"2"} align={"center"}>
                  {font.style.fontFamily.split(",")[0].replaceAll("'", "")}
                </Text>
              </Flex>
            </RadioCards.Item>
          ))}
        </RadioCards.Root>
      </Box>
    </Box>
  );
}
