import { Box, Button, Card, Popover, Spinner } from "@radix-ui/themes";
import { useDrag } from "react-dnd";
import { yrdzst } from "app/fonts";

interface Character {
  simplified: string;
  traditional: string;
  rank: number;
  definitions: Definition[];
}

interface Definition {
  pinyin: string;
  text: string;
}
export default function HanziCard({ character }: { character?: Character }) {
  const [collected, drag, dragPreview] = useDrag(() => ({
    type: "card",
    item: { id: 0 },
  }));

  return (
    <Card ref={dragPreview}>
      {character ? (
        <Box className="text-center space-y-16 p-10">
          <div className={`text-8xl ${yrdzst.className}`}>
            {character.simplified}
          </div>
          <Popover.Root>
            <Popover.Trigger>
              <Button variant="soft">Definition</Button>
            </Popover.Trigger>
            <Popover.Content align="center">
              <Box>
                {character.definitions.map((def, index) => (
                  <div key={index}>
                    {def.pinyin}: {def.text}
                  </div>
                ))}
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
