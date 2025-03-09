import { Box } from "@radix-ui/themes";
import React from "react";
import { useDrop } from "react-dnd";

export default function Bin({
  content,
  colour_class,
  onDrop,
}: {
  content: string;
  colour_class: string;
  onDrop: () => void;
}) {
  const [collected, noDrop] = useDrop(() => ({
    accept: "card",
    drop: onDrop,
    collect: (monitor) => ({ isOver: monitor.isOver() }),
  }));

  return (
    <Box
      // @ts-expect-error ref
      ref={noDrop}
      width={"50%"}
      className={`${colour_class} text-black text-4xl text-center`}
      content="center"
      style={{ opacity: collected.isOver ? 0.5 : 0 }}
    >
      <strong>{content}</strong>
    </Box>
  );
}
