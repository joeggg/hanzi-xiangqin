"use client";

import { useParams, useRouter } from "next/navigation";
import { JSX, useCallback, useEffect, useState } from "react";
import { DndProvider } from "react-dnd";
import { TouchBackend } from "react-dnd-touch-backend";
import { Box, Button, Flex } from "@radix-ui/themes";

import HanziCard from "app/components/card";
import client from "app/tools/client";

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

export default function TestPage() {
  const { id } = useParams();
  const router = useRouter();

  const [card, setCard] = useState<JSX.Element>(<HanziCard />);

  const nextCharacter = useCallback(async (): Promise<Character | null> => {
    try {
      const response = await client.get(`/tests/${id}/next`);
      const data = response.data;
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

  const sendAnswer = useCallback(
    async (answer: boolean): Promise<undefined> => {
      try {
        await client.post(`/tests/${id}/answer?answer=${answer}`);
      } catch (error) {
        console.error(error);
        return;
      }

      setCard(<HanziCard />);

      // Small delay to wait for processing
      await new Promise((resolve) => setTimeout(resolve, 100));
      const character = await nextCharacter();
      if (character) {
        setCard(<HanziCard character={character} />);
        return;
      }
    },
    [id, nextCharacter],
  );

  const sendYes = useCallback(() => {
    sendAnswer(true);
  }, [sendAnswer]);

  const sendNo = useCallback(() => {
    sendAnswer(false);
  }, [sendAnswer]);

  useEffect(() => {
    nextCharacter().then((character) => {
      if (character) {
        setCard(<HanziCard character={character} />);
      }
    });
  }, [nextCharacter]);

  return (
    <DndProvider backend={TouchBackend} options={{ enableMouseEvents: true }}>
      <Box className="items-center">{card}</Box>
      <Flex gap={"8"} align={"center"}>
        <Button onClick={sendNo}>no</Button>
        <Button onClick={sendYes}>yes</Button>
      </Flex>
    </DndProvider>
  );
}
