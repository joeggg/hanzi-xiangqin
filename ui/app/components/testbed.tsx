"use client";

import { JSX, useCallback, useEffect, useState } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { TouchBackend } from "react-dnd-touch-backend";
import { useRouter } from "next/navigation";

import client from "@/app/tools/client";
import { Character } from "@/app/types/character";
import Backdrop from "./backdrop";
import HanziCard from "./card";

export default function TestBed({ id, isMb }: { id: string; isMb: boolean }) {
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
      // @ts-expect-error no type on code
      if (error.status === 404) {
        router.push(`/error?code=notfound`);
      } else {
        router.push(`/error?code=unknown`);
      }
    }
    return null;
  }, [id, router]);

  const sendAnswer = useCallback(
    async (answer: boolean): Promise<undefined> => {
      try {
        await client.post(`/tests/${id}/answer`, { answer });
      } catch {
        router.push(`/error?code=unknown`);
      }

      setCard(<HanziCard />);

      // Small delay to wait for processing
      await new Promise((resolve) => setTimeout(resolve, 100));
      const character = await nextCharacter();
      if (character) {
        setCard(<HanziCard character={character} />);
      }
    },
    [id, router, nextCharacter],
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
    <>
      {isMb && (
        <DndProvider backend={TouchBackend}>
          <Backdrop onNo={sendNo} onYes={sendYes} isMobile={isMb}>
            {card}
          </Backdrop>
        </DndProvider>
      )}
      {!isMb && (
        <DndProvider backend={HTML5Backend}>
          <Backdrop onNo={sendNo} onYes={sendYes} isMobile={isMb}>
            {card}
          </Backdrop>
        </DndProvider>
      )}
    </>
  );
}
