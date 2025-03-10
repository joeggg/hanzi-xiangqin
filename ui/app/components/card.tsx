import { Box, Button, Card, Popover, Spinner } from "@radix-ui/themes";
import { yrdzst } from "app/fonts";

import type { Character } from "@/app/types/character";

export default function HanziCard({ character }: { character?: Character }) {
  return (
    <Card>
      {character ? (
        <Box className="text-center space-y-16 p-10">
          <div className={`text-8xl ${yrdzst.className}`}>
            {character.simplified}
          </div>
          <Popover.Root>
            <Popover.Trigger>
              <Button variant="soft">Definition</Button>
            </Popover.Trigger>
            <Popover.Content align="center" maxWidth="300px">
              <Box>
                {character.definitions.length > 0 ? (
                  character.definitions.map((def, index) => (
                    <div key={index} className="text-wrap">
                      <strong>{def.pinyin}</strong>: {def.text}
                    </div>
                  ))
                ) : (
                  <div>Unable to find definition :(</div>
                )}
              </Box>
            </Popover.Content>
          </Popover.Root>
        </Box>
      ) : (
        <Box>
          <Spinner />
        </Box>
      )}
    </Card>
  );
}
