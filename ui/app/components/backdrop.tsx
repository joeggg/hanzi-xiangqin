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
      <Bin content="No" colour_class="bg-red-200" onDrop={onNo} />
      <Box
        // @ts-expect-error ref
        ref={drag}
        style={{ opacity: collected.isDragging ? 0 : 1 }}
      >
        {children}
      </Box>
      {isMobile && preview.display && (
        // @ts-expect-error ref
        <Box className="items-center" ref={preview.ref} style={preview.style}>
          {children}
        </Box>
      )}
      <Bin content="Yes" colour_class="bg-green-200" onDrop={onYes} />
    </Flex>
  );
}
