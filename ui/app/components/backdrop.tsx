"use client";

import { Box, Flex } from "@radix-ui/themes";
import { useDrag } from "react-dnd";
import { usePreview } from "react-dnd-preview";

import Bin from "./bin";

export default function Backdrop({
  onYes,
  onNo,
  isMobile,
  children,
}: {
  onYes: () => void;
  onNo: () => void;
  isMobile: boolean;
  children: React.ReactNode;
}) {
  const [collected, drag] = useDrag(() => ({
    type: "card",
    item: { id: 0 },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));
  // Simulates a dragPreview while using touch backend. Set to a copy of the card content
  const preview = usePreview({ placement: "center", padding: { x: 0, y: 0 } });

  return (
    <Flex width={"100%"}>
      <Bin content="No" className="bg-red-200 rounded-r-4xl" onDrop={onNo} />
      <Box
        // @ts-expect-error ref
        ref={drag}
        style={{ opacity: collected.isDragging ? 0 : 1 }}
      >
        {children}
      </Box>
      {isMobile && preview.display && (
        <Box
          className="items-center"
          // @ts-expect-error ref
          ref={preview.ref}
          style={{ ...preview.style, opacity: 0.9 }}
        >
          {children}
        </Box>
      )}
      <Bin
        content="Yes"
        className="bg-green-200 rounded-l-4xl"
        onDrop={onYes}
      />
    </Flex>
  );
}
