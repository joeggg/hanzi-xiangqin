import { Box, Button, Card, Popover, Spinner } from "@radix-ui/themes";
import { yrdzst } from "app/fonts";

import type { Character } from "@/app/types/character";

export default function HanziCard({ character }: { character?: Character }) {
  return (
    <Card>
      <Box className="text-center space-y-16 p-10">
        {character ? (
          <div className={`text-8xl ${yrdzst.className}`}>
            {character.simplified}
          </div>
        ) : (
          <Spinner className="p-12" />
        )}
        <Popover.Root>
          <Popover.Trigger>
            <Button variant="soft">Definition</Button>
          </Popover.Trigger>
          <Popover.Content align="center" maxWidth="300px">
            {character && (
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
            )}
          </Popover.Content>
        </Popover.Root>
      </Box>
    </Card>
  );
}
