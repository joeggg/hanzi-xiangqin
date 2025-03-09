import TestBed from "@/app/components/testbed";
import { isMobile } from "@/app/tools/misc";

export default async function TestPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const isMb = await isMobile();

  return <TestBed id={id} isMb={isMb} />;
}
