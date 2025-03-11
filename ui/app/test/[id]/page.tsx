import TestBed from "@/app/components/testbed";
import { isMobile } from "@/app/tools/misc";
import { Flex } from "@radix-ui/themes";
import Image from "next/image";

export default async function TestPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const isMb = await isMobile();

  return (
    <>
      <TestBed id={id} isMb={isMb} />
      <Flex className="gap-20 justify-center opacity-50">
        <Flex className="gap-2 items-center text-2xl">
          <Image
            src="/arrow-left.svg"
            alt="Left arrow"
            width={56}
            height={56}
          />
          No
        </Flex>
        <Flex className="gap-2 items-center text-2xl">
          Yes
          <Image
            src="/arrow-right.svg"
            alt="Right arrow"
            width={56}
            height={56}
          />
        </Flex>
      </Flex>
    </>
  );
}
