"use client";

import { Box, Button, Card, Popover } from "@radix-ui/themes";
import { useParams, useRouter } from "next/navigation";
import { JSX, useCallback, useEffect, useState } from "react";

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

const newCard = (character: Character): JSX.Element => {
  return (
    <Card>
      <div className="font-semibold text-8xl text-center">
        {character.simplified}
      </div>
      <Popover.Root>
        <Popover.Trigger>
          <Button variant="soft">Definition</Button>
        </Popover.Trigger>
        <Popover.Content>
          <Box>
            {character.definitions.map((def, index) => (
              <div key={index}>{def.text}</div>
            ))}
          </Box>
        </Popover.Content>
      </Popover.Root>
    </Card>
  );
};

export default function TestPage() {
  const { id } = useParams();
  const [card, setCard] = useState<JSX.Element | null>(null);
  const router = useRouter();

  const nextCharacter = useCallback(async (): Promise<Character | null> => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BASE_URL}/tests/${id}/next`,
      );
      const data = await response.json();
      if (data && data.character) {
        return data.character as Character;
      }
      if (data.done) {
        router.push(`/test/${id}/results`);
      }
    } catch (error) {
      console.error(error);
    }
    return null;
  }, [id, router]);

  const submitAnswer = async () => {
    const character = await nextCharacter();
    if (character) {
      setCard(<div>{character.simplified}</div>);
    }
  };

  useEffect(() => {
    nextCharacter().then((character) => {
      if (character) {
        setCard(newCard(character));
      }
    });
  }, [nextCharacter]);

  return (
    <div className="items-center">
      <Box width="240px" height="400px" className="items-center">
        <button onClick={submitAnswer} className="items-center">
          {card}
        </button>
      </Box>
    </div>
  );
}
